import sys
from unittest import mock
sys.modules['jenkins_files.jenkins_manager'] = mock.MagicMock()
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
sys.modules['pysnow'] = mock.MagicMock()
from maintenance_jenkins import *
import pytz
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def mock_qa_build():
    build = mock.MagicMock()
    build.id = "42"
    build.status = None
    build.build_info = "{'id' : 42}"
    build.repo = 'Test repo'
    build.change_number = None
    build.app_sysid = "Test existing app_sysid"
    build.rcv_date = None
    return build


@pytest.fixture()
def mock_jenkins_build():
    build = mock.MagicMock()
    build.repo = None
    build.status = None
    build.build_info = {}
    build.failure_desc = None
    build.scan_link = None
    return build

@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch('maintenance_jenkins.appsecjenkins')
def test_main(mock_appsecjenkins, head_log_mock):
    main()
    mock_appsecjenkins.assert_called_once()
    head_log_mock.assert_called_once()

@mock.patch.object(Misc, "end_timer")
@mock.patch.object(Misc, "start_timer")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.check_stuck_builds")
def test_appsecjenkins_stuck_builds(check_stuck_builds_mock, log_mock,s_timer_mock,
                                    e_timer_mock, mock_qa_build):
    check_stuck_builds_mock.return_value = [mock_qa_build]
    appsecjenkins()
    s_timer_mock.assert_called_once()
    check_stuck_builds_mock.assert_called_once()
    log_mock.assert_called_once()
    e_timer_mock.assert_called_once()

@mock.patch.object(Misc, "end_timer")
@mock.patch.object(Misc, "start_timer")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.Alerts.manual_alert")
@mock.patch("maintenance_jenkins.update_qa_builds_table")
@mock.patch("maintenance_jenkins.check_stuck_builds")
def test_appsecjenkins_no_stuck_builds(check_stuck_builds_mock,update_qa_builds_table_mock,ma_mock,
                                       log_mock,s_timer_mock,e_timer_mock):
    check_stuck_builds_mock.return_value = []
    appsecjenkins()
    s_timer_mock.assert_called_once()
    update_qa_builds_table_mock.assert_called_once()
    assert ma_mock.call_count == 0
    log_mock.assert_called_once()
    e_timer_mock.assert_called_once()


@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch("maintenance_jenkins.Alerts.create_change_ticket_link")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.get_new_builds")
@mock.patch("maintenance_jenkins.Alerts.manual_alert")
def test_check_stuck_builds_currently_stuck_build(send_slack_message_stuck_build_mock,
                                                  get_new_builds_mock,log_mock,ch_lnk_mock,head_log_mock):
    get_new_builds_mock.return_value = [['id',
                                         datetime.now(pytz.timezone("America/Denver")).replace(
                                             tzinfo=None) - timedelta(minutes=10), 'status', 'change number','repo']]
    result = check_stuck_builds()
    assert result is not None
    send_slack_message_stuck_build_mock.assert_called_once()
    assert log_mock.call_count == 2
    assert ch_lnk_mock.call_count == 1
    head_log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch("maintenance_jenkins.TheLogs.process_exceptions")
@mock.patch("maintenance_jenkins.TheLogs.function_exception")
@mock.patch("maintenance_jenkins.Alerts.create_change_ticket_link")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.get_new_builds")
@mock.patch("maintenance_jenkins.Alerts.manual_alert", side_effect=Exception())
def test_check_stuck_builds_currently_stuck_build_exception(send_slack_message_stuck_build_mock,
                                                  get_new_builds_mock,log_mock,ch_lnk_mock, fe_log_mock, pe_log_mock, head_log_mock):
    get_new_builds_mock.return_value = [['id',
                                         datetime.now(pytz.timezone("America/Denver")).replace(
                                             tzinfo=None) - timedelta(minutes=10), 'status', 'change number','repo']]
    check_stuck_builds()
    head_log_mock.assert_called_once()
    try:
        send_slack_message_stuck_build_mock.assert_called_once()
    except Exception:
        fe_log_mock.assert_called_once()
        pe_log_mock.assert_called_once()
    assert log_mock.call_count == 2
    assert ch_lnk_mock.call_count == 1

