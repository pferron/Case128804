"""Runs the scripts for nightly updates"""

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
from maintenance_database_backups import backup_databases
from maintenance_jira_issues import update_all_jira_issues
from maintenance_checkmarx import run_checkmarx_maintenance
from alerts_automation_failures import alert_on_failed_runs
from tool_checkmarx import all_cx_updates
from tool_mend import MendRepos

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
    TheLogs.log_info(f'Running {ALERT_SOURCE}...',0,None,LOG)
    ScrVar.run_nightly_updates()

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
    def run_nightly_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs our nightly updates"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        do_step = 0
        if socket.gethostname().lower() == 'slc-prdappcmx01':
            do_step += 1
            db_backups = backup_the_database(do_step,main_log,ex_log,ex_file)
            if db_backups is False:
                ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
                return
        do_step += 1
        jiraissues_updates = update_jiraissues_table(do_step,main_log,ex_log,ex_file)
        if jiraissues_updates is False:
            ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
            return
        do_step += 1
        sastprojects = update_sastprojects(do_step,main_log,ex_log,ex_file)
        if sastprojects == 0:
            do_step += 1
            process_sast_reports_and_tickets(do_step,main_log,ex_log,ex_file)
        do_step += 1
        process_os_reports_and_tickets(do_step,main_log,ex_log,ex_file)
        do_step += 1
        update_jiraissues_table(do_step,main_log,ex_log,ex_file)
        send_slack_alerts_for_failed_runs(main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)

    @staticmethod
    def get_message(fatal_count,exception_count,step):
        """Creates the summary message for each step"""
        match step:
            case 1:
                message = "Database backups were successful"
                if fatal_count != 0:
                    message = f"Database backups failed due to {fatal_count} fatal exception(s)"
            case 2:
                message = "JiraIssues successfully updated"
                if fatal_count != 0:
                    message = f"Updates to JiraIssues failed due to {fatal_count} fatal "
                    message += "exception(s)"
            case 3:
                message = "Checkmarx maintenance successfully completed"
                if fatal_count != 0:
                    message = f"Checkmarx maintenance failed due to {fatal_count} fatal "
                    message += "exception(s)"
            case 4:
                message = "SAST findings successfully processed"
                if fatal_count != 0:
                    message = f"Processing of SAST findings failed due to {fatal_count} fatal "
                    message += "exception(s)"
            case 5:
                message = "Open source findings successfully processed"
                if fatal_count != 0:
                    message = f"Processing of open source findings failed due to {fatal_count} "
                    message += "fatal exception(s)"
        if fatal_count == 0 and exception_count != 0:
            message = f"{message}, but {exception_count} exception(s) occurred"
        return message

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
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ScrVar.src}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def backup_the_database(step=1,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Run the database updates"""
    TheLogs.log_headline(f'STEP {step}: RUNNING DATABASE BACKUPS',1,"~",main_log)
    db_backups = backup_databases()
    ScrVar.update_exception_info(db_backups)
    message = ScrVar.get_message(db_backups['FatalCount'],db_backups['ExceptionCount'],1)
    TheLogs.log_info(message,1,"*",main_log)
    if db_backups['FatalCount'] > 0:
        return False
    return True

def update_jiraissues_table(step=2,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates JiraIssues"""
    TheLogs.log_headline(f'STEP {step}: UPDATING JIRA TICKETS IN JiraIssues',1,"~",main_log)
    run = step - 1
    jira_updates = update_all_jira_issues(run=run,)
    ScrVar.update_exception_info(jira_updates)
    message = ScrVar.get_message(jira_updates['FatalCount'],jira_updates['ExceptionCount'],2)
    TheLogs.log_info(message,1,"*",main_log)
    if jira_updates['FatalCount'] > 0:
        return False
    return True

def update_sastprojects(step=3,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates Checkmarx info in the database and performs general maintenance"""
    TheLogs.log_headline(f'STEP {step}: PERFORMING CHECKMARX MAINTENANCE',1,"~",main_log)
    cx_maint = run_checkmarx_maintenance()
    ScrVar.update_exception_info(cx_maint)
    message = ScrVar.get_message(cx_maint['FatalCount'],cx_maint['ExceptionCount'],3)
    TheLogs.log_info(message,1,"*",main_log)
    return cx_maint['FatalCount']

def process_sast_reports_and_tickets(step=4,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates SASTFindings and manages Cx Tickets"""
    TheLogs.log_headline(f'STEP {step}: PROCESSING SAST FINDINGS',1,"~",main_log)
    sast_findings = all_cx_updates()
    ScrVar.update_exception_info(sast_findings)
    message = ScrVar.get_message(sast_findings['FatalCount'],sast_findings['ExceptionCount'],4)
    TheLogs.log_info(message,1,"*",main_log)

def process_os_reports_and_tickets(step=5,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates OSFindings and manages Mend Tickets"""
    TheLogs.log_headline(f'STEP {step}: PROCESSING OPEN SOURCE FINDINGS',1,"~",main_log)
    os_findings = MendRepos.run_all_mend()
    ScrVar.update_exception_info(os_findings)
    message = ScrVar.get_message(os_findings['FatalCount'],os_findings['ExceptionCount'],5)
    TheLogs.log_info(message,1,"*",main_log)

def send_slack_alerts_for_failed_runs(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Alert for scripts that haven't run"""
    try:
        alert_on_failed_runs(ScrVar.today)
    except Exception as e_details:
        func = f"alert_on_failed_runs('{ScrVar.today}') from alerts_automation_failures.py"
        e_code = "UN-SSAFFR-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3])
        ScrVar.ex_cnt += 1

if __name__ == "__main__":
    main()
