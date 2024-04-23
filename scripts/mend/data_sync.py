"""Syncs version info to JiraIssues and reported date and JiraIssueKey (if ticket has been moved)
to OSFindings"""

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
    src = ALERT_SOURCE.replace("-","\\")
    a_cnt = 0
    v_cnt = 0
    t_cnt = 0
    d_cnt = 0
    ne_cnt = 0
    fp_cnt = 0
    c_cnt = 0
    ip_cnt = 0
    td_cnt = 0
    nfa_cnt = 0

class MendSync():
    """Script functions"""

    @staticmethod
    def single_repo_updates(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs all of the updates for a single repo"""
        TheLogs.log_headline(f'SYNCING DATA FOR {repo}',2,"#",main_log)
        sql = f"""SELECT DISTINCT wsProductToken FROM ApplicationAutomation WHERE Repo = '{repo}'
        AND wsProductToken IS NOT NULL"""
        try:
            get_token = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-SRU-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if get_token != []:
            mark_tech_debt_boarded(repo,main_log,ex_log,ex_file)
            sync_group_id(repo,main_log,ex_log,ex_file)
            sync_tickets_and_versions(repo,main_log,ex_log,ex_file)
            sync_statuses(repo,main_log,ex_log,ex_file)
        else:
            TheLogs.log_info(f'There is no wsProductToken for repo: {repo}',3,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def is_security_exception(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Determines whether the ticket has an active security exception"""
    is_accepted = False
    sql = f"""SELECT JiraIssueKey FROM JiraIssues WHERE JiraIssueKey = '{ticket}' AND RITMTicket
    IS NOT NULL AND ExceptionApproved = 1 AND JiraDueDate > GETDATE() AND Source =
    'Mend OS'"""
    try:
        has_exception = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-ISE-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return False
    if has_exception != []:
        is_accepted = True
    return is_accepted

def sync_group_id(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Ensures JiraIssues wsGroupId column is populated for open findings"""
    u_cnt = 0
    TheLogs.log_headline(f'UPDATING MISSING wsGroupIds FOR {repo}',3,"#",main_log)
    sql = f"""SELECT JiraIssueKey, JiraSummary FROM JiraIssues WHERE Source = 'Mend OS'
    AND (JiraStatusCategory != 'Done' OR JiraStatusCategory IS NULL) AND wsGroupId IS NULL AND
    Repo = '{repo}'"""
    try:
        to_fix = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-SGI-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return
    if to_fix != []:
        for item in to_fix:
            ticket = item[0]
            summary = item[1]
            group_id = summary.split(": ",1)[1].split(" - ",1)[0]
            updates = jiraissues_update(group_id,repo,ticket,main_log,ex_log,ex_file)
            if updates != 0:
                u_cnt += 1
    u_lng = f"Entries updated: {u_cnt}"
    TheLogs.log_info(u_lng,3,"*",main_log)

def jiraissues_update(group_id,repo,ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''updates wsGroupId in JiraIssues table'''
    results = 0
    sql = f"""UPDATE JiraIssues SET wsGroupId = '{group_id}' WHERE Repo = '{repo}' AND
            JiraIssueKey = '{ticket}'"""
    try:
        results += DBQueries.update(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-JI-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return results
    return results

def sync_tickets_and_versions(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Ensures JiraIssues wsVersion is up-to-date"""
    ScrVar.v_cnt = 0
    ScrVar.t_cnt = 0
    ScrVar.d_cnt = 0
    ScrVar.ne_cnt = 0
    ScrVar.fp_cnt = 0
    ScrVar.c_cnt = 0
    ScrVar.ip_cnt = 0
    ScrVar.td_cnt = 0
    ScrVar.nfa_cnt = 0
    to_update = get_mend_jira_data(repo,main_log,ex_log,ex_file)
    if to_update != []:
        TheLogs.log_headline(f'UPDATING JiraIssueKey IN OSFindings FOR {repo}',3,'#',main_log)
        for item in to_update:
            ticket = item[0]
            group_id = item[1]
            get_type = str(item[2]).split(": ",1)[0]
            f_type = 'Vulnerability'
            if get_type == 'Unapproved Open Source License':
                f_type = 'License Violation'
            c_d = item[3]
            c_dt = item[4]
            reported = None
            if c_dt is not None:
                reported = c_dt
            elif c_d is not None:
                reported = c_d
            updates = update_jiraissuekey_osfindings(ticket,repo,group_id,f_type,main_log,
                                                     ex_log,ex_file)
            ScrVar.t_cnt += updates
        t_lng = f"JiraIssueKey updated for {ScrVar.t_cnt} finding(s) in OSFindings"
        TheLogs.log_info(t_lng,3,"*",main_log)
        TheLogs.log_headline(f'UPDATING MISSING ReportedDate OSFindings FOR {repo}',3,"#",main_log)
        for item in to_update:
            ticket = item[0]
            group_id = item[1]
            get_type = str(item[2]).split(": ",1)[0]
            f_type = 'Vulnerability'
            if get_type == 'Unapproved Open Source License':
                f_type = 'License Violation'
            c_d = item[3]
            c_dt = item[4]
            reported = None
            if c_dt is not None:
                reported = c_dt
            elif c_d is not None:
                reported = c_d
            updates = update_reporteddate_osfindings(reported,repo,group_id,f_type,ticket,main_log,
                                                     ex_log,ex_file)
            ScrVar.d_cnt += updates
        d_lng = f"ReportedDate updated for {ScrVar.d_cnt} finding(s) in OSFindings"
        TheLogs.log_info(d_lng,3,"*",main_log)
        TheLogs.log_headline(f'UPDATING wsVersion IN JiraIssues FOR {repo}',3,"#",main_log)
        for item in to_update:
            ticket = item[0]
            group_id = item[1]
            versions = []
            get_versions = get_version_osfindings(repo,group_id,ticket,main_log,ex_log,ex_file)
            if get_versions != []:
                for item in get_versions:
                    versions.append(item[0])
                versions = str(versions).replace("[","").replace("]","").replace("'","")
                updates = update_wsversion(versions,repo,group_id,ticket,main_log,ex_log,ex_file)
                ScrVar.v_cnt += updates
        v_lng = f"wsVersion updated for {ScrVar.v_cnt} ticket(s) in JiraIssues"
        TheLogs.log_info(v_lng,3,"*",main_log)

def sync_statuses(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates IngestionStatus and Status in OSFindings based on tickets in JiraIssues"""
    to_update = get_mend_jira_data(repo,main_log,ex_log,ex_file)
    if to_update:
        TheLogs.log_headline(f'UPDATING IngestionStatus AND Status IN OSFindings FOR {repo}',3,"#",
                             main_log)
        for item in to_update:
            ticket = item[0]
            status = item[5]
            update_statuses_osfindings(ticket,status,repo,main_log,ex_log,ex_file)
        cl_cnt = ScrVar.ne_cnt + ScrVar.fp_cnt + ScrVar.c_cnt + ScrVar.nfa_cnt + ScrVar.a_cnt
        cl_lng = f"IngestionStatus and/or Status field(s) updated for {cl_cnt} finding(s) in "
        cl_lng += "OSFindings"
        TheLogs.log_info(cl_lng,3,"*",main_log)
        TheLogs.log_info(f'False Positive(s) updated: {ScrVar.fp_cnt}',4,"-",main_log)
        TheLogs.log_info(f'Not Exploitable(s) updated: {ScrVar.ne_cnt}',4,"-",main_log)
        TheLogs.log_info(f'Security Exception(s) updated: {ScrVar.a_cnt}',4,"-",main_log)
        nfa_lng = 'No Fix Available finding(s) with closed ticket(s) updated:'
        TheLogs.log_info(f'{nfa_lng} {ScrVar.c_cnt}',4,"-",main_log)
        TheLogs.log_info(f'Finding(s) with closed ticket(s) updated: {ScrVar.c_cnt}',4,"-",
                            main_log)
        ip_lng = f'IngestionStatus updated for {ScrVar.ip_cnt} finding(s) with tickets in '
        ip_lng += 'progress in OSFindings'
        TheLogs.log_info(ip_lng,3,"*",main_log)
        td_lng = f'IngestionStatus updated for {ScrVar.td_cnt} finding(s) for to do tickets '
        td_lng += 'in OSFindings'
        TheLogs.log_info(td_lng,3,"*",main_log)

def mark_tech_debt_boarded(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Set tech debt as boarded"""
    sql = f"""UPDATE ApplicationAutomation SET wsTechDebtBoarded = 1, wsLicenseTechDebtBoarded = 1,
    wsVulnTechDebtBoarded = 1 WHERE Repo = '{repo}'
    UPDATE Applications SET wsTechDebtBoarded = 1, wsLicenseTechDebtBoarded = 1,
    wsVulnTechDebtBoarded = 1 WHERE Repo = '{repo}'"""
    try:
        DBQueries.update(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-MTDB-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1

def get_mend_jira_data(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''gets Mend findings Jira data for a repo'''
    results = []
    sql = f"""SELECT JiraIssueKey, wsGroupId, JiraSummary, JiraCreated, CreatedDateTime,
    JiraStatusCategory FROM JiraIssues WHERE Source = 'Mend OS' AND wsGroupId IS NOT NULL
    AND Repo = '{repo}' AND JiraIssueKey IS NOT NULL ORDER BY JiraStatusCategory"""
    try:
        results = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-GMJD-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return results
    return results

def update_jiraissuekey_osfindings(ticket,repo,group_id,f_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                                   ex_file=EX_LOG_FILE):
    '''updates JiraIssueKey for finding'''
    results = 0
    sql = f"""UPDATE OSFindings SET JiraIssueKey = '{ticket}' WHERE Repo = '{repo}' AND GroupId =
    '{group_id}' AND JiraIssueKey IS NOT NULL AND FindingType = '{f_type}'"""
    try:
        results = DBQueries.update(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-UJO-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return results
    return results

def update_statuses_osfindings(ticket,status,repo,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE):
    """Updates the IngestionStatus and Status fields in OSFindings"""
    is_accepted = is_security_exception(ticket,main_log,ex_log,ex_file)
    if is_accepted is True:
        sa_sql = f"""UPDATE OSFindings SET IngestionStatus = 'Security Exception', Status =
        'Accepted' WHERE JiraIssueKey = '{ticket}' AND (FindingType = 'License Violation' OR
        (FindingType = 'Vulnerability' AND JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM
        JiraIssues WHERE JiraStatusCategory != 'Done')))"""
        try:
            ScrVar.a_cnt += DBQueries.update(sa_sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-USO-001"
            TheLogs.sql_exception(sa_sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    if status == 'Done':
        ne_sql = f"""UPDATE OSFindings SET IngestionStatus = 'Closed' WHERE Repo = '{repo}' AND
        JiraIssueKey = '{ticket}' AND ((Status = 'Not Exploitable' AND IngestionStatus NOT IN
        ('Closed','False Positive','Project Removed') AND Status != 'Accepted') OR
        (Status = 'No Fix Available' AND IngestionStatus != 'Closed' AND Status != 'Accepted'))"""
        try:
            ScrVar.ne_cnt += DBQueries.update(ne_sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-USO-002"
            TheLogs.sql_exception(ne_sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        fp_sql = f"""UPDATE OSFindings SET IngestionStatus = 'False Positive' WHERE Repo = '{repo}'
        AND JiraIssueKey = '{ticket}' AND Status = 'False Positive'"""
        try:
            ScrVar.fp_cnt += DBQueries.update(fp_sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-USO-003"
            TheLogs.sql_exception(fp_sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        c_sql = f"""UPDATE OSFindings SET IngestionStatus = 'Closed', Status = 'Closed' WHERE
        Repo = '{repo}' AND JiraIssueKey = '{ticket}' AND ((Status NOT IN ('False Positive',
        'No Fix Available') AND (IngestionStatus != 'Closed' OR Status != 'Closed')) OR
        (Status = 'Accepted' AND FindingType != 'License Violation'))"""
        try:
            ScrVar.c_cnt += DBQueries.update(c_sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-USO-004"
            TheLogs.sql_exception(c_sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    elif status in ('In Progress','To Do'):
        sql = f"""UPDATE OSFindings SET IngestionStatus = 'Reported' WHERE Repo =
        '{repo}' AND JiraIssueKey = '{ticket}' AND ((IngestionStatus NOT IN ('Closed',
        'Project Removed','False Positive') AND IngestionStatus != 'Reported' AND Status !=
        'Accepted') OR (IngestionStatus NOT IN ('Closed','Project Removed','False Positive') AND
        Status != 'Accepted'))"""
        try:
            ScrVar.ip_cnt += DBQueries.update(sql,'AppSec')
        except Exception as e_details:
            e_code = "DS-USO-005"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1

def update_reporteddate_osfindings(reported,repo,group_id,f_type,ticket,main_log=LOG,
                                   ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''updates ReportedDate for repo, group_id, finding type and ticket'''
    results = 0
    sql = f"""UPDATE OSFindings SET ReportedDate = '{reported}' WHERE Repo = '{repo}'
            AND GroupId = '{group_id}' AND JiraIssueKey IS NOT NULL AND FindingType = '{f_type}'
            AND JiraIssueKey = '{ticket}' AND ReportedDate IS NULL"""
    try:
        results += DBQueries.update(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-URO-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def get_version_osfindings(repo,group_id,ticket,main_log=LOG,ex_log=LOG_EXCEPTION,
                           ex_file=EX_LOG_FILE):
    '''gets Version from osfindings for repo, group_id, ticket'''
    results = []
    sql = f"""SELECT DISTINCT Version FROM OSFindings WHERE Repo = '{repo}' AND Version IS NOT
            NULL AND GroupId = '{group_id}' AND JiraIssueKey = '{ticket}' ORDER BY Version"""
    try:
        results = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-GVO-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results

def update_wsversion(versions,repo,group_id,ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''updates wsVersion for a ticket'''
    results = 0
    sql = f"""UPDATE JiraIssues SET wsVersion = '{versions}' WHERE Repo = '{repo}'
            AND wsGroupId = '{group_id}' AND JiraIssueKey = '{ticket}' AND (JiraStatusCategory IS
            NOT NULL OR JiraStatusCategory != 'Done')"""
    try:
        results = DBQueries.update(sql,'AppSec')
    except Exception as e_details:
        e_code = "DS-UW-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return results
