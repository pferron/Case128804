"""Functions for maintenance_application_tables"""

import os
import traceback
import inspect
from datetime import datetime
from common.logging import TheLogs
from common.database_generic import DBQueries

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
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class JIDatabase():
    """"For database interaction"""

    @staticmethod
    def update_jirasummary(repo,jira_ticket,title,main_log=LOG,ex_log=LOG_EXCEPTION,
                           ex_file=EX_LOG_FILE):
        """Updates the title of the Jira ticket in JiraIssues"""
        sql = f"""UPDATE JiraIssues SET Repo = '{repo}', JiraSummary = '{title}'
        WHERE JiraIssueKey = '{jira_ticket}' OR OldJiraIssueKey = '{jira_ticket}'"""
        try:
            DBQueries.update(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-UJ-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def ticket_titles_to_fix(repo='All',source='All',main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Gets the tickets with non-standard tickets for the given source so they can be fixed"""
        result = []
        sql = f"""SELECT JiraIssueKey, Repo FROM JiraIssues WHERE Source = '{source}' AND
        JiraStatusCategory != 'Done'"""
        if source.lower() == 'checkmarx':
            sql += """ AND JiraSummary NOT LIKE 'SAST Finding:%'"""
        elif source.lower() == 'mend os':
            sql += """ AND JiraSummary NOT LIKE 'Open Source Vulnerability:%' AND JiraSummary NOT
            LIKE 'Unapproved Open Source License Use:%'"""
        if repo != 'All':
            sql += f""" AND Repo = '{repo}'"""
        if (source.lower() not in ('checkmarx','mend os')):
            e_details = "This function must be executed using an accepted source: 'Checkmarx' "
            e_details += "or 'Mend OS'."
            e_code = "JIDQ-TTTF-001"
            func = f"""ticket_titles_to_fix('{repo}','{source}')"""
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3])
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        try:
            get_tickets = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-TTTF-002"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        if get_tickets != []:
            for tkt in get_tickets:
                result.append({'Ticket':tkt[0],'Repo':tkt[1]})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def tool_tickets_to_update(table,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the tickets to update in the specified tool ('Checkmarx' or
        'Mend OS') table"""
        ScrVar.reset_exception_counts()
        result = []
        sql = f"""SELECT DISTINCT JiraIssueKey, OldJiraIssueKey FROM JiraIssues
        WHERE JiraIssueKey != OldJiraIssueKey AND OldJiraIssueKey IS NOT NULL AND OldJiraIssueKey
        IN (SELECT DISTINCT JiraIssueKey FROM {table} WHERE JiraIssueKey IS NOT NULL)
        ORDER BY JiraIssueKey"""
        try:
            get_changes = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-TTTU-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        if get_changes != []:
            for item in get_changes:
                result.append({'NewTicket':item[0],'OldTicket':item[1]})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def get_all_jira_issues(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if issue exists in JiraIssues"""
        result = None
        sql = """SELECT DISTINCT Repo, CurrentEpic, CurrentEpicProjectKey, JiraIssueKey,
        JiraProjectKey FROM JiraIssues WHERE JiraStatusCategory != 'Done' ORDER BY Repo,
        CurrentEpic, JiraIssueKey"""
        try:
            result = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GAJI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def get_repo_jira_issues(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if issue exists in JiraIssues"""
        result = None
        sql = f"""SELECT DISTINCT Repo, CurrentEpic, CurrentEpicProjectKey, JiraIssueKey,
        JiraProjectKey FROM JiraIssues WHERE Repo = '{repo}' AND JiraStatusCategory != 'Done'
        ORDER BY Repo, CurrentEpic, JiraIssueKey"""
        try:
            result = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GRJI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def update_missing_ji_data(repo,tool,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """For updating tool-specific data in JiraIssues"""
        u_cnt = 0
        empty_fields = None
        get_fields = None
        update_fields = None
        tool_table = None
        headline = f" FOR {repo}"
        s_repo = f" AND Repo = '{repo}'"
        if repo == 'All' or repo is None:
            s_repo = ''
            headline = " FOR ALL REPOS"
        headline = f'UPDATING MISSING {tool.upper()} DATA IN JiraIssues{headline}'
        TheLogs.log_headline(headline,2,"#",main_log)
        if tool.lower() == 'checkmarx':
            empty_fields = '(cxSimilarityID IS NULL OR cxProjectID IS NULL)'
            get_fields = ['cxProjectID','cxSimilarityID']
            update_fields = ['cxProjectID','cxSimilarityID']
            tool_table = 'SASTFindings'
        elif 'mend os' in tool.lower():
            empty_fields = '(wsGroupId IS NULL OR wsVersion IS NULL)'
            tool = 'Mend OS'
            get_fields = ['GroupId','Version']
            update_fields = ['wsGroupId','wsVersion']
            tool_table = 'OSFindings'
        to_update = JIDatabase.get_tool_tickets(tool,empty_fields,repo,tool_table)
        if to_update != []:
            for ticket in to_update:
                to_post = []
                use_index = 0
                for field in get_fields:
                    update_text = ''
                    sql = f"""SELECT DISTINCT {field} FROM {tool_table} WHERE JiraIssueKey =
                    '{ticket[0]}' AND {field} IS NOT NULL ORDER BY {field}"""
                    try:
                        updates = DBQueries.select(sql,'AppSec')
                    except Exception as e_details:
                        e_code = "JIDQ-UMJD-001"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              ScrVar.src,inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if updates != []:
                        for val in updates:
                            update_text += f"{val[0]}, "
                        update_text = update_text[:-2]
                        to_post.append({'SET':{update_fields[use_index]:update_text},
                                        'WHERE_EQUAL':{'JiraIssueKey':ticket[0]}})
                    use_index += 1
                try:
                    updated = DBQueries.update_multiple('JiraIssues',to_post,'AppSec',
                                                        show_progress=False,update_to_null=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('JiraIssues',{to_post},'AppSec',"
                    func += "show_progress=False,update_to_null=False)"
                    e_code = "JIDQ-UMJD-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if len(to_post) > 0 and updated != 0:
                    u_cnt += len(to_post)
        TheLogs.log_info(f'Missing {tool} data added for {u_cnt} Jira tickets',2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_tool_tickets(tool,empty_fields,repo,tool_table,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        '''Gets all of the Jira issues for a tool'''
        to_update = []
        if repo is not None and repo != 'All':
            repo = f" AND repo = '{repo}'"
        if empty_fields is not None:
            sql = f"""SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE Source = '{tool}' AND
            {empty_fields}{repo} AND JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM
            {tool_table})"""
            try:
                to_update = DBQueries.select(sql,'AppSec')
            except Exception as e_details:
                e_code = "JIDQ-GTT-001"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return to_update
        return to_update

    @staticmethod
    def check_for_jira_issue(jira_issue,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if issue exists in JiraIssues"""
        result = False
        sql = f"""SELECT JiraIssueKey FROM JiraIssues WHERE JiraIssueKey = '{jira_issue}'"""
        try:
            exists = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-CFJI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        if exists != []:
            result = True
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def update_moved_tool_tickets(repo,tool,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """If a ticket has a new JiraIssueKey, update it in the tool table"""
        updates = []
        u_cnt = 0
        table = None
        if repo == 'four':
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        TheLogs.log_headline(f'UPDATING MOVED {tool.upper()} TICKETS FOR {repo}',2,"#",main_log)
        if tool.lower() == 'checkmarx':
            table = 'SASTFindings'
        elif 'mend os' in tool.lower():
            table = 'OSFindings'
            tool = 'Mend OS'
        sql = f"""SELECT JiraIssueKey, OldJiraIssueKey FROM JiraIssues WHERE JiraIssueKey !=
        OldJiraIssueKey AND Source = '{tool}' AND Repo = '{repo}' AND OldJiraIssueKey IN (SELECT
        DISTINCT JiraIssueKey FROM {table} WHERE JiraIssueKey IS NOT NULL) AND (JiraResolutionDate
        IS NULL OR JiraResolutionDate > DATEADD(day,-14,GETDATE()))"""
        if table is not None:
            try:
                to_update = DBQueries.select(sql,'AppSec')
            except Exception as e_details:
                e_code = "JIDQ-UMTT-001"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
            if to_update != []:
                for item in to_update:
                    updates.append({'SET':{'JiraIssueKey':item[0]},
                                'WHERE_EQUAL':{'JiraIssueKey':item[1]}})
            try:
                updated = DBQueries.update_multiple(table,updates,'AppSec',show_progress=False,
                                                    update_to_null=False)
                if updated != 0:
                    u_cnt += len(updates)
            except Exception as e_details:
                func = f"DBQueries.update_multiple('{table}',{updates},'AppSec',"
                func += "show_progress=False,update_to_null=False)"
                e_code = "JIDQ-UMTT-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           ScrVar.src,inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{table} updated for {u_cnt} moved Jira ticket(s)',2,"*",main_log)
        else:
            TheLogs.log_info(f'Provided tool ({tool}) needs a table set in the code',2,"!",
                             main_log)
            func = None
            e_details = f"The tool provided ({tool}) when running update_moved_tool_tickets does "
            e_details += "not have a valid table set in update_moved_tool_tickets in "
            e_details += f"{ScrVar.src}. Jira tickets that have been moved since their creation "
            e_details += f"will not be properly reflected in the findings table for {tool}. "
            e_details += "Please update the code to add the necessary table reference."
            e_code = "JIDQ-UMTT-003"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        ScrVar.src,inspect.stack()[0][3])
            ScrVar.fe_cnt += 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_project_key(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets Jira project key for the specified repo"""
        keys = []
        sql = f"""SELECT JiraProjectKey FROM ApplicationAutomation WHERE Repo = '{repo}' AND
        JiraProjectKey IS NOT NULL"""
        try:
            get_key = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GPK-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':keys}
        if get_key != []:
            for proj_key in get_key:
                keys.append(proj_key[0])
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results': keys}

    @staticmethod
    def get_cancelled_tickets(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets a list of cancelled tickets where the current Epic needs to be removed"""
        tickets = []
        if repo == 'All':
            sql = """SELECT DISTINCT JiraIssueKey FROM JiraIssues
            WHERE JiraStatus = 'Cancelled' AND CurrentEpic IS NOT NULL AND Source IN
            ('Mend OS', 'Checkmarx') AND JiraStatusCategory = 'Done' AND JiraSummary NOT
            LIKE '%Unapproved Open Source License Use%' ORDER BY JiraIssueKey"""
        else:
            sql = f"""SELECT DISTINCT JiraIssueKey FROM JiraIssues
            WHERE JiraStatus = 'Cancelled' AND CurrentEpic IS NOT NULL AND Source IN
            ('Mend OS', 'Checkmarx') AND JiraStatusCategory = 'Done' AND Repo = '{repo}'
            AND JiraSummary NOT LIKE '%Unapproved Open Source License Use%' ORDER BY JiraIssueKey"""
        try:
            g_cancelled = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GCT-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':tickets}
        if g_cancelled:
            for ticket in g_cancelled:
                tickets.append(ticket[0])
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':tickets}

    @staticmethod
    def get_original_epic(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the original epic and jira ticket pair for the specified repo (or All repos)"""
        pairs = []
        if repo == 'All':
            sql = """SELECT DISTINCT OriginalEpic, JiraIssueKey FROM JiraIssues
            WHERE JiraStatus != 'Cancelled' AND OriginalEpic IS NOT NULL AND CurrentEpic IS NULL
            AND Source IN ('Mend OS', 'Checkmarx') AND JiraResolutionDate >=
            DATEADD(day, -7, GETDATE()) AND JiraResolutionDate IS NOT NULL AND JiraStatusCategory =
            'Done' ORDER BY JiraIssueKey"""
        else:
            sql = f"""SELECT DISTINCT OriginalEpic, JiraIssueKey FROM JiraIssues
            WHERE JiraStatus != 'Cancelled' AND OriginalEpic IS NOT NULL AND CurrentEpic IS NULL
            AND Source IN ('Mend OS', 'Checkmarx') AND Repo = '{repo}' AND
            JiraResolutionDate >= DATEADD(day, -7, GETDATE()) AND JiraResolutionDate IS NOT NULL
            AND JiraStatusCategory = 'Done' ORDER BY JiraIssueKey"""
        try:
            g_orig_epics = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GOE-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':pairs}
        if g_orig_epics:
            for item in g_orig_epics:
                pairs.append({'OriginalEpic': item[0],'JiraIssueKey': item[1]})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':pairs}

    @staticmethod
    def get_tickets_with_missing_repos(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns a list of tickets whose Repo fields are blank"""
        array = []
        sql = """SELECT JiraIssueKey, JiraSummary FROM JiraIssues WHERE Source IN
        ('Mend OS','Checkmarx') AND (Repo IS NULL OR Repo = 'All')"""
        try:
            missing_repos = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GTWMR-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':array}
        if missing_repos:
            for item in missing_repos:
                summary = item[1]
                repo = summary.split(" - ",1)[1]
                repo = repo.split(" ",1)[0]
                array.append({'SET': {'Repo': repo},
                              'WHERE_EQUAL': {'JiraIssueKey': item[0]}})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':array}

    @staticmethod
    def get_ticket_current_epic(jira_issue_key,main_log=LOG,ex_log=LOG_EXCEPTION,
                                ex_file=EX_LOG_FILE):
        """Gets the current epic for the specified ticket"""
        result = {}
        sql = f"""SELECT CurrentEpic, CurrentEpicProjectKey from JiraIssues WHERE JiraIssueKey =
        '{jira_issue_key}' AND CurrentEpic IS NOT NULL AND CurrentEpicProjectKey IS NOT NULL"""
        try:
            get_epic = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "JIDQ-GTCE-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        if get_epic != []:
            result['Epic'] = get_epic[0][0]
            result['ProjectKey'] = get_epic[0][1]
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
