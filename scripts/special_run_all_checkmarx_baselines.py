"""This file is to kickoff baseline scans for all Checkmarx projects
ALLOW AT LEAST 2 HOURS FOR ALL SCANS TO COMPLETE"""

import os
import sys
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from checkmarx.api_connections import CxAPI
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.database_appsec import select
from common.general import General
from common.alerts import Alerts
from tool_checkmarx import ScrVar as ToolCx
from maint.checkmarx_maintenance import CxMaint

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
    "Default stuff"
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
    ### FOR ONE REPO:
    # kick_off_all_scans('appsec-ops',LOG)
    ### FOR ALL REPOS:
    # kick_off_all_scans(None,LOG)

def kick_off_all_scans(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs all functions sequentially"""
    running_function = 'kick_off_all_scans'
    start_timer = Misc.start_timer()
    if repo is None:
        TheLogs.log_headline('UPDATING CHECKMARX DATA IN ApplicationAutomation FOR ALL REPOS',
                                2,"#",main_log)
        cx_up = ToolCx.get_cx_availability('appsec-ops',1,main_log)
    else:
        TheLogs.log_headline(f'UPDATE CHECKMARX DATA IN ApplicationAutomation FOR {repo}',2,
                                "#",main_log)
        cx_up = ToolCx.get_cx_availability(repo,1,main_log)
    if cx_up is False:
        func = f"ToolCx.get_cx_availability(1,'{main_log}')"
        e_code = "SRACB-KOAS-001"
        details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
        details += "and that there are no license issues."
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        ScrVar.fe_array.append(e_code)
    else:
        if repo is None:
            try:
                CxMaint.base_sastprojects_updates(main_log,ex_log,ex_file)
            except Exception as details:
                func = f"base_sastprojects_updates(None,'{main_log}')"
                e_code = "SRACB-KOAS-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                ScrVar.fe_array.append(e_code)
        else:
            try:
                CxMaint.base_sastprojects_updates(main_log,ex_log,ex_file)
            except Exception as details:
                func = f"update_baseline_data('{repo}','{main_log}')"
                e_code = "SRACB-KOAS-003"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                ScrVar.fe_array.append(e_code)
        if ScrVar.fe_cnt == 0:
            if repo is None:
                sql = """SELECT DISTINCT Repo,cxProjectID,cxLastScanDate FROM
                ApplicationAutomation WHERE cxProjectID IS NOT NULL AND (Retired IS NULL OR
                Retired = 0) ORDER BY cxLastScanDate DESC"""
            else:
                sql = f"""SELECT DISTINCT Repo,cxProjectID,cxLastScanDate FROM
                ApplicationAutomation WHERE cxProjectID IS NOT NULL AND (Retired IS NULL OR
                Retired = 0) AND Repo = '{repo}' ORDER BY cxLastScanDate DESC"""

            try:
                to_scan = select(sql)
            except Exception as details:
                e_code = "SRACB-KOAS-004"
                TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                ScrVar.fe_array.append(e_code)
        if ScrVar.fe_cnt == 0:
            if to_scan:
                for item in to_scan:
                    repo = item[0]
                    proj_id = item[1]
                    comment = "Scan initiated by automation due to recent Checkmarx update."
                    TheLogs.log_headline(f'INITIATING SCAN FOR {repo}',1,"#",main_log)
                    try:
                        launched = CxAPI.launch_cx_scan(proj_id,comment)
                    except Exception as details:
                        func = f"CxAPI.launch_cx_scan({proj_id},'{comment}')"
                        e_code = "SRACB-KOAS-005"
                        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,LOG,
                                                   EX_LOG_FILE)
                        ScrVar.ex_cnt += 1
                        ScrVar.ex_array.append(e_code)
                        continue
                    if launched is True:
                        TheLogs.log_info('Scan successfully requested',1,"*",main_log)
                    else:
                        ScrVar.f_array.append(repo)
                        TheLogs.log_info(f'Scan request failed for {repo}',1,"!",main_log)
    TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
    TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
    ScrVar.f_array = sorted(set(ScrVar.f_array))
    if len(ScrVar.f_array) > 0:
        Alerts.manual_alert(rf'{ALERT_SOURCE}',ScrVar.f_array,len(ScrVar.f_array),8,SLACK_URL)
    Misc.end_timer(start_timer,rf'{ALERT_SOURCE}',running_function,ScrVar.ex_cnt,ScrVar.fe_cnt)

if __name__ == "__main__":
    main()
