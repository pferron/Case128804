"""This file contains functions for the maintenance performed in nonprodsec_infosecdashboard.py"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from common.logging import TheLogs
from common.database_generic import DBQueries

parent = os.path.abspath('.')
sys.path.insert(1,parent)

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
    db_default = 'InfoSecDashboard'

class IFDQueries():
    """Has useful functions"""

    @staticmethod
    def check_if_epic_exists(epic_key,main_log=LOG):
        """Checks if the epic exists in JiraEpics"""
        exists = False
        sql = f"""SELECT ProjectKey FROM JiraEpics WHERE EpicKey = '{epic_key}'"""
        try:
            project_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CIEE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return False
        if project_exists:
            exists = True
        return exists

    @staticmethod
    def check_if_issue_exists(use_table,issue_key,main_log=LOG):
        """Checks if the issue exists in the specified project table"""
        exists = False
        sql = f"""SELECT IssueKey FROM {use_table} WHERE IssueKey = '{issue_key}' AND
            SubTaskIssueKey IS NULL"""
        try:
            project_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CIIE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return False
        if project_exists:
            exists = True
        return exists

    @staticmethod
    def check_if_project_exists(project_key,main_log=LOG):
        """Checks if the project exists in JiraProjects"""
        exists = False
        sql = f"""SELECT ProjectKey FROM JiraProjects WHERE ProjectKey = '{project_key}'"""
        try:
            project_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CIPJE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return False
        if project_exists:
            exists = True
        return exists

    @staticmethod
    def check_if_program_exists(program_issue_key,main_log=LOG):
        """Checks if the program exists in JiraPrograms"""
        exists = False
        sql = f"""SELECT ProgramKey FROM JiraPrograms WHERE ProgramKey = '{program_issue_key}'"""
        try:
            project_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CIPGE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return False
        if project_exists:
            exists = True
        return exists

    @staticmethod
    def check_if_subtask_exists(use_table,task_key,main_log=LOG):
        """Checks if the subtask exists in the specified project table"""
        exists = False
        sql = f"""SELECT SubTaskIssueKey FROM {use_table} WHERE SubTaskIssueKey = '{task_key}'"""
        try:
            project_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CISE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return False
        if project_exists:
            exists = True
        return exists

    @staticmethod
    def check_if_table_exists(use_table,main_log=LOG):
        """Checks the InfoSecDashboard to see if the project table exists"""
        exists = False
        sql = f"""SELECT name FROM sys.tables WHERE name = '{use_table}'"""
        try:
            table_exists = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CITE-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            return False
        if table_exists:
            exists = True
        else:
            table_exists = IFDQueries.create_new_project_table(use_table,main_log)
        return exists

    @staticmethod
    def create_new_project_table(use_table,main_log=LOG):
        """If a project table does not exist, create it"""
        sql = f"""SELECT TOP 0 * INTO dbo.{use_table} FROM dbo.TicketTemplate"""
        try:
            DBQueries.update(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-CNPT-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            return False
        return True

    @staticmethod
    def get_epics_for_project(project_name,main_log=LOG):
        """Gets epics for the specified project"""
        epics = []
        sql = f"""SELECT DISTINCT EpicKey FROM JiraEpics WHERE JiraProjectName =
        '{project_name}'"""
        try:
            get_epics = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-GEFP-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            return []
        for epic in get_epics:
            epics.append(epic[0])
        return epics

    @staticmethod
    def get_projects(main_log=LOG):
        """Gets the projects from the InfoSec database"""
        sql = """SELECT DISTINCT JiraProjectKey, JiraProjectName, InfoSecDashboardTable FROM
        JiraTeams ORDER BY JiraProjectKey"""
        try:
            jira_projects = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-GP-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return []
        return jira_projects

    @staticmethod
    def get_programs_for_project(project_name,main_log=LOG):
        """Gets the program key(s) and name(s) for the project"""
        programs = []
        sql = f"""SELECT DISTINCT ProgramKey, ProgramName FROM JiraPrograms WHERE
        JiraProjectName = '{project_name}' ORDER BY ProgramKey"""
        try:
            programs = DBQueries.select(sql,ScrVar.db_default)
        except Exception as details:
            e_code = "ISDD-GPFP-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            return []
        return programs
