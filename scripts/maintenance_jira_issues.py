"""Updates the JiraIssues table in the AppSec database"""

import os
import sys
import traceback
import inspect
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from datetime import datetime
from common.miscellaneous import Misc
from common.jira_functions import (get_open_jira_issues,check_moved_issue,GeneralTicketing,
                                   get_open_tool_issues)
from common.logging import TheLogs
from common.database_generic import DBQueries
from common.general import General
from maint.jira_issues_database_queries import JIDatabase

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    u_cnt = 0
    a_cnt = 0
    start_timer = None
    running_function = ''
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

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # update_all_jira_issues()
    # update_jira_project_tickets('four')
    # update_jiraissues_for_tool_and_repo('dde','Checkmarx')

def update_all_jira_issues(run=1,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates JiraIssues for all Repos"""
    ScrVar.reset_exception_counts()
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    if run == 1:
        check_all_for_moved_tickets(main_log,ex_log,ex_file)
    cycle_through_all_jira_issues('All',50,0,'All',main_log,ex_log,ex_file)
    remove_epic_from_cancelled('All',main_log,ex_log,ex_file)
    add_epic_to_closed('All',main_log,ex_log,ex_file)
    reset_ticket_titles('All',main_log,ex_log,ex_file)
    add_missing_repos(main_log,ex_log,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt}

def update_jira_project_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates information for Jira tickets that have been created/updated in the past 7 days"""
    ScrVar.reset_exception_counts()
    ScrVar.u_cnt = 0
    ScrVar.a_cnt = 0
    g_pk = JIDatabase.get_project_key(repo,main_log)
    ScrVar.update_exception_info(g_pk)
    if g_pk['Results'] != []:
        # check_repo_for_moved_tickets(repo,main_log,ex_log,ex_file)
        cycle_through_all_jira_issues(repo,50,0,g_pk['Results'][0],main_log,ex_log,ex_file)
        if repo != 'four':
            remove_epic_from_cancelled(repo,main_log,ex_log,ex_file)
            add_epic_to_closed(repo,main_log,ex_log,ex_file)
        add_missing_repos(main_log,ex_log,ex_file)
        reset_ticket_titles(repo,main_log,ex_log,ex_file)
    return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt}

