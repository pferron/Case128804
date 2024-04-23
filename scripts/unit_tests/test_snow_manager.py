import sys
from unittest import mock
import pytest
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
sys.modules['pysnow'] = mock.MagicMock()
from snow.snow_manager import *


@mock.patch("snow.snow_manager.pysnow")
def test_get_jira_key(pysnow_mock):
    snow_manager = SnowManager()
    snow_manager.jira_table = mock.MagicMock()
    snow_manager.get_jira_key(0)
    snow_manager.jira_table.get.assert_called_once()


def test_get_sn_jira_project_key():
    snow_manager = SnowManager()
    snow_manager.get_jira_key = mock.MagicMock()
    snow_manager.get_sn_jira_project_key('0')
    snow_manager.get_jira_key.assert_called_once()


@pytest.mark.parametrize("group_id",
                         [
                             'group_id',
                             None
                         ])
def test_get_app_owned_by(group_id):
    snow_manager = SnowManager()
    snow_manager.group_table = mock.MagicMock()
    res = snow_manager.get_app_owned_by(group_id)
    if group_id:
        snow_manager.group_table.get.assert_called_once()
    else:
        assert res == ''


def test_get_app_owned_by_exception():
    snow_manager = SnowManager()
    snow_manager.group_table = mock.MagicMock()
    snow_manager.group_table.get.return_value = {}
    res = snow_manager.get_app_owned_by('group_id')
    assert res == ''


@pytest.mark.parametrize("user_id",
                         [
                             'user_id',
                             None
                         ])
def test_get_app_managed_by(user_id):
    snow_manager = SnowManager()
    snow_manager.user_table = mock.MagicMock()
    res = snow_manager.get_app_managed_by(user_id)
    if user_id:
        snow_manager.user_table.get.assert_called_once()
    else:
        assert res == ''


def test_get_app_managed_by_exception():
    snow_manager = SnowManager()
    snow_manager.user_table = mock.MagicMock()
    snow_manager.user_table.get.return_value = {}
    res = snow_manager.get_app_managed_by('user_id')
    assert res == ''


def test_get_snow_app():
    snow_manager = SnowManager()
    snow_manager.cmdb_table = mock.MagicMock()
    snow_manager.get_snow_app('repo')
    snow_manager.cmdb_table.get.assert_called_once()


def test_get_all_snow_apps():
    snow_manager = SnowManager()
    snow_manager.app_table = mock.MagicMock()
    snow_manager.get_all_snow_apps()
    snow_manager.app_table.get.assert_called_once()


def test_get_snow_apps_after_date():
    snow_manager = SnowManager()
    snow_manager.app_table = mock.MagicMock()
    snow_manager.get_snow_apps_after_date(datetime.now())
    snow_manager.app_table.get.assert_called_once()


@pytest.mark.parametrize("time_zone",
                         [
                             'local',
                             'utc'
                         ])
def test_get_datetime(time_zone):
    snow_manager = SnowManager()
    snow_manager.app_table = mock.MagicMock()
    res = snow_manager.get_datetime(time_zone)
    assert type(res) == datetime


@pytest.mark.parametrize("time",
                         [
                             datetime.now(),
                             ''
                         ])
def test_local_to_utc(time):
    snow_manager = SnowManager()
    res = snow_manager.local_to_utc(time)
    if time:
        assert type(res) == datetime
    else:
        assert res == ''


@pytest.mark.parametrize("time",
                         [
                             '2023-01-01 00:00:00',
                             ''
                         ])
def test_utc_to_local(time):
    snow_manager = SnowManager()
    res = snow_manager.utc_to_local(time)
    if time:
        assert type(res) == str
    else:
        assert res == ''
