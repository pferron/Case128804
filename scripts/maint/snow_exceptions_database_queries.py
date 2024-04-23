"""SNow related queries for the AppSec database"""

import os
import traceback
import inspect
from datetime import datetime, timedelta
from dotenv import load_dotenv
from common.logging import TheLogs
from common.database_generic import DBQueries

load_dotenv()
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

class SNowQueries():
    """SNow related queries for the AppSec database"""

    @staticmethod
    def mark_approvers_inactive(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Sets the CurrentApprover column in SNowSecurityApprovers to 0 for all users'''
        ScrVar.reset_exception_counts()
        sql = """UPDATE SNowSecurityApprovers SET CurrentApprover = 0"""
        try:
            response = DBQueries.update(sql,'AppSec')
        except Exception as e_details:
            e_code = "SEDQ-MAI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_all_ritms(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Returns a list of RITM items for reference'''
        ScrVar.reset_exception_counts()
        tickets = {'JiraSet':[],'JiraNotSet':[]}
        result = {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':tickets}
        sql = """SELECT DISTINCT RITMTicket, JiraTickets FROM SNowSecurityExceptions"""
        try:
            response = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "SEDQ-GAR-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return result
        if response != []:
            for item in response:
                if item[1] is None:
                    tickets['JiraNotSet'].append(item[0])
                else:
                    tickets['JiraSet'].append(item[0])
        return result

    @staticmethod
    def get_all_jiraissues(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Returns a list of RITM items for reference'''
        ScrVar.reset_exception_counts()
        tickets = []
        result = {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':tickets}
        sql = """SELECT DISTINCT JiraIssueKey, OldJiraIssueKey FROM JiraIssues"""
        try:
            response = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "SEDQ-GAJI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return result
        if response != []:
            for item in response:
                if item[0] is not None:
                    tickets.append(item[0])
                if item[1] is not None:
                    tickets.append(item[1])
        tickets = sorted(set(tickets))
        return result
