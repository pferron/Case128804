"""Performs maintenance on Checkmarx data"""

import os
import sys
import inspect
import traceback
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.miscellaneous import Misc
from common.logging import TheLogs
from common.general import General
from checkmarx.api_connections import CxAPI
from checkmarx.project_creation import CxCreate
from maint.checkmarx_maintenance import CxMaint

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        globals()[cmd['function']]()
    # run_checkmarx_maintenance()

class ScrVar():
    """Script-wide stuff"""
    ex_cnt = 0
    fe_cnt = 0
    start_timer = None
    running_function = None

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
    def get_cx_availability(repo,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """For checking if CX is up"""
        try:
            run_script = CxAPI.checkmarx_availability(proj_id,main_log,ex_log,ex_file)
        except Exception as e_details:
            func = f"CxAPI.checkmarx_availability({proj_id})"
            e_code = "MC-GCA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return False
        if run_script is False:
            TheLogs.log_headline(f"UNABLE TO PROCESS UPDATES FOR {repo}",2,"!",main_log)
            func = f"CxAPI.checkmarx_availability({proj_id})"
            details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
            details += "and that there are no license issues."
            e_code = "MC-GCA-002"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return False
        return run_script

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()
        cx_available = ScrVar.get_cx_availability('appsec-ops',10915,main_log,ex_log,ex_file)
        if cx_available is False:
            TheLogs.log_headline("UNABLE TO PROCESS ANY UPDATES FOR CHECKMARX",2,"!",main_log)
            func = "ScrVar.get_cx_availability('appsec-ops',10915)"
            details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
            details += "and that there are no license issues."
            e_code = "MC-TSS-001"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ALERT_SOURCE}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def run_checkmarx_maintenance(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Performs all Checkmarx maintenance'''
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    TheLogs.log_headline('UPDATING ALL PROJECTS: SASTProjects TABLE',1,"~",main_log)
    sp_maint_1 = CxMaint.base_sastprojects_updates(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(sp_maint_1)
    if sp_maint_1['Results'] is False:
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
    TheLogs.log_headline('CREATING MISSING PROJECTS: CHECKMARX',2,"#",main_log)
    p_create = CxCreate.run_all(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(p_create)
    sp_maint_2 = {'Results':True}
    if len(p_create['Results']) > 0:
        sp_maint_2 = CxMaint.update_created_baseline_projects(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(sp_maint_2)
    if sp_maint_2['Results'] is False:
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
    sp_details = CxMaint.update_sastprojects_details(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(sp_details)
    TheLogs.log_headline('UPDATING BASELINE PROJECTS: ApplicationAutomation & Applications TABLES',
                            1,"~",main_log)
    app_maint = CxMaint.update_baseline_projects(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(app_maint)
    TheLogs.log_headline('UPDATING PROJECT DETAILS: cxBaselineProjectDetails TABLE',1,"~",main_log)
    project_details = CxMaint.update_project_details(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(project_details)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

if __name__ == "__main__":
    main()
