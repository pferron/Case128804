"""This file contains generic functions that are commonly used in other scripts"""

import os
from dotenv import load_dotenv
import math
import time
from datetime import datetime
from common.database_appsec import insert, delete_row
from common.logging import TheLogs

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []
    log_main = None
    log_exceptions = None
    log_file_ex = None

    @staticmethod
    def check_logs(main_log,ex_log,ex_file):
        """Checks if log info is set - if not, create log files"""
        ScrVar.log_main = main_log
        ScrVar.log_exceptions = ex_log
        ScrVar.log_file_ex = ex_file
        if ScrVar.log_main is None:
            log_main_loc = rf"C:\AppSec\logs\{BACKUP_DATE}-{LOG_BASE_NAME}.log"
            ScrVar.log_main = TheLogs.setup_logging(log_main_loc)
        if ScrVar.log_file_ex is None:
            ScrVar.log_file_ex = rf"C:\AppSec\logs\{BACKUP_DATE}-{LOG_BASE_NAME}_exceptions.log"
        if ScrVar.log_exceptions is None:
            ScrVar.log_exceptions = TheLogs.setup_logging(ScrVar.log_file_ex)

class Misc:
    """Miscellaneous functions for us in various scripts"""
    @staticmethod
    def start_timer():
        """Starts the script execution timer"""
        start_date_time = datetime.now()
        start_date_time = start_date_time.strftime("%m/%d/%Y %H:%M:%S")
        script_start = time.time()
        return script_start, start_date_time

    @staticmethod
    def end_timer(script_start_info,alert_source,func,exception_count,fatal_exceptions,
                  main_log=None,ex_log=None,ex_file=None):
        """Ends the script timer and logs execution in the database"""
        ScrVar.check_logs(main_log,ex_log,ex_file)
        script_start = script_start_info[0]
        start_date_time = script_start_info[1]
        script_end = time.time()
        script_time = math.ceil(script_end - script_start)
        script_time = time.strftime("%H:%M:%S", time.gmtime(script_time))
        timezone = datetime.now()
        timezone = timezone.astimezone()
        timezone = timezone.tzinfo
        end_time = time.localtime()
        end_time = time.strftime("%H:%M:%S", end_time)
        if func == 'update_all_jira_issues' and alert_source == 'maintenance_jira_issues.py':
            record_jira_issues_updates(alert_source,func,start_date_time,end_time,timezone,
                                       main_log,ex_log,ex_file)
        record_script_execution(alert_source,func,start_date_time,script_time,exception_count,
                                fatal_exceptions,main_log,ex_log,ex_file)

    @staticmethod
    def day_of_the_week():
        """Gets the name of the day of the week"""
        today = datetime.now()
        today_is = today.strftime("%A")
        return today_is

    @staticmethod
    def progress_bar(completed,total,indent):
        """Creates a progress bar"""
        l_m = "\u2591"
        d_m = "\u2588"
        if completed == 0 or total == 0:
            progress = 0
            pct = 0
            done = 0
            todo = 32
        else:
            progress = (completed / total) * 100
            pct = round(progress, 2)
            done = math.floor(progress / 3.125)
            todo = math.floor(32 - done)
        if completed == 0:
            p_bar = print((" "*indent)+(l_m*todo)+"  "+str(pct)+"%     ",end="\r")
        elif completed == total:
            p_bar = print(" "*150,end="\r")
        else:
            p_bar = print((" "*indent)+(d_m*done)+(l_m*todo)+"  "+str(pct)+"%     ",end="\r")
        return p_bar

def record_jira_issues_updates(alert_source,func,start_date_time,end_time,timezone,main_log=None,
                               ex_log=None,ex_file=None):
    """Adds an entry into JiraIssuesUpdates and deletes entries older than 2 weeks"""
    ScrVar.check_logs(main_log,ex_log,ex_file)
    sql = f"""INSERT INTO JiraIssuesUpdates (Script, FunctionName, UpdatedDate,
    UpdatedTime, TimeZone) VALUES ('{alert_source}', '{func}', '{start_date_time}',
    '{end_time}', '{timezone}')"""
    try:
        insert(sql)
    except Exception as details:
        e_code = 'CM-RJIU-001'
        TheLogs.sql_exception(sql,e_code,details,ScrVar.log_exceptions,ScrVar.log_main,
                              ScrVar.log_file_ex)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,ScrVar.log_file_ex)
        TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,ScrVar.log_file_ex)
        return
    sql = "DELETE FROM JiraIssuesUpdates WHERE UpdatedDate <= DATEADD(day, -14, GETDATE())"
    try:
        delete_row(sql)
    except Exception as details:
        e_code = 'CM-RJIU-002'
        TheLogs.sql_exception(sql,e_code,details,ScrVar.log_exceptions,ScrVar.log_main,
                              ScrVar.log_file_ex)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,ScrVar.log_file_ex)
        TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,ScrVar.log_file_ex)
        return

def record_script_execution(alert_source,func,start_date_time,script_time,exception_count,
                            fatal_exceptions,main_log=None,ex_log=None,ex_file=None):
    """Adds a line to the ScriptExecutionTimes table to document that a script run completed"""
    ScrVar.check_logs(main_log,ex_log,ex_file)
    sql = f"""INSERT INTO ScriptExecutionTimes (Script, FunctionName, ExecutionDate,
    ExecutionTime, ExceptionsThrown, FatalExceptions) VALUES ('{alert_source}', '{func}',
    '{start_date_time}', '{script_time}', '{exception_count}', '{fatal_exceptions}')"""
    try:
        insert(sql)
    except Exception as details:
        e_code = 'CM-ET-001'
        TheLogs.sql_exception(sql,e_code,details,ScrVar.log_exceptions,ScrVar.log_main,
                              ScrVar.log_file_ex)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,ScrVar.log_file_ex)
        TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,ScrVar.log_file_ex)
        return
