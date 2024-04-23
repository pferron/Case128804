"""Runs maintenance scripts for updating Mend products/projects"""

from datetime import datetime
import os
import sys
import inspect
import traceback
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.jira_functions import GeneralTicketing
from common.logging import TheLogs
from common.database_appsec import select,update,insert
from mend.api_connections import MendAPI

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)


class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    u_cnt = 0
    a_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

class MendMaint():
    """For use from external scripts"""

    @staticmethod
    def get_all_mend_repos(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns a list of repos with Mend projects"""
        repo_list = []
        sql = """SELECT DISTINCT Repo FROM ApplicationAutomation WHERE wsProductToken IS NOT NULL
        ORDER BY Repo"""
        try:
            get_repos = select(sql)
        except Exception as e_details:
            e_code = "MGM-GAMR-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':repo_list}
        if get_repos != []:
            for repo in get_repos:
                repo_list.append(repo[0])
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':repo_list}

    @staticmethod
    def all_mend_maintenance(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Sequentially runs all of the maintenance scripts"""
        update_mend_products(main_log,ex_log,ex_file)
        update_projects(repo,main_log,ex_log,ex_file)
        retire_mend_products(repo,main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_mend_products(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Pulls all Mend projects into OSProjects and
    updates ApplicationAutomation and Applications"""
    u_cnt = 0
    TheLogs.log_headline('UPDATING MEND PRODUCTS IN THE DATABASE',2,"#",main_log)
    try:
        ws_products = MendAPI.get_org_prod_vitals()
    except Exception as e_details:
        func = "MendAPI.get_org_prod_vitals()"
        e_code = "TMM-UMP-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if ws_products != []:
        zero_out_sca(main_log,ex_log,ex_file)
        for item in ws_products:
            repo = item['Repo']
            token = item['wsProductToken']
            r_exists_aa = repo_exists_in_table(repo,'ApplicationAutomation',main_log,ex_log,
                                                   ex_file)
            if r_exists_aa is True:
                set_token_in_table(repo,token,'ApplicationAutomation',main_log,ex_log,ex_file)
            elif r_exists_aa is False:
                if repo is not None and token is not None:
                    insert_token_into_table(repo,token,'ApplicationAutomation',main_log,ex_log,
                                            ex_file)
            r_exists_app = repo_exists_in_table(repo,'Applications',main_log,ex_log,ex_file)
            if r_exists_app is True:
                set_token_in_table(repo,token,'Applications',main_log,ex_log,ex_file)
            elif r_exists_app is False:
                if repo is not None and token is not None:
                    insert_token_into_table(repo,token,'Applications',main_log,ex_log,ex_file)
            u_cnt += 1
        update_tech_debt_boarded(main_log,ex_log,ex_file)
    TheLogs.log_info(f"Product information synced for {u_cnt} repo(s)",2,"*",main_log)

def repo_exists_in_table(repo,table,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Checks to see if the repo is present in the specified table'''
    exists = False
    sql = f"""SELECT Repo FROM {table} WHERE Repo = '{repo}'"""
    try:
        has_repo = select(sql)
    except Exception as e_details:
        e_code = "TMM-REIT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return None
    if has_repo != []:
        exists = True
    return exists

def set_token_in_table(repo,token,table,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Sets product token for Mend by repo in the specified table'''
    if table == 'ApplicationAutomation':
        active_field = 'SCAActive'
    else:
        active_field = 'wsActive'
    sql = f"""UPDATE {table} SET {active_field} = 1, wsProductToken = '{token}'
    WHERE Repo = '{repo}'"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-STIT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def insert_token_into_table(repo,token,table,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
    '''Inserts the repo and token into the specified table'''
    if table == 'ApplicationAutomation':
        active_field = 'SCAActive'
    else:
        active_field = 'wsActive'
    sql = f"""INSERT INTO {table} ({active_field},wsProductToken,Repo)
    VALUES (1,'{token}','{repo}')"""
    try:
        insert(sql)
    except Exception as e_details:
        e_code = "TMM-ITIT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def zero_out_sca(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''sets sca fields to null or 0'''
    sql = """UPDATE ApplicationAutomation SET wsProductToken = NULL,
    SCAActive = 0 UPDATE Applications SET wsProductToken = NULL, wsActive = 0"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-ZOS-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def update_tech_debt_boarded(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''zeroes a NULL tech debt status'''
    sql = """UPDATE ApplicationAutomation SET wsTechDebtBoarded = 0 WHERE wsTechDebtBoarded IS
        NULL"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-STZ-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def retire_mend_products(repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Deletes the Mend project for retired repos and cancels all remaining tickets"""
    TheLogs.log_headline(f'CHECKING {repo} FOR RETIREMENT STATUS',2,"#",main_log)
    retired = get_retire_repo(repo,main_log,ex_log,ex_file)
    if retired:
        for item in retired:
            repo = item[0]
            token = item[1]
            removed = False
            t_array = []
            osprojects_exists = check_osprojects(repo,main_log,ex_log,ex_file)
            if osprojects_exists is True:
                retire_repo_osprojects(repo,main_log,ex_log,ex_file)
            else:
                message = f"THERE ARE NO ENTRIES IN OSProjects for {repo}, "
                message += "MOST LIKELY THERE ARE NO RELEASE BRANCH SCANS."
                TheLogs.log_info(message,2,"#",main_log)
            if token is not None:
                removed = delete_product(token,main_log,ex_log,ex_file)
            if removed is False:
                TheLogs.log_info("Mend product deletion failed",2,"!",main_log)
            else:
                if token is not None:
                    update_osprojs_retired(repo)
                    deactivate_mend(repo,main_log,ex_log,ex_file)
                TheLogs.log_info("Mend product has been deleted",2,"*",main_log)
                TheLogs.log_headline(f'CANCELLING TICKETS FOR {repo}',2,"#",main_log)
                tickets = get_jira_to_retire(repo,main_log,ex_log,ex_file)
                t_cnt = 0
                if tickets:
                    for item in tickets:
                        ticket = item[0]
                        cancelled = cancel_jira_tickets(repo,ticket,main_log,ex_log,ex_file)
                        if cancelled is True:
                            t_cnt += 1
                            t_array.append(ticket)
                TheLogs.log_info(f"{t_cnt} ticket(s) cancelled",2,"*",main_log)
                for tkt in t_array:
                    TheLogs.log_info(tkt,3,"-",main_log)
    else:
        TheLogs.log_info('Repo is not retired',2,"*",main_log)

def check_osprojects(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''checks to see if repo is in OSProjects, if not it means
    only Feature branches have been scanned'''
    exists = False
    sql = f"""SELECT DISTINCT wsProductName FROM OSProjects WHERE wsProductName = '{repo}'"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TMM-COP-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return exists
    if results != []:
        exists = True
    return exists

def get_retire_repo(repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''gets repo and wsProductTokens of retired repos in AA'''
    results = []
    if repo is None:
        sql = """SELECT DISTINCT Repo, wsProductToken FROM ApplicationAutomation
        WHERE Retired = 1 AND wsProductToken IS NOT NULL"""
    else:
        sql = f"""SELECT DISTINCT Repo, wsProductToken FROM ApplicationAutomation
        WHERE Retired = 1 AND Repo = '{repo}' AND wsProductToken IS NOT NULL"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TMM-GRR-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def retire_repo_osprojects(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''sets repo to retired in OSProjects table'''
    sql = f"""UPDATE OSProjects SET RepoRetired = 1 WHERE wsProductName = '{repo}'"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-RROP-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def delete_product(token,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''deletes product in Mend per token'''
    try:
        removed = MendAPI.delete_product(token)
        return removed
    except Exception as e_details:
        func = f"MendAPI.delete_product('{token}')"
        e_code = "TMM-DP-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return False

def deactivate_mend(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''deactivates mend for repo in AA table'''
    sql = f"""UPDATE ApplicationAutomation SET SCAActive = 0, wsProductToken = NULL
    WHERE Repo = '{repo}' UPDATE Applications SET wsActive = 0, wsProductToken = NULL
    WHERE Repo = '{repo}'"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-DM-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def get_jira_to_retire(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''gets list of tickets to retire for repo'''
    results = []
    sql = f"""SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE Repo = '{repo}' AND
            (JiraStatusCategory != 'Done' OR (JiraStatusCategory = 'Done' AND
            RITMTicket IS NOT NULL)) AND Source = 'Mend OS'"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TMM-GJTR-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def cancel_jira_tickets(repo,ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''cancels Jira tickets for retired repo'''
    comment = "ProdSec was informed this repo is retired."
    try:
        cancelled = GeneralTicketing.cancel_jira_ticket(repo,ticket,comment)
        return cancelled
    except Exception as e_details:
        func = f"GeneralTicketing.cancel_jira_ticket('{repo}','{ticket}',"
        func += f"'{comment}')"
        e_code = "TMM-CJT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return False

def update_osprojs_retired(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''sets retired fields in OSProjects table'''
    deleted = datetime.now().strftime("%m/%d/%Y")
    sql = f"""UPDATE OSProjects SET jiraClosedForDeleted = 1, wsDeletionDate =
                '{deleted}', wsDeleted = 1, RepoRetired = 1 WHERE wsProductName = '{repo}'"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-UOPR-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def update_projects(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the OSProjects table in the database"""
    products = get_os_projects(repo,ex_log,ex_file)
    if products:
        zero_active(repo,main_log,ex_log,ex_file)
        for item in products:
            TheLogs.log_headline(f'UPDATING PROJECTS FOR {repo}',2,"#",main_log)
            repo = item[0]
            token = item[1]
            ScrVar.u_cnt = 0
            ScrVar.a_cnt = 0
            ws_projects = get_projects(repo,token,main_log,ex_log,ex_file)
            if ws_projects:
                for project in ws_projects:
                    p_nme = project['wsProjectName']
                    p_token = project['wsProjectToken']
                    p_id = project['wsProjectId']
                    updated = project['wsLastUpdatedDate']
                    p_exists = project_check(p_nme,repo,main_log,ex_log,ex_file)
                    if p_exists is True:
                        if p_token is not None or updated is not None:
                            update_osprojects(p_nme,p_token,p_id,updated,repo,token,main_log,
                                              ex_log,ex_file)
                    else:
                        if p_token is not None or updated is not None:
                            insert_osprojects(p_nme,p_token,p_id,updated,repo,token,main_log,
                                              ex_log,ex_file)
    TheLogs.log_info(f'{ScrVar.u_cnt} project(s) updated',2,"*",main_log)
    TheLogs.log_info(f'{ScrVar.a_cnt} project(s) added',2,"*",main_log)

def get_os_projects(repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''gets repo and wsProductTokens of retired repos in AA'''
    results = []
    if repo is None:
        sql = """SELECT DISTINCT Repo, wsProductToken FROM ApplicationAutomation
        WHERE wsProductToken IS NOT NULL ORDER BY Repo"""
    else:
        sql = f"""SELECT DISTINCT Repo, wsProductToken FROM ApplicationAutomation
        WHERE wsProductToken IS NOT NULL AND Repo = '{repo}' ORDER BY Repo"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TMM-GOP-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def zero_active(repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''zeroes wsActive for one or all OSProjects depending if repo is passed or not'''
    if repo is None:
        sql = "UPDATE OSProjects SET wsActive = 0"
    else:
        sql = f"UPDATE OSProjects SET wsActive = 0 WHERE wsProductName = '{repo}'"
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TMM-ZA-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def get_projects(repo,token,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """gets project details associated with product(repo) from Mend"""
    try:
        ws_projects = MendAPI.get_projects(repo,token)
        return ws_projects
    except Exception as e_details:
        func = "MendAPI.get_projects()"
        e_code = "TMM-GP-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return

def project_check(p_nme,repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''checks to see if project exists in OSProjects table already'''
    exists = False
    sql = f"""SELECT wsProjectName FROM OSProjects WHERE wsProductName = '{repo}'
                    AND wsProjectName = '{p_nme}'"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TMM-PC-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return exists
    if results != []:
        exists = True
    return exists

def update_osprojects(p_nme,p_token,p_id,updated,repo,token,main_log=LOG,ex_log=LOG_EXCEPTION,
                      ex_file=EX_LOG_FILE):
    '''updates existing OSProjects based on what data available'''
    results = 0
    sql = f"UPDATE OSProjects SET wsProductToken = '{token}', wsActive = 1"
    if p_token is not None:
        sql += f", wsProjectToken = '{p_token}'"
    if p_id is not None:
        sql += f", wsProjectId = '{p_id}'"
    if updated is not None:
        sql += f", wsLastUpdatedDate = '{updated}'"
    sql += f" WHERE wsProductName = '{repo}' AND wsProjectName = '{p_nme}'"
    try:
        results += update(sql)
    except Exception as e_details:
        e_code = "TMM-UOP-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    ScrVar.u_cnt += results

def insert_osprojects(p_nme,p_token,p_id,updated,repo,token,main_log=LOG,ex_log=LOG_EXCEPTION,
                      ex_file=EX_LOG_FILE):
    '''inserts new OSProjects if they don't exist'''
    results = 0
    sql = """INSERT INTO OSProjects (wsProductName, wsProductToken,
                            wsProjectName, wsActive, RepoRetired, wsDeleted"""
    sql_values = f") VALUES ('{repo}', '{token}', '{p_nme}', 1, 0, 0"
    if p_token is not None:
        sql += ", wsProjectToken"
        sql_values += f", '{p_token}'"
    if p_id is not None:
        sql += ", wsProjectId"
        sql_values += f", '{p_id}'"
    if updated is not None:
        sql += ", wsLastUpdatedDate"
        sql_values += f", '{updated}'"
    sql = f"{sql}{sql_values})"
    try:
        results += insert(sql)
    except Exception as e_details:
        e_code = "TMM-IOP-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    ScrVar.a_cnt += results
