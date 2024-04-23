"""Processing of weekly Slack alerts"""

import os
import sys
import inspect
import traceback
from datetime import datetime
from dotenv import load_dotenv
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from automation_alerts.weekly_database_queries import WADatabase
from common.database_generic import DBQueries
from common.jira_functions import GeneralTicketing
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.alerts import Alerts
from common.general import General

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_CX = os.environ.get('SLACK_URL_CX')

def main():
    "Default stuff"
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' not in cmd:
            globals()[cmd['function']]()
    # WeeklyAlerts.process_all_alerts()

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        if isinstance(dictionary,dict):
            if ('FatalCount' in dictionary and
                isinstance(dictionary['FatalCount'],int)):
                ScrVar.fe_cnt += dictionary['FatalCount']
            if ('ExceptionCount' in dictionary and
                isinstance(dictionary['ExceptionCount'],int)):
                ScrVar.ex_cnt = dictionary['ExceptionCount']

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

class WeeklyAlerts():
    """For executing from other files"""
    @staticmethod
    def process_all_alerts(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        "Runs all of the functions included in this script to generate weekly alerts"
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        missing_jira_info(main_log,ex_log,ex_file)
        missing_sf_ticket_type(main_log,ex_log,ex_file)
        missing_cx_baseline_scans(main_log,ex_log,ex_file)
        overdue_cx_baseline_scans(main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def verify_sf_exists(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Verify Security Finding issue type exists"""
    aa_cnt = 0
    a_cnt = 0
    u_array = []
    TheLogs.log_headline('UPDATING HasJiraSecurityFindingType IN THE DATABASE',2,"#",
                        main_log)
    proj_keys = WADatabase.get_unique_jira_keys(main_log)
    ScrVar.update_exception_info(proj_keys)
    if proj_keys['Results'] != []:
        for proj in proj_keys['Results']:
            try:
                has_sf = GeneralTicketing.has_sf_ticket_type(proj)
            except Exception as e_details:
                func = f"GeneralTicketing.has_sf_ticket_type('{proj}')"
                e_code = "AW-VSE-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            u_array.append({'SET': {'HasJiraSecurityFindingType': has_sf},
                            'WHERE_EQUAL': {'JiraProjectKey': proj},
                            'WHERE_NOT': None})
    try:
        aa_cnt += DBQueries.update_multiple('ApplicationAutomation',u_array,'AppSec',
                                            show_progress=False)
    except Exception as e_details:
        func = f"DBQueries.update_multiple('ApplicationAutomation',{u_array},'AppSec',"
        func += "show_progress=False)"
        e_code = "AW-VSE-002"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    try:
        a_cnt += DBQueries.update_multiple('Applications',u_array,'AppSec',
                                            show_progress=False)
    except Exception as e_details:
        func = f"DBQueries.update_multiple('Applications',{u_array},'AppSec',"
        func += "show_progress=False)"
        e_code = "AW-VSE-003"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f'Line(s) updated in ApplicationAutomation: {aa_cnt}',2,"*",main_log)
    TheLogs.log_info(f'Line(s) updated in Applications: {a_cnt}',2,"*",main_log)

def missing_jira_info(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Creates an alert for repo(s) missing Jira info"""
    TheLogs.log_headline('CHECKING REPOS FOR MISSING JIRA INFO',2,"#",main_log)
    cnt = 0
    missing_info = WADatabase.get_repos_missing_jira_info(main_log)
    ScrVar.update_exception_info(missing_info)
    if missing_info['Results'] != []:
        cnt += len(missing_info['Results'])
    if cnt != 0:
        try:
            sent = Alerts.manual_alert(rf'{ScrVar.src}',missing_info['Results'],cnt,16,SLACK_URL)
            if sent != 1:
                raise Exception
            TheLogs.log_info('Slack alert sent',2,"*",main_log)
        except Exception as e_details:
            func = rf"Alerts.manual_alert('{ScrVar.src}',{missing_info['Results']},{cnt},16,"
            func += f"'{SLACK_URL}')"
            e_code = "AW-MJI-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                       traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    else:
        TheLogs.log_info('No Slack alert needed',2,"*",main_log)

def missing_sf_ticket_type(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks Repos that are setup in Mend SCA and/or Checkmarx for a Security Finding
    issue type in Jira and returns a list of Repos missing that type"""
    verify_sf_exists(main_log,ex_log,ex_file)
    cnt = 0
    TheLogs.log_headline('CHECKING REPOS FOR MISSING SECURITY FINDING ISSUE TYPE',2,"#",main_log)
    missing_sf = WADatabase.get_projects_missing_security_finding_type(main_log)
    ScrVar.update_exception_info(missing_sf)
    if missing_sf['Results'] != []:
        cnt += len(missing_sf['Results'])
    if cnt != 0:
        try:
            sent = Alerts.manual_alert(rf'{ScrVar.src}',missing_sf['Results'],cnt,17,SLACK_URL)
            if sent != 1:
                raise Exception
            TheLogs.log_info('Slack alert sent',2,"*",main_log)
        except Exception as e_details:
            func = rf"Alerts.manual_alert('{ScrVar.src}',{missing_sf['Results']},{cnt},17,"
            func += f"'{SLACK_URL}')"
            e_code = "AW-MSTT-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                       traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    else:
        TheLogs.log_info('No Slack alert needed',2,"*",main_log)

def missing_cx_baseline_scans(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks if a repo has a pipeline scan but is missing a baseline scan"""
    cnt = 0
    TheLogs.log_headline('CHECKING FOR MISSING CHECKMARX BASELINE SCANS',2,"#",main_log)
    missing_bl = WADatabase.get_missing_baseline_scans(main_log)
    ScrVar.update_exception_info(missing_bl)
    if missing_bl['Results'] != []:
        cnt += len(missing_bl['Results'])
    if cnt != 0:
        try:
            sent = Alerts.manual_alert(rf'{ScrVar.src}',missing_bl['Results'],cnt,19,SLACK_URL_CX)
            if sent != 1:
                raise Exception
            TheLogs.log_info('Slack alert sent',2,"*",main_log)
        except Exception as e_details:
            func = rf"Alerts.manual_alert('{ScrVar.src}',{missing_bl['Results']},{cnt},19,"
            func += f"'{SLACK_URL_CX}')"
            e_code = "AW-MCBS-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                       traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    else:
        TheLogs.log_info('No Slack alert needed',2,"*",main_log)

def overdue_cx_baseline_scans(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks if a repo has had a baseline scan in the past 7 days"""
    cnt = 0
    TheLogs.log_headline('CHECKING FOR OVERDUE CHECKMARX BASELINE SCANS',2,"#",main_log)
    overdue_bl = WADatabase.get_baselines_with_overdue_scans(main_log)
    ScrVar.update_exception_info(overdue_bl)
    if overdue_bl['Results'] is not None:
        cnt += overdue_bl['Count']
    if cnt != 0:
        try:
            sent = Alerts.manual_alert(rf'{ScrVar.src}',[],cnt,18,SLACK_URL_CX,
                                       column_layout=overdue_bl['Results'])
            if sent != 1:
                raise Exception
            TheLogs.log_info('Slack alert sent',2,"*",main_log)
        except Exception as e_details:
            func = rf"Alerts.manual_alert('{ScrVar.src}',[],{cnt},18,"
            func += f"'{SLACK_URL_CX}',column_layout='{overdue_bl['Results']}')"
            e_code = "AW-OCBS-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                       traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    else:
        TheLogs.log_info('No Slack alert needed',2,"*",main_log)

if __name__ == "__main__":
    main()