@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch("maintenance_jenkins.Alerts.create_change_ticket_link")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.get_new_builds")
@mock.patch("maintenance_jenkins.Alerts.manual_alert")
def test_check_stuck_builds_currently_stuck_build_more_than_10_minutes(send_slack_message_stuck_build_mock,
                                                  get_new_builds_mock,log_mock,ch_lnk_mock,head_log_mock):
    get_new_builds_mock.return_value = [['id',
                                         datetime.now(pytz.timezone("America/Denver")).replace(
                                             tzinfo=None) - timedelta(minutes=15), 'status', 'change number','repo']]
    result = check_stuck_builds()
    assert result is None
    send_slack_message_stuck_build_mock.assert_not_called()
    assert log_mock.call_count == 1
    ch_lnk_mock.assert_not_called()
    assert head_log_mock.call_count == 2

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.Alerts.create_change_ticket_link")
@mock.patch("maintenance_jenkins.get_new_builds")
@mock.patch("maintenance_jenkins.Alerts.manual_alert")
def test_check_stuck_builds_recently_stuck_build(send_slack_message_stuck_build_mock,
                                                 get_new_builds_mock,ch_lnk_mock,log_mock):
    get_new_builds_mock.return_value = [
        [None, datetime.now(pytz.timezone("America/Denver")).replace(tzinfo=None), None, None]
    ]
    result = check_stuck_builds()
    assert result is None
    assert not send_slack_message_stuck_build_mock.called
    assert ch_lnk_mock.call_count == 0
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.Alerts.create_change_ticket_link")
@mock.patch("maintenance_jenkins.get_new_builds")
@mock.patch("maintenance_jenkins.Alerts.manual_alert")
def test_check_stuck_builds_no_stuck_builds(send_slack_message_stuck_build_mock,
                                            get_new_builds_mock,ch_lnk_mock):
    get_new_builds_mock.return_value = []
    result = check_stuck_builds()
    assert result is None
    assert not send_slack_message_stuck_build_mock.called

@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_get_new_builds(conn_mock):
    get_new_builds()
    conn_mock.assert_called_once()

@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_get_processing_builds(conn_mock):
    get_processing_builds()
    conn_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_processing_builds")
@mock.patch("maintenance_jenkins.update_new_builds")
@mock.patch("maintenance_jenkins.get_qa_builds")
def test_update_qa_builds_table_both_builds_exist(get_qa_builds_mock,
                                                  update_new_builds_mock,
                                                  update_processing_builds_mock,log_mock):
    get_qa_builds_mock.return_value = (['new build'], ['processing_build'])
    update_qa_builds_table()
    update_new_builds_mock.assert_called_once()
    update_processing_builds_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_processing_builds")
@mock.patch("maintenance_jenkins.update_new_builds")
@mock.patch("maintenance_jenkins.get_qa_builds")
def test_update_qa_builds_table_new_builds_exist(get_qa_builds_mock,
                                                 update_new_builds_mock,
                                                 update_processing_builds_mock,log_mock):
    get_qa_builds_mock.return_value = (['new build'], [])
    update_qa_builds_table()
    update_new_builds_mock.assert_called_once()
    assert not update_processing_builds_mock.called
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_processing_builds")
@mock.patch("maintenance_jenkins.update_new_builds")
@mock.patch("maintenance_jenkins.get_qa_builds")
def test_update_qa_builds_table_processing_builds_exist(get_qa_builds_mock,
                                                        update_new_builds_mock,
                                                        update_processing_builds_mock,log_mock):
    get_qa_builds_mock.return_value = ([], ['processing build'])
    update_qa_builds_table()
    assert not update_new_builds_mock.called
    update_processing_builds_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_processing_builds")
@mock.patch("maintenance_jenkins.update_new_builds")
@mock.patch("maintenance_jenkins.get_qa_builds")
def test_update_qa_builds_table_no_builds_exist(
                                                get_qa_builds_mock,
                                                update_new_builds_mock,
                                                update_processing_builds_mock,log_mock):
    get_qa_builds_mock.return_value = ([], [])
    update_qa_builds_table()
    assert not update_new_builds_mock.called
    assert not update_processing_builds_mock.called
    assert log_mock.call_count == 2


@mock.patch("maintenance_jenkins.get_processing_builds")
@mock.patch("maintenance_jenkins.get_new_builds")
def test_get_qa_builds(get_new_builds_mock, get_processing_builds_mock):
    get_qa_builds()
    get_new_builds_mock.assert_called_once()
    get_processing_builds_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch("maintenance_jenkins.JenkinsManager")
@mock.patch("maintenance_jenkins.trigger_jenkins_build_and_get_build_info")
@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_update_new_builds_with_app_sysid(conn_mock, trigger_jenkins_build_and_get_build_info_mock,
                                          jenkins_server_mock,head_log_mock,mock_qa_build):
    mock_builds = [mock_qa_build]
    update_new_builds(mock_builds, jenkins_server_mock)
    trigger_jenkins_build_and_get_build_info_mock.assert_called_once()
    conn_mock.assert_called_once()
    head_log_mock.call_count == 2

