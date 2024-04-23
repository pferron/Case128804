"""Runs the scripts for hourly updates"""

import os
import inspect
import socket
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.logging import TheLogs
from common.miscellaneous import Misc
from maintenance_security_exceptions import update_all_snow_exceptions
from alerts_automation_failures import alert_on_failed_runs
from maintenance_snow import process_all_updates

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
    ScrVar.run_hourly_updates()

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def run_hourly_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs our hourly updates"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        update_security_exceptions(main_log,ex_log,ex_file)
        run_snow_maintenance(main_log,ex_log,ex_file)
        send_slack_alerts_for_failed_runs(main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = 0
        exception_count = 0
        if 'FatalCount' in dictionary:
            fatal_count = dictionary['FatalCount']
        if 'ExceptionCount' in dictionary:
            exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ALERT_SOURCE}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def update_security_exceptions(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs SNow security exception maintenance"""
    update_all_snow_exceptions('hourly')

def run_snow_maintenance(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs the SNow portion of CCSX maintenance"""
    try:
        process_all_updates()
    except Exception as e_details:
        func = "process_all_updates() from maintenance_snow.py"
        e_code = "UH-RSM-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3])
        ScrVar.fe_cnt += 1

def send_slack_alerts_for_failed_runs(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Alert for scripts that haven't run"""
    try:
        alert_on_failed_runs('Hourly')
    except Exception as e_details:
        func = "alert_on_failed_runs('Hourly') from alerts_automation_failures.py"
        e_code = "UH-SSAFFR-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3])
        ScrVar.ex_cnt += 1

if __name__ == "__main__":
    main()
