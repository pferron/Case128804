"""Updates the JiraIssues table in the AppSec database"""

import os
import sys
import traceback
import inspect
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from datetime import datetime
from dotenv import load_dotenv
from common.alerts import Alerts
from common.miscellaneous import Misc
from common.logging import TheLogs
from common.general import General
from maint.mend_user_cleanup import MendUsers
from maint.checkmarx_user_cleanup import CxUsers

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []
    u_cnt = 0
    a_cnt = 0

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = dictionary['FatalCount']
        exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        globals()[cmd['function']]()
    # perform_user_maintenance()

def perform_user_maintenance(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Removes accounts from Mend and Checkmarx for users that are no longer with the company"""
    running_function = inspect.stack()[0][3]
    start_timer = Misc.start_timer()
    remove_mend_users(main_log,ex_log,ex_file)
    remove_checkmarx_users(main_log,ex_log,ex_file)
    TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
    TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
    TheLogs.log_headline('RUN SUMMARY',1,'~',main_log)
    TheLogs.log_info(f'Fatal Exceptions: {ScrVar.fe_cnt}',1,'*',main_log)
    TheLogs.log_info(f'Non-fatal Exceptions: {ScrVar.ex_cnt}',1,'*',main_log)
    Misc.end_timer(start_timer,rf'{ALERT_SOURCE}',running_function,ScrVar.ex_cnt,ScrVar.fe_cnt)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def remove_mend_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Processes through Mend users to delete accounts"""
    TheLogs.log_headline('REMOVING MEND ACCOUNTS FOR PAST EMPLOYEES',1,'~',main_log)
    remove_inactive_users = MendUsers.remove_deactivated_users(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(remove_inactive_users)
    if remove_inactive_users['Results'] != []:
        try:
            Alerts.manual_alert(rf'{ALERT_SOURCE}',remove_inactive_users['Results'],
                            len(remove_inactive_users['Results']),23,SLACK_URL)
        except Exception as e_details:
            func = rf"Alerts.manual_alert({ALERT_SOURCE},{remove_inactive_users['Results']},"
            func += f"{len(remove_inactive_users['Results'])},23,{SLACK_URL})"
            e_code = "MTC-PMU-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    return

def remove_checkmarx_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Processes through Checkmarx users to delete accounts"""
    TheLogs.log_headline('REMOVING CHECKMARX ACCOUNTS FOR PAST EMPLOYEES',1,'~',main_log)
    remove_inactive_users = CxUsers.remove_deactivated_users(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(remove_inactive_users)
    if remove_inactive_users['Results'] != []:
        try:
            Alerts.manual_alert(rf'{ALERT_SOURCE}',remove_inactive_users['Results'],
                            len(remove_inactive_users['Results']),24,SLACK_URL)
        except Exception as e_details:
            func = rf"Alerts.manual_alert({ALERT_SOURCE},{remove_inactive_users['Results']},"
            func += f"{len(remove_inactive_users['Results'])},24,{SLACK_URL})"
            e_code = "MTC-PMU-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    return

if __name__ == "__main__":
    main()
