"""IMPORTANT: RUN special-run-all-checkmarx-baselines.py AND WAIT FOR SCANS TO COMPLETE BEFORE
RUNNING THIS FILE. SCAN COMPLETION FOR ALL REPOS GENERALLY TAKES ABOUT 2 HOURS, BUT CHECK THE
QUEUE IN CHECKMARX TO ENSURE ALL ARE DONE.
This file will mark new findings in the first scan after a Checkmarx update as Tech Debt to avoid
blocking teams on irrelevant findings. For expedience, this file ONLY HANDLES NEW FINDINGS IN
SUCCESSFULLY COMPLETED SCANS."""

import os
import sys
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.alerts import Alerts
from common.general import General
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.database_appsec import update_multiple_in_table
from checkmarx.api_connections import CxAPI
from maint.checkmarx_database_queries import CxASDatabase
from tool_checkmarx import ScrVar as ToolCx, single_project_updates

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')


class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    ex_array = []
    fe_array = []
    f_array = []

def main():
    """Executes default stuff """
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
    ### FOR ONE REPO:
    # update_all_scans('appsec-ops')
    ### FOR ALL REPOS:
    # update_all_scans(None)

def update_all_scans(repo, main_log=LOG):
    """Runs all functions sequentially"""
    running_function = 'update_all_scans'
    start_timer = Misc.start_timer()
    u_array = []
    u_cnt = 0
    if repo is None:
        TheLogs.log_headline('UPDATING CHECKMARX FINDINGS FOR ALL REPOS',2,"#",main_log)
        cx_up = ToolCx.get_cx_availability('dde',1,main_log)
    else:
        TheLogs.log_headline(f'UPDATING CHECKMARX FINDINGS FOR {repo}',2,"#",main_log)
        cx_up = ToolCx.get_cx_availability(repo,1,main_log)
    if cx_up is False:
        func = f"ToolCx.get_cx_availability(1,'{main_log}')"
        e_code = "SRACU-UAS-001"
        details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
        details += "and that there are no license issues."
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
    else:
        to_update = CxASDatabase.get_repo_and_project_id(repo,main_log)
        update_exception_count(to_update)
        if to_update['Results'] != []:
            for item in to_update['Results']:
                repo = item['Repo']
                proj_id = item['cxProjectID']
                update_multiple_in_table('ApplicationAutomation',
                                         {'SET': {'cxTechDebtBoarded': 0},
                                          'WHERE_EQUAL': {'Repo': repo},
                                          'WHERE_NOT': None})
                set_results = CxASDatabase.get_results_to_confirm(proj_id,main_log)
                update_exception_count(to_update)
                for result in set_results['Results']:
                    comment = "Confirming finding for Tech Debt designation."
                    try:
                        CxAPI.update_res_state(result['cxScanID'],result['cxPathID'],2,comment)
                    except Exception as details:
                        func = f"CxAPI.update_res_state({result['cxScanID']},{result['cxPathID']},"
                        func += f"2,'{comment}')"
                        e_code = "SRACU-UAS-002"
                        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,LOG,
                                                   EX_LOG_FILE)
                        ScrVar.ex_cnt += 1
                        ScrVar.ex_array.append(e_code)
                        ScrVar.f_array.append(repo)
                        continue
                if repo not in ScrVar.f_array:
                    try:
                        single_project_updates(repo,proj_id,0,main_log)
                    except Exception as details:
                        func = f"single_project_updates('{repo}',{proj_id},0,'{main_log}')"
                        e_code = "SRACU-UAS-003"
                        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,LOG,
                                                   EX_LOG_FILE)
                        ScrVar.ex_cnt += 1
                        ScrVar.ex_array.append(e_code)
                        ScrVar.f_array.append(repo)
                        continue
                    u_array.append({'SET': {'cxTechDebtBoarded': 1},
                                    'WHERE_EQUAL': {'Repo': repo},
                                    'WHERE_NOT': None})
    if u_array != []:
        u_cnt += update_multiple_in_table('ApplicationAutomation',u_array)
    u_lng = f'{u_cnt} repo(s) updated'
    TheLogs.log_info(u_lng,2,"*",main_log)
    TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
    TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
    ScrVar.f_array = sorted(set(ScrVar.f_array))
    if len(ScrVar.f_array) > 0:
        Alerts.manual_alert(rf'{ALERT_SOURCE}',ScrVar.f_array,len(ScrVar.f_array),9,SLACK_URL)
    Misc.end_timer(start_timer,rf'{ALERT_SOURCE}',running_function,ScrVar.ex_cnt,ScrVar.fe_cnt)

def update_exception_count(dictionary):
    """Updates the count of exceptions"""
    if 'FatalCount' in dictionary:
        ScrVar.fe_cnt += dictionary['FatalCount']
    if 'ExceptionCount' in dictionary:
        ScrVar.ex_cnt += dictionary['ExceptionCount']

if __name__ == "__main__":
    main()
