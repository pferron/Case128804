"""Functions for maintenance_application_tables"""

import os
import inspect
import traceback
from dotenv import load_dotenv
from common.logging import TheLogs
from common.database_generic import DBQueries

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\automation_alerts-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\automation_alerts-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')


class ScrVar:
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

class WADatabase():
    """"For database interaction"""

    @staticmethod
    def get_unique_jira_keys(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves a list of unique Jira project keys from ApplicationAutomation"""
        keys = []
        sql = """SELECT DISTINCT JiraProjectKey FROM ApplicationAutomation WHERE (wsProductToken IS
        NOT NULL OR (cxProjectID IS NOT NULL AND cxProjectID != 0)) AND (JiraProjectKey != '' OR
        JiraProjectKey IS NOT NULL) AND (ExcludeTickets IS NULL OR ExcludeTickets != 1) AND
        (ExcludeScans IS NULL OR ExcludeScans != 1) AND Repo IS NOT NULL AND Repo != 'four'"""
        try:
            proj_keys = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "WDQ-GUJK-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,inspect.stack()[0][3],
                                  traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': keys}
        if proj_keys:
            for item in proj_keys:
                keys.append(item[0])
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': keys}

    @staticmethod
    def get_repos_missing_jira_info(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if issue exists in JiraIssues"""
        repos = []
        sql = """SELECT DISTINCT Repo FROM ApplicationAutomation WHERE (wsProductToken IS NOT NULL
        OR (cxProjectID IS NOT NULL AND cxProjectID != 0)) AND (JiraIssueParentKey IS NULL OR
        JiraProjectKey IS NULL OR JiraIssueParentKey = '' OR JiraProjectKey = '') AND
        (ExcludeTickets IS NULL OR ExcludeTickets != 1) AND (ExcludeScans IS NULL OR
        ExcludeScans != 1) AND Repo IS NOT NULL ORDER BY Repo"""
        try:
            missing_info = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "WDQ-GRMJI-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,inspect.stack()[0][3],
                                  traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}
        if missing_info:
            for repo in missing_info:
                repos.append(repo[0])
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}

    @staticmethod
    def get_projects_missing_security_finding_type(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns an array of repos missing the security finding ticket type in Jira"""
        repos = []
        sql = """SELECT DISTINCT Repo, JiraProjectKey FROM ApplicationAutomation WHERE
        HasJiraSecurityFindingType = 0 AND Repo IS NOT NULL AND (wsProductToken IS NOT NULL OR
        (cxProjectID IS NOT NULL AND cxProjectID != 0)) AND (JiraIssueParentKey IS NOT NULL OR
        JiraProjectKey IS NOT NULL) AND (ExcludeTickets IS NULL OR ExcludeTickets != 1) AND
        (ExcludeScans IS NULL OR ExcludeScans != 1) AND Repo != 'four' ORDER BY Repo"""
        try:
            missing_sf = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "WDQ-GPMSFT-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,inspect.stack()[0][3],
                                  traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}
        if missing_sf:
            for item in missing_sf:
                desc = f'{item[0]} ({item[1]})'
                repos.append(desc)
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}

    @staticmethod
    def get_missing_baseline_scans(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns a list of repos that have pipeline scans, but not baseline scans"""
        repos = []
        sql = """SELECT DISTINCT Repo FROM SASTProjects WHERE cxPipelineProjectId != 0 AND
        cxPipelineProjectId IS NOT NULL AND (cxBaselineProjectId = 0 OR cxBaselineProjectId IS
        NULL) AND Repo NOT IN (SELECT DISTINCT Repo FROM ApplicationAutomation WHERE
        ExcludeScans = 1) ORDER BY Repo"""
        try:
            missing_bl = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "WDQ-GMBS-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,inspect.stack()[0][3],
                                  traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}
        if missing_bl:
            for item in missing_bl:
                repos.append(item[0])
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': repos}

    @staticmethod
    def get_baselines_with_overdue_scans(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets a list of repos whose baseline scans are overdue"""
        repos = None
        r_cnt = 0
        sql = """SELECT DISTINCT Repo, LastBaselineScan FROM SASTProjects WHERE LastBaselineScan IS
        NULL OR LastBaselineScan <= DATEADD(day,-8,GETDATE()) AND Repo NOT IN (SELECT DISTINCT Repo
        FROM ApplicationAutomation WHERE Retired = 1 OR ExcludeScans = 1 OR ProjectOnHold = 1 OR
        ManualRetired = 1) ORDER BY Repo"""
        try:
            overdue_bl = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "AW-OCBS-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,inspect.stack()[0][3],
                                  traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results':repos,
                    'Count':r_cnt}
        if overdue_bl != []:
            repos = 'slack_headers:Repo\\Last Scan Date'
            for item in overdue_bl:
                ls_date = f'{item[1]}'
                if item[1] is None:
                    ls_date = 'Never'
                ls_date = ls_date.split(" ",1)[0]
                repos += f'\n{item[0]}\\{ls_date}'
                r_cnt += 1
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results':repos,
                'Count':r_cnt}
