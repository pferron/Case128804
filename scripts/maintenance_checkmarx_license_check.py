"""Retrieves the Checkmarx license and ensures it is active"""

import sys
import os
import inspect
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.general import General
from checkmarx.hid_lic_copy import copy_from_cx_server
from checkmarx.hid_license_check import checkmarx_license_check

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
    # verify_checkmarx_license()

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

class ScriptSteps():
    """The steps to run"""

    @staticmethod
    def copy_hid_and_license(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Copies the current HID/LIC files to the local server"""
        try:
            lic_copied = copy_from_cx_server(main_log=main_log)
            ScrVar.update_exception_info(lic_copied)
        except Exception as e_details:
            func = f"copy_from_cx_server(main_log={main_log})"
            e_code = "MCLC-CHAL-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3])
            ScrVar.fe_cnt += 1
            return False
        return lic_copied['IsCopied']

    @staticmethod
    def hid_and_license_comparison(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Compares the HID/LIC files on the local server and issues a Slack alert if they do not
        match"""
        try:
            check_complete = checkmarx_license_check(main_log=main_log)
            ScrVar.update_exception_info(check_complete)
        except Exception as e_details:
            func = f"checkmarx_license_check(main_log={main_log})"
            e_code = "MCLC-HALC-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3])
            ScrVar.fe_cnt += 1
            return False
        return check_complete['Success']

def verify_checkmarx_license(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Verifies that the Checkmarx license is current"""
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    copied = ScriptSteps.copy_hid_and_license(main_log,ex_log,ex_file)
    if copied is True:
        ScriptSteps.hid_and_license_comparison(main_log,ex_log,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

if __name__ == '__main__':
    main()
