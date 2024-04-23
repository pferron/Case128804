import pytest
from unittest import mock
import sys
sys.modules['pysnow'] = mock.MagicMock()
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
from maintenance_snow import *


JIRA_KEY = 'FAKE_KEY_123'
REPO = 'REPO'


@mock.patch("maintenance_snow.change_in_table")
@mock.patch.object(General, "cmd_processor")
def test_main(cmd_processor_mock, change_in_table_mock):
    cmd_processor_mock.return_value = [{'args': {'arg_1': 'test'},
                                       'function': 'change_in_table'}]
    main()


@mock.patch("maintenance_snow.process_new_records")
@mock.patch.object(Misc, "end_timer")
@mock.patch.object(Misc, "start_timer")
def test_every_5_minutes(start_timer_mock, end_timer_mock, process_new_records_mock):
    every_5_minutes()
    start_timer_mock.assert_called_once()
    end_timer_mock.assert_called_once()
    process_new_records_mock.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_task_table(client_mock):
    task_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_change_table(client_mock):
    change_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_app_table(client_mock):
    app_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_cmdb_table(client_mock):
    cmdb_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_jira_table(client_mock):
    jira_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.getJiraKey")
def test_get_sn_jira_project_key(get_jira_key_mock):
    get_jira_key_mock.return_value = [{'u_project_key': 'KEY'}]
    res = getsnJiraProjectKey(JIRA_KEY)
    assert res == 'KEY'


@mock.patch("maintenance_snow.jira_table")
@mock.patch("maintenance_snow.pysnow")
def test_get_jira_key(pysnow_mock, jira_table_mock):
    getJiraKey('KEY')
    pysnow_mock.QueryBuilder.assert_called_once()
    jira_table_mock.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_user_table(client_mock):
    user_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_group_table(client_mock):
    group_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@mock.patch("maintenance_snow.pysnow.Client")
def test_approval_table(client_mock):
    approval_table()
    client_mock.assert_called_once()
    client_mock.return_value.resource.assert_called_once()


@pytest.mark.parametrize("time",
                         [
                             '2023-01-01 00:00:00',
                             ''
                         ])
def test_utc_to_local(time):
    res = utc_to_local(time)
    if time:
        assert type(res) == str
    else:
        assert res == ''


@pytest.mark.parametrize("time",
                         [
                             datetime.now(),
                             ''
                         ])
def test_local_to_utc(time):
    res = local_to_utc(time)
    if time:
        assert type(res) == datetime
    else:
        assert res == ''


@mock.patch("maintenance_snow.task_table")
def test_get_task(task_table_mock):
    task_table_mock.return_value.get.return_value.all.return_value = ['record']
    get_task(0)
    task_table_mock.assert_called_once()


@mock.patch("maintenance_snow.task_table")
@mock.patch("maintenance_snow.pysnow")
def test_get_all_tasks(pysnow_mock, task_table_mock):
    get_all_tasks()
    pysnow_mock.QueryBuilder.assert_called_once()
    task_table_mock.assert_called_once()


@mock.patch("maintenance_snow.task_table")
@mock.patch("maintenance_snow.pysnow")
@mock.patch("maintenance_snow.local_to_utc")
def test_get_tasks_after_date(local_to_utc_mock, pysnow_mock, task_table_mock):
    get_tasks_after_date('')
    local_to_utc_mock.assert_called_once()
    pysnow_mock.QueryBuilder.assert_called_once()
    task_table_mock.assert_called_once()


@mock.patch("maintenance_snow.task_table")
@mock.patch("maintenance_snow.pysnow")
def test_get_all_open_tasks(pysnow_mock, task_table_mock):
    get_all_open_tasks()
    pysnow_mock.QueryBuilder.assert_called_once()
    task_table_mock.assert_called_once()


@mock.patch("maintenance_snow.change_table")
@mock.patch("maintenance_snow.pysnow")
@mock.patch("maintenance_snow.local_to_utc")
def test_get_changes_after_date(local_to_utc_mock, pysnow_mock, change_table_mock):
    get_changes_after_date('')
    local_to_utc_mock.assert_called_once()
    pysnow_mock.QueryBuilder.assert_called_once()
    change_table_mock.assert_called_once()


