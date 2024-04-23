import os
import pyodbc
import pytz
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from common.alerts import Alerts
from common.logging import TheLogs
from common.database_sql_server_connection import SQLServerConnection
from common.miscellaneous import Misc
from jenkins_files.jenkins_manager import JenkinsManager
from snow.task_manager import SNTasksManager

# What does this script does?
# 1. Checks if there are stuck builds and sends a message to appsec alerts if there are any.
#   Stuck builds are builds that haven been in New status for more than 5 minutes.
# 2. Updates new builds
#   Trigger run for new builds and moves it into processing in QA builds table.
# 3. Updates processing builds
#   Checks if the builds is still running.
#     a. if it is, just log that it's still running
#     b. if not:
#       i. update qa builds table since it's finished
#       ii. if it fails, update SNow ticket and send alert to appsec-alerts
#       iii. if it's successful, just add comment to SNow

load_dotenv()
ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".", 1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_ALERTS = os.environ.get('SLACK_URL_ALERTS')
conn = SQLServerConnection(source=ALERT_SOURCE, log_file=LOG_FILE, exception_log_file=EX_LOG_FILE)
main_log = LOG

class ScrVar:
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []
    nraa_array = []

def main() -> None:
    TheLogs.log_headline('BEGINNING appsecjenkins', 3, "#", main_log)
    appsecjenkins()


def appsecjenkins() -> None:
    running_function = "appsecjenkins"
    start_timer = Misc.start_timer()
    stuck_builds = check_stuck_builds()
    if not stuck_builds:
        update_qa_builds_table()
    TheLogs.log_info("Script done.", 2, "*", main_log)
    Misc.end_timer(start_timer, rf'{ALERT_SOURCE}', running_function, ScrVar.ex_cnt, ScrVar.fe_cnt)

def check_stuck_builds() -> List[pyodbc.Row]:
    stuck_builds = get_new_builds()
    if stuck_builds:
        TheLogs.log_info("Found stuck builds.", 2, "*", main_log)
        stuck_date = stuck_builds[0][1]
        time_stuck = datetime.now(pytz.timezone("America/Denver")).replace(tzinfo=None) - stuck_date
        if time_stuck.seconds >= 300:
            TheLogs.log_headline('There are builds stuck for more than 5 minutes', 3, "#", main_log)
            if time_stuck.seconds <= 650:
                time_stuck = str(time_stuck).split(".",1)[0]
                status = stuck_builds[0][2]
                change_request_num = stuck_builds[0][3]
                repo = stuck_builds[0][4]
                ch_lnk = Alerts.create_change_ticket_link(change_request_num)
                TheLogs.log_info("Sending slack message to appsecalerts to alert stuck builds.",
                                    2, "*", main_log)
                msg = [f'*Time Stuck:*  {time_stuck}',f'*Status:*  {status}',
                       f'*Repo:*  {repo}',f'*Change Number:*  {change_request_num}>']
                if ch_lnk is not None:
                    msg = [f'*Time Stuck:*  {time_stuck}',f'*Status:*  {status}',
                           f'*Repo:*  {repo}',f'*Change Number:*  {ch_lnk}']
                try:
                    Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 10, SLACK_URL_ALERTS)
                except Exception as details:
                    func = rf"Alerts.manual_alert('{ALERT_SOURCE}', msg, 1, 10, SLACK_URL_ALERTS)"
                    e_code = "MJ-MAIN-001"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.fe_cnt += 1
                    ScrVar.fe_array.append(e_code)
                    if ScrVar.fe_cnt > 0:
                        TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,
                                                   EX_LOG_FILE)
                return stuck_builds
            else:
                TheLogs.log_headline("Build has been stuck for more than 10 minutes, "
                                     "NOT sending Slack message.", 3, "*", main_log)

def get_new_builds() -> Optional[List[pyodbc.Row]]:
    """gets new_builds from QABuilds table"""
    sql = """
        SELECT ID as id, RcvDate AS rcv_date, Status AS status, ChangeRequestNum AS
        change_request_num, Repo AS repo, Branch AS branch, BuildInfo AS build_info,
        AppSysID as app_sysid
        FROM QABuilds
        WHERE Status = 'New' ORDER BY RcvDate DESC
        """
    conn.func = 'get_new_builds'
    new_builds = conn.query_with_logs(sql)
    return new_builds

def get_processing_builds() -> Optional[List[pyodbc.Row]]:
    """gets builds in status Processing"""
    sql = """
        SELECT ID as id, RcvDate AS rcv_date, Status AS status, ChangeRequestNum AS
        change_request_num, Repo AS repo, Branch AS branch, BuildInfo AS build_info,
        AppSysID as app_sysid
        FROM QABuilds
        WHERE Status = 'Processing' ORDER BY RcvDate DESC
        """
    conn.func = 'get_processing_builds'
    processing_builds = conn.query_with_logs(sql)
    return processing_builds