@mock.patch("maintenance_jenkins.TheLogs.log_headline")
@mock.patch("maintenance_jenkins.JenkinsManager")
@mock.patch("maintenance_jenkins.trigger_jenkins_build_and_get_build_info")
@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_update_new_builds_no_app_sysid(conn_mock,
                                        trigger_jenkins_build_and_get_build_info_mock,
                                        jenkins_server_mock,head_log_mock, mock_qa_build):
    mock_qa_build.app_sysid = ""
    mock_builds = [mock_qa_build]
    update_new_builds(mock_builds, jenkins_server_mock)
    trigger_jenkins_build_and_get_build_info_mock.assert_called_once()
    assert conn_mock.call_count == 2
    assert head_log_mock.call_count == 2


@mock.patch("maintenance_jenkins.get_jenkins_job_status")
@mock.patch("maintenance_jenkins.JenkinsManager")
@mock.patch("maintenance_jenkins.SNTasksManager")
@mock.patch('maintenance_jenkins.TheLogs.log_info')
def test_update_processing_builds_no_status(log_mock, snow_task_manager_mock,
                                            jenkins_server_mock, get_jenkins_job_status_mock,
                                            mock_qa_build):
    mock_qa_build.build_info = mock_qa_build.build_info
    processing_builds = [mock_qa_build]
    get_jenkins_job_status_mock.return_value = {"status": ""}
    update_processing_builds(processing_builds, snow_task_manager_mock,
                             jenkins_server_mock)
    get_jenkins_job_status_mock.assert_called_once()
    assert log_mock.call_count == 4

@mock.patch("maintenance_jenkins.change_can_be_approved")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_failed_jobs")
@mock.patch("maintenance_jenkins.update_completed_jobs")
@mock.patch("maintenance_jenkins.get_jenkins_job_status")
@mock.patch("maintenance_jenkins.JenkinsManager")
@mock.patch("maintenance_jenkins.SNTasksManager")
def test_update_processing_builds_completed_and_failed(snow_task_manager_mock,
                                                       jenkins_server_mock,
                                                       get_jenkins_job_status_mock,
                                                       update_completed_jobs_mock,
                                                       update_failed_jobs_mock,log_mock,change_approve_mock,mock_qa_build):
    processing_builds = [mock_qa_build]
    get_jenkins_job_status_mock.return_value = {"status": "FAILURE"}
    update_processing_builds(processing_builds, snow_task_manager_mock,
                             jenkins_server_mock)
    update_completed_jobs_mock.assert_called_once()
    get_jenkins_job_status_mock.assert_called_once()
    update_failed_jobs_mock.assert_called_once()
    assert log_mock.call_count == 3
    change_approve_mock.assert_called_once()

@mock.patch("maintenance_jenkins.change_can_be_approved")
@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.update_successful_jobs")
@mock.patch("maintenance_jenkins.update_completed_jobs")
@mock.patch("maintenance_jenkins.get_jenkins_job_status")
@mock.patch("maintenance_jenkins.JenkinsManager")
@mock.patch("maintenance_jenkins.SNTasksManager")
def test_update_processing_builds_completed_and_success(snow_task_manager_mock,
                                                        jenkins_server_mock,
                                                        get_jenkins_job_status_mock,
                                                        update_completed_jobs_mock,
                                                        update_successful_jobs_mock,log_mock,change_approve_mock,mock_qa_build):
    processing_builds = [mock_qa_build]
    get_jenkins_job_status_mock.return_value = {"status": "SUCCESS"}
    update_processing_builds(processing_builds, snow_task_manager_mock,
                             jenkins_server_mock)
    update_completed_jobs_mock.assert_called_once()
    get_jenkins_job_status_mock.assert_called_once()
    update_successful_jobs_mock.assert_called_once()
    assert log_mock.call_count == 3
    change_approve_mock.assert_called_once()


@mock.patch("maintenance_jenkins.JenkinsManager")
def test_trigger_jenkins_build_and_get_build_info(jenkins_server_mock):
    trigger_jenkins_build_and_get_build_info('Test Repo', 'Test branch', jenkins_server_mock)
    jenkins_server_mock.get_job_info.assert_called_once()
    jenkins_server_mock.build_job.assert_called_once()
    jenkins_server_mock.get_build_info.assert_called_once()