@mock.patch("maintenance_snow.change_table")
@mock.patch("maintenance_snow.pysnow")
def test_get_all_changes(pysnow_mock, change_table_mock):
    get_all_changes()
    pysnow_mock.QueryBuilder.assert_called_once()
    change_table_mock.assert_called_once()


@mock.patch("maintenance_snow.change_table")
@mock.patch("maintenance_snow.pysnow")
def test_get_change_by_number(pysnow_mock, change_table_mock):
    get_change_by_number(0)
    pysnow_mock.QueryBuilder.assert_called_once()
    change_table_mock.assert_called_once()


@mock.patch("maintenance_snow.change_table")
def test_get_change_by_query(change_table_mock):
    get_change_by_query('query')
    change_table_mock.assert_called_once()


@mock.patch("maintenance_snow.change_table")
@mock.patch("maintenance_snow.pysnow")
def test_execute_query(pysnow_mock, change_table_mock):
    change_table_mock.return_value.get.return_value.all.return_value = [{'number': '0',
                                                                        'status': 'done',
                                                                        'estimated_production_date':
                                                                            'date'}]
    execute_query()
    assert pysnow_mock.QueryBuilder.call_count == 2
    assert change_table_mock.call_count == 2


@mock.patch("maintenance_snow.get_task")
@mock.patch("maintenance_snow.select")
def test_validate_open_tasks(select_mock, get_task_mock):
    row = mock.MagicMock()
    row.taskNumber = 'task'
    select_mock.return_value = [row]
    validate_open_tasks()
    select_mock.assert_called_once()
    get_task_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_headline")
@mock.patch("maintenance_snow.process_app_updates")
@mock.patch("maintenance_snow.process_task_updates")
@mock.patch("maintenance_snow.process_change_updates")
@mock.patch.object(Misc, "start_timer")
@mock.patch.object(Misc, "end_timer")
def test_process_all_updates(end_timer_mock, start_timer_mock, process_change_updates_mock,
                             process_task_updates_mock, process_app_updates_mock,
                             log_headline_mock):
    process_all_updates()
    process_change_updates_mock.assert_called_once()
    process_task_updates_mock.assert_called_once()
    process_app_updates_mock.assert_called_once()
    start_timer_mock.assert_called_once()
    end_timer_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_headline")
@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.update_task_db")
@mock.patch("maintenance_snow.task_in_table")
@mock.patch("maintenance_snow.get_all_tasks")
def test_process_task_updates(get_all_tasks_mock, task_in_table_mock, update_task_db_mock,
                              log_headline_mock, log_info_mock):
    task = {'number': 'num'}
    get_all_tasks_mock.return_value = [task]
    process_task_updates()
    get_all_tasks_mock.assert_called_once()
    task_in_table_mock.assert_called_once()
    update_task_db_mock.assert_called_once()


@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("select_return_value, expected",
                         [
                             ([[True]], True),
                             ([], None)
                         ])
def test_task_in_table(select_mock, select_return_value, expected):
    select_mock.return_value = select_return_value
    res = task_in_table(2)
    select_mock.assert_called_once()
    assert res == expected


@mock.patch("maintenance_snow.utc_to_local")
@mock.patch("maintenance_snow.get_task_state_text")
@mock.patch("maintenance_snow.insert")
@mock.patch("maintenance_snow.get_change_by_query")
def test_write_task_db(get_change_by_query_mock, insert_mock, get_task_state_text_mock,
                       utc_to_local_mock):
    task = {'parent': {'value': 'val'},
            'number': 'num',
            'state': 'state',
            'sys_created_on': 'test',
            'sys_updated_on': 'test'}
    write_task_db(task)
    get_change_by_query_mock.assert_called_once()
    insert_mock.assert_called_once()
    get_task_state_text_mock.assert_called_once()
    assert utc_to_local_mock.call_count == 2


