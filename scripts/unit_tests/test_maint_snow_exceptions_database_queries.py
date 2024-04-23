'''Unit tests for maint\snow_exceptions_database_queries.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from maint.snow_exceptions_database_queries import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    """Tests ScrVar.reset_exception_counts"""
    ScrVar.ex_cnt = 1
    ScrVar.fe_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 0

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.update')
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_mark_approvers_inactive(ex_reset,sql_upd,ex_sql):
    """Tests SNowQueries.mark_approvers_inactive"""
    SNowQueries.mark_approvers_inactive()
    assert ex_reset.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.update',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_mark_approvers_inactive_ex_sql_upd(ex_reset,sql_upd,ex_sql):
    """Tests SNowQueries.mark_approvers_inactive"""
    SNowQueries.mark_approvers_inactive()
    assert ex_reset.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.select',
            return_value=[('RITM',None,),('RITM','ABC-123',),])
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_get_all_ritms(ex_reset,sql_sel,ex_sql):
    """Tests SNowQueries.get_all_ritms"""
    SNowQueries.get_all_ritms()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.select',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_get_all_ritms_ex_sql_upd(ex_reset,sql_sel,ex_sql):
    """Tests SNowQueries.get_all_ritms"""
    SNowQueries.get_all_ritms()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.select',
            return_value=[('RITM',None,),('RITM','ABC-123',),])
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_get_all_jiraissues(ex_reset,sql_sel,ex_sql):
    """Tests SNowQueries.get_all_jiraissues"""
    SNowQueries.get_all_jiraissues()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_database_queries.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_database_queries.DBQueries.select',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_database_queries.ScrVar.reset_exception_counts')
def test_snowqueries_get_all_jiraissues_ex_sql_upd(ex_reset,sql_sel,ex_sql):
    """Tests SNowQueries.get_all_jiraissues"""
    SNowQueries.get_all_jiraissues()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

if __name__ == '__main__':
    unittest.main()