@mock.patch("maintenance_jenkins.JenkinsManager")
def test_get_jenkins_job_status_build_still_running(jenkins_server_mock, mock_qa_build):
    mock_qa_build.build_info = eval(mock_qa_build.build_info)
    mock_qa_build.build_info['fullDisplayName'] = 'test'
    jenkins_server_mock.get_build_info.return_value = {"building": True}

    result = get_jenkins_job_status(mock_qa_build.build_info, jenkins_server_mock)
    assert result['status'] == ''


@mock.patch("maintenance_jenkins.JenkinsManager")
@pytest.mark.parametrize("console_output, failure_description",
                         [("SAST high severity results are above threshold",
                           "New high findings detected in Checkmarx scan"),
                          ("Couldn't find any revision to build. Verify the repository and branch "
                           "configuration for this job.",
                           "Invalid branch information provided for scan"),
                          ("[Cx-Error]: Creation of the new project",
                           "Checkmarx project does not exist"),
                          ("stderr: fatal: repository",
                           "Requested repository was not found"),
                          ])
def test_get_jenkins_job_status_custom_failure_descriptions(jenkins_server_mock,
                                                            mock_qa_build, console_output,
                                                            failure_description):
    mock_qa_build.build_info = eval(mock_qa_build.build_info)
    mock_qa_build.build_info['fullDisplayName'] = 'test'
    jenkins_server_mock.get_build_info.return_value = {"building": False,
                                                       "result": "Test result"
                                                       }
    jenkins_server_mock.get_build_console_output.return_value = console_output
    result = get_jenkins_job_status(mock_qa_build.build_info, jenkins_server_mock)
    assert result['failure_desc'] == failure_description
    assert result['status'] == 'Test result'
    jenkins_server_mock.get_build_console_output.assert_called_once()


@mock.patch("maintenance_jenkins.JenkinsManager")
@pytest.mark.parametrize("console_output, scan_link",
                         [("Scan results location: loc1_ loc_2", "loc1_ loc_2"),
                          ("", ""),
                          ])
def test_get_jenkins_job_status_scan_link(jenkins_server_mock, mock_qa_build, console_output,
                                          scan_link):
    mock_qa_build.build_info = eval(mock_qa_build.build_info)
    mock_qa_build.build_info['fullDisplayName'] = 'test'
    jenkins_server_mock.get_build_info.return_value = {"building": False,
                                                       "result": "Test result"
                                                       }
    jenkins_server_mock.get_build_console_output.return_value = console_output
    result = get_jenkins_job_status(mock_qa_build.build_info, jenkins_server_mock)
    assert result['scan_link'] == scan_link
    jenkins_server_mock.get_build_console_output.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_update_completed_jobs(conn_mock, log_mock, mock_qa_build):
    mock_qa_build.build_info = eval(mock_qa_build.build_info)
    jenkins_build_status = {"status": "test",
                            "build_info": "test",
                            "failure_desc": None}
    update_completed_jobs(mock_qa_build, jenkins_build_status, mock_qa_build.build_info)
    conn_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.SNTasksManager")
def test_update_failed_jobs(snow_task_manager_mock,log_mock,mock_qa_build):
    jenkins_build_status = {"failure_desc": None}
    update_failed_jobs(mock_qa_build, jenkins_build_status, snow_task_manager_mock)
    snow_task_manager_mock.get_task_for_change.assert_called_once()
    snow_task_manager_mock.add_comment_to_task.assert_called_once()
    snow_task_manager_mock.fail_validation_on_task.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("maintenance_jenkins.TheLogs.log_info")
@mock.patch("maintenance_jenkins.SNTasksManager")
def test_update_successful_jobs(snow_task_manager_mock,log_mock,mock_qa_build):
    update_successful_jobs(mock_qa_build, snow_task_manager_mock)
    snow_task_manager_mock.get_task_for_change.assert_called_once()
    snow_task_manager_mock.add_comment_to_task.assert_called_once()
    log_mock.assert_called_once()

@mock.patch('maintenance_jenkins.TheLogs.log_info')
@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_change_can_be_approved(conn_mock, log_mock):
    conn_mock.return_value = []
    change_can_be_approved('number')
    conn_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch('maintenance_jenkins.TheLogs.log_info')
@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_change_can_be_approved_bad_scans(conn_mock, log_mock):
    conn_mock.return_value = ['baaad_scans']
    change_can_be_approved('number')
    conn_mock.assert_called_once()
    log_mock.assert_called_once()


@mock.patch("maintenance_jenkins.conn.query_with_logs")
def test_get_task_number(conn_mock):
    get_task_number('number')
    conn_mock.assert_called_once()
