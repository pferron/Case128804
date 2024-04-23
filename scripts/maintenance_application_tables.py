"""Updates the ApplicationAutomation and Applications tables in the AppSec database"""

import os
import sys
import inspect
import traceback
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from datetime import datetime
from dotenv import load_dotenv
from common.miscellaneous import Misc
from common.logging import TheLogs
from common.general import General
from common.alerts import Alerts
from common.jira_functions import GeneralTicketing
from common.database_generic import DBQueries
from common.bitbucket import BitBucket
from maint.application_tables_database_queries import AppQueries

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
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        globals()[cmd['function']]()
    # update_all_application_tables()

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

def update_all_application_tables(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Sequentially runs all updates"""
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    bitbucket_updates(main_log,ex_log,ex_file)
    get_jira_from_progteams(main_log,ex_log,ex_file)
    set_security_finding_status(main_log,ex_log,ex_file)
    set_jira_project_name(main_log,ex_log,ex_file)
    progteam_info_sync(main_log,ex_log,ex_file)
    applications_table_sync(main_log,ex_log,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt}

def bitbucket_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates BitBucket information in the ApplicationAutomation table"""
    repo_cnt = 0
    TheLogs.log_headline('UPDATING BITBUCKET INFORMATION IN ApplicationAutomation',2,"#",main_log)
    bb_updates = BitBucket.update_bitbucket(main_log=main_log,ex_log=ex_log,ex_file=ex_file)
    ScrVar.update_exception_info(bb_updates)
    TheLogs.log_info(f"{bb_updates['UpdatedRepos']} repo(s) updated",2,"*",main_log)
    if bb_updates['AddedRepos'] != []:
        added_repos = sorted(set(bb_updates['AddedRepos']))
        repo_cnt += len(added_repos)
    a_lng = f"{repo_cnt} repo(s) added"
    TheLogs.log_info(a_lng,2,"*",main_log)
    if repo_cnt > 0:
        for item in added_repos:
            TheLogs.log_info(item,3,"-",main_log)
        try:
            sent = Alerts.manual_alert(rf'{ScrVar.src}',added_repos,repo_cnt,7,SLACK_URL)
            if sent != 1:
                raise Exception
        except Exception as e_details:
            e_code = "MAT-BU-001"
            func = f"Alerts.manual_alert('{rf'{ScrVar.src}'}',{added_repos},{repo_cnt},7,{SLACK_URL})"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1

def get_jira_from_progteams(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """If JiraProjectKey and/or JiraIssueParentKey is null in ApplicationAutomation, but ProgTeam
    is set, try to get the Jira information from ProgTeams"""
    u_cnt = 0
    update_array = []
    to_update = AppQueries.get_available_progteam_jira_updates(main_log)
    ScrVar.update_exception_info(to_update)
    if to_update['Results'] != []:
        TheLogs.log_headline('ATTEMPTING TO RETRIEVE JIRA INFO FROM ProgTeams',2,"#",main_log)
        for item in to_update['Results']:
            repo = item[0]
            team = item[1]
            updates = AppQueries.get_jira_keys_for_team(team,main_log)
            ScrVar.update_exception_info(updates)
            if updates['Results'] != []:
                if len(updates['Results']) == 1:
                    project_key = updates['Results'][0][0]
                    parent_key = updates['Results'][0][1]
                    update_array.append({'SET': {'JiraProjectKey': project_key,
                                                 'JiraIssueParentKey': parent_key},
                                         'WHERE_EQUAL': {'Repo': repo,
                                                         'ProgTeam': team},
                                         'WHERE_NOT': None})
        try:
            u_cnt += DBQueries.update_multiple('ApplicationAutomation',update_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-GJFP-001"
            func = f"DBQueries.update_multiple('ApplicationAutomation',{update_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
    u_lng = f"{u_cnt} repo(s) updated"
    TheLogs.log_info(u_lng, 2, "*", main_log)

def set_security_finding_status(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Checks to make sure each Jira project key has a Security Finding ticket type"""
    u_cnt = 0
    update_array = []
    TheLogs.log_headline('CHECKING ALL JIRA PROJECTS FOR SECURITY FINDING TICKET TYPE',2,"#",
                         main_log)
    get_keys = AppQueries.get_applicationautomation_jira_project_keys(main_log)
    ScrVar.update_exception_info(get_keys)
    if get_keys['Results'] != []:
        reset_array = [{'SET': {'HasJiraSecurityFindingType': 0},
                        'WHERE_NOT': {'JiraProjectKey': None}}]
        try:
            u_cnt += DBQueries.update_multiple('ApplicationAutomation',reset_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-SSFS-001"
            func = f"DBQueries.update_multiple('ApplicationAutomation',{reset_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        for key in get_keys['Results']:
            proj_key = key[0]
            sf_value = 0
            try:
                has_sf = GeneralTicketing.verify_security_finding_type(proj_key)
            except Exception as e_details:
                func = f"GeneralTicketing.verify_security_finding_type('{proj_key}')"
                e_code = "MAT-SSFS-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if has_sf is True:
                sf_value = 1
            update_array.append({'SET': {'HasJiraSecurityFindingType': sf_value},
                                         'WHERE_EQUAL': {'JiraProjectKey': proj_key}})
        try:
            u_cnt += DBQueries.update_multiple('ApplicationAutomation',update_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-SSFS-002"
            func = f"DBQueries.update_multiple('ApplicationAutomation',{update_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
    u_lng = f"{u_cnt} repo(s) updated"
    TheLogs.log_info(u_lng,2,"*",main_log)

def set_jira_project_name(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the Jira project name in the ApplicationAutomation table"""
    u_cnt = 0
    update_array = []
    TheLogs.log_headline('UPDATING JIRA PROJECT NAMES',2,"#",main_log)
    get_keys = AppQueries.get_applicationautomation_jira_project_keys(main_log)
    ScrVar.update_exception_info(get_keys)
    if get_keys['Results'] != []:
        for item in get_keys['Results']:
            proj_name = None
            proj_key = item[0]
            try:
                proj_name = GeneralTicketing.get_project_name(proj_key)
            except Exception as e_details:
                e_code = "MAT-SJPN-001"
                func = f"GeneralTicketing.get_project_name('{proj_key})"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if proj_name is not None:
                update_array.append({'SET': {'JiraProjectName': proj_name},
                                            'WHERE_EQUAL': {'JiraProjectKey': proj_key},
                                            'WHERE_NOT': None})
        try:
            u_cnt += DBQueries.update_multiple('ApplicationAutomation',update_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-SJPN-002"
            func = f"DBQueries.update_multiple('ApplicationAutomation',{update_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
    u_lng = f"{u_cnt} repo(s) updated"
    TheLogs.log_info(u_lng,2,"*",main_log)

def progteam_info_sync(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the ProgTeam, ProductOwner (ProductManager), and TechLead"""
    u_cnt = 0
    update_array = []
    TheLogs.log_headline('SYNCING INFO FROM ProgTeams TO ApplicationAutomation',2,"#",main_log)
    get_keys = AppQueries.get_applicationautomation_jira_project_keys(main_log)
    ScrVar.update_exception_info(get_keys)
    if get_keys['Results'] != []:
        for item in get_keys['Results']:
            proj_key = item[0]
            get_teams = AppQueries.get_progteams_teams(proj_key,main_log)
            ScrVar.update_exception_info(get_teams)
            if get_teams['Results'] != []:
                if len(get_teams['Results']) == 1:
                    proj_name = get_teams['Results'][0][0]
                    tech_lead = get_teams['Results'][0][1]
                    prod_owner = get_teams['Results'][0][2]
                    update_array.append({'SET': {'ProgTeam': proj_name,
                                                'TechLead': tech_lead,
                                                'ProductOwner': prod_owner},
                                                'WHERE_EQUAL': {'JiraProjectKey': proj_key}})
        try:
            u_cnt += DBQueries.update_multiple('ApplicationAutomation',update_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-PIS-001"
            func = f"DBQueries.update_multiple('ApplicationAutomation',{update_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
    u_lng = f"{u_cnt} repo(s) updated"
    TheLogs.log_info(u_lng,2,"*",main_log)

def applications_table_sync(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Syncs relevant data to the Applications table"""
    u_cnt = 0
    update_array = []
    TheLogs.log_headline('SYNCING INFO FROM ApplicationAutomation TO Applications',2,"#",main_log)
    get_info = AppQueries.get_applicationautomation_data(main_log)
    ScrVar.update_exception_info(get_info)
    if get_info['Results'] != []:
        for item in get_info['Results']:
            update_array.append({'SET': {'HasJiraSecurityFindingType': item[1],
                                        'cxProjectID': item[2],
                                        'cxLastScanID': item[3],
                                        'LastSASTScanDate': item[4],
                                        'TechDebtBoarded': item[5],
                                        'SASTAutomationEnabled': item[6],
                                        'CxActive': item[7],
                                        'ProductOwner': item[8],
                                        'TechLead': item[9],
                                        'wsActive': item[10],
                                        'wsProductToken': item[11],
                                        'wsLastUpdatedDate': item[12],
                                        'wsVulnTechDebtBoarded': item[13],
                                        'wsLicenseTechDebtBoarded': item[14],
                                        'wsTechDebtBoarded': item[15],
                                        'Retired': item[16],
                                        'ManualRetired': item[17]},
                                        'WHERE_EQUAL': {'Repo': item[0]},
                                        'WHERE_NOT': None})
        try:
            u_cnt += DBQueries.update_multiple('Applications',update_array,'AppSec',
                                                show_progress=False,update_to_null=False)
        except Exception as e_details:
            e_code = "MAT-ATS-001"
            func = f"DBQueries.update_multiple('Applications',{update_array},'AppSec',"
            func += "show_progress=False,update_to_null=False)"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
    u_lng = f"{u_cnt} repo(s) updated"
    TheLogs.log_info(u_lng,2,"*",main_log)

if __name__ == "__main__":
    main()
