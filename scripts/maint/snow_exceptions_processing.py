"""SNow related queries for the AppSec database"""

import os
import traceback
import inspect
from datetime import datetime
from dotenv import load_dotenv
from common.alerts import Alerts
from common.logging import TheLogs
from common.database_appsec import select,update,delete_row,update_multiple_in_table
from common.database_generic import DBQueries
from common.general import General
from common.jira_functions import GeneralTicketing
from maint.snow_exceptions_database_queries import SNowQueries
from checkmarx.pipeline_sync import CxPipelines
from checkmarx.api_connections import CxAPI
from mend.api_connections import MendAPI
from maintenance_jira_issues import update_jira_project_tickets

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_SNOW_EXCEPTIONS')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

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

class SNowProc():
    """SNow related queries for the AppSec database"""

    @staticmethod
    def alerts_for_missing_jira_tickets(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''If an active RITM does not have Jira tickets associated with it, send a Slack alert'''
        column_layout = ''
        updates = []
        log_message = 'Slack alert not needed - no active RITM tickets missing Jira tickets'
        get_alerts = General.do_script_query(2,main_log)
        ScrVar.update_exception_info(get_alerts)
        if get_alerts['Results'] != []:
            column_layout = 'slack_headers:\\RITM Ticket\\Contact(s)'
            for item in get_alerts['Results']:
                ticket_link = "<https://progleasing.service-now.com/nav_to.do"
                ticket_link += f"?uri=%2Fsc_req_item.do%3Fsys_id%3D{item[1]}|{item[0]}>"
                contact = f'{item[3]} and {item[4]}'
                if item[3] == item[4]:
                    contact = item[3]
                column_layout += f'\n{ticket_link} ({item[2]})\\{contact}'
            try:
                send_alert = Alerts.manual_alert(rf'{ScrVar.src}',None,len(get_alerts['Results']),
                                                 30,SLACK_URL,column_layout=column_layout)
            except Exception as e_details:
                func = rf"Alerts.manual_alert('{ScrVar.src}',None,{len(get_alerts['Results'])},"
                func += f"30,'{SLACK_URL}',column_layout={column_layout})"
                e_code = "SEP-AFMJT-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
            if send_alert != 0:
                log_message = f"Slack alert issued for {len(get_alerts['Results'])} RITM tickets "
                log_message == "missing Jira tickets"
                for item in get_alerts['Results']:
                    updates.append({'SET':{'MissingJiraNotifSent':1},
                                    'WHERE_EQUAL':{'RITMTicket': item[0]}})
                    TheLogs.log_info(f"-  {item[0]}",3,"*",main_log)
                try:
                    DBQueries.update_multiple('SNowSecurityExceptions',updates,'AppSec',
                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('SNowSecurityExceptions',{updates},'AppSec',"
                    func += "show_progress=False)"
                    e_code = "SEP-AFMJT-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                rf'{ScrVar.src}',inspect.stack()[0][3],
                                                traceback.format_exc())
                    ScrVar.ex_cnt += 1
        TheLogs.log_info(log_message,2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def alerts_for_pending_approvals(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''If there are approvals pending, send an alert to Slack'''
        result = []
        updates = []
        ScrVar.reset_exception_counts()
        get_alerts = General.do_script_query(1,main_log)
        ScrVar.update_exception_info(get_alerts)
        if get_alerts['Results'] != []:
            for item in get_alerts['Results']:
                ticket_link = "<https://progleasing.service-now.com/nav_to.do"
                ticket_link += f"?uri=%2Fsc_req_item.do%3Fsys_id%3D{item[1]}|{item[0]}>"
                due_dt = datetime.strptime(str(item[3]),'%Y-%m-%d %H:%M:%S')
                due = due_dt.strftime('%m-%d-%Y')
                result.append({'RITM Ticket':ticket_link,
                            'Requested For': item[4],
                            'Escalation':item[2],
                            'Approval Due By':due,
                            'RITMTicketNo':item[0]})
            try:
                Alerts.manual_alert(rf'{ScrVar.src}',result,len(result),27,SLACK_URL)
            except Exception as e_details:
                func = rf"Alerts.manual_alert('{ScrVar.src}',{result},{len(result)},27,'{SLACK_URL}')"
                e_code = "SEP-AFPA-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        log_message = 'Slack alert not needed - no RITM tickets pending approval'
        if len(result) > 0:
            log_message = f'Slack alert issued for {len(result)} RITM tickets pending approval'
        TheLogs.log_info(log_message,2,"*",main_log)
        for item in result:
            updates.append({'SET':{'NotifSent':1},
                            'WHERE_EQUAL':{'RITMTicket': item['RITMTicketNo']}})
            TheLogs.log_info(f"-  {item['RITMTicketNo']}",3,"*",main_log)
        DBQueries.update_multiple('SNowSecurityExceptions',updates,'AppSec',3,show_progress=True)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':{}}

    @staticmethod
    def sync_with_jiraissues(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Syncs RITM tickets to JiraIssues, Jira tickets to SNowSecurityExceptions,
        and then handles Jira ticket updates'''
        ScrVar.reset_exception_counts()
        TheLogs.log_headline('SYNCING RITM TICKETS FROM SNowSecurityExceptions TO JiraIssues',3,
                             "*",main_log)
        sync_ritms_from_snowsecurityexceptions_to_jiraissues(main_log,ex_log,ex_file)
        TheLogs.log_headline('SYNCING RITM TICKETS FROM JiraIssues TO SNowSecurityExceptions',3,
                             "*",main_log)
        sync_ritms_from_jiraissues_to_snowsecurityexceptions(main_log,ex_log,ex_file)
        TheLogs.log_headline('REMOVING NON-PRODSEC RITM TICKETS FROM SNowSecurityExceptions',3,
                             "*",main_log)
        remove_non_appsec_ritms(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':{}}

    @staticmethod
    def update_tool_and_jira_exceptions(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates Jira tickets, the tool's results, and associated tables"""
        ScrVar.reset_exception_counts()
        update_unprocessed_exceptions('Checkmarx',main_log,ex_log,ex_file)
        update_unprocessed_exceptions('Mend OS',main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':{}}

def sync_ritms_from_snowsecurityexceptions_to_jiraissues(main_log=LOG,ex_log=LOG_EXCEPTION,
                                                         ex_file=EX_LOG_FILE):
    '''If an Exception is active (approved and not expired) or is awaiting approval,
    ensures the RITM is logged in JiraIssues'''
    ritm_sse_by_type_sync('ticket',main_log,ex_log,ex_file)
    ritm_sse_by_type_sync('repo',main_log,ex_log,ex_file)

def ritm_sse_by_type_sync(type,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''If an Exception is active (approved and not expired) or is awaiting approval,
    ensures the RITM is logged in JiraIssues'''
    updated = 0
    if type == 'ticket':
        key_field = """JiraTickets"""
        msg_lng = " for ticket-based exceptions"
    elif type == 'repo':
        key_field = """AppliesToFullRepo"""
        msg_lng = " for repo-based exceptions"
    else:
        e_details = f"The type parameter of '{type}' is not valid. Only 'ticket' or 'repo' may "
        e_details += "be passed through to this function."
        func = f"ritm_sse_by_type_sync('{type}')"
        e_code = "SEP-RSBTS-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3])
        ScrVar.fe_cnt += 1
        return
    sql = f"""SELECT RITMTicket, {key_field}, ExceptionStandard, ApprovedByName FROM
    SNowSecurityExceptions WHERE {key_field} IS NOT NULL AND ApprovalStatus != 'Rejected' AND
    (ExceptionExpirationDate > GETDATE() OR ExceptionExpirationDate IS NULL) AND Status NOT IN
    ('Canceled By User','Closed Incomplete')"""
    if type == 'ticket':
        sql += """ AND AppliesToFullRepo IS NULL"""
    try:
        to_update = select(sql)
    except Exception as e_details:
        e_code = "SEP-RSBTS-002"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if to_update != []:
        for item in to_update:
            update_items = []
            approved = None
            if item[3] is not None:
                approved = 1
            if type == 'ticket':
                if item[1] is not None:
                    if "," in item[1]:
                        for tkt in item[1].split(','):
                            update_items.append(tkt)
                    else:
                        update_items.append(item[1])
                for ticket in update_items:
                    sql = f"""UPDATE JiraIssues SET RITMTicket = '{item[0]}', ExceptionApproved =
                    {approved} WHERE (JiraIssueKey = '{ticket}' OR OldJiraIssueKey = '{ticket}') AND
                    (RITMTicket != '{item[0]}' OR RITMTicket IS NULL OR ExceptionApproved !=
                    {approved} OR ExceptionApproved IS NULL) AND JiraStatusCategory != 'Done'"""
                    try:
                        update(sql)
                        updated += 1
                    except Exception as e_details:
                        e_code = "SEP-RSBTS-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              rf'{ScrVar.src}',inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
            elif type == 'repo':
                if item[1] is not None:
                    if "," in item[1]:
                        for rep in item[1].split(','):
                            update_items.append(rep)
                    else:
                        update_items.append(item[1])
                for repo in update_items:
                    sql = f"""UPDATE JiraIssues SET RITMTicket = '{item[0]}', ExceptionApproved =
                    {approved} WHERE Repo = '{repo}' AND JiraStatusCategory != 'Done'"""
                    try:
                        update(sql)
                        updated += 1
                    except Exception as e_details:
                        e_code = "SEP-RSBTS-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              rf'{ScrVar.src}',inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
    TheLogs.log_info(f'{updated} Jira ticket(s) updated in JiraIssues{msg_lng}',3,"*",main_log)

def sync_ritms_from_jiraissues_to_snowsecurityexceptions(main_log=LOG,ex_log=LOG_EXCEPTION,
                                                         ex_file=EX_LOG_FILE):
    '''If an RITM is logged in JiraIssues but not noted in SNowSecurityExceptions, this will
    add it to the JiraTicket field in SNowSecurityExceptions'''
    updated = 0
    sql = """SELECT DISTINCT RITMTicket FROM JiraIssues WHERE RITMTicket IS NOT NULL"""
    try:
        ritms_logged = select(sql)
    except Exception as e_details:
        e_code = "SEP-SRFJTS-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if ritms_logged != []:
        for ritm in ritms_logged:
            jira_tickets = ritm_jira_tickets(ritm[0],main_log,ex_log,ex_file)
            if jira_tickets is not None:
                sql = f"""UPDATE SNowSecurityExceptions SET JiraTickets = '{jira_tickets}'
                WHERE RITMTicket = '{ritm[0][0]}'"""
                try:
                    update(sql)
                    updated += 1
                except Exception as e_details:
                    e_code = "SEP-SRFJTS-002"
                    TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                          rf'{ScrVar.src}',inspect.stack()[0][3],
                                          traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
    TheLogs.log_info(f'{updated} RITM ticket(s) updated in SNowSecurityExceptions',3,"*",main_log)

def remove_non_appsec_ritms(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Deletes RITMS FROM SNowSecurityExceptions that do not include IS18.x AND do not have Jira
    tickets in the JiraIssues table'''
    count = 0
    sql = """DELETE FROM SNowSecurityExceptions WHERE JiraTickets IS NULL AND ExceptionStandard
    NOT LIKE 'IS18%'"""
    try:
        count += delete_row(sql)
    except Exception as e_details:
        e_code = "SEP-RNAR-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    TheLogs.log_info(f'{count} non-ProdSec RITMs removed',3,"*",main_log)

def get_all_jiraissues(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Get a full list of JiraIssueKey and OldJiraIssueKey entries from JiraIssues'''
    full_list = []
    sql = """SELECT DISTINCT JiraIssueKey, OldJiraIssueKey FROM JiraIssues ORDER BY JiraIssueKey,
    OldJiraIssueKey"""
    try:
        get_all_issues = select(sql)
    except Exception as e_details:
        e_code = "SEP-RTJI-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return full_list
    if get_all_issues != []:
        for item in get_all_issues:
            if item[0] is not None and item[0] not in full_list:
                full_list.append(item[0])
            if item[1] is not None and item[1] not in full_list:
                full_list.append(item[1])
    return full_list

def ritm_jira_tickets(ritm_ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Returns a list of Jira tickets from JiraIssues that are associated with an RITM ticket'''
    ticket_list = None
    sql = f"""SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE RITMTicket = '{ritm_ticket}'"""
    try:
        jira_tickets = select(sql)
    except Exception as e_details:
        e_code = "SEP-RJT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return ticket_list
    if jira_tickets != []:
        ticket_list = []
        for ticket in jira_tickets:
            ticket_list.append(ticket[0])
        ticket_list = sorted(set(ticket_list))
        ticket_list = ','.join(ticket_list)
    return ticket_list

def update_unprocessed_exceptions(tool,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Identifies exceptions that need to be updated in their respective tool and/or table(s) and
    then executes updates, if needed"""
    select_fields = ''
    join_tables = ''
    items = []
    TheLogs.log_headline(f'UPDATING EXCEPTIONS FOR {tool.upper()} FINDINGS',2,"#",main_log)
    if tool.lower() == 'checkmarx':
        select_fields = ', SASTFindings.JiraIssueKey, SASTFindings.ExceptionPipelineSync, '
        select_fields += 'SASTFindings.Status, SASTFindings.cxResultState, '
        select_fields += 'SASTFindings.cxProjectID, SASTFindings.cxResultID'
        join_tables = """JOIN SASTFindings ON SASTFindings.JiraIssueKey = JiraIssues.JiraIssueKey
        OR SASTFindings.JiraIssueKey = JiraIssues.OldJiraIssueKey """
    elif tool.lower() == 'mend os':
        select_fields = ', OSFindings.JiraIssueKey, OSFindings.FindingType, '
        select_fields += 'OSFindings.AlertStatus, OSFindings.AlertUuid, OSFindings.Status, '
        select_fields += 'JiraIssues.JiraStatusCategory, OSProjects.wsProjectToken'
        join_tables = """JOIN OSFindings ON OSFindings.JiraIssueKey = JiraIssues.JiraIssueKey
        OR OSFindings.JiraIssueKey = JiraIssues.OldJiraIssueKey JOIN OSProjects ON
        OSProjects.wsProjectId = OSFindings.ProjectId """
    else:
        e_details = f"The tool parameter of '{tool}' is not valid. Only 'checkmarx' or "
        e_details += "'mend os' may be passed through to this function."
        func = f"ritm_sse_by_type_sync('{tool}')"
        e_code = "SEP-UUE-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3])
        ScrVar.fe_cnt += 1
        return
    sql = f"""SELECT DISTINCT JiraIssues.Repo, JiraIssues.JiraDueDate,
    JiraIssues.RITMTicket, SNowSecurityExceptions.ExceptionExpirationDate,
    SNowSecurityExceptions.ExceptionStandard, SNowSecurityExceptions.ExceptionDuration,
    SNowSecurityExceptions.ApprovedDate {select_fields} FROM JiraIssues JOIN SNowSecurityExceptions
    ON SNowSecurityExceptions.RITMTicket = JiraIssues.RITMTicket {join_tables}WHERE
    JiraIssues.RITMTicket IS NOT NULL AND JiraIssues.ExceptionApproved = 1 AND
    (JiraIssues.JiraDueDate > GETDATE() OR SNowSecurityExceptions.ExceptionExpirationDate >
    GETDATE())"""
    if tool.lower() == 'checkmarx':
        sql += """ AND SASTFindings.Status NOT LIKE '%Closed%' AND (SASTFindings.Status NOT IN
        ('Accepted','False Positive','Not Exploitable') OR SASTFindings.ExceptionPipelineSync IS
        NULL OR SASTFindings.ExceptionPipelineSync != 1 OR SASTFindings.cxResultState !=
        'Confirmed') AND SASTFindings.FoundInLastScan = 1"""
    elif tool.lower() == 'mend os':
        sql += """ AND ((OSFindings.Status NOT LIKE '%Closed%' AND (OSFindings.Status  NOT IN
        ('Accepted','False Positive','No Fix Available') OR OSFindings.AlertStatus NOT IN
        ('Ignored','Library Removed') OR OSFindings.AlertStatus IS NULL) AND
        OSFindings.FoundInLastScan = 1) OR (OSFindings.FindingType = 'License Violation')) AND
        ProjectId NOT IN (SELECT DISTINCT wsProjectID FROM OSProjects WHERE wsActive = 0)"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "SEP-UUE-002"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if tool.lower() == 'checkmarx':
        items = []
        for item in results:
            ex_due = None
            if item[3] is not None:
                ex_due = str(item[3])
            items.append({'Repo':item[0],
                            'JiraDue':str(item[1]),
                            'RITMTicket':item[2],
                            'ExceptionDue':ex_due,
                            'ExStandard':item[4],
                            'ExDuration':item[5],
                            'ApprovedDate':item[6],
                            'JiraTicket':item[7],
                            'PipelineSync':item[8],
                            'Status':item[9],
                            'cxState':item[10],
                            'cxProjectID':item[11],
                            'cxScanId':item[12].split("-",1)[0],
                            'cxPathId':item[12].split("-",1)[1]})
        process_checkmarx_exceptions(items,main_log,ex_log,ex_file)
    elif tool.lower() == 'mend os':
        items = []
        for item in results:
            ex_due = None
            if item[3] is not None:
                ex_due = str(item[3])
            items.append({'Repo':item[0],
                            'JiraDue':str(item[1]),
                            'RITMTicket':item[2],
                            'ExceptionDue':ex_due,
                            'ExStandard':item[4],
                            'ExDuration':item[5],
                            'ApprovedDate':item[6],
                            'JiraTicket':item[7],
                            'Type':item[8],
                            'mStatus':item[9],
                            'mAlert':item[10],
                            'Status':item[11],
                            'JiraStatus':item[12],
                            'ProjectToken':item[13]})
        process_mend_exceptions(items,main_log,ex_log,ex_file)

def process_checkmarx_exceptions(array,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Identifies and executes changes that need to be made for Checkmarx exceptions"""
    u_due = 0
    u_finding = 0
    u_pipeline = 0
    u_status = 0
    status_updates = []
    res_updates = []
    for item in array:
        if item['JiraDue'] != item['ExceptionDue']:
            try:
                comment = f"Security exception {item['RITMTicket']} to {item['ExStandard']} was "
                comment += f"approved for {item['ExDuration']} month(s) on {item['ApprovedDate']}."
                comment += f" Due date is extended to {item['ExceptionDue']}."
                GeneralTicketing.update_ticket_due(item['JiraTicket'],item['Repo'],
                                                   item['ExceptionDue'],comment)
                u_due += 1
            except Exception as e_details:
                func = f"GeneralTicketing.update_ticket_due('{item['JiraTicket']}',"
                func += f"'{item['Repo']}','{item['ExceptionDue']}','{comment}')"
                e_code = "SEP-PCE-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
        if item['cxState'] != 'Confirmed':
            comment = f"Covered by {item['RITMTicket']}, due {item['ExceptionDue']}."
            try:
                CxAPI.update_res_state(item['cxScanId'],item['cxPathId'],2,comment)
                u_finding += 1
                res_updates.append({'SET':{'cxResultState':'Confirmed','cxResultStateValue':2},
                                    'WHERE_EQUAL':{'cxProjectID':item['cxProjectID'],
                                                   'JiraIssueKey':item['JiraTicket'],
                                            'cxResultID':f"{item['cxScanId']}-{item['cxPathId']}"}})
            except Exception as e_details:
                func = f"CxAPI.update_res_state('{item['cxScanId']}','{item['cxPathId']}',2,"
                func += f"'{comment}')"
                e_code = "SEP-PCE-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
        if item['PipelineSync'] is not True:
            u_pipeline += 1
        if item['Status'] != 'Accepted':
            status_updates.append({'SET':{'Status':'Accepted'},
                                   'WHERE_EQUAL':{'JiraIssueKey':item['JiraTicket']}})
        if u_pipeline > 0:
            try:
                u_pipeline = CxPipelines.sync_state_to_pipeline('Accepted',item['cxProjectID'],
                                                                main_log,ex_log,ex_file,False)
            except Exception as e_details:
                func = f"CxPipelines.sync_state_to_pipeline('Accepted','{item['cxProjectID']}'"
                e_code = "SEP-PCE-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
    try:
        update_multiple_in_table('SASTFindings',status_updates,show_progress=False)
        u_status = len(status_updates)
    except Exception as e_details:
        func = f"update_multiple_in_table('SASTFindings',{status_updates},show_progress=False)"
        e_code = "SEP-PCE-004"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('SASTFindings',res_updates,show_progress=False)
        u_finding = len(res_updates)
    except Exception as e_details:
        func = f"update_multiple_in_table('SASTFindings',{res_updates},show_progress=False)"
        e_code = "SEP-PCE-005"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f'Due date updated in {u_due} Jira tickets',2,"*",main_log)
    TheLogs.log_info(f'Alert status updated in Checkmarx for {u_finding} findings',2,"*",main_log)
    TheLogs.log_info(f'Pipeline sync completed for {u_pipeline} findings',2,"*",main_log)
    TheLogs.log_info(f'Status updated in SASTFindings for {u_status} findings',2,"*",main_log)

def process_mend_exceptions(array,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Identifies and executes changes that need to be made for Mend SCA exceptions"""
    u_due = 0
    c_tickets = 0
    u_alert = 0
    u_status = 0
    tickets_to_close = []
    closed_tickets = []
    due_updated = []
    ji_repo_updates = []
    u_alerts_table = []
    u_alerts_findings = []
    u_status_findings = []
    for item in array:
        if item['JiraDue'] != item['ExceptionDue'] and item['JiraTicket'] not in due_updated:
            try:
                comment = f"Security exception {item['RITMTicket']} to {item['ExStandard']} was "
                comment += f"approved for {item['ExDuration']} month(s) on {item['ApprovedDate']}."
                comment += f" Due date is extended to {item['ExceptionDue']}."
                if item['Type'] == 'License Violation':
                    comment = None
                GeneralTicketing.update_ticket_due(item['JiraTicket'],item['Repo'],
                                                   item['ExceptionDue'],comment)
                ji_repo_updates.append(item['Repo'])
                due_updated.append(item['JiraTicket'])
            except Exception as e_details:
                func = f"GeneralTicketing.update_ticket_due('{item['JiraTicket']}',"
                func += f"'{item['Repo']}','{item['ExceptionDue']}','{comment}')"
                e_code = "SEP-PME-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
        if item['JiraStatus'] != 'Done' and item['Type'] == 'License Violation':
            tickets_to_close.append({'Repo':item['Repo'],'JiraTicket':item['JiraTicket']})
        if item['mStatus'].lower() != 'ignored':
            alert_comment = f"Exception {item['RITMTicket']} was approved on "
            alert_comment += f"{item['ApprovedDate']}. Finding will be ignored until exception "
            alert_comment += f"expires on {item['ExceptionDue']}."
            try:
                updated = MendAPI.update_alert_status(item['ProjectToken'],item['mAlert'],
                                                      'IGNORED',alert_comment)
                if updated is True:
                    u_alerts_table.append({'SET':{'AlertStatus':'Ignored',
                                                  'JiraIssueKey':item['JiraTicket']},
                                                  'WHERE_EQUAL':{'AlertUuid':item['mAlert'],
                                                                 'ProjectToken':item['ProjectToken']}})
                    u_alerts_findings.append({'SET':{'AlertStatus':'Ignored'},
                                              'WHERE_EQUAL':{'AlertUuid':item['mAlert'],
                                                             'Repo':item['Repo']}})
            except Exception as details:
                func = f"MendAPI.update_alert_status('{item['ProjectToken']}','{item['mAlert']}',"
                func += f"'Active','{alert_comment}')"
                e_code = "TCAC-PME-002"
                TheLogs.function_exception(func,e_code,details,ex_log,main_log,
                                            ex_file)
                ScrVar.ex_cnt += 1
        if item['Status'] != 'Accepted':
            u_status_findings.append({'SET':{'Status':'Accepted'},
                                      'WHERE_EQUAL':{'JiraIssueKey':item['JiraTicket'],
                                                     'FoundInLastScan':1}})
    values = []
    close_tickets = []
    for item in tickets_to_close:
        if not item['JiraTicket'] in values:
            close_tickets.append({'Repo':item['Repo'],'JiraTicket':item['JiraTicket']})
            values.append(item['JiraTicket'])
    for ticket in close_tickets:
        comment = ''
        if any(d['JiraTicket'] == ticket['JiraTicket'] for d in array):
            item = [e for e in array if e['JiraTicket'] == ticket['JiraTicket']][0]
            comment = f"License exception {item['RITMTicket']} to {item['ExStandard']} "
            comment += f"was approved for {item['ExDuration']} month(s) on "
            comment += f"{item['ApprovedDate']}. Ticket is being closed, but will reopen "
            comment += f"when the exception expires on {item['ExceptionDue']}."
        closed = GeneralTicketing.close_jira_ticket(ticket['Repo'],ticket['JiraTicket'],comment)
        if closed is True:
            closed_tickets.append(ticket['JiraTicket'])
    c_tickets = len(closed_tickets)
    u_due = len(due_updated)
    try:
        update_multiple_in_table('OSAlerts',u_alerts_table,show_progress=False)
        u_alert = len(u_alerts_table)
    except Exception as e_details:
        func = f"update_multiple_in_table('OSAlerts',{u_alerts_table},show_progress=False)"
        e_code = "SEP-PME-004"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSFindings',u_alerts_findings,show_progress=False)
    except Exception as e_details:
        func = f"update_multiple_in_table('OSFindings',{u_alerts_findings},show_progress=False)"
        e_code = "SEP-PME-004"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSFindings',u_status_findings,show_progress=False)
        u_status = len(u_status_findings)
    except Exception as e_details:
        func = f"update_multiple_in_table('OSFindings',{u_status_findings},show_progress=False)"
        e_code = "SEP-PME-004"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    ji_repo_updates = sorted(set(ji_repo_updates))
    for repo in ji_repo_updates:
        ticket_updates = update_jira_project_tickets(repo,main_log,ex_log,ex_file)
        ScrVar.update_exception_info(ticket_updates)
    TheLogs.log_info(f'Due date updated in {u_due} Jira tickets',2,"*",main_log)
    TheLogs.log_info(f'{c_tickets} Jira tickets temporarily closed for license violations',2,"*",
                     main_log)
    for item in closed_tickets:
        TheLogs.log_info(f"   -  {item}",2,None,main_log)
    TheLogs.log_info(f'Alert status updated in Mend for {u_alert} findings',2,"*",main_log)
    TheLogs.log_info(f'Status updated in OSFindings for {u_status} findings',2,"*",main_log)
