import sys
from unittest import mock
import pytest
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
sys.modules['pysnow'] = mock.MagicMock()
from snow.change_manager import *


@mock.patch("snow.change_manager.pysnow")
def test_get_change_by_number(pysnow_mock):
    sn_change_manager = SNChangeManager()
    sn_change_manager.change_table = mock.MagicMock()
    sn_change_manager.get_change_by_number(0)
    pysnow_mock.QueryBuilder.assert_called_once()
    sn_change_manager.change_table.get.assert_called_once()


@mock.patch("snow.change_manager.pysnow")
def test_get_changes_after_date(pysnow_mock):
    sn_change_manager = SNChangeManager()
    sn_change_manager.change_table = mock.MagicMock()
    sn_change_manager.get_changes_after_date(datetime.now())
    pysnow_mock.QueryBuilder.assert_called_once()
    sn_change_manager.change_table.get.assert_called_once()


@mock.patch("snow.change_manager.pysnow")
def test_get_all_changes(pysnow_mock):
    sn_change_manager = SNChangeManager()
    sn_change_manager.change_table = mock.MagicMock()
    sn_change_manager.get_all_changes()
    sn_change_manager.change_table.get.assert_called_once()


def test_get_change_by_query():
    sn_change_manager = SNChangeManager()
    sn_change_manager.change_table = mock.MagicMock()
    sn_change_manager.get_change_by_query({'query': 'query'})
    sn_change_manager.change_table.get.assert_called_once()


@mock.patch("snow.change_manager.pysnow")
@pytest.mark.parametrize("approvals, expected",
                         [
                             ([], ''),
                             ([{'sys_updated_on': 'val'}], 'val'),
                         ])
def test_check_change_approval(pysnow_mock, approvals, expected):
    sn_change_manager = SNChangeManager()
    sn_change_manager.approval_table.get = mock.MagicMock()
    sn_change_manager.approval_table.get.return_value.all.return_value = approvals
    res = sn_change_manager.check_change_approval(0)
    assert res == expected
