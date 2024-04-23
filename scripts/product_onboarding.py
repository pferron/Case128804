"""Runs all necessary scripts to maintain Mend info in the database and related Jira tickets. Run update_all for both Mend and Checkmarx scripts. Run update_checkmarx for just Checkmarx. Run update_mend for just Mend"""

import os
import sys
import inspect
import traceback
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from tool_mend import MendRepos
from tool_checkmarx import single_project_updates
from special_run_after_checkmarx_updates import update_all_scans
from checkmarx.api_connections import CxAPI
from common.logging import TheLogs
from common.database_sql_server_connection import SQLServerConnection
from common.general import General

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
conn = SQLServerConnection(source=ALERT_SOURCE,log_file=LOG_FILE, exception_log_file=EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        # else:
        #     globals()[cmd['function']]()
    # update_all('appsec-ops')
    # update_checkmarx('appsec-ops')
    # update_mend('appsec-ops',LOG)

def update_all(repo,main_log=LOG):
    """Runs updates for Checkmarx and Mend for the specified repo"""
    update_checkmarx(repo,main_log)
    update_mend(repo)

def update_checkmarx(repo,main_log=LOG):
    """Run required updates for Checkmarx for the specified repo"""
    TheLogs.log_headline(f'RUNNING CHECKMARX UPDATES FOR {repo}',1,"#",LOG)
    get_proj_id = project_id(repo)
    proj_id = project_id_transform(get_proj_id)
    if proj_id != '' and proj_id is not None:
        repo_exists_aa = repo_check_aa(repo, main_log)
        if repo_exists_aa:
            update_aa_table(proj_id, repo, main_log)
        repo_exists_app = repo_check_app(repo, main_log)
        if repo_exists_app:
            update_app_table(proj_id, repo, main_log)
    single_project_onboard(repo, proj_id, main_log)
    TheLogs.log_headline("CHECKMARX UPDATES COMPLETE",1,"#",LOG)

def project_id(repo):
    """gets the project ID from Checkmarx if it exists"""
    try:
        get_proj_id = CxAPI.get_repo_project_id(repo, 52)
        return get_proj_id
    except Exception as details:
        details = str(details)
        details += "\nRunning Function:\n"
        details += f"CxAPI.get_repo_project_data('{repo}', 52)"
        e_code = "PO-UC-001"
        TheLogs.exception(details,e_code,LOG_EXCEPTION,LOG,EX_LOG_FILE,rf'{ALERT_SOURCE}',
                          inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return

def project_id_transform(get_proj_id):
    """gets cxProjectId from returned get_repo_project_data in project_id()"""
    if get_proj_id != [] and get_proj_id is not None:
        proj_id = get_proj_id['cxProjectId']
        return proj_id
    else:
        return "No or None proj ID"

def repo_check_aa(repo, main_log=LOG):
    '''checks to see if repo exists in ApplicationAutomation table'''
    conn.func = 'repo_check_aa'
    sql = f"SELECT Repo FROM ApplicationAutomation WHERE Repo = '{repo}'"
    results = conn.query_with_logs(sql, main_log)
    results = sql_success_check(results)
    return results

def update_aa_table(proj_id, repo, main_log=LOG):
    '''updates the AA table'''
    conn.func = 'update_aa_table'
    sql = f"""UPDATE ApplicationAutomation SET cxProjectId = '{proj_id}', cxTeam = 52,
    SASTActive = 1 WHERE Repo = '{repo}'"""
    results = conn.query_with_logs(sql, main_log)
    results = sql_success_check(results)
    if results > 0:
        TheLogs.log_info("cxProjectId updated in ApplicationAutomation",1,"*",LOG)
    return results

def repo_check_app(repo, main_log=LOG):
    '''checks to see if repo exists in ApplicationAutomation table'''
    conn.func = 'repo_check_app'
    sql = f"""SELECT Repo FROM Applications WHERE Repo = '{repo}'"""
    results = conn.query_with_logs(sql, main_log)
    results = sql_success_check(results)
    return results

def update_app_table(proj_id, repo, main_log=LOG):
    '''updates the Applications table'''
    conn.func = 'update_app_table'
    sql = f"""UPDATE Applications SET cxProjectID = '{proj_id}', CxTeam = 52,
            CxActive = 1 WHERE Repo = '{repo}'"""
    results = conn.query_with_logs(sql, main_log)
    results = sql_success_check(results)
    if results > 0:
        TheLogs.log_info("cxProjectId updated in Applications table",1,"*",LOG)
    return results

def single_project_onboard(repo, proj_id, main_log):
    '''runs single_project_updates from tool_checkmarx'''
    try:
        single_project_updates(repo, proj_id, 1, main_log)
    except Exception as details:
        func = f"single_project_updates('{repo}', {proj_id}, 1, '{main_log}')"
        e_code = "PO-UC-006"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,LOG,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        ScrVar.ex_array.append(e_code)

def update_mend(repo,main_log=LOG):
    """Run required updates for Mend SCA for the specified repo"""
    TheLogs.log_headline(f'RUNNING MEND SCA UPDATES FOR {repo}',1,"#",main_log)
    try:
        MendRepos.onboard_single_repo(repo,main_log)
    except Exception as details:
        details = str(details)
        details += "\nRunning Function:\n"
        details += f"MendRepos.onboard_single_repo('{repo}','{main_log}')"
        e_code = "PO-UM-001"
        TheLogs.exception(details,e_code,LOG_EXCEPTION,LOG,EX_LOG_FILE,rf'{ALERT_SOURCE}',
                          inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return
    TheLogs.log_headline('MEND UPDATES COMPLETE',1,"#",main_log)

def checkmarx_update_run(repo,main_log=LOG):
    """If Checkmarx has been updated and a pipeline is being blocked for a repo, run this"""
    update_all_scans(repo,main_log)

def sql_success_check(results):
    '''checks to see if sql call was successful'''
    if isinstance(results,int) or 'SQL-CONNECT-01' not in results:
        return results
    else:
        ScrVar.fe_cnt += results[0]
        ScrVar.fe_array.append(results[1])
        return None

if __name__ == "__main__":
    main()
