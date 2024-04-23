"""This file contains a common function for retrieving CWE details"""

import os
import sys
import traceback
import inspect
from datetime import datetime
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from cwe import Database
from common.logging import TheLogs
from common.database_appsec import select

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
    fe_array = []
    ex_cnt = 0
    ex_array = []
    src = ALERT_SOURCE.replace("-","\\")

class VulnDetails():
    """Has all of the stuff for getting CWE details"""

    @staticmethod
    def get_cwe(cwe_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves info for a CWE"""
        cwe_info = {}
        weakness = None
        cwe_link = f"https://cwe.mitre.org/data/definitions/{cwe_id}.html"
        try:
            weakness = Database().get(cwe_id)
        except Exception as e_details:
            func = f"Database().get('{cwe_id}')"
            e_code = 'CVI-GC-001'
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,ScrVar.src,SLACK_URL,1,ex_file)
            TheLogs.process_exceptions(ScrVar.ex_array,ScrVar.src,SLACK_URL,2,ex_file)
        if weakness is not None:
            cwe_info = {}
            cwe_info['cwe_id'] = f"CWE-{cwe_id}"
            cwe_title = None
            if weakness.name is not None and weakness.name != '':
                cwe_title = weakness.name
                cwe_title = str(cwe_title).replace("'","")
            cwe_info['name'] = cwe_title
            cwe_description = weakness.description
            if cwe_description == '':
                cwe_description = weakness.extended_description
            cwe_description = cwe_description.replace("'","")
            cwe_info['description'] = cwe_description
            cwe_info['link'] = cwe_link
        if cwe_info == {} or cwe_info is None:
            sql = f"SELECT Name, Description FROM CWE WHERE [CWE-ID] = {cwe_id}"
            try:
                cwe_data = select(sql)
            except Exception as e_details:
                e_code = 'CVI-GC-002'
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                ScrVar.ex_array.append(e_code)
                TheLogs.process_exceptions(ScrVar.fe_array,ScrVar.src,SLACK_URL,1,ex_file)
                TheLogs.process_exceptions(ScrVar.ex_array,ScrVar.src,SLACK_URL,2,ex_file)
                return
            if cwe_data:
                title = str(cwe_data[0][0]).replace("'","")
                description = str(cwe_data[0][1]).replace("'","")
                cwe_info['name'] = title
                cwe_info['description'] = description
                cwe_info['link'] = cwe_link
        return cwe_info
