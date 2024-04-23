"""Some common functions for Checkmarx processing"""

import os
import sys
import traceback
import inspect
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from common.database_appsec import select
from common.logging import TheLogs

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

class ScrVar:
    """Script-wide stuff"""
    ex_cnt = 0
    fe_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class CxCommon:
    """Common functions for Checkmarx processing"""

    @staticmethod
    def get_severity_id(severity,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the numeric value of the severity"""
        severity_id = None
        severity = severity.capitalize()
        match severity:
            case 'Critical':
                severity_id = 0
            case 'High':
                severity_id = 1
            case 'Medium':
                severity_id = 2
        return severity_id

    @staticmethod
    def get_result_state_id(result_state,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the numeric value of the result state"""
        result_state_id = None
        match result_state:
            case 'To Verify':
                result_state_id = 0
            case 'Not Exploitable':
                result_state_id = 1
            case 'Confirmed':
                result_state_id = 2
            case 'Urgent':
                result_state_id = 3
            case 'Proposed Not Exploitable':
                result_state_id = 4
            case 'Tech Debt':
                result_state_id = 5
        return result_state_id

    @staticmethod
    def verify_found_in_last_scan(scan_id,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                                  ex_file=EX_LOG_FILE):
        """Checks if the provided Baseline scan ID was the most recent scan"""
        found_in_last_scan = 0
        sql = f"""SELECT DISTINCT ScanID FROM SASTScans WHERE ScanID = {scan_id} AND
        BaselineProjectID = {proj_id}"""
        try:
            found = select(sql)
        except Exception as e_details:
            e_code = "CMN-VFILS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                    'Results':found_in_last_scan}
        if found != []:
            found_in_last_scan = 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                'Results':found_in_last_scan}
