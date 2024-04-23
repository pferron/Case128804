"""For information retrieval and processing"""

import os
from common.logging import TheLogs
from common.database_appsec import select

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []

class ProcessAutomation():
    """For retrieving and processing information"""

    @staticmethod
    def get_missing_runs(column_name,main_log=LOG):
        """Retrieves the missing runs"""
        missing_array = []
        files = retrieve_batch_files(column_name,main_log)
        if ScrVar.fe_cnt > 0:
            return {"FatalCount": ScrVar.fe_cnt,
                    "ExceptionCount": ScrVar.ex_cnt,
                    "Results": missing_array}
        if files:
            for file in files:
                batch_array = {}
                script_list = retrieve_scripts(file,column_name,main_log)
                if ScrVar.fe_cnt > 0:
                    continue
                if script_list:
                    batch_array['Batch File'] = file
                    batch_array['Scripts'] = []
                    for item in script_list:
                        item_array = {}
                        item_array['Script'] = item
                        func_array = retrieve_functions(file,column_name,item,main_log)
                        if ScrVar.fe_cnt > 0:
                            continue
                        item_array['Functions'] = func_array
                        batch_array['Scripts'].append(item_array)
                    missing_array.append(batch_array)
        return {"FatalCount": ScrVar.fe_cnt,
                "ExceptionCount": ScrVar.ex_cnt,
                "Results": missing_array}

def retrieve_batch_files(column_name,main_log=LOG):
    """Gets what scripts/functions need to be checked"""
    files = []
    sql = f"""SELECT DISTINCT BatchFile FROM ScriptExecutionSchedule WHERE {column_name} = 1 AND
    AlertOnSkippedRun = 1 ORDER BY BatchFile"""
    try:
        get_files = select(sql)
    except Exception as details:
        e_code = 'AAP-RBF-001'
        TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return files
    if get_files:
        for file in get_files:
            files.append(file[0])
    return files

def retrieve_scripts(batch_file,column_name,main_log=LOG):
    """Gets what scripts/functions need to be checked"""
    script_array = []
    duration = 'DATEADD(hour,-24,GETDATE())'
    if column_name in ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'):
        duration = 'DATEADD(day,-6.99,GETDATE())'
    elif column_name == 'FirstOfMonth':
        duration = 'DATEADD(month,-1,GETDATE())'
    elif column_name == 'Every5Minutes':
        duration = 'DATEADD(minute,-10,GETDATE())'
    elif column_name == 'Hourly':
        duration = 'DATEADD(hour,-1.25,GETDATE())'
    sql = f"""SELECT DISTINCT Script FROM ScriptExecutionSchedule WHERE BatchFile = '{batch_file}'
    AND {column_name} = 1 AND AlertOnSkippedRun = 1 ORDER BY Script"""
    try:
        get_files = select(sql)
    except Exception as details:
        e_code = 'AAP-RS-001'
        TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return script_array
    if get_files:
        for file in get_files:
            it_ran = did_it_run(file[0],None,duration)
            if it_ran is False:
                script_array.append(file[0])
    return script_array

def retrieve_functions(batch_file,column_name,script,main_log=LOG):
    """Gets what scripts/functions need to be checked"""
    func_array = []
    duration = 'DATEADD(hour,-24,GETDATE())'
    if column_name in ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'):
        duration = 'DATEADD(day,-6.99,GETDATE())'
    elif column_name == 'FirstOfMonth':
        duration = 'DATEADD(month,-1,GETDATE())'
    elif column_name == 'Every5Minutes':
        duration = 'DATEADD(minute,-10,GETDATE())'
    elif column_name == 'Hourly':
        duration = 'DATEADD(hour,-1.25,GETDATE())'
    sql = f"""SELECT DISTINCT FunctionName FROM ScriptExecutionSchedule WHERE BatchFile =
    '{batch_file}' AND {column_name} = 1 AND Script = '{script}' AND AlertOnSkippedRun = 1 ORDER
    BY FunctionName"""
    try:
        get_funcs = select(sql)
    except Exception as details:
        e_code = 'AAP-RF-001'
        TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return func_array
    if get_funcs:
        for func in get_funcs:
            it_ran = did_it_run(script,func[0],duration)
            if it_ran is False:
                func_array.append(func[0])
    return func_array

def did_it_run(script,function_name,duration,main_log=LOG):
    """Determines if the script/function ran as expected"""
    it_ran = False
    func_incl = ''
    if function_name is not None:
        func_incl = f" AND FunctionName = '{function_name}'"
    sql = f"""SELECT Script FROM ScriptExecutionTimes WHERE Script = '{script}'{func_incl} AND
    ExecutionDate >= {duration}"""
    try:
        run_happened = select(sql)
    except Exception as details:
        e_code = 'AAP-DIR-001'
        TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
        return it_ran
    if run_happened:
        it_ran = True
    return it_ran