@mock.patch("maintenance_snow.utc_to_local")
@mock.patch("maintenance_snow.get_task_state_text")
@mock.patch("maintenance_snow.update")
@mock.patch("maintenance_snow.get_change_by_query")
def test_update_task_db(get_change_by_query_mock, update_mock, get_task_state_text_mock,
                        utc_to_local_mock):
    task = {'parent': {'value': 'val'},
            'state': 'state',
            'sys_updated_on': 'date',
            'number': 'num'}
    get_change_by_query_mock.return_value = {'number': 'number'}
    update_task_db(task)
    get_change_by_query_mock.assert_called_once()
    utc_to_local_mock.assert_called_once()
    assert update_mock.call_count == 1
    assert get_task_state_text_mock.call_count == 1


@mock.patch.object(TheLogs, "log_headline")
@mock.patch("maintenance_snow.null_blank_change_dates")
@mock.patch("maintenance_snow.update_change_db")
@mock.patch("maintenance_snow.change_in_table")
@mock.patch("maintenance_snow.get_all_changes")
def test_process_change_updates(get_all_changes_mock, change_in_table_mock, update_change_db_mock,
                                null_blank_change_dates_mock, log_headline_mock):
    get_all_changes_mock.return_value = [{'number': 'CCSX0003987'}]
    change_in_table_mock.return_value = True
    process_change_updates()
    get_all_changes_mock.assert_called_once()
    change_in_table_mock.assert_called_once()
    update_change_db_mock.assert_called_once()
    null_blank_change_dates_mock.assert_called_once()


@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("select_return_value, expected",
                         [
                             ([[True]], True),
                             ([], None)
                         ])
def test_change_in_table(select_mock, select_return_value, expected):
    select_mock.return_value = select_return_value
    res = change_in_table(0)
    select_mock.assert_called_once()
    assert res == expected


@mock.patch("maintenance_snow.insert")
@mock.patch("maintenance_snow.get_change_status_text")
@mock.patch("maintenance_snow.utc_to_local")
@mock.patch("maintenance_snow.all_cis_verified")
@mock.patch("maintenance_snow.get_app_names_from_sysid")
@mock.patch("maintenance_snow.check_sast_ci")
@pytest.mark.parametrize("sast_ci, all_cis_verified_val, change",
                         [
                             (['ci_1'], True, {'u_cmdb_ci': '', 'estimated_production_date': '',
                                               'rc_branch': 'Master'}),
                             ([], False, {'u_cmdb_ci': 'test', 'estimated_production_date': 'test',
                                          'rc_branch': 'dev'})
                         ])
def test_write_change_db(check_sast_ci_mock, get_app_names_from_sys_id_mock, all_cis_verified_mock,
                         utc_to_local_mock, get_change_status_text_mock, insert_mock, sast_ci,
                         all_cis_verified_val, change):
    change.update({'number': 'number', 'sys_created_on': 'date', 'sys_updated_on': 'date',
                   'sys_id': 'sys_id', 'status': 'status', 'short_description': 'description',
                   'rc_entry': 'rc_entry', 'estimated_production_date': 'date',
                   'new_software': 'test', 'change_type': 'test', 'deployment_end': 'test',
                   'closed_at': 'test'})
    check_sast_ci_mock.return_value = sast_ci
    all_cis_verified_mock.return_value = all_cis_verified_val
    write_change_db(change)
    check_sast_ci_mock.assert_called_once()
    assert get_app_names_from_sys_id_mock.call_count == 2
    all_cis_verified_mock.assert_called_once()
    assert utc_to_local_mock.call_count == 4
    get_change_status_text_mock.assert_called_once()
    insert_mock.assert_called_once()