def update_qa_builds_table() -> None:
    """updates or inserts into QABuilds table"""
    TheLogs.log_info("Updating QA Builds", 2, "*", main_log)
    snow_task_manager = SNTasksManager()
    jenkins_server = JenkinsManager()
    new_builds, processing_builds = get_qa_builds()
    if new_builds:
        update_new_builds(new_builds, jenkins_server)
    if processing_builds:
        update_processing_builds(processing_builds, snow_task_manager, jenkins_server)
    if not new_builds and not processing_builds:
        TheLogs.log_info("There are no new or processing builds.",1,"*",LOG)

def get_qa_builds() -> Tuple[List[pyodbc.Row], List[pyodbc.Row]]:
    """gets builds in new and/or processing status"""
    new_builds = get_new_builds()
    processing_builds = get_processing_builds()
    return new_builds, processing_builds

def update_new_builds(new_builds: List[pyodbc.Row],
                      jenkins_server: JenkinsManager) -> None:
    """updates new builds in QABuilds table from Jenkins build info"""
    TheLogs.log_headline(f"Found {len(new_builds)} new builds.", 3, "#", main_log)
    for build in new_builds:
        jenkins_build_info = trigger_jenkins_build_and_get_build_info(build.repo, build.branch,
                                                                      jenkins_server)
        if build.app_sysid == "":
            sql = f"SELECT snSysID from Applications WHERE repo = '{build.repo}'"
            conn.func= 'update_new_builds'
            app = conn.query_with_logs(sql)[0]
            build.app_sysid = app.sysid
        TheLogs.log_headline(f"Updating QABuilds table for {build.repo}:{build.app_sysid}", 3, "#",
                             main_log)
        sql = """UPDATE QABuilds SET Status = '{0}', BuildInfo = '{1}', LastUpdateDate = '{2}',
        BuildNum = {3}, AppSysID = '{4}'
        WHERE ID = {5}""".format("Processing", str(jenkins_build_info).replace("'", "''"),
                                 str(datetime.now())[:-7], jenkins_build_info["id"],
                                 build.app_sysid, build.id)
        conn.func = 'update_new_builds'
        conn.query_with_logs(sql)

def update_processing_builds(builds: List[pyodbc.Row],
                             snow_task_manager: SNTasksManager,
                             jenkins_server: JenkinsManager) -> None:
    """updates processing QABuilds based on Jenkins build info"""
    message = f"Found {len(builds)} processing builds."
    TheLogs.log_info(message, 2, "*", main_log)
    for build in builds:
        TheLogs.log_info(f"Current change: {build.change_request_num}",1,"*",LOG)
        build.build_info = eval(build.build_info)
        jenkins_build_status = get_jenkins_job_status(build.build_info, jenkins_server)
        status = jenkins_build_status['status']
        message = f"Jenkins build status: {status}"
        TheLogs.log_info(message, 2, "*", main_log)
        if status == "":
            message = f"Job # {build.build_info['id']} for repo {build.repo} is still running"
            TheLogs.log_info(message, 2, "*", main_log)
        else:
            update_completed_jobs(build, jenkins_build_status, build.build_info)
            if status == 'FAILURE':
                update_failed_jobs(build, jenkins_build_status, snow_task_manager)
            elif status == 'SUCCESS':
                update_successful_jobs(build, snow_task_manager)
            if build.change_request_num is not None:
                if change_can_be_approved(build.change_request_num):
                    task_number = get_task_number(build.change_request_num)
                    change_number = build.change_request_num
                    snow_task_manager.pass_validation_on_task(task_number, change_number)

def trigger_jenkins_build_and_get_build_info(build_repo: str, build_branch: str,
                                             jenkins_server: JenkinsManager) -> Dict[str, Any]:
    """triggers Jenkins build and gets build info"""
    job_name = build_repo + " (Pipeline)"
    token = ""
    parameters = {'BRANCH': build_branch}
    next_build_number = jenkins_server.get_job_info(job_name)['nextBuildNumber']
    jenkins_server.build_job(job_name, parameters=parameters, token=token)
    build_info = jenkins_server.get_build_info(job_name, next_build_number)
    return build_info

