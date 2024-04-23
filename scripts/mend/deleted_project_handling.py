"""Queries for handling deleted Mend projects"""

import os
import sys
import inspect
import traceback
from dotenv import load_dotenv
from datetime import datetime
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.logging import TheLogs
from common.database_generic import DBQueries
from common.jira_functions import GeneralTicketing, update_jira_description
from mend.ticket_handling import MendTicketing

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

class DeletedProjects():
    """Stuff you want to call from other scripts"""

    @staticmethod
    def cancel_tickets_for_deleted_projects(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets a list of all OSProjects with wsActive = 0"""
        u_products = []
        TheLogs.log_headline('HANDLING DELETED MEND PROJECTS',2,"#",main_log)
        products = get_deleted_products(main_log,ex_log,ex_file)
        if products != []:
            for product in products:
                c_tickets = []
                finding_cancels = []
                upd_cnt = []
                cncl_cnt = []
                u_cnt = 0
                c_cnt = 0
                p_cnt = 0
                TheLogs.log_info(f'Processing deleted project(s) for {product[0]}',2,"*",main_log)
                projects = get_deleted_project_list(product[0],main_log,ex_log,ex_file)
                TheLogs.log_info('Deleted project(s):',3,"*",main_log)
                for project in projects['ProjectNames']:
                    TheLogs.log_info(f'{project}',4,"-",main_log)
                if projects['ProjectIds'] != '':
                    TheLogs.log_info('Cancelling tickets for deleted project(s):',3,
                                     "*",main_log)
                    tickets = get_tickets_to_cancel(product[0],projects['ProjectIds'],
                                                   main_log,ex_log,ex_file)
                    if tickets != []:
                        for ticket in tickets:
                            cancel_status = 'could not be cancelled'
                            cancelled = False
                            get_projects = get_deleted_project_names_for_ticket(ticket[0],main_log,
                                                                                ex_log,ex_file)
                            deleted_projects = ''
                            if get_projects != []:
                                for project in get_projects:
                                    deleted_projects += f'\n - {project[0]}'
                                comment = "Ticket is being cancelled because the following "
                                comment += "project(s) have been deleted from Mend SCA:"
                                comment += f"{deleted_projects}"
                                try:
                                    cancelled = GeneralTicketing.cancel_jira_ticket(product[0],
                                                                                    ticket[0],
                                                                                    comment)
                                except Exception as e_details:
                                    func = f"GeneralTicketing.cancel_jira_ticket('{product[0]}',"
                                    func += f"'{ticket[0]}','{comment}')"
                                    e_code = 'DPH-CTFDP-001'
                                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                               main_log,ex_file,rf'{ScrVar.src}',
                                                               inspect.stack()[0][3],
                                                               traceback.format_exc())
                                    ScrVar.ex_cnt += 1
                                    continue
                            if cancelled is True:
                                for project in get_projects:
                                    finding_cancels.append({'SET':{'Status':'Closed',
                                                                   'IngestionStatus':'Project Removed',
                                                                   'FoundInLastScan':0},
                                                            'WHERE_EQUAL':{'ProjectName':project[0],
                                                                           'Repo':product[0],
                                                                           'JiraIssueKey':ticket[0]}})
                                    cncl_cnt.append(ticket[0])
                                cancel_status = 'has been cancelled'
                            TheLogs.log_info(f'{ticket[0]} {cancel_status}',4,"-",main_log)
                    else:
                        TheLogs.log_info('No tickets found',4,"-",main_log)
                    TheLogs.log_info('Adding comments to tickets with active & deleted project(s):',
                                     3,"*",main_log)
                    tickets = open_tickets_to_add_comment(product[0],projects['ProjectIds'],
                                                          main_log,ex_log,ex_file)
                    if tickets != []:
                        for ticket in tickets:
                            finding_updates = []
                            updated = set_findings_to_close(ticket[0],projects['ProjectIds'],
                                                            main_log,ex_log,ex_file)
                            if updated is True:
                                get_projects = get_deleted_project_names_for_ticket(ticket[0],
                                                                                    main_log,ex_log,
                                                                                    ex_file)
                                deleted_projects = ''
                                if get_projects != []:
                                    for project in get_projects:
                                        deleted_projects += f'\n - {project[0]}'
                                    comment = "The following project(s) have been deleted from "
                                    comment += "Mend SCA:"
                                    comment += f"{deleted_projects}"
                                    comment += "\n\n Related finding(s) have been removed from "
                                    comment += "this ticket."
                                for project in get_projects:
                                    finding_updates.append({'SET':{'FoundInLastScan':0,
                                                                   'IngestionStatus':'To Update'},
                                                            'WHERE_EQUAL':{'ProjectName':project[0],
                                                                           'Repo':product[0],
                                                                           'JiraIssueKey':ticket[0]}})
                                    c_tickets.append({'SET':{'IngestionStatus':'Project Removed',
                                                             'Status':'Closed'},
                                                      'WHERE_EQUAL':{'ProjectName':project[0],
                                                                     'Repo':product[0],
                                                                     'JiraIssueKey':ticket[0]}})
                                    try:
                                        DBQueries.update_multiple('OSFindings',finding_updates,
                                                                  'AppSec',show_progress=False)
                                    except Exception as e_details:
                                        func = "DBQueries.update_multiple('OSFindings',"
                                        func += f"{finding_updates},'AppSec',show_progress=False)"
                                        e_code = 'DPH-CTFDP-002'
                                        TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                                    main_log,ex_file,rf'{ScrVar.src}',
                                                                    inspect.stack()[0][3],
                                                                    traceback.format_exc())
                                        ScrVar.ex_cnt += 1
                                    upd_cnt.append(ticket[0])
                                deleted_project_ticket_update(product[0],ticket[0],comment,main_log,
                                                              ex_log,ex_file)
                                TheLogs.log_info(f'{ticket[0]}',4,"-",main_log)
                    else:
                        TheLogs.log_info('No tickets found',4,"-",main_log)
                try:
                    DBQueries.update_multiple('OSFindings',finding_cancels,'AppSec',show_progress=False)
                    cncl_cnt = list(dict.fromkeys(cncl_cnt))
                    c_cnt += len(cncl_cnt)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('OSFindings',{finding_cancels},'AppSec',"
                    func += "show_progress=False)"
                    e_code = 'DPH-CTFDP-003'
                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                main_log,ex_file,rf'{ScrVar.src}',
                                                inspect.stack()[0][3],
                                                traceback.format_exc())
                    ScrVar.ex_cnt += 1
                TheLogs.log_info(f'{c_cnt} ticket(s) cancelled',3,"*",main_log)
                try:
                    DBQueries.update_multiple('OSFindings',c_tickets,'AppSec',show_progress=False)
                    upd_cnt = list(dict.fromkeys(upd_cnt))
                    u_cnt += len(upd_cnt)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('OSFindings',{c_tickets},'AppSec',"
                    func += "show_progress=False)"
                    e_code = 'DPH-CTFDP-004'
                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                main_log,ex_file,rf'{ScrVar.src}',
                                                inspect.stack()[0][3],
                                                traceback.format_exc())
                    ScrVar.ex_cnt += 1
                TheLogs.log_info(f'{u_cnt} ticket(s) updated',3,"*",main_log)
                u_products.append({'SET':{'wsDeleted':1,
                                          'wsDeletionDate':f'{BACKUP_DATE}',
                                          'jiraClosedForDeleted':1},
                                   'WHERE_EQUAL':{'wsProductName':product[0],
                                                  'wsActive':0}})
                try:
                    DBQueries.update_multiple('OSProjects',u_products,'AppSec',show_progress=False)
                    p_cnt += len(projects['ProjectNames'])
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('OSProducts',{u_products},'AppSec',"
                    func += "show_progress=False)"
                    e_code = 'DPH-CTFDP-005'
                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                main_log,ex_file,rf'{ScrVar.src}',
                                                inspect.stack()[0][3],
                                                traceback.format_exc())
                    ScrVar.ex_cnt += 1
                TheLogs.log_info(f'{u_cnt} deleted project(s) processed',3,"*",main_log)
        else:
            TheLogs.log_info("No deleted projects to process",2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def get_deleted_products(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Gets a list of repos with deleted projects"""
    product_list = []
    sql = """SELECT DISTINCT wsProductName FROM OSProjects WHERE wsActive = 0 AND
    wsProjectId IN (SELECT DISTINCT ProjectId FROM OSFindings WHERE Status != 'Closed' AND
    JiraIssueKey IS NOT NULL) ORDER BY wsProductName"""
    try:
        product_list = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GDP-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return product_list
    return product_list

def get_deleted_project_list(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Gets a list of repos with deleted projects"""
    project_list = {'ProjectNames':[],'ProjectIds':''}
    sql = f"""SELECT DISTINCT wsProjectName, wsProjectId FROM OSProjects WHERE wsActive = 0 AND
    wsProjectId IN (SELECT DISTINCT ProjectId FROM OSFindings WHERE Status != 'Closed' AND
    JiraIssueKey IS NOT NULL) AND wsProductName = '{repo}' ORDER BY wsProjectName"""
    try:
        get_projects = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GDPL-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return project_list
    if get_projects != []:
        projects = []
        project_ids = []
        for project in get_projects:
            projects.append(project[0])
            project_ids.append(str(project[1]))
        project_ids = ",".join(project_ids)
        project_list = {'ProjectNames':projects,'ProjectIds':project_ids}
    return project_list

def get_tickets_to_cancel(repo,project_ids,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Retrieves a list of open tickets that are eligible to cancel"""
    tickets_to_cancel = []
    sql = f"""SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE Status != 'Closed' AND
    JiraIssueKey IS NOT NULL AND Repo = '{repo}' AND ProjectId IN ({project_ids}) AND
    JiraIssueKey NOT IN (SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE JiraIssueKey IS NOT
    NULL AND ProjectId IN (SELECT DISTINCT wsProjectId FROM OSProjects WHERE wsActive = 1))"""
    try:
        tickets_to_cancel = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GTTC-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return tickets_to_cancel
    return tickets_to_cancel

def open_tickets_to_add_comment(repo,project_ids,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Retrieves a list of open tickets that are not eligible to close because they have findings
    from an active project"""
    tickets_to_comment = []
    sql = f"""SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE Status != 'Closed' AND
    JiraIssueKey IS NOT NULL AND Repo = '{repo}' AND ProjectId IN ({project_ids}) AND
    JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE JiraIssueKey IS NOT
    NULL AND ProjectId IN (SELECT DISTINCT wsProjectId FROM OSProjects WHERE wsActive = 1))"""
    try:
        tickets_to_comment = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GTTC-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return tickets_to_comment
    return tickets_to_comment

def get_deleted_project_names_for_ticket(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,
                                         ex_file=EX_LOG_FILE):
    """Returns a list of deleted project names associated with the ticket"""
    project_names = []
    sql = f"""SELECT DISTINCT ProjectName FROM OSFindings WHERE JiraIssueKey = '{ticket}' AND
    ProjectId IN (SELECT DISTINCT wsProjectId FROM OSProjects WHERE wsActive = 0)"""
    try:
        project_names = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GDPNFT-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return project_names
    return project_names

def set_findings_to_close(ticket,project_list,main_log=LOG,ex_log=LOG_EXCEPTION,
                          ex_file=EX_LOG_FILE):
    """For tickets that have active and deleted projects, set the findings for the deleted
    project(s) to 'To Close' status and change FoundInLastScan to 0"""
    updated = False
    sql = f"""UPDATE OSFindings SET Status = 'Project Deleted', IngestionStatus = 'To Update'
    WHERE JiraIssueKey = '{ticket}' AND ProjectId IN ({project_list})"""
    try:
        DBQueries.update(sql,'AppSec')
        updated = True
    except Exception as e_details:
        e_code = 'DPH-SFTC-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return updated
    return updated

def deleted_project_ticket_update(repo,ticket,comment,main_log=LOG,ex_log=LOG_EXCEPTION,
                                  ex_file=EX_LOG_FILE):
    """Updates a ticket for deleted projects where the ticket has active projects on too"""
    to_update = get_group_and_finding_type(ticket,main_log,ex_log,ex_file)
    if to_update != []:
        description = MendTicketing.create_jira_descriptions(repo,deleted_project=True,
                                                             deleted_to_update=to_update,
                                                             deleted_ticket=ticket)
        if description != []:
            update_jira_description(ticket,repo,description[0]['Description'])
            GeneralTicketing.add_comment_to_ticket(repo,ticket,comment)

def get_group_and_finding_type(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Gets the group_id and finding type for a ticket"""
    needs_tickets = []
    sql = f"SELECT DISTINCT GroupId, FindingType FROM OSFindings WHERE JiraIssueKey = '{ticket}'"
    try:
        tickets_needed = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = 'DPH-GGAFT-001'
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                              rf'{ScrVar.src}',inspect.stack()[0][3],
                              traceback.format_exc())
        ScrVar.ex_cnt += 1
        return needs_tickets
    if tickets_needed != []:
        for ticket in tickets_needed:
            needs_tickets.append({'GroupId': ticket[0],'FindingType': ticket[1]})
    return needs_tickets