@mock.patch("maintenance_snow.count_cis")
@mock.patch("maintenance_snow.null_blank_change_dates")
@mock.patch("maintenance_snow.update")
@mock.patch("maintenance_snow.utc_to_local")
@mock.patch("maintenance_snow.get_change_status_text")
@mock.patch("maintenance_snow.select")
@mock.patch("maintenance_snow.check_change_approval")
@mock.patch("maintenance_snow.all_cis_verified")
@mock.patch("maintenance_snow.get_app_names_from_sysid")
@mock.patch("maintenance_snow.check_sast_ci")
@pytest.mark.parametrize("sast_ci, all_cis_verified_val, check_change_approval_val, branch",
                         [
                             ['', False, 'approved', 'Master'],
                             ['sast_ci', True, '', 'branch']
                         ])
def test_update_change_db(check_sast_ci_mock, get_app_names_from_sysid_mock, all_cis_verified_mock,
                          check_change_approval_mock, select_mock, get_change_status_text_mock,
                          utc_to_local_mock, update_mock, null_blank_change_dates_mock,
                          count_cis_mock, sast_ci, all_cis_verified_val, check_change_approval_val,
                          branch):
    change = {'number': 'number', 'u_cmdb_ci': 'ci', 'rc_branch': branch,
              'estimated_production_date': 'date', 'status': 'status', 'sys_updated_on': 'date',
              'short_description': 'description', 'rc_entry': 'rc_entry', 'new_software': 'test',
              'change_type': 'test', 'deployment_end': 'test', 'closed_at': 'test'}
    check_sast_ci_mock.return_value = sast_ci
    all_cis_verified_mock.return_value = all_cis_verified_val
    check_change_approval_mock.return_value = check_change_approval_val
    update_change_db(change)
    check_sast_ci_mock.assert_called_once()
    all_cis_verified_mock.assert_called_once()
    check_change_approval_mock.assert_called_once()
    select_mock.assert_called_once()
    update_mock.assert_called_once()
    null_blank_change_dates_mock.assert_called_once()
    get_change_status_text_mock.assert_called_once()
    count_cis_mock.assert_called_once()
    assert get_app_names_from_sysid_mock.call_count == 2
    assert utc_to_local_mock.call_count == 4


@mock.patch("maintenance_snow.update")
def test_null_blank_change_dates(update_mock):
    null_blank_change_dates()
    assert update_mock.call_count == 2


@mock.patch.object(TheLogs, "log_headline")
@mock.patch("maintenance_snow.process_new_changes")
@mock.patch("maintenance_snow.process_new_tasks")
def test_process_new_records(process_new_changes_mock, process_new_tasks_mock, log_headline_mock):
    process_new_records()
    process_new_changes_mock.assert_called_once()
    process_new_tasks_mock.assert_called_once()


@mock.patch.object(SNTasksManager, "pass_validation_on_task")
@mock.patch("maintenance_snow.review_required_on_change")
@mock.patch("maintenance_snow.add_comment_to_task")
@mock.patch("maintenance_snow.schedule_scans_for_change")
@mock.patch("maintenance_snow.write_required_scans_db")
@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.update_change_db")
@mock.patch("maintenance_snow.get_change_by_query")
@mock.patch("maintenance_snow.write_task_db")
@mock.patch("maintenance_snow.get_tasks_after_date")
@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("required_scans, review_required_on_change_return_value",
                         [
                             ([{'name': 'name', 'sysid': 'sysid'}], True),
                             ([], True),
                             ([], False)
                         ])
def test_process_new_tasks(select_mock, get_tasks_after_date_mock, write_task_db_mock,
                           get_change_by_query_mock, update_change_db_mock, log_info_mock,
                           write_required_scans_db_mock, schedule_scans_for_change_mock,
                           add_comment_to_task_mock, review_required_on_change_mock,
                           pass_validation_on_task_mock, required_scans,
                           review_required_on_change_return_value):
    task = {'number': '0', 'parent': {'value': 'value'}, }
    get_tasks_after_date_mock.return_value = [task]
    get_change_by_query_mock.return_value = {'number': '0'}
    write_required_scans_db_mock.return_value = required_scans
    review_required_on_change_mock.return_value = review_required_on_change_return_value
    process_new_tasks()
    select_mock.assert_called_once()
    get_tasks_after_date_mock.assert_called_once()
    get_change_by_query_mock.assert_called_once()
    if required_scans:
        schedule_scans_for_change_mock.assert_called_once()
        add_comment_to_task_mock.assert_called_once()
    else:
        review_required_on_change_mock.assert_called_once()
        add_comment_to_task_mock.assert_called_once()
        pass_validation_on_task_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.insert")
