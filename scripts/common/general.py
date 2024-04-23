"""This file contains generally useful functions"""

import os
import sys
import traceback
import inspect
from datetime import datetime
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
    '''Script-wide stuff'''
    fe_cnt = 0
    ex_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class General():
    """Has portable functions"""

    @staticmethod
    def do_script_query(query_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Retrieves the specified query from ScriptInfo.ScriptQueries and returns the results'''
        ScrVar.reset_exception_counts()
        result = []
        sql = f"""SELECT UsingDatabase, FullQuery FROM ScriptQueries WHERE ID = {query_id}"""
        try:
            response = DBQueries.select(sql,'ScriptInfo')
        except Exception as e_details:
            func = f"DBQueries.select({sql},'ScriptInfo')"
            e_code = "CG-DSQ-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}
        if response != []:
            result = do_dbquery(response[0][1],response[0][0],main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':result}

    @staticmethod
    def replace_blanks_in_list_of_dicts(array):
        """Set blank values (or x = 'None') to x = None in a list of dictionaries"""
        new_array = []
        for item in array:
            item_array = {}
            for key, value in item.items():
                if isinstance(value, str):
                    value = value.replace("'","")
                if value is None or value == 'None' or value == '':
                    item_array[key] = None
                else:
                    item_array[key] = value
            new_array.append(item_array)
        return new_array

    @staticmethod
    def replace_blanks_in_dict(items):
        """Replaces blank ('') values in a dictionary with None"""
        result = {}
        for key, value in items.items():
            if value is None or value == 'None' or value == '':
                value = None
            if isinstance(value, str):
                value = value.replace("'","").replace("\n","; ")
            result[key] = value
        return result

    @staticmethod
    def combine_dictionaries_in_list_of_dictionaries(array1,array2):
        """Combine values from a list of dictionaries"""
        combined = []
        for item in array1:
            i_array = {}
            for key, value in item.items():
                i_array[key] = value
            for item2 in array2:
                if item['name'] == item2['name']:
                    for key, value in item2.items():
                        if key not in item:
                            i_array[key] = value
            combined.append(i_array)
        return combined

    @staticmethod
    def cmd_processor(sys_args):
        """For being able to execute a function from the command line
        SETUP:
        from common.general import General
        In the calling file, insert the following into main()

            run_cmd = General.cmd_processor(sys.argv)
            for cmd in run_cmd:
                if 'args' in cmd:
                    globals()[cmd['function']](*cmd['args'])
                else:
                    globals()[cmd['function']]()

        USAGE:
        When calling a function from the command line, you can pass through as many arguments as
        needed for the function you wish to run. DO NOT use quotes (' or ") around your arguments,
        but DO wrap each function in double quotes. Please note lists, dictionaries, etc. cannot
        be processed by this script due to the simplicity of the implemented processing. If needed,
        this may be added as a feature in the future.
        Example calling a function with no arguments:
            python.exe your_file.py "your_function"
        Example calling a function with 1 argument:
            python.exe your_file.py "your_function(value1)"
        Example calling a function with 3 arguments:
            python.exe your_file.py "your_function(value1,value2,value3)"
        Example calling 2 functions:
            python.exe your_file.py "your_function" "other_function(value1,value2,value3,value4)"
        """
        to_run = []
        if len(sys_args) > 1:
            sys_args.pop(0)
            for arg in sys_args:
                if "(" in arg and "()" not in arg:
                    arg_list = []
                    func = arg.split("(",1)[0]
                    args = arg.split("(",1)[1][:-1]
                    args = args.split(",")
                    for item in args:
                        arg_list.append(item.replace("'",""))
                    to_run.append({'function': func, 'args': arg_list})
                else:
                    to_run.append({'function': arg})
        return to_run

def do_dbquery(sql,database,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    rv = []
    try:
        rv = DBQueries.select(sql,database)
    except Exception as e_details:
        func = f"DBQueries.select({sql},'{database}')"
        e_code = "CG-DDQ-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
    return rv