def get_jenkins_job_status(build_info: Dict[str, Any],
                           jenkins_server: JenkinsManager) -> Dict[str, str]:
    """gets Jenkins job status data"""
    failure_desc = "NULL"
    job_name = build_info["fullDisplayName"].split("#")[0].strip()
    job_id = build_info["id"]
    jenkins_build_info = jenkins_server.get_build_info(job_name, int(job_id))
    if jenkins_build_info["building"]:
        return {"status": "", "failure_desc": failure_desc, "build_info": jenkins_build_info,
                "scan_link": ''}
    else:
        status = jenkins_build_info["result"]
        console_output = jenkins_server.get_build_console_output(job_name, int(job_id))
        if "SAST high severity results are above threshold" in console_output:
            failure_desc = "New high findings detected in Checkmarx scan"
        elif "Couldn't find any revision to build. Verify the repository and branch " \
             "configuration for this job." in console_output:
            failure_desc = "Invalid branch information provided for scan"
        elif "[Cx-Error]: Creation of the new project" in console_output:
            failure_desc = "Checkmarx project does not exist"
        elif "stderr: fatal: repository" in console_output:
            failure_desc = "Requested repository was not found"

        if "Scan results location:" in console_output:
            scan_link = console_output.split("Scan results location: ")[1].split("\n")[0]
        else:
            scan_link = ""

        return {"status": status, "failure_desc": failure_desc, "build_info": build_info,
                "scan_link": scan_link}

def update_completed_jobs(build: pyodbc.Row, jenkins_build_status: Dict[str, Any],
                          build_info: Dict[str, Any]) -> None:
    """updates completed jobs in QABuilds table"""
    TheLogs.log_info(f"Job # {build_info['id']} for repo {build.repo} completed with status of "
                 f"{jenkins_build_status['status']}",1,"*",LOG)
    sql = """
    UPDATE QABuilds
    SET Status = '{0}', BuildInfo = '{1}', LastUpdateDate = '{2}', FailureReason = '{3}'
    WHERE ID = {4}
    """.format(jenkins_build_status["status"], str(jenkins_build_status["build_info"]).
               replace("'", "''"), str(datetime.now())[:-7],
               jenkins_build_status["failure_desc"], build.id)
    conn.func = 'update_completed_jobs'
    conn.query_with_logs(sql)

def update_failed_jobs(build: pyodbc.Row, jenkins_build_status: Dict[str, Any],
                       snow_task_manager: SNTasksManager) -> None:
    """updates RequiredScans table, calls functions to add comments and fails SNow task"""
    comment = f"Scan of {build.repo} ({build.app_sysid}) on branch: {build.branch} failed due " \
              f"to {jenkins_build_status['failure_desc']}"
    task = snow_task_manager.get_task_for_change(build.change_request_num)
    message = f"Updating Required scans for: {build.repo}:{build.app_sysid} "
    TheLogs.log_info(message, 2, "*", main_log)
    sql = f"""UPDATE RequiredScans SET ScanDate = '{str(datetime.now())[:-7]}',
        ScanStatus = 'FAILURE' WHERE AppSysID = '{build.app_sysid}'
        """
    conn.func = 'update_failed_jobs'
    conn.query_with_logs(sql)
    task = str(task['number'])
    snow_task_manager.add_comment_to_task(task, comment, LOG)
    snow_task_manager.fail_validation_on_task(task, build.change_request_num,
                                              send_slack_message=True, main_log=LOG)

def update_successful_jobs(build: pyodbc.Row, snow_task_manager: SNTasksManager) -> None:
    """updates RequiredScans and calls function to add comment to SNow task"""
    comment = f"Scan of {build.repo} ({build.app_sysid}) on branch: {build.branch} " \
              f"was successful with no new high findings"
    task = snow_task_manager.get_task_for_change(build.change_request_num)
    message = f"Updating Required scans for: {build.app_sysid} "
    TheLogs.log_info(message, 2, "*", main_log)
    sql = f"""UPDATE RequiredScans SET ScanDate = '{str(datetime.now())[:-7]}',
        ScanStatus = 'SUCCESS' WHERE AppSysID = '{build.app_sysid}'
        """
    conn.func = 'update_successful_jobs'
    conn.query_with_logs(sql)
    snow_task_manager.add_comment_to_task(task['number'], comment, LOG)

def change_can_be_approved(change_request_num: int):
    """checks to see if all required scans have been successful"""
    sql = f"SELECT * FROM RequiredScans WHERE (ScanStatus != 'SUCCESS' OR ScanStatus IS NULL) " \
          f"AND ChangeNumber = '{change_request_num}'"
    conn.func = 'change_can_be_approved'
    bad_scans = conn.query_with_logs(sql)
    if not bad_scans:
        TheLogs.log_info("No bad scans found. Change can be approved.", 2, "*", main_log)
        return True
    else:
        message = f"Failed or unfinished scans found: {bad_scans}"
        TheLogs.log_info(message, 2, "*", main_log)
        return False

def get_task_number(change_request_num: int):
    """gets task number using change request number from snTaskNumber"""
    sql = f"SELECT snTaskNumber FROM snTaskRecords WHERE snChangeRequest = '{change_request_num}'"
    conn.func = 'get_task_number'
    task_number = conn.query_with_logs(sql)
    return task_number[0][0]

if __name__ == '__main__':
    main()