@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("CIs",
                         [
                             '',
                             'sysid_1'
                         ])
def test_write_required_scans_db(select_mock, insert_mock, log_info_mock, CIs):
    select_mock.return_value = [[CIs]]
    write_required_scans_db('0')
    if not CIs:
        select_mock.assert_called_once()
    else:
        assert select_mock.call_count == 2


@mock.patch("maintenance_snow.select")
def test_review_required_on_change(select_mock):
    review_required_on_change('0')
    select_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.get_changes_after_date")
@mock.patch("maintenance_snow.write_change_db")
@mock.patch("maintenance_snow.select")
def test_process_new_changes(select_mock, write_change_db_mock, get_changes_after_date_mock,
                             log_info_mock):
    get_changes_after_date_mock.return_value = [{'number': 0}]
    process_new_changes()
    select_mock.assert_called_once()
    get_changes_after_date_mock.assert_called_once()
    select_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_headline")
@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.write_app_db")
@mock.patch("maintenance_snow.update_app_db")
@mock.patch("maintenance_snow.app_in_db")
@mock.patch("maintenance_snow.all_snow_apps")
def test_process_app_updates(all_snow_apps_mock, app_in_db_mock, update_app_db_mock,
                             write_app_db_mock, log_info_mock, log_headline_mock):
    app_with_sys_id = {'sys_id': 'sys_id'}
    app_in_db_mock.side_effect = [True, None]
    all_snow_apps_mock.return_value = [app_with_sys_id, app_with_sys_id]
    process_app_updates()
    all_snow_apps_mock.assert_called_once()
    update_app_db_mock.assert_called_once()
    write_app_db_mock.assert_called_once()
    assert app_in_db_mock.call_count == 2


@mock.patch("maintenance_snow.app_table")
@mock.patch("maintenance_snow.pysnow")
def test_all_snow_apps(pysnow_mock, app_table_mock):
    all_snow_apps()
    pysnow_mock.QueryBuilder.assert_called_once()
    app_table_mock.assert_called_once()


@mock.patch("maintenance_snow.cmdb_table")
@mock.patch("maintenance_snow.pysnow")
def test_single_snow_app(pysnow_mock, cmdb_table_mock):
    single_snow_app(REPO)
    pysnow_mock.QueryBuilder.assert_called_once()
    cmdb_table_mock.assert_called_once()


@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("select_return_value, expected",
                         [
                             ([[True]], True),
                             ([], None)
                         ])
def test_app_in_db(select_mock, select_return_value, expected):
    select_mock.return_value = select_return_value
    res = app_in_db('APP_ID')
    select_mock.assert_called_once()
    assert res == expected


@mock.patch("maintenance_snow.update")
@mock.patch("maintenance_snow.getsnJiraProjectKey")
@mock.patch("maintenance_snow.app_managed_by")
@mock.patch("maintenance_snow.app_owned_by")
@pytest.mark.parametrize("owned_by, managed_by, u_ci_cd_pipeline, u_jira_project",
                         [
                             ['', '', 'Yes', {'one': 'one'}],
                             [{'value': 'value'},
                              {'value': 'value'},
                              'No',
                              {'one': 'one', 'value': 'value'}]
                         ])
def test_update_app_db(app_owned_by_mock, app_managed_by_mock, getsnJiraProjectKey_mock,
                       update_mock, owned_by, managed_by, u_ci_cd_pipeline, u_jira_project):
    app = {'name': 'name', 'used_for': 'used_for',
           'service_classification': 'service_classification', 'u_repository_name': 'repo_name',
           'sys_id': 'sys_id', 'owned_by': owned_by, 'managed_by': managed_by,
           'u_ci_cd_pipeline': u_ci_cd_pipeline, 'u_jira_project': u_jira_project}
    update_app_db(app)
    if u_ci_cd_pipeline == 'No':
        app_owned_by_mock.assert_called_once()
        app_managed_by_mock.assert_called_once()
        getsnJiraProjectKey_mock.assert_called_once()
    update_mock.assert_called_once()


