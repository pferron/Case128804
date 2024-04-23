"""Runs the scripts for non-prodsec updates"""

import os
import inspect
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.logging import TheLogs
from common.miscellaneous import Misc
from nonprodsec_infosecdashboard import infosecdashboard_updates
from nonprodsec_bitsight import BitSight
from nonprodsec_knowbe4 import process_knowbe4_updates

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs the specified stuff"""
    ScrVar.run_nonprodsec_updates()

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    u_cnt = 0
    a_cnt = 0
    today = datetime.now().strftime('%A')
    start_timer = None
    src = ALERT_SOURCE.replace("-","\\")
    running_function = ''

    @staticmethod
    def run_nonprodsec_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs daily updates for non-ProdSec stuff"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        update_infosecdashboard_database(1,main_log,ex_log,ex_file)
        update_bitsight_database(2,main_log,ex_log,ex_file)
        update_knowbe4_database(3,main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_message(fatal_count,exception_count):
        """Creates the summary message for each step"""
        message = "Updates were successful"
        if fatal_count != 0 and exception_count == 0:
            message = f"Updates failed due to {fatal_count} exception(s)"
        elif fatal_count != 0 and exception_count != 0:
            message = f"Updates failed due to {fatal_count} exception(s) and an additional "
            message += f"{exception_count} exception(s) occurred"
        elif fatal_count == 0 and exception_count != 0:
            message = f"{message}, but {exception_count} exception(s) occurred"
        return message

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        Misc.end_timer(ScrVar.start_timer,rf'{ALERT_SOURCE}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def update_infosecdashboard_database(step=1,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs updates for the InfoSecDashboard database"""
    TheLogs.log_headline(f'STEP {step}: RUNNING UPDATES FOR InfoSecDashboard',1,"~",main_log)
    isd_updates = infosecdashboard_updates(main_log)
    message = ScrVar.get_message(isd_updates['FatalCount'],isd_updates['ExceptionCount'])
    TheLogs.log_info(message,1,"*",main_log)

def update_bitsight_database(step=2,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs updates for the BitSight database"""
    TheLogs.log_headline(f'STEP {step}: RUNNING UPDATES FOR BitSight',1,"~",main_log)
    bs_updates = BitSight.update_all_bitsight(main_log)
    message = ScrVar.get_message(bs_updates['FatalCount'],bs_updates['ExceptionCount'])
    TheLogs.log_info(message,1,"*",main_log)

def update_knowbe4_database(step=3,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs updates for the KnowBe4 database"""
    TheLogs.log_headline(f'STEP {step}: RUNNING UPDATES FOR KnowBe4',1,"~",main_log)
    kb4_updates = process_knowbe4_updates(main_log)
    message = ScrVar.get_message(kb4_updates['FatalCount'],kb4_updates['ExceptionCount'])
    TheLogs.log_info(message,1,"*",main_log)

if __name__ == "__main__":
    main()
