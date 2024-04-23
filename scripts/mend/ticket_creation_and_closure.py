"""Runs maintenance scripts for updating Mend reports"""

import os
import sys
import inspect
import traceback
from datetime import datetime, timedelta
from common.jira_functions import GeneralTicketing
from common.logging import TheLogs
from common.database_appsec import select,insert,update
from maintenance_jira_issues import update_jiraissues_for_tool_and_repo
from mend.api_connections import MendAPI
from mend.ticket_handling import MendTicketing
parent = os.path.abspath('.')
sys.path.insert(1,parent)

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

class ScrVar():
    """Script-wide stuff"""
    process_product = 1
    fe_cnt = 0
    ex_cnt = 0
    u_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class MendTickets():
    """Handles reopening, closing, and opening of Jira tickets for Mend products/projects."""

    @staticmethod
    def single_repo_ticketing(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Sequentially cycles through the necessary functions for creating, updating, and closing
        tickets for a single repos"""
        ScrVar.reset_exception_counts()
        TheLogs.log_headline(f'PROCESSING MEND/JIRA TICKETING FOR {repo}',2,"#",main_log)
        create_tickets = True
        update_jiraissues(repo,main_log,ex_log,ex_file)
        no_jira = cannot_ticket(repo,main_log,ex_log,ex_file)
        no_tickets = do_not_ticket(repo,main_log,ex_log,ex_file)
        on_hold = project_on_hold(repo,main_log,ex_log,ex_file)
        if no_jira is True or no_tickets is True or on_hold is True:
            create_tickets = False
        if create_tickets is True:
            process_closed_tickets(repo,main_log,ex_log,ex_file)
            close_jira_tickets(repo,main_log,ex_log,ex_file)
            create_and_update_tickets(repo,main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_jiraissues(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """For single repo ticketing, updates JiraIssues for the repo"""
    sql = f"SELECT JiraProjectKey FROM ApplicationAutomation WHERE Repo = '{repo}'"
    try:
        get_pk = select(sql)
    except Exception as e_details:
        e_code = "TCAC-UJI-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if get_pk != []:
        TheLogs.log_headline(f"UPDATING JiraIssues FOR {repo}",3,"#",main_log)
        update_jiraissues_for_tool_and_repo(repo,'mend os',main_log,ex_log,ex_file)
        TheLogs.log_info("JiraIssues has been updated",3,"*",main_log)

def cannot_ticket(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Determines if the repo has the required Jira information in ApplicationAutomation to
    handle ticketing"""
    no_jira = False
    ScrVar.u_cnt = 0
    sql = f"""SELECT DISTINCT Repo FROM ApplicationAutomation WHERE Repo = '{repo}' AND
    (JiraIssueParentKey IS NULL OR JiraProjectKey IS NULL)"""
    try:
        ticketing_info = select(sql)
    except Exception as e_details:
        e_code = "TCAC-CT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return no_jira
    if ticketing_info != []:
        ScrVar.u_cnt += update_cannot_osfindings(repo,main_log,ex_log,ex_file)
        no_jira = True
    if ScrVar.u_cnt != 0:
        TheLogs.log_headline(f"NO JIRA INFORMATION ON FILE FOR {repo}",3,"!",main_log)
        TheLogs.log_info(f"{ScrVar.u_cnt} finding(s) marked as Cannot Ticket",3,"!",main_log)
    return no_jira

def update_cannot_osfindings(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Updates Status to Cannot Ticket in OSFindings'''
    results = 0
    sql = f"UPDATE OSFindings SET Status = 'Cannot Ticket' WHERE Repo = '{repo}'"
    try:
        results += update(sql)
    except Exception as e_details:
        e_code = "TCAC-UCO-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def do_not_ticket(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Determines if the repo is marked as ExcludeTickets or ExcludeScans in ApplicationAutomation
    and sets the status to Do Not Ticket for findings"""
    ScrVar.u_cnt = 0
    no_tickets = False
    sql = f"""SELECT Repo FROM ApplicationAutomation WHERE Repo = '{repo}' AND ((ExcludeScans = 1
    AND ExcludeScans IS NOT NULL) OR (ExcludeTickets = 1 AND ExcludeTickets IS NOT NULL))"""
    try:
        ticketing_info = select(sql)
    except Exception as e_details:
        e_code = "TCAC-DNT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return no_tickets
    if ticketing_info:
        ScrVar.u_cnt += update_osfindings_dont_ticket(repo,main_log,ex_log,ex_file)
        no_tickets = True
    if ScrVar.u_cnt != 0:
        TheLogs.log_headline(f"{repo} IS DESIGNATED TO EXCLUDE SCANS/TICKETS",3,"!",main_log)
        TheLogs.log_info(f"{ScrVar.u_cnt} finding(s) marked as Do Not Ticket",3,"!",main_log)
    return no_tickets

def update_osfindings_dont_ticket(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Updates Status to Do Not Ticket in OSFindings'''
    results = 0
    sql = f"UPDATE OSFindings SET Status = 'Do Not Ticket' WHERE Repo = '{repo}'"
    try:
        results += update(sql)
    except Exception as e_details:
        e_code = "TCAC-UODT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def project_on_hold(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Determines if the repo is marked as ProjectOnHold in ApplicationAutomation and sets the
    status to Project On Hold for findings"""
    ScrVar.u_cnt = 0
    on_hold = False
    sql = f"""SELECT Repo FROM ApplicationAutomation WHERE Repo = '{repo}' AND ProjectOnHold = 1
    AND ProjectOnHold IS NOT NULL"""
    try:
        ticketing_info = select(sql)
    except Exception as e_details:
        e_code = "TCAC-POH-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return on_hold
    if ticketing_info != []:
        ScrVar.u_cnt += update_osfindings_poh(repo,main_log,ex_log,ex_file)
        on_hold = True
    if ScrVar.u_cnt != 0:
        TheLogs.log_headline(f"{repo} IS DESIGNATED AS ON HOLD",3,"!",main_log)
        TheLogs.log_info(f"{ScrVar.u_cnt} finding(s) marked as Project On Hold",3,"!",main_log)
    return on_hold

def update_osfindings_poh(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Updates Status to Project On Hold in OSFindings'''
    results = 0
    sql = f"UPDATE OSFindings SET Status = 'Do Not Ticket' WHERE Repo = '{repo}'"
    try:
        results += update(sql)
    except Exception as e_details:
        e_code = "TCAC-UOPOH-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def close_jira_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """If a ticket has no open findings, close or cancel it"""
    c_cnt = 0
    c_tickets = []
    TheLogs.log_headline(f"CLOSING/CANCELLING ELIGIBLE TICKETS FOR {repo}",3,"#",main_log)
    sql = f"""SELECT DISTINCT JiraIssueKey, Status FROM OSFindings WHERE Repo = '{repo}' AND
    Status != 'Closed' AND IngestionStatus NOT IN ('Closed','False Positive','Project Removed')
    AND FoundInLastScan = 0 AND JiraIssueKey IS NOT NULL AND JiraIssueKey NOT IN (SELECT DISTINCT
    JiraIssueKey FROM OSFindings WHERE FoundInLastScan = 1 AND JiraIssueKey IS NOT NULL AND
    Status != 'Closed')"""
    try:
        to_close = select(sql)
    except Exception as e_details:
        e_code = "TCAC-CJT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if to_close != []:
        for tkt in to_close:
            comment = "Finding(s) in this ticket are no longer reported by Mend SCA."
            if tkt[1] in ('False Positive','Not Exploitable'):
                comment = "Finding(s) in this ticket have been marked as False Positive by the "
                comment += "ProdSec team."
            if tkt[1] == 'No Fix Available':
                comment = "No fix is currently available to remediate this finding."
            try:
                closed = GeneralTicketing.close_or_cancel_jira_ticket(repo,tkt[0],comment,'Mend OS')
            except Exception as e_details:
                func = f"GeneralTicketing.close_or_cancel_jira_ticket('{repo}','{tkt[0]}',"
                func += f"'{comment}','Mend OS')"
                e_code = "TCAC-CJT-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           ScrVar.src,inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if closed is True:
                c_cnt += 1
                c_tickets.append(tkt[0])
                sql = f"""UPDATE OSFindings SET IngestionStatus = 'Closed', Status =
                'Closed' WHERE JiraIssueKey = '{tkt[0]}' AND Status NOT IN ('False Positive',
                'No Fix Available')
                UPDATE OSFindings SET IngestionStatus = 'Closed' WHERE JiraIssueKey =
                '{tkt[0]}' AND Status IN ('False Positive','No Fix Available')"""
                try:
                    update(sql)
                except Exception as e_details:
                    e_code = "TCAC-CJT-003"
                    TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                            inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.ex_cnt += 1
        proj_key = get_project_key(repo,main_log,ex_log,ex_file)
        if proj_key is not None:
            update_jiraissues_for_tool_and_repo(repo,'mend os',main_log,ex_log,ex_file)
    TheLogs.log_info(f"{c_cnt} ticket(s) closed",3,"*",main_log)
    if c_cnt > 0:
        if c_tickets != []:
            for tkt in c_tickets:
                TheLogs.log_info(tkt,4,"-",main_log)

def get_project_key(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Returns the JiraProjectKey for a Repo'''
    project_key = None
    sql = f"""SELECT DISTINCT JiraProjectKey FROM ApplicationAutomation WHERE Repo = '{repo}'
    AND JiraProjectKey IS NOT NULL"""
    try:
        get_pk = select(sql)
    except Exception as e_details:
        e_code = "TCAC-GPK-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return project_key
    if get_pk != []:
        project_key = get_pk[0][0]
    return project_key

def process_closed_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """For tickets closed outside of the automation, reactivate alerts and remove the finding"""
    a_cnt = 0
    TheLogs.log_headline(f'PROCESSING CLOSED TICKETS FOR {repo}',3,"#",main_log)
    sql = f"""SELECT DISTINCT JiraIssueKey, RITMTicket, ExceptionApproved FROM JiraIssues WHERE
    JiraStatusCategory = 'Done' AND Repo = '{repo}' AND ((JiraIssueKey IN (SELECT DISTINCT
    JiraIssueKey FROM OSFindings WHERE JiraIssueKey IS NOT NULL AND Repo = '{repo}' AND Status
    NOT IN ('False Positive', 'No Fix Available','Not Exploitable','Closed'))) OR (JiraIssueKey
    IN (SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE (FindingType = 'License Violation'
    AND FoundInLastScan = 1 AND Status != 'Accepted'))))"""
    try:
        closed = select(sql)
    except Exception as e_details:
        e_code = "TCAC-PCT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if closed != []:
        for tkt in closed:
            ticket = tkt[0]
            findings = get_project_details(ticket,main_log,ex_log,ex_file)
            if findings:
                alert_comment = f"{ticket} has been closed. Reactivating this alert."
                for finding in findings:
                    reactivate_alert = 1
                    token = finding[0]
                    updated = finding[1].date()
                    alert_uuid = finding[3]
                    alert_status = finding[4]
                    found = finding[5]
                    finding_type = finding[6]
                    if found == 1 and alert_status == 'Ignored':
                        now = datetime.now().date()
                        analyze = get_jiraissue_data(ticket,main_log,ex_log,ex_file)
                        if analyze:
                            if now <= analyze[0][1]:
                                reactivate_alert = 0
                            else:
                                alert_comment = f"{ticket} was reopened and was due on "
                                alert_comment += f"{analyze[0][1]}."
                                if analyze[0][2] is not None and analyze[0][3] == 1:
                                    alert_comment += " The security exception has expired."
                                    comment = f"{analyze[0][2]} expired on {analyze[0][1]}. A new "
                                    comment += "license exception to IS18.05 should be submitted "
                                    comment += "for approval using the Information Security "
                                    comment += "Standard Exception (https://progleasing.service-"
                                    comment += "now.com/prognation?id=sc_cat_item&sys_id=5bc4a803"
                                    comment += "1b0f6010fe43db56dc4bcbb3). Please include this "
                                    comment += f"Jira ticket number ({ticket}) in your exception "
                                    comment += "request to ensure prompt automated processing of "
                                    comment += "this ticket once the exception is approved."
                                    GeneralTicketing.reopen_mend_license_violation_jira_ticket(ticket,comment)
                                elif analyze[0][4] == 1 and analyze[0][2] is None:
                                    alert_comment += " This ticket was created as tech debt."
                    if (alert_status in ('Active','Library Removed') or
                        (finding_type == 'License Violation' and found == 1)):
                        reactivate_alert = 0
                    if reactivate_alert == 1:
                        updated = False
                        try:
                            updated = MendAPI.update_alert_status(token,alert_uuid,'Active',
                                                                  alert_comment)
                        except Exception as details:
                            func = f"MendAPI.update_alert_status('{token}','{alert_uuid}',"
                            func += f"'Active','{alert_comment}')"
                            e_code = "TCAC-PCT-002"
                            TheLogs.function_exception(func,e_code,details,ex_log,main_log,
                                                       ex_file)
                            ScrVar.ex_cnt += 1
                            continue
                        if updated is True:
                            update_osfindings_status(repo,alert_uuid,main_log,ex_log,ex_file)
                            a_cnt += 1
        update_jiraissues_for_tool_and_repo(repo,'mend os',main_log,ex_log,ex_file)
    TheLogs.log_info(f"{a_cnt} alert(s) reactivated",3,"*",main_log)

def get_jiraissue_data(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Gets the ticket details from JiraIssues'''
    results = []
    sql = f"""SELECT JiraIssueKey, JiraDueDate, RITMTicket, ExceptionApproved, TechDebt FROM
    JiraIssues WHERE JiraIssueKey = '{ticket}' AND ((RITMTicket IS NOT NULL AND
    ExceptionApproved = 1) OR TechDebt = 1)"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TCAC-GJID-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def update_osfindings_status(repo,alert_uuid,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Updates AlertStatus to Active in OSFindings'''
    sql = f"""UPDATE OSFindings SET AlertStatus = 'Active' WHERE Repo = '{repo}' AND AlertUuid =
    '{alert_uuid}' UPDATE OSAlerts SET AlertStatus = 'Active' WHERE Repo = '{repo}' AND
    AlertUuid = '{alert_uuid}'"""
    try:
        update(sql)
    except Exception as e_details:
        e_code = "TCAC-UOSFS-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def get_project_details(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Gets the project details from OSProjects and OSFindings for the specified ticket'''
    results = []
    sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSProjects.wsLastUpdatedDate,
    OSFindings.ProjectName, OSFindings.AlertUuid, OSFindings.AlertStatus,
    OSFindings.FoundInLastScan, OSFindings.FindingType FROM OSFindings INNER JOIN OSProjects ON
    OSFindings.Repo = OSProjects.wsProductName AND OSFindings.ProjectName =
    OSProjects.wsProjectName WHERE JiraIssueKey = '{ticket}'"""
    try:
        results = select(sql)
    except Exception as e_details:
        e_code = "TCAC-GPD-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def create_and_update_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates past due to flag their status, creates tickets for new findings, and updates tickets
    with new or fixed items"""
    n_cnt = 0
    ScrVar.u_cnt = 0
    n_array = []
    u_array = []
    proj_key = None
    epic = None
    try:
        ticketing_info = GeneralTicketing.get_jira_info(repo,'mend os')
    except Exception as e_details:
        func = f"GeneralTicketing.get_jira_info('{repo}','mend os')"
        e_code = "TCAC-CAUT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if ticketing_info is not None:
        labels = None
        td_status = None
        pci = ticketing_info[0][0]
        proj_key = ticketing_info[0][1]
        epic = ticketing_info[0][2]
        td_boarded = ticketing_info[0][3]
        s_u = ''
        if td_boarded == 1 and td_boarded is not None:
            labels = ['security_finding',repo.lower()]
            td_status = 0
            s_u = 'Open'
        else:
            labels = ['security_finding','tech_debt',repo.lower()]
            td_status = 1
            s_u = 'Tech Debt'
        if pci is not None and pci == 1:
            labels.append('pci')
    if (proj_key is None or epic is None):
        TheLogs.log_headline(f'NO TICKETS CAN BE CREATED FOR {repo}',3,"!",main_log)
        TheLogs.log_info('No Jira info is on file',3,'!',main_log)
        cannot_ticket(repo,main_log,ex_log,ex_file)
        return
    else:
        try:
            get_descriptions = MendTicketing.create_jira_descriptions(repo)
        except Exception as e_details:
            func = f"MendTicketing.create_jira_descriptions('{repo}')"
            e_code = "TCAC-CAUT-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return
        if get_descriptions != []:
            TheLogs.log_headline(f'CREATING AND UPDATING TICKETS FOR {repo}',3,"#",main_log)
            for item in get_descriptions:
                add_comment = None
                remediation_days = 0
                if td_boarded != 1 or td_boarded is None:
                    remediation_days = 180
                else:
                    if item['Severity'] == 'Critical':
                        remediation_days = 30
                    elif item['Severity'] == 'High':
                        remediation_days = 90
                    elif item['Severity'] == 'Medium':
                        remediation_days = 180
                created_dt = datetime.now()
                created_date = str(created_dt).split('.',1)[0]
                due_date = str(datetime.now() + timedelta(remediation_days))[:10]
                repo_exceptions = GeneralTicketing.has_repo_exceptions(repo,due_date,main_log,
                                                                       ex_log,ex_file)
                # {'RITMTicket':None,'Standard':None,'ApprovedDate':None,'Duration':None,'Due':None}
                if repo_exceptions['Due'] is not None:
                    due_date = repo_exceptions['Due']
                    add_comment = f"Security exception {repo_exceptions['RITMTicket']} to "
                    add_comment += f"{repo_exceptions['Standard']} was approved for "
                    add_comment += f"{repo_exceptions['Duration']} month(s) on "
                    add_comment += f"{str(repo_exceptions['Approved'])}. Due date is extended to "
                    add_comment += f"{str(repo_exceptions['Due'])}."
                jira_title = item['Summary']
                item['Summary'] = jira_title
                if item['ExistingTicket'] is None:
                    if proj_key == 'PROG':
                        t_date = (datetime.now() + timedelta(remediation_days)).strftime("%b %d, %Y")
                        jira_title = f'{jira_title} - {t_date}'
                    try:
                        ticket = GeneralTicketing.create_jira_ticket(repo,proj_key,jira_title,
                                                                     item['Description'],
                                                                     item['Severity'],labels,
                                                                     due_date,epic)
                    except Exception as e_details:
                        func = f"GeneralTicketing.create_jira_ticket('{repo}','{proj_key}',"
                        func += f"'{jira_title}','{item['Description']}',"
                        func += f"'{item['Severity']}','{labels}','{due_date}','{epic}')"
                        e_code = "TCAC-CAUT-003"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   ScrVar.src,inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if ticket is not None:
                        n_cnt += 1
                        n_array.append(ticket)
                        reported_date = datetime.now()
                        get_type = str(jira_title).split(": ",1)[0]
                        f_type = 'License Violation'
                        if get_type == 'Open Source Vulnerability':
                            f_type = 'Vulnerability'
                        if add_comment is not None:
                            try:
                                GeneralTicketing.add_comment_to_ticket(repo,ticket,add_comment)
                            except Exception as e_details:
                                func = f"GeneralTicketing.add_comment_to_ticket('{repo}',"
                                func += f"'{ticket}','{add_comment}')"
                                e_code = "TCAC-CAUT-004"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                        ScrVar.src,inspect.stack()[0][3],
                                                        traceback.format_exc())
                                ScrVar.ex_cnt += 1
                        update_osfindings_ticket(ticket,s_u,reported_date,repo,item,f_type,
                                                 main_log,ex_log,ex_file)
                        insert_jiraissues(repo,epic,proj_key,ticket,item,due_date,created_date,
                                          td_status,main_log,ex_log,ex_file)
                else:
                    if proj_key == 'PROG':
                        t_date = (datetime.now() + timedelta(remediation_days)).strftime("%b %d, %Y")
                        jira_title = f'{jira_title} - {t_date}'
                    try:
                        updated = GeneralTicketing.update_jira_ticket(item['ExistingTicket'],repo,
                                                                      item['Description'],
                                                                      jira_title)
                    except Exception as e_details:
                        func = f"GeneralTicketing.update_jira_ticket('{item['ExistingTicket']}',"
                        func += f"'{repo},'{item['Description']}','{jira_title}')"
                        e_code = "TCAC-CAUT-005"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   ScrVar.src,inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if updated is True:
                        status = 'Open'
                        i_stat = 'Reported'
                        try:
                            exception = GeneralTicketing.check_exceptions(item['ExistingTicket'])
                        except Exception as e_details:
                            func = f"GeneralTicketing.check_exceptions('{item['ExistingTicket']}')"
                            e_code = "TCAC-CAUT-006"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        try:
                            tech_debt = GeneralTicketing.check_tech_debt(item['ExistingTicket'])
                        except Exception as e_details:
                            func = f"GeneralTicketing.check_tech_debt('{item['ExistingTicket']}')"
                            e_code = "TCAC-CAUT-007"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        if tech_debt is True and exception is False:
                            status = 'Tech Debt'
                        try:
                            past_due = GeneralTicketing.check_past_due(item['ExistingTicket'])
                        except Exception as e_details:
                            func = f"GeneralTicketing.check_past_due('{item['ExistingTicket']}')"
                            e_code = "TCAC-CAUT-008"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        if past_due is True:
                            status = 'Past Due'
                            i_stat = 'Past Due'
                        f_type = 'License Violation'
                        get_type = str(jira_title).split(": ",1)[0]
                        if get_type == 'Open Source Vulnerability':
                            f_type = 'Vulnerability'
                        part_1 = f"""UPDATE OSFindings SET IngestionStatus = '{i_stat}', Status =
                        '{status}', JiraIssueKey = '{item['ExistingTicket']}' WHERE Repo = '{repo}'
                         AND GroupId = '{item['GroupId']}' AND Status NOT IN ('Accepted',
                         'False Positive','Not Exploitable','Library Removed') AND FindingType =
                         '{f_type}'"""
                        part_2 = f"""UPDATE OSFindings SET IngestionStatus = 'Closed', Status =
                         'Closed in Ticket', JiraIssueKey = '{item['ExistingTicket']}' WHERE Repo =
                         '{repo}' AND GroupId = '{item['GroupId']}' AND FoundInLastScan = 0 AND
                         FindingType = '{f_type}'"""
                        sql = f"{part_1} {part_2}"
                        try:
                            update(sql)
                        except Exception as e_details:
                            e_code = "TCAC-CAUT-009"
                            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                                  ScrVar.src,inspect.stack()[0][3],
                                                  traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        ScrVar.u_cnt += 1
                        u_array.append(item['ExistingTicket'])
            update_jiraissues_for_tool_and_repo(repo,'mend os',main_log,ex_log,ex_file)
    TheLogs.log_info(f"{n_cnt} new ticket(s) created",3,"*",main_log)
    if n_cnt > 0:
        for tkt in n_array:
            TheLogs.log_info(tkt,4,"-",main_log)
    TheLogs.log_info(f"{ScrVar.u_cnt} existing ticket(s) updated",3,"*",main_log)
    if ScrVar.u_cnt > 0:
        for tkt in u_array:
            TheLogs.log_info(tkt,4,"-",main_log)

def update_osfindings_ticket(ticket,s_u,reported_date,repo,item,f_type,main_log=LOG,
                             ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Updates existing ticket info in OSFindings'''
    results = 0
    sql = f"""UPDATE OSFindings SET JiraIssueKey = '{ticket}', Status = '{s_u}', IngestionStatus =
    'Reported', ReportedDate = '{reported_date}' WHERE Repo = '{repo}' AND GroupId =
    '{item['GroupId']}' AND FindingType = '{f_type}' AND Status NOT IN ('Accepted',
    'False Positive','No Fix Available')
    UPDATE OSFindings SET JiraIssueKey = '{ticket}', IngestionStatus = 'Security Exception',
    ReportedDate = '{reported_date}' WHERE Repo = '{repo}' AND GroupId =
    '{item['GroupId']}' AND FindingType = '{f_type}' AND Status = 'Accepted'"""
    try:
        results += update(sql)
    except Exception as e_details:
        e_code = "TCAC-UOSFT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def insert_jiraissues(repo,epic,proj_key,ticket,item,due_date,created_date,td_status,main_log=LOG,
                      ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Inserts new ticket info into JiraIssues table'''
    results = 0
    sql = f"""INSERT INTO JiraIssues (Repo, OriginalEpic,
                        OriginalEpicProjectKey, CurrentEpic, CurrentEpicProjectKey, JiraIssueKey,
                        JiraProjectKey, wsGroupId, JiraSummary, JiraPriority, JiraDueDate,
                        AssignedDueDate, JiraCreated, CreatedDateTime, Source, TechDebt) VALUES
                        ('{repo}', '{epic}', '{proj_key}', '{epic}', '{proj_key}', '{ticket}',
                        '{proj_key}', '{item['GroupId']}', '{item['Summary']}',
                        '{item['Severity']}', '{due_date}', '{due_date}', '{created_date}',
                        '{created_date}', 'Mend OS', {td_status})"""
    try:
        results += insert(sql)
    except Exception as e_details:
        e_code = "TCAC-IJI-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results
