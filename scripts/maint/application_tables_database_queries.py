"""Functions for maintenance_application_tables"""

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
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

class AppQueries():
    """"For database interaction"""

    @staticmethod
    def get_available_progteam_jira_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets repo/team pairs that need Jira info in ApplicationAutomation"""
        updates = []
        sql = """SELECT DISTINCT Repo, ProgTeam FROM ApplicationAutomation WHERE ProgTeam IS NOT NULL
        AND JiraProjectKey IS NULL AND ProgTeam IN (SELECT DISTINCT ProgTeam FROM ProgTeams WHERE
        JiraKey IS NOT NULL OR JiraParentKey IS NOT NULL) AND Repo IS NOT NULL"""
        try:
            updates = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "ATDQ-GAPTJU-001"
            func = f"DBQueries.select(\"{sql}\",'AppSec')"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':updates}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':updates}

    @staticmethod
    def get_jira_keys_for_team(team,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the JiraKey and JiraParent key for the specified team"""
        keys = []
        sql = f"""SELECT JiraKey, JiraParentKey FROM ProgTeams WHERE ProgTeam = '{team}'
        AND (JiraKey IS NOT NULL OR JiraParentKey IS NOT NULL)"""
        try:
            keys = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "ATDQ-GJKFT-001"
            func = f"DBQueries.select(\"{sql}\",'AppSec')"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':keys}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':keys}

    @staticmethod
    def get_applicationautomation_jira_project_keys(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets existing JiraProjectKey entries from the ApplicationAutomation table in the AppSec
        database"""
        keys = []
        sql = """SELECT DISTINCT JiraProjectKey FROM ApplicationAutomation WHERE JiraProjectKey IS
        NOT NULL ORDER BY JiraProjectKey"""
        try:
            keys = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "ATDQ-GAAJPK-001"
            func = f"DBQueries.select(\"{sql}\",'AppSec')"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':keys}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':keys}

    @staticmethod
    def get_progteams_teams(proj_key,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets prog team info from the ProgTeams table in the AppSec database"""
        teams = []
        sql = f"""SELECT DISTINCT ProgTeam, TechLead, ProductManager FROM ProgTeams WHERE
        JiraKey = '{proj_key}' AND Active = 1 AND JiraKey IS NOT NULL"""
        try:
            teams = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "ATDQ-GPT-001"
            func = f"DBQueries.select(\"{sql}\",'AppSec')"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':teams}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':teams}

    @staticmethod
    def get_applicationautomation_data(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets info from the ApplicationAutomation table in the AppSec database to update the
        Applications table"""
        get_info = []
        sql = """SELECT DISTINCT Repo, HasJiraSecurityFindingType, cxProjectID, cxLastScanID,
        cxLastScanDate, cxTechDebtBoarded, cxAutomated, SASTActive, ProductOwner, TechLead, SCAActive,
        wsProductToken, wsLastUpdatedDate, wsVulnTechDebtBoarded, wsLicenseTechDebtBoarded,
        wsTechDebtBoarded, Retired, ManualRetired FROM ApplicationAutomation WHERE Repo IS NOT NULL
        AND Repo IN (SELECT DISTINCT Repo FROM Applications) ORDER BY Repo"""
        try:
            get_info = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "ATDQ-GAAD-001"
            func = f"DBQueries.select(\"{sql}\",'AppSec')"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':get_info}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':get_info}
