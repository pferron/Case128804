"""This file processes Checkmarx changes and scans"""

import os
import sys
import traceback
import inspect
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from datetime import datetime
from common.logging import TheLogs
from common.database_appsec import select
from common.general import General
from common.miscellaneous import Misc
from checkmarx.api_connections import CxAPI
from checkmarx.ticketing import CxTicketing
from checkmarx.report_processing import CxReports
from checkmarx.pipeline_sync import CxPipelines
from maintenance_jira_issues import update_jira_project_tickets

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # all_cx_updates()
    # single_project_updates('merchant-crm',82,1)

class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    start_timer = None
    running_function = ''

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = dictionary['FatalCount']
        exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()
        cx_available = ScrVar.get_cx_availability('appsec-ops',10915,main_log,ex_log,ex_file)
        if cx_available is False:
            TheLogs.log_headline("UNABLE TO PROCESS ANY UPDATES FOR CHECKMARX",2,"!",main_log)
            func = "CxAPI.checkmarx_availability(1)"
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

    @staticmethod
    def get_cx_availability(repo,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """For checking if CX is up"""
        try:
            run_script = CxAPI.checkmarx_availability(proj_id,main_log,ex_log,ex_file)
        except Exception as e_details:
            func = f"CxAPI.checkmarx_availability({proj_id})"
            e_code = "TC-GCA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return False
        if run_script is False:
            TheLogs.log_headline(f"UNABLE TO PROCESS UPDATES FOR {repo}",2,"!",main_log)
            func = f"CxAPI.checkmarx_availability({proj_id})"
            details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
            details += "and that there are no license issues."
            e_code = "TC-GCA-002"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return False
        return run_script

def single_project_updates(repo,proj_id,force_scan_update,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
    """Updates Checkmarx data for a single repo"""
    update_tickets = update_jira_project_tickets(repo,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(update_tickets)
    reports = CxReports.update_results(proj_id,force_scan_update,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(reports)
    statuses = CxReports.update_finding_statuses(proj_id,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(statuses)
    states = CxReports.update_all_baseline_states(proj_id,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(states)
    can_ticket = CxTicketing.can_ticket(proj_id,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(can_ticket)
    if can_ticket['Results'] is True:
        cocne = CxTicketing.close_or_cancel_not_exploitable(repo,proj_id,main_log,ex_log,
                                                            ex_file)
        ScrVar.update_exception_info(cocne)
        if repo == 'four':
            caut = CxTicketing.create_and_update_tickets_by_query_src_and_dest(repo,proj_id,
                                                                               main_log,ex_log,
                                                                               ex_file)
        else:
            caut = CxTicketing.create_and_update_tickets(repo,proj_id,main_log,ex_log,ex_file)
        ScrVar.update_exception_info(caut)
        attc = CxTicketing.add_tickets_to_cx(repo,proj_id,main_log,ex_log,ex_file)
        ScrVar.update_exception_info(attc)
        coct = CxTicketing.close_or_cancel_tickets(repo,proj_id,main_log,ex_log,ex_file)
        ScrVar.update_exception_info(coct)
    pipeline_sync = CxPipelines.sync_findings_to_pipeline(proj_id,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(pipeline_sync)
    update_tickets = update_jira_project_tickets(repo,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(update_tickets)
    if force_scan_update == 1:
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
            'missing_similarity_ids': reports['missing_similarity_ids']}

def all_cx_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Sequentially runs all Checkmarx updates"""
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    cx_available = ScrVar.get_cx_availability('appsec-ops',10915,main_log,ex_log,ex_file)
    if cx_available is False:
        TheLogs.log_headline("UNABLE TO PROCESS ANY UPDATES FOR CHECKMARX",2,"!",main_log)
        func = "CxAPI.checkmarx_availability(1)"
        details = "Unable to connect to the Checkmarx API. Please ensure the server is running "
        details += "and that there are no license issues."
        e_code = "TC-ACU-001"
        TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
    TheLogs.log_headline("CHECKMARX AVAILABILITY HAS BEEN VERIFIED",2,"#",main_log)
    TheLogs.log_info("Processing will continue",2,"*",main_log)
    sql = """SELECT DISTINCT CxProjectID, Repo FROM ApplicationAutomation WHERE cxProjectID IS NOT
    NULL AND (Retired != 1 OR Retired IS NULL) AND (ProjectOnHold IS NULL OR ProjectOnHold != 1)
    AND (ManualRetired IS NULL OR ManualRetired != 1) AND Repo != 'four' ORDER BY Repo"""
    try:
        all_projects = select(sql)
    except Exception as e_details:
        e_code = "TC-ACU-002"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
    no_similarityid_projects = []
    if all_projects != []:
        for project in all_projects:
            repo = project[1]
            proj_id = project[0]
            project_info = single_project_updates(repo,proj_id,0,main_log,ex_log,ex_file)
            if project_info['missing_similarity_ids'] > 0:
                no_similarityid_projects.append(proj_id)
    man_rev = CxReports.alert_on_findings_needing_manual_review(main_log,ex_log,ex_file)
    ScrVar.update_exception_info(man_rev)
    if len(no_similarityid_projects) > 0:
        TheLogs.process_exceptions(no_similarityid_projects,rf'{ALERT_SOURCE}',SLACK_URL,14,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

if __name__ == "__main__":
    main()