@mock.patch("maintenance_snow.insert")
@mock.patch("maintenance_snow.getsnJiraProjectKey")
@mock.patch("maintenance_snow.app_managed_by")
@mock.patch("maintenance_snow.app_owned_by")
@pytest.mark.parametrize("owned_by, managed_by, u_ci_cd_pipeline, u_jira_project",
                         [
                             ['', '', 'Yes', {'one': 'one'}],
                             [{'value': 'value'},
                              {'value': 'value'},
                              'No',
                              {'one': 'one', 'value': 'value'}]
                         ])
def test_write_app_db(app_owned_by_mock, app_managed_by_mock, getsnJiraProjectKey_mock, insert_mock,
                      owned_by, managed_by, u_ci_cd_pipeline, u_jira_project):
    app = {'name': 'name', 'used_for': 'used_for',
           'service_classification': 'service_classification', 'u_repository_name': 'repo_name',
           'sys_id': 'sys_id', 'owned_by': owned_by, 'managed_by': managed_by,
           'u_ci_cd_pipeline': u_ci_cd_pipeline, 'u_jira_project': u_jira_project}
    write_app_db(app)
    if u_ci_cd_pipeline == 'No':
        app_owned_by_mock.assert_called_once()
        app_managed_by_mock.assert_called_once()
        getsnJiraProjectKey_mock.assert_called_once()
    insert_mock.assert_called_once()


@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("select_return_value",
                         [
                              '1',
                              None
                         ])
def test_check_sast_ci(select_mock, select_return_value):
    ci_list = 'ci_1'
    check_sast_ci(ci_list)
    select_mock.assert_called_once()


@mock.patch("maintenance_snow.select")
def test_get_app_names_from_sysid(select_mock):
    sys_id_list = 'sysid_1'
    select_mock.return_value = [['app_name']]
    res = get_app_names_from_sysid(sys_id_list)
    select_mock.assert_called_once()
    assert res == 'app_name'


@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("sys_id_list, select_return_value",
                         [
                             ['', True],
                             ['sys_id_1', True],
                             ['sys_id_1, sys_id_2' , None]
                         ])
def test_all_cis_verified(select_mock, sys_id_list, select_return_value):
    select_mock.return_value = select_return_value
    all_cis_verified(sys_id_list)
    if sys_id_list:
        select_mock.assert_called_once()


@mock.patch("maintenance_snow.approval_table")
@pytest.mark.parametrize("approvals",
                         [
                             [],
                             [{'sys_updated_on': 'date'}]
                         ])
def test_check_change_approval(approval_table_mock, approvals):
    approval_table_mock.return_value.get.return_value.all.return_value = approvals
    res = check_change_approval('0')
    approval_table_mock.assert_called_once()
    if approvals:
        assert res == 'date'
    else:
        assert res == ''


@mock.patch("maintenance_snow.update")
@mock.patch("maintenance_snow.get_app_names_from_sysid")
@mock.patch("maintenance_snow.select")
def test_update_orig_app_names(select_mock, get_app_names_from_sysid_mock, update_mock):
    row = mock.MagicMock()
    row.OrigCI = 'value'
    select_mock.return_value = [row]
    update_orig_app_names()
    select_mock.assert_called_once()
    get_app_names_from_sysid_mock.assert_called_once()
    update_mock.assert_called_once()


def test_count_cis():
    change_cis = 'ci_1, ci_2'
    res = count_cis(change_cis)
    assert res == 2


@pytest.mark.parametrize("state, index",
                         [
                             ['Unused', '0'],
                             ['Pipeline', '1'],
                             ['Ready for RC', '2'],
                             ['Index3', '3'],
                             ['Index4', '4'],
                             ['Ready for RC Deployment', '5'],
                             ['RC Testing', '6'],
                             ['CIO Production Sign-Off', '7'],
                             ['Scheduled for Deployment', '8'],
                             ['Deployed to Produciton', '9'],
                             ['Failed/Rolled back', '10'],
                             ['Cancelled', '11'],
                             ['val', '999']
                         ])
