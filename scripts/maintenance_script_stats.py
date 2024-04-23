"""Runs maintenance for ScriptExecutionAverageRunTimes"""

import sys
import os
import inspect
import traceback
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.general import General
from common.database_generic import DBQueries

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # ScriptStats.update_run_times()

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

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

class ScriptStats():
    """Test class"""

    @staticmethod
    def update_run_times(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates the ScriptExecutionAverageRunTimes table"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        cycle_through_execution_months(main_log,ex_log,ex_file)
        update_overall_stats(main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def cycle_through_execution_months(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Cycles through the past 12 months to get data for ScriptExecutionAverageRunTimes"""
    month = 0
    while month < 13:
        added = 0
        updated = 0
        the_month = get_month_name(month)
        TheLogs.log_headline(f"UPDATING ScriptExecutionAverageRunTimes FOR {the_month}",
                             2,"#",main_log)
        scripts = get_list_of_logged_scripts(month,main_log,ex_log,ex_file)
        for script in scripts:
            data = get_runs_for_script_and_function(script['Script'],script['FunctionName'],month,
                                                    main_log,ex_log,ex_file)
            updates = update_database(month,data,main_log,ex_log,ex_file)
            added += updates['Added']
            updated += updates['Updates']
        month += 1
        TheLogs.log_info(f"{added} line item(s) added",2,"*",main_log)
        TheLogs.log_info(f"{updated} line item(s) updated",2,"*",main_log)

def update_overall_stats(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the all-time columns for ScriptExecutionAverageRunTimes"""
    added = 0
    updated = 0
    TheLogs.log_headline(f"UPDATING ScriptExecutionAverageRunTimes FOR ALL TIME STATS",
                            2,"#",main_log)
    scripts = get_list_of_logged_scripts(1200,main_log,ex_log,ex_file)
    for script in scripts:
        data = get_runs_for_script_and_function(script['Script'],script['FunctionName'],1200,
                                                main_log,ex_log,ex_file)
        updates = update_database(1200,data,main_log,ex_log,ex_file)
        added += updates['Added']
        updated += updates['Updates']
    TheLogs.log_info(f"{added} line item(s) added",2,"*",main_log)
    TheLogs.log_info(f"{updated} line total update(s) made",2,"*",main_log)

def get_list_of_logged_scripts(month,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Returns a list of all script/function pairs from ScriptExecutionTimes"""
    script_list = []
    sql = """SELECT DISTINCT Script, FunctionName FROM ScriptExecutionTimes """
    if month != 1200:
        sql += f"""WHERE MONTH(ExecutionDate) = MONTH(DATEADD(month,-{month},GETDATE())) AND
        YEAR(ExecutionDate) = YEAR(DATEADD(month,-{month},GETDATE()))
        ORDER BY Script, FunctionName"""
    try:
        response = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "MSS-GLOLS-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return script_list
    if response != []:
        for item in response:
            script_list.append({'Script':item[0],'FunctionName':item[1]})
    return script_list

def get_runs_for_script_and_function(script,function_name,month,main_log=LOG,
                                     ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Returns the number of times a script/function ran and the average run time"""
    script_data = {'Script':script,'FunctionName':function_name,
                   'AverageTime':None,'Executions':None}
    sql = f"""SELECT ExecutionTime FROM ScriptExecutionTimes WHERE Script = '{script}' AND
    FunctionName = '{function_name}' """
    if month != 1200:
        sql += f"""AND MONTH(ExecutionDate) = MONTH(DATEADD(month,-{month},GETDATE())) AND
        YEAR(ExecutionDate) = YEAR(DATEADD(month,-{month},GETDATE()))"""
    try:
        response = DBQueries.select(sql,'AppSec')
    except Exception as e_details:
        e_code = "MSS-GRFSAF-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return script_data
    if response != []:
        ex_times = []
        total_seconds = 0
        for item in response:
            print(item)
            ex_times.append(item[0])
            hh, mm, ss = str(item[0]).split(":")
            script_seconds = int(hh)*3600+int(mm)*60+int(ss)
            total_seconds += script_seconds
        average_seconds = math.ceil(total_seconds/len(ex_times))
        script_data['AverageTime'] = str(datetime.strptime(str(timedelta(seconds=average_seconds)),
                                                           "%H:%M:%S").time())
        script_data['Executions'] = len(ex_times)
    return script_data

def update_database(month,data_dict,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Posts updates to ScriptExecutionAverageRunTimes"""
    runs_column = 'RunsThisMonth'
    avg_time_column = 'AvgTimeThisMonth'
    ins_cnt = 0
    upd_cnt = 0
    if month == 1200:
        runs_column = 'RunsAllTime'
        avg_time_column = 'AvgTimeAllTime'
    elif month == 1:
        runs_column = 'Runs1MonthAgo'
        avg_time_column = 'AvgTime1MonthAgo'
    elif month > 1 and month < 13:
        runs_column = f'Runs{month}MonthsAgo'
        avg_time_column = f'AvgTime{month}MonthsAgo'
    if data_dict['Executions'] is not None:
        ins_data = [{'Script':data_dict['Script'],'FunctionName':data_dict['FunctionName'],
                     runs_column:data_dict['Executions'],avg_time_column:data_dict['AverageTime']}]
        upd_data = [{'SET':{runs_column:data_dict['Executions'],
                            avg_time_column:data_dict['AverageTime']},
                     'WHERE_EQUAL':{'Script':data_dict['Script'],
                                    'FunctionName':data_dict['FunctionName']}}]
        try:
            count = DBQueries.insert_multiple('ScriptExecutionAverageRunTimes',ins_data,
                                                 'AppSec',verify_on=['Script','FunctionName'],
                                                 show_progress=False)
            if count > 0:
                ins_cnt += count
        except Exception as e_details:
            func = f"DBQueries.insert_multiple('ScriptExecutionAverageRunTimes',{ins_data},"
            func += "verify_on=['Script','FunctionName'],show_progress=False)"
            e_code = "MSS-UD-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        try:
            count = DBQueries.update_multiple('ScriptExecutionAverageRunTimes',upd_data,
                                                  'AppSec',show_progress=False)
            if count > 0:
                upd_cnt += count
        except Exception as e_details:
            func = f"DBQueries.update_multiple('ScriptExecutionAverageRunTimes',{upd_data},"
            func += "show_progress=False)"
            e_code = "MSS-UD-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    return {'Added':ins_cnt,'Updates':upd_cnt}

def get_month_name(the_month,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Returns the name of the specified month"""
    month_names = ['January','February','March','April','May','June','July','August','September',
                   'October','November','December']
    calc_month = datetime.now() + relativedelta(months=-the_month)
    m_text = f"{month_names[calc_month.month-1].upper()} {calc_month.year}"
    return m_text

if __name__ == '__main__':
    main()