def cycle_through_all_jira_issues(repo,max_results,start_at,proj_key,main_log=LOG,
                                  ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Cycles through paginated Jira issues to update JiraIssues"""
    add_cycle = 0
    if start_at == 0:
        ScrVar.a_cnt = 0
        ScrVar.u_cnt = 0
        hl_lng = f'{repo} ({proj_key})'
        if repo == 'All':
            hl_lng = "ALL PROG REPOS"
        TheLogs.log_headline(f'UPDATING JIRA TICKET INFO FOR {hl_lng}',2,"#",main_log)
    try:
        report = get_open_jira_issues(repo,max_results,start_at,proj_key)
    except Exception as e_details:
        func = f"get_open_jira_issues('{repo}',{max_results},{start_at},'{proj_key}')"
        e_code = "MJI-CTAJI-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if report['Results'] != {}:
        start_at = 0
        total = 0
        issue_count = 0
        if 'startAt' in report['Results']:
            start_at = report['Results']['startAt']
        if 'total' in report['Results']:
            total = report['Results']['total']
        if 'issueCount' in report['Results']:
            issue_count = report['Results']['issueCount']
        if issue_count + start_at + 1 <= total:
            add_cycle = 1
        if issue_count > 0:
            if 'issues' in report['Results']:
                try:
                    ScrVar.a_cnt += DBQueries.insert_multiple('JiraIssues',
                                                              report['Results']['issues'],'AppSec',
                                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.insert_multiple('JiraIssues',{report['Results']['issues']},"
                    func += "'AppSec',show_progress=False)"
                    e_code = "MJI-CTAJI-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
            if report['Results']['updates'] != []:
                try:
                    ScrVar.u_cnt += DBQueries.update_multiple('JiraIssues',
                                                              report['Results']['updates'],'AppSec',
                                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('JiraIssues',{report['Results']['issues']},"
                    func += "'AppSec',show_progress=False)"
                    e_code = "MJI-CTAJI-003"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
    if add_cycle == 1:
        start_at = start_at + 50
        cycle_through_all_jira_issues(repo,max_results,start_at,proj_key,main_log,ex_log,ex_file)
    else:
        a_lng = f"{ScrVar.a_cnt} ticket(s) added to JiraIssues"
        TheLogs.log_info(a_lng,2,"*",main_log)
        u_lng = f"{ScrVar.u_cnt} ticket(s) updated in JiraIssues"
        TheLogs.log_info(u_lng,2,"*",main_log)
        if repo == 'All':
            cycle_through_all_jira_issues('four',50,0,'FOUR',main_log,ex_log,ex_file)

def remove_epic_from_cancelled(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Removes the epic from tickets that are in Cancelled status"""
    e_cnt = 0
    if repo == 'All':
        TheLogs.log_headline('REMOVING EPIC FROM CANCELLED TICKETS FOR ALL REPOS',2,"#",
                                main_log)
    else:
        TheLogs.log_headline(f'REMOVING EPIC FROM CANCELLED TICKETS FOR {repo}',2,"#",main_log)
    g_cancelled = JIDatabase.get_cancelled_tickets(repo,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(g_cancelled)
    if g_cancelled['Results'] != []:
        for ticket in g_cancelled['Results']:
            epic = JIDatabase.get_ticket_current_epic(ticket,main_log,ex_log,ex_file)
            ScrVar.update_exception_info(epic)
            if epic['Results'] != []:
                removed = False
                try:
                    removed = GeneralTicketing.remove_epic_link(ticket)
                except Exception as e_details:
                    func = f"GeneralTicketing.remove_epic_link('{ticket}')"
                    e_code = "MJI-REFC-001"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if removed is True:
                    update = {'SET': {'CurrentEpic': None,
                                    'CurrentEpicProjectKey': None,
                                    'OriginalEpic': epic['Results']['Epic'],
                                    'OriginalEpicProjectKey':epic['Results']['ProjectKey']},
                            'WHERE_EQUAL': {'JiraIssueKey': ticket}}
                    try:
                        DBQueries.update_multiple('JiraIssues',update,'AppSec',
                                                    show_progress=False)
                    except Exception as e_details:
                        func = f"DBQueries.update_multiple('JiraIssues',{update},'AppSec',"
                        func += "show_progress=False)"
                        e_code = "MJI-REFC-002"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                    ex_file,ScrVar.src,inspect.stack()[0][3],
                                                    traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    e_cnt += 1
    TheLogs.log_info(f"Epic removed from {e_cnt} ticket(s)",2,"*",main_log)
    return e_cnt

def add_epic_to_closed(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """If the Epic has been removed from a non-cancelled closed item,set it back to the
    original epic"""
    a_cnt = 0
    if repo == 'All':
        TheLogs.log_headline('ADDING EPIC TO CLOSED TICKETS FOR ALL REPOS',2,"#",main_log)
    else:
        TheLogs.log_headline(f'ADDING EPIC TO CLOSED TICKETS FOR {repo}',2,"#",main_log)
    g_orig_epics = JIDatabase.get_original_epic(repo,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(g_orig_epics)
    if g_orig_epics['Results'] != []:
        for item in g_orig_epics['Results']:
            epic = item['OriginalEpic']
            ticket = item['JiraIssueKey']
            try:
                added = GeneralTicketing.add_epic_link(ticket,epic)
            except Exception as e_details:
                func = f"GeneralTicketing.add_epic_link('{ticket}','{epic}')"
                e_code = "MJI-AETC-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           ScrVar.src,inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if added is True:
                epic_pk = epic.split("-",1)[0]
                update = {'SET': {'CurrentEpic': epic,
                                  'CurrentEpicProjectKey': epic_pk},
                          'WHERE_EQUAL': {'JiraIssueKey': ticket}}
                try:
                    DBQueries.update_multiple('JiraIssues',update,'AppSec',show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('JiraIssues',{update},'AppSec',"
                    func += "show_progress=False)"
                    e_code = "MJI-AETC-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            ScrVar.src,inspect.stack()[0][3],
                                            traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                a_cnt += 1
    TheLogs.log_info(f"Epic added to {a_cnt} ticket(s)",2,"*",main_log)
    return a_cnt

def add_missing_repos(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Makes sure the repo is filled in correctly for Checkmarx and Mend SCA tickets"""
    u_cnt = 0
    TheLogs.log_headline('ADDING MISSING REPOS FOR ALL TICKETS',2,"#",main_log)
    missing_repos = JIDatabase.get_tickets_with_missing_repos(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(missing_repos)
    if missing_repos['Results'] != []:
        try:
            u_cnt += DBQueries.update_multiple('JiraIssues',missing_repos['Results'],'AppSec',
                                               show_progress=False)
        except Exception as e_details:
            func = f"DBQueries.update_multiple('JiraIssues',{missing_repos['Results']},'AppSec',"
            func += "show_progress=False)"
            e_code = "MJI-AMR-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3],
                                    traceback.format_exc())
            ScrVar.ex_cnt += 1
    TheLogs.log_info(f"Repo added for {u_cnt} ticket(s)",2,"*",main_log)

def check_all_for_moved_tickets(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Makes sure the database reflects the correct current JiraIssueKey and CurrentEpic"""
    u_cnt = 0
    TheLogs.log_headline('UPDATING MOVED JIRA TICKETS FOR ALL REPOS',2,"#",main_log)
    tickets = JIDatabase.get_all_jira_issues(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(tickets)
    if tickets['Results'] is not None and tickets['Results'] != []:
        for tkt in tickets['Results']:
            u_cnt += check_moved_issue(tkt[0],tkt[1],tkt[2],tkt[3],tkt[4],main_log)
    u_lng = f"{u_cnt} moved ticket(s) updated"
    TheLogs.log_info(u_lng,2,"*",main_log)
    update_tool_tickets('Checkmarx')
    update_tool_tickets('Mend OS')

def check_repo_for_moved_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Makes sure the database reflects the correct current JiraIssueKey and CurrentEpic for a
    single repo"""
    u_cnt = 0
    TheLogs.log_headline(f'UPDATING MOVED JIRA TICKETS FOR {repo}',2,"#",main_log)
    tickets = JIDatabase.get_repo_jira_issues(repo,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(tickets)
    if tickets['Results'] is not None:
        for tkt in tickets['Results']:
            u_cnt += check_moved_issue(tkt[0],tkt[1],tkt[2],tkt[3],tkt[4],main_log)
    TheLogs.log_info(f"{u_cnt} moved ticket(s) updated",2,"*",main_log)
    update_tool_tickets('Checkmarx')
    update_tool_tickets('Mend OS')

def update_jiraissues_for_tool_and_repo(repo,tool,main_log=LOG,ex_log=LOG_EXCEPTION,
                                        ex_file=EX_LOG_FILE):
    """Updates just tickets for the specified repo and tool"""
    u_mvd = JIDatabase.update_moved_tool_tickets(repo,tool,main_log)
    ScrVar.update_exception_info(u_mvd)
    cycle_through_tool_tickets(repo,50,0,tool,main_log,ex_log,ex_file)
    u_missing = JIDatabase.update_missing_ji_data(repo,tool,main_log)
    ScrVar.update_exception_info(u_missing)
    if repo != 'four':
        remove_epic_from_cancelled(repo,main_log,ex_log,ex_file)
        add_epic_to_closed(repo,main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def cycle_through_tool_tickets(repo,max_results,start_at,tool,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE):
    """Cycles through paginated tool-specific Jira tickets to update JiraIssues"""
    add_cycle = 0
    if start_at == 0:
        ScrVar.a_cnt = 0
        ScrVar.u_cnt = 0
        if repo == 'All':
            TheLogs.log_headline(f'UPDATING {tool.upper()} TICKETS FOR PROG REPOS',2,"#",main_log)
        else:
            TheLogs.log_headline(f'UPDATING {tool.upper()} TICKETS FOR {repo}',2,"#",main_log)
    try:
        report = get_open_tool_issues(repo,max_results,start_at,tool)
    except Exception as e_details:
        func = f"get_open_tool_issues('{repo}',{max_results},{start_at})"
        e_code = "MJI-CTCT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if report['Results'] != {}:
        issue_count = 0
        start_at = 0
        total = 0
        if 'startAt' in report['Results']:
            start_at = report['Results']['startAt']
        if 'total' in report['Results']:
            total = report['Results']['total']
        if 'issueCount' in report['Results']:
            issue_count = report['Results']['issueCount']
        if issue_count + start_at + 1 < total:
            add_cycle = 1
        if issue_count > 0:
            if 'issues' in report['Results']:
                try:
                    ScrVar.a_cnt += DBQueries.insert_multiple('JiraIssues',
                                                              report['Results']['issues'],'AppSec',
                                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.insert_multiple('JiraIssues',{report['Results']['issues']},"
                    func += "'AppSec',show_progress=False)"
                    e_code = "MJI-CTCT-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
            if report['Results']['updates'] != []:
                try:
                    ScrVar.u_cnt += DBQueries.update_multiple('JiraIssues',
                                                              report['Results']['updates'],'AppSec',
                                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('JiraIssues',{report['Results']['updates']},"
                    func += "'AppSec',show_progress=False)"
                    e_code = "MJI-CTCT-003"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
    if add_cycle == 1:
        start_at = start_at + 50
        cycle_through_tool_tickets(repo,max_results,start_at,tool,main_log,ex_log,ex_file)
    else:
        TheLogs.log_info(f"{ScrVar.a_cnt} ticket(s) added to JiraIssues",2,"*",main_log)
        TheLogs.log_info(f"{ScrVar.u_cnt} ticket(s) updated in JiraIssues",2,"*",main_log)
        if repo == 'All':
            cycle_through_tool_tickets('four',50,0,tool,main_log,ex_log,ex_file)

def update_tool_tickets(tool,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """If a ticket has moved, this will update either 'Checkmarx' or 'Mend OS'
    findings with the new ticket"""
    u_array = []
    u_cnt = 0
    table = None
    TheLogs.log_headline(f'UPDATING MOVED {tool.upper()} TICKETS IN {table}',2,"#",main_log)
    if tool.lower() == 'checkmarx':
        table = 'SASTFindings'
    elif 'mend os' in tool.lower():
        table = 'OSFindings'
    else:
        TheLogs.log_info(f'Provided tool ({tool}) needs a table set in the code',2,"!",
                            main_log)
        func = None
        e_details = f"The tool provided ({tool}) when running update_moved_tool_tickets does "
        e_details += "not have a valid table set in update_moved_tool_tickets in "
        e_details += f"{ScrVar.src}. Jira tickets that have been moved since their creation "
        e_details += f"will not be properly reflected in the findings table for {tool}. "
        e_details += "Please update the code to add the necessary table reference."
        e_code = "MJI-UTT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3])
        ScrVar.fe_cnt += 1
        return
    if table is not None:
        to_update = JIDatabase.tool_tickets_to_update(table,main_log,ex_log,ex_file)
        ScrVar.update_exception_info(to_update)
        if to_update['Results'] != []:
            for ticket in to_update['Results']:
                u_array.append({'SET':{'JiraIssueKey':ticket['NewTicket']},
                                'WHERE_EQUAL':{'JiraIssueKey':ticket['OldTicket']}})
        try:
            u_cnt += DBQueries.update_multiple(table,u_array,'AppSec',show_progress=False)
        except Exception as e_details:
            func = f"update_multiple_in_table('{table}',{u_array},'AppSec',show_progress=False)"
            e_code = "MJI-UTT-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        ScrVar.src,inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    TheLogs.log_info(f'Finding(s) updated in {table}: {u_cnt}',2,"*",main_log)

def reset_ticket_titles(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs functions to reset the ticket titles"""
    reset_titles_to_default(repo,'Mend OS',main_log,ex_log,ex_file)
    reset_titles_to_default(repo,'Checkmarx',main_log,ex_log,ex_file)

def reset_titles_to_default(repo,source,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Resets titles for OS vulnerabilities and license violations"""
    fixed = 0
    TheLogs.log_headline(f'RESETTING {source} TICKET TITLES',2,"#",main_log)
    to_fix = JIDatabase.ticket_titles_to_fix(repo,source,main_log)
    ScrVar.update_exception_info(to_fix)
    for ticket in to_fix['Results']:
        t_repo = ticket['Repo']
        tkt = ticket['Ticket']
        title = create_title(tkt,source,main_log,ex_log,ex_file)
        if title is not None:
            try:
                GeneralTicketing.update_jira_summary(tkt,repo,title)
            except Exception as e_details:
                func = f"GeneralTicketing.update_jira_summary('{tkt}','{repo}','{title}')"
                e_code = "MJI-RTTD-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            fixed += 1
            try:
                JIDatabase.update_jirasummary(repo,tkt,title)
            except Exception as e_details:
                func = f"JIDatabase.update_jirasummary('{repo}','{tkt}','{title}')"
                e_code = "MJI-RTTD-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
    TheLogs.log_info(f'{fixed} title(s) reset to default',2,"*",main_log)

def create_title(jira_ticket,source,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Creates the correct ticket title"""
    title = None
    sql = None
    license_title = "Unapproved Open Source License Use:"
    vulns_title = "Open Source Vulnerability:"
    cx_title = "SAST Finding:"
    if source.lower() == 'mend os':
        sql = f"""SELECT Repo, FindingType, GroupId FROM OSFindings WHERE JiraIssueKey =
        '{jira_ticket}'"""
    elif source.lower() == 'checkmarx':
        sql = f"""SELECT ApplicationAutomation.Repo, SASTFindings.cxQuery FROM SASTFindings
        JOIN ApplicationAutomation ON SASTFindings.cxProjectID = ApplicationAutomation.cxProjectID
        AND JiraIssueKey = '{jira_ticket}'"""
    try:
        title_info = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "MJI-CT-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return title
    if title_info != []:
        if source.lower() == 'mend os':
            if title_info[0][1] == 'Vulnerability':
                title = f"{vulns_title} {title_info[0][2]} - {title_info[0][0]}"
            if title_info[0][1] == 'License Violation':
                title = f"{license_title} {title_info[0][2]} - {title_info[0][0]}"
        elif source.lower() == 'checkmarx':
            title = f"{cx_title} {title_info[0][1]} - {title_info[0][0]}"
    if jira_ticket.split("-",1)[0] == "PROG" and title is not None:
        get_due = GeneralTicketing.get_ticket_due_date(jira_ticket,main_log)
        ScrVar.update_exception_info(get_due)
        title = f"{title} - {get_due['Results']}"
    return title

if __name__ == "__main__":
    main()
