"""Runs the scripts for nightly updates"""

import os
import inspect
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.logging import TheLogs
from common.miscellaneous import Misc
from alerts_team_notifs import class_setup
from alerts_weekly import WeeklyAlerts
from maintenance_checkmarx_license_check import verify_checkmarx_license
from maintenance_log_cleanup import LogCleanup
from maintenance_script_stats import ScriptStats

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
    ScrVar.run_morning_updates()

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
    def run_morning_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs our morning updates"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        new_ticket_slack_notifications('daily',1,main_log,ex_log,ex_file)
        checkmarx_hid_license_check(2,main_log,ex_log,ex_file)
        update_script_runtime_stats(3,main_log,ex_log,ex_file)
        ScrVar.run_day_of_the_week_scripts(ScrVar.today,4,main_log,ex_log,ex_file)
        TheLogs.log_headline('ALL MORNING UPDATE STEPS COMPLETE',1,"~",main_log)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)

    @staticmethod
    def run_day_of_the_week_scripts(day_name,step,main_log=LOG,ex_log=LOG_EXCEPTION,
                                    ex_file=EX_LOG_FILE):
        """For running scripts that only need to execute on a particular day"""
        match day_name:
            case "Monday":
                new_ticket_slack_notifications('daily',step,main_log,ex_log,ex_file)
                TheLogs.log_headline(f'STEP {step+1}: BEGIN PROCESSING WEEKLY ALERTS',1,"~",main_log)
                WeeklyAlerts.process_all_alerts(main_log)
            case "Thursday":
                TheLogs.log_headline(f'STEP {step}: BEGIN PROCESSING WEEKLY ALERTS',1,"~",main_log)
                LogCleanup.all_maintenance(main_log=main_log)

    @staticmethod
    def get_message(fatal_exceptions,exception_count):
        """Creates the summary message for each step"""
        message = "Step was run successfully"
        if fatal_exceptions != 0:
            message = f"Step failed due to {fatal_exceptions} fatal exception(s)"
        if fatal_exceptions == 0 and exception_count != 0:
            message = f"{message}, but {exception_count} exception(s) occurred"
        return message

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

def new_ticket_slack_notifications(period='daily',step=1,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Creates Slack alerts for new tickets"""
    fatal_error = 0
    TheLogs.log_headline(f'STEP {step}: BEGIN NEW TICKET SLACK NOTIFICATION SCRIPT',1,"~",main_log)
    try:
        class_setup(period)
    except Exception as e_details:
        func = f"class_setup('{period}')"
        e_code = "UM-NTSN-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3])
        ScrVar.fe_cnt += 1
        fatal_error = 1
    message = ScrVar.get_message(fatal_error,0)
    TheLogs.log_info(message,1,"*",main_log)

def checkmarx_hid_license_check(step=2,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks to see if HID changed on Checkmarx server"""
    fatal_error = 0
    TheLogs.log_headline(f'STEP {step}: BEGIN HID LICENSE CHECKMARX CHECK',1,"~",main_log)
    try:
        verify_checkmarx_license()
    except Exception as e_details:
        func = "verify_checkmarx_license()"
        e_code = "UM-CHLC-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3])
        ScrVar.fe_cnt += 1
        fatal_error = 1
    message = ScrVar.get_message(fatal_error,0)
    TheLogs.log_info(message,1,"*",main_log)

def update_script_runtime_stats(step=3,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks to see if HID changed on Checkmarx server"""
    TheLogs.log_headline(f'STEP {step}: BEGIN ScriptExecutionAverageRunTimes UPDATES',1,"~",
                         main_log)
    run_script = ScriptStats.update_run_times()
    message = ScrVar.get_message(run_script['FatalCount'],run_script['ExceptionCount'])
    TheLogs.log_info(message,1,"*",main_log)

if __name__ == "__main__":
    main()