def test_get_change_status_text(state, index):
    res = get_change_status_text(index)
    if index != '999':
        assert res == state
    else:
        assert res == index


@pytest.mark.parametrize("state, index",
                         [
                             ['Unused', '0'],
                             ['Open', '1'],
                             ['Cancelled', '2'],
                             ['Passed Validation', '3'],
                             ['Failed Validation', '4'],
                             ['Unknown', '5']
                         ])
def test_get_task_state_text(state, index):
    res = get_task_state_text(index)
    assert res == state


@mock.patch("maintenance_snow.insert")
@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("ci_cd, branch",
                         [
                             (None, False),
                             (True, False),
                             (True, True)
                         ])
def test_schedule_scans_for_change(select_mock, insert_mock, ci_cd, branch):
    select_value = mock.MagicMock()
    select_value.sast_ids = 'sastci_1'
    sn_record = mock.MagicMock()
    sn_record.cicd = ci_cd
    sn_record.branch = branch
    select_mock.side_effect = [[select_value], [sn_record]]
    schedule_scans_for_change('0')
    insert_mock.assert_called_once()
    assert select_mock.call_count == 2


@mock.patch("maintenance_snow.task_table")
@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "create_change_ticket_link_by_task")
@mock.patch.object(Alerts, "manual_alert")
@mock.patch("maintenance_snow.select")
@pytest.mark.parametrize("change_number",
                         [
                             [[[1, 1, 1]]]
                         ])
def test_pass_validation_on_task(select_mock, create_change_ticket_link_by_task_mock, log_info_mock,
                                 manual_alert_mock, task_table_mock, change_number):
    create_change_ticket_link_by_task_mock.return_value = 'link'
    select_mock.return_value = [change_number]
    pass_validation_on_task("0")
    select_mock.assert_called_once()
    if change_number[0][0][2] == 1:
        create_change_ticket_link_by_task_mock.assert_called_once()
        manual_alert_mock.assert_called_once()
    else:
        task_table_mock.assert_called_once()
        if int(change_number[-4:]) < 6500:
            manual_alert_mock.assert_called_once()


@mock.patch.object(Alerts, "manual_alert")
@mock.patch.object(Alerts, "create_change_ticket_link")
@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.task_table")
def test_fail_validation_on_task(task_table_mock, log_info_mock, create_change_ticket_link_mock,
                                 manual_alert_mock):

    create_change_ticket_link_mock.return_value = 'CHNG00000'
    fail_validation_on_task("0")
    task_table_mock.assert_called_once()
    create_change_ticket_link_mock.assert_called_once()
    manual_alert_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.task_table")
def test_add_comment_to_task(task_table_mock, log_info_mock):
    add_comment_to_task("0", "0")
    task_table_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch("maintenance_snow.write_change_db")
@mock.patch("maintenance_snow.get_change_by_number")
def test_add_change_to_db(get_change_by_number_mock, write_change_db_mock, log_info_mock):
    add_change_to_db("0")
    get_change_by_number_mock.assert_called_once()
    write_change_db_mock.assert_called_once()


@mock.patch("maintenance_snow.task_table")
@mock.patch("maintenance_snow.pysnow.QueryBuilder")
@mock.patch("maintenance_snow.get_change_by_number")
def test_get_task_for_change(get_change_by_number_mock, query_builder_mock, task_table_mock):
    get_task_for_change("0")
    get_change_by_number_mock.assert_called_once()
    task_table_mock.assert_called_once()


@mock.patch("maintenance_snow.user_table")
def test_app_managed_by(user_table_mock):
    app_managed_by("0")
    user_table_mock.assert_called_once()


@mock.patch("maintenance_snow.group_table")
def test_app_owned_by(group_table_mock):
    app_owned_by("0")
    group_table_mock.assert_called_once()