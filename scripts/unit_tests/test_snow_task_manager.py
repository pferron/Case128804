import sys
from unittest import mock
import pytest
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
sys.modules['pysnow'] = mock.MagicMock()
from snow.task_manager import *
import datetime


@mock.patch.object(TheLogs, "log_info")
def test_add_comment_to_task(log_info_mock):
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.add_comment_to_task('0', 'comment')
    snow_task_manager.task_table.update.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "create_change_ticket_link")
@mock.patch.object(Alerts, "manual_alert")
def test_pass_validation_on_task_review_required_on_change(create_change_ticket_link_mock,
                                                           manual_alert_mock, log_info_mock):
    create_change_ticket_link_mock.return_value = 'ch_lnk'
    snow_task_manager = SNTasksManager()
    snow_task_manager.review_required_on_change = mock.MagicMock()
    snow_task_manager.review_required_on_change.return_value = True
    snow_task_manager.pass_validation_on_task(0, 0)
    create_change_ticket_link_mock.assert_called_once()
    manual_alert_mock.assert_called_once()


@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "create_change_ticket_link")
@mock.patch.object(Alerts, "manual_alert")
@pytest.mark.parametrize("last_four_change",
                         [
                             '600',
                             '6500'
                          ])
def test_pass_validation_on_task_no_review_required_on_change(create_change_ticket_link_mock,
                                                              manual_alert_mock, log_info_mock,
                                                              last_four_change):
    create_change_ticket_link_mock.return_value = 'ch_lnk'
    snow_task_manager = SNTasksManager()
    snow_task_manager.review_required_on_change = mock.MagicMock()
    snow_task_manager.conn = mock.MagicMock()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.review_required_on_change.return_value = False
    snow_task_manager.pass_validation_on_task(0, last_four_change)
    if last_four_change == 600:
        manual_alert_mock.assert_called_once()
    snow_task_manager.conn.query.assert_called_once()
    snow_task_manager.task_table.update.assert_called_once()


@mock.patch.object(TheLogs, "function_exception")
@mock.patch.object(TheLogs, "process_exceptions")
@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "create_change_ticket_link")
@mock.patch.object(Alerts, "manual_alert", side_effect=Exception)
def test_pass_validation_on_task_exception_one(create_change_ticket_link_mock, manual_alert_mock,
                                               log_info_mock, process_exception_mock,
                                               function_exception_mock):
    create_change_ticket_link_mock.return_value = 'ch_lnk'
    snow_task_manager = SNTasksManager()
    snow_task_manager.review_required_on_change = mock.MagicMock()
    snow_task_manager.review_required_on_change.return_value = True
    snow_task_manager.pass_validation_on_task(0, 0)
    process_exception_mock.assert_called_once()
    function_exception_mock.assert_called_once()


@mock.patch.object(TheLogs, "function_exception")
@mock.patch.object(TheLogs, "process_exceptions")
@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "create_change_ticket_link")
@mock.patch.object(Alerts, "manual_alert", side_effect=Exception)
def test_pass_validation_on_task_exception_two(create_change_ticket_link_mock, manual_alert_mock,
                                               log_info_mock, process_exception_mock,
                                               function_exception_mock):
    create_change_ticket_link_mock.return_value = 'ch_lnk'
    snow_task_manager = SNTasksManager()
    snow_task_manager.review_required_on_change = mock.MagicMock()
    snow_task_manager.conn = mock.MagicMock()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.review_required_on_change.return_value = False
    snow_task_manager.pass_validation_on_task(0, '0')
    process_exception_mock.assert_called_once()
    function_exception_mock.assert_called_once()


@mock.patch.object(SNTasksManager, "get_task_state_text")
@mock.patch.object(SNTasksManager, "utc_to_local")
@mock.patch.object(TheLogs, "log_info")
def test_add_task_to_db(log_info_mock, utc_to_local_mock, get_task_state_text_mock):
    snow_task_manager = SNTasksManager()
    snow_change_manager_mock = mock.MagicMock()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.conn = mock.MagicMock()
    task = {'parent': {'value': 'val'},
            'sys_created_on': 'val',
            'sys_updated_on': 'val',
            'number': 'val',
            'state': 'val'}
    snow_task_manager.add_task_to_db(task, snow_change_manager_mock)
    snow_change_manager_mock.get_change_by_query.assert_called_once()
    snow_task_manager.conn.query.assert_called_once()
    get_task_state_text_mock.assert_called_once()
    assert utc_to_local_mock.call_count == 2


@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "manual_alert")
@mock.patch.object(Alerts, "create_change_ticket_link")
def test_fail_validation_on_task(create_change_ticket_link_mock, manual_alert_mock, log_info_mock):
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.conn = mock.MagicMock()
    snow_task_manager.fail_validation_on_task('0', '0', True)
    snow_task_manager.conn.query.assert_called_once()
    create_change_ticket_link_mock.assert_called_once()


@mock.patch.object(TheLogs, "function_exception")
@mock.patch.object(TheLogs, "process_exceptions")
@mock.patch.object(TheLogs, "log_info")
@mock.patch.object(Alerts, "manual_alert", side_effect=Exception)
@mock.patch.object(Alerts, "create_change_ticket_link")
def test_fail_validation_on_task_exception(create_change_ticket_link_mock, manual_alert_mock,
                                           log_info_mock, process_exception_mock,
                                           function_exception_mock):
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.conn = mock.MagicMock()
    snow_task_manager.fail_validation_on_task('0', '0', True)
    process_exception_mock.assert_called_once()
    function_exception_mock.assert_called_once()


def test_get_task():
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.get_task('0')
    snow_task_manager.task_table.get.assert_called_once()


def test_get_all_tasks():
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.get_all_tasks()
    snow_task_manager.task_table.get.assert_called_once()


def test_get_tasks_after_date():
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.get_tasks_after_date(datetime.datetime.now())
    snow_task_manager.task_table.get.assert_called_once()


def test_get_all_open_tasks():
    snow_task_manager = SNTasksManager()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.get_all_open_tasks()
    snow_task_manager.task_table.get.assert_called_once()


@mock.patch("snow.task_manager.pysnow")
def test_get_task_for_change(pysnow_mock):
    snow_task_manager = SNTasksManager()
    snow_task_manager.change_table = mock.MagicMock()
    snow_task_manager.task_table = mock.MagicMock()
    snow_task_manager.get_task_for_change(0)
    snow_task_manager.change_table.get.assert_called_once()
    snow_task_manager.task_table.get.assert_called_once()


def test_review_required_on_change():
    snow_task_manager = SNTasksManager()
    snow_task_manager.conn = mock.MagicMock()
    snow_task_manager.review_required_on_change(0)
    snow_task_manager.conn.query.assert_called_once()


@pytest.mark.parametrize("index, expected",
                         [
                             (0, "Unused"),
                             (1, "Open"),
                             (2, "Cancelled"),
                             (3, "Passed Validation"),
                             (4, "Failed Validation"),
                             (5, "Unknown"),
                         ])
def test_get_task_state_text(index, expected):
    snow_task_manager = SNTasksManager()
    snow_task_manager.conn = mock.MagicMock()
    res = snow_task_manager.get_task_state_text(index)
    assert res == expected
