'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from common.miscellaneous import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_misc_start_timer():
    """Tests Misc.start_timer"""
    start = Misc.start_timer()
    assert isinstance(start,tuple)
    assert all(start)
    assert len(start) == 2

@mock.patch('common.miscellaneous.record_script_execution')
@mock.patch('common.miscellaneous.record_jira_issues_updates')
def test_misc_end_timer_no_jira_updates(jira,script):
    """Tests Misc.end_timer"""
    Misc.end_timer((1689872138.358389, '07/20/2023 12:55:38'),'source','function',0,0)
    assert jira.call_count == 0
    assert script.call_count == 1

@mock.patch('common.miscellaneous.record_script_execution')
@mock.patch('common.miscellaneous.record_jira_issues_updates')
def test_misc_end_timer_with_jira_updates(jira,script):
    """Tests Misc.end_timer"""
    Misc.end_timer((1689872138.358389, '07/20/2023 12:55:38'),'maintenance_jira_issues.py',
                   'update_all_jira_issues',0,0)
    assert jira.call_count == 1
    assert script.call_count == 1

def test_misc_day_of_the_week():
    """Tests Misc.day_of_the_week"""
    days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    get_today = Misc.day_of_the_week()
    assert get_today in days

def test_misc_progress_bar_not_started():
    """Tests Misc.progress_bar"""
    Misc.progress_bar(0,100,0)

def test_misc_progress_bar_in_progress():
    """Tests Misc.progress_bar"""
    Misc.progress_bar(50,100,0)

def test_misc_progress_bar_done():
    """Tests Misc.progress_bar"""
    Misc.progress_bar(100,100,0)

@mock.patch('common.miscellaneous.TheLogs.process_exceptions')
@mock.patch('common.miscellaneous.TheLogs.sql_exception')
@mock.patch('common.miscellaneous.delete_row')
@mock.patch('common.miscellaneous.insert')
def test_record_jira_issues_updates_success(insert,delete,s_exception,p_exceptions):
    """Tests record_jira_issues_updates"""
    record_jira_issues_updates('source','function','start','end','timezone')
    assert insert.call_count == 1
    assert delete.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('common.miscellaneous.TheLogs.process_exceptions')
@mock.patch('common.miscellaneous.TheLogs.sql_exception')
@mock.patch('common.miscellaneous.delete_row')
@mock.patch('common.miscellaneous.insert',
            side_effect=Exception)
def test_record_jira_issues_updates_exception_insert(insert,delete,s_exception,p_exceptions):
    """Tests record_jira_issues_updates"""
    record_jira_issues_updates('source','function','start','end','timezone')
    assert insert.call_count == 1
    assert delete.call_count == 0
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('common.miscellaneous.TheLogs.process_exceptions')
@mock.patch('common.miscellaneous.TheLogs.sql_exception')
@mock.patch('common.miscellaneous.delete_row',
            side_effect=Exception)
@mock.patch('common.miscellaneous.insert')
def test_record_jira_issues_updates_success(insert,delete,s_exception,p_exceptions):
    """Tests record_jira_issues_updates"""
    record_jira_issues_updates('source','function','start','end','timezone')
    assert insert.call_count == 1
    assert delete.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('common.miscellaneous.TheLogs.process_exceptions')
@mock.patch('common.miscellaneous.TheLogs.sql_exception')
@mock.patch('common.miscellaneous.insert')
def test_record_script_execution_success(insert,s_exception,p_exceptions):
    """Tests record_script_execution"""
    record_script_execution('source','function','start','time',0,0)
    assert insert.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('common.miscellaneous.TheLogs.process_exceptions')
@mock.patch('common.miscellaneous.TheLogs.sql_exception')
@mock.patch('common.miscellaneous.insert',
            side_effect=Exception)
def test_record_script_execution_exception(insert,s_exception,p_exceptions):
    """Tests record_script_execution"""
    record_script_execution('source','function','start','time',0,0)
    assert insert.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

if __name__ == '__main__':
    unittest.main()
