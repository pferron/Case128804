'''Unit tests for the maintenance_log_cleanup script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from datetime import datetime, timedelta
from maintenance_log_cleanup import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maintenance_log_cleanup.LogCleanup.all_maintenance')
def test_main(am):
    """Tests the main() function"""
    main()
    assert am.call_count == 0

@mock.patch.object(Misc, "end_timer")
@mock.patch.object(Misc, "start_timer")
@mock.patch('maintenance_log_cleanup.archive_cleanup')
@mock.patch('maintenance_log_cleanup.archive_logs')
def test_all_maintenance(al,ac,st,et):
    """Tests LogCleanup.all_maintenance"""
    LogCleanup.all_maintenance()
    assert st.call_count == 1
    assert al.call_count == 1
    assert ac.call_count == 1
    assert et.call_count == 1

@mock.patch.object(LogCleanup,'move_logs',return_value=1)
def test_archive_logs(ml):
    """Tests archive_logs"""
    archive_logs()
    assert ml.call_count == 1

@mock.patch.object(LogCleanup,'move_logs',return_value=0)
def test_archive_logs_no_updates(ml):
    """Tests archive_logs"""
    archive_logs()
    assert ml.call_count == 1

@mock.patch.object(LogCleanup,'delete_archives',return_value=1)
def test_archive_cleanup(da):
    """Tests archive_cleanup"""
    archive_cleanup(30)
    assert da.call_count == 1

@mock.patch.object(LogCleanup,'delete_archives',return_value=0)
def test_archive_cleanup_no_deleted(da):
    """Tests archive_cleanup"""
    archive_cleanup(30)
    assert da.call_count == 1

@mock.patch('maintenance_log_cleanup.TheLogs.function_exception')
@mock.patch('maintenance_log_cleanup.os.stat',
            return_value=[0,0,0,0,0,0,0,0,datetime.timestamp(datetime.today()-timedelta(days=2))])
@mock.patch('maintenance_log_cleanup.os.walk',
            return_value=[('/foo', ('bar',), ('baz',)),('/foo/bar', (), ('spam', 'eggs')),])
@mock.patch('maintenance_log_cleanup.os.remove')
@mock.patch('maintenance_log_cleanup.os.chdir')
def test_logcleanup_delete_archives(os_cd,os_rem,os_wlk,os_st,ex_func):
    """Tests LogCleanup.delete_archives"""
    LogCleanup.delete_archives(-1,["\\"])
    assert os_cd.call_count == 1
    assert os_rem.call_count == 3
    assert os_wlk.call_count == 1
    assert os_st.call_count == 3
    assert ex_func.call_count == 0

@mock.patch('maintenance_log_cleanup.TheLogs.function_exception')
@mock.patch('maintenance_log_cleanup.os.stat',
            return_value=[0,0,0,0,0,0,0,0,datetime.timestamp(datetime.today()-timedelta(days=2))])
@mock.patch('maintenance_log_cleanup.os.walk',
            return_value=[('/foo', ('bar',), ('baz',)),('/foo/bar', (), ('spam', 'eggs')),])
@mock.patch('maintenance_log_cleanup.os.remove',
            side_effect=Exception)
@mock.patch('maintenance_log_cleanup.os.chdir')
def test_logcleanup_delete_archives_exception(os_cd,os_rem,os_wlk,os_st,ex_func):
    """Tests LogCleanup.delete_archives"""
    LogCleanup.delete_archives(-1,["\\"])
    assert os_cd.call_count == 1
    assert os_rem.call_count == 3
    assert os_wlk.call_count == 1
    assert os_st.call_count == 3
    assert ex_func.call_count == 3

@mock.patch('maintenance_log_cleanup.TheLogs.function_exception')
@mock.patch('maintenance_log_cleanup.shutil.move')
@mock.patch('builtins.open',new_callable=mock.mock_open,read_data='1')
def test_logcleanup_move_logs(m_open,m_file,ex_func):
    """Tests LogCleanup.move_logs"""
    # mock_open = mock.mock_open(spec='file.log',read_data='Some data')
    with mock.patch('os.listdir') as mocked_listdir:
        mocked_listdir.return_value = ['file.log']
        LogCleanup.move_logs(["c:\\appsec\\logs\\"])
        assert m_open.call_count == 1
        assert m_file.call_count == 1
        assert ex_func.call_count == 0

@mock.patch('maintenance_log_cleanup.TheLogs.function_exception')
@mock.patch('maintenance_log_cleanup.shutil.move',
            side_effect=Exception)
@mock.patch('builtins.open',new_callable=mock.mock_open,read_data='1')
def test_logcleanup_move_logs_exception(m_open,m_file,ex_func):
    """Tests LogCleanup.move_logs"""
    # mock_open = mock.mock_open(spec='file.log',read_data='Some data')
    with mock.patch('os.listdir') as mocked_listdir:
        mocked_listdir.return_value = ['file.log']
        LogCleanup.move_logs(["c:\\appsec\\logs\\"])
        assert m_open.call_count == 1
        assert m_file.call_count == 1
        assert ex_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
