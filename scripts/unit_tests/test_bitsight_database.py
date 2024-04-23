'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from bitsight.database import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            return_value=[('guid','name')])
def test_dbqueries_ratings_details_available_success(select,s_exception,p_exceptions):
    """Tests DBQueries.ratings_details_available"""
    DBQueries.ratings_details_available()
    assert select.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            side_effect=Exception)
def test_dbqueries_ratings_details_available_exception(select,s_exception,p_exceptions):
    """Tests DBQueries.ratings_details_available"""
    DBQueries.ratings_details_available()
    assert select.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            return_value=[('guid','name',750,'12-20-2022')])
def test_dbqueries_get_score_change_list_success(select,s_exception,p_exceptions):
    """Tests DBQueries.get_score_change_list"""
    DBQueries.get_score_change_list()
    assert select.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            side_effect=Exception)
def test_dbqueries_get_score_change_list_exception(select,s_exception,p_exceptions):
    """Tests DBQueries.get_score_change_list"""
    DBQueries.get_score_change_list()
    assert select.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            return_value=[('guid','name',750,'12-20-2022')])
def test_dbqueries_get_watchlist_success(select,s_exception,p_exceptions):
    """Tests DBQueries.get_watchlist"""
    DBQueries.get_watchlist()
    assert select.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.select',
            side_effect=Exception)
def test_dbqueries_get_watchlist_exception(select,s_exception,p_exceptions):
    """Tests DBQueries.get_watchlist"""
    DBQueries.get_watchlist()
    assert select.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.delete_row')
def test_dbqueries_clear_table_success(d_rows,s_exception,p_exceptions):
    """Tests DBQueries.clear_table"""
    DBQueries.clear_table('table')
    assert d_rows.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.delete_row',
            side_effect=Exception)
def test_dbqueries_clear_table_exception(d_row,s_exception,p_exceptions):
    """Tests DBQueries.clear_table"""
    DBQueries.clear_table('table')
    assert d_row.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.insert')
def test_dbqueries_insert_into_table_success(insert,s_exception,p_exceptions):
    """Tests DBQueries.insert_into_table"""
    DBQueries.insert_into_table('table',{'Repo': 'repo','Something': 'value'})
    assert insert.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.insert',
            side_effect=Exception)
def test_dbqueries_insert_into_table_exception(insert,s_exception,p_exceptions):
    """Tests DBQueries.insert_into_table"""
    DBQueries.insert_into_table('table',{'Repo': 'repo','Something': 'value'})
    assert insert.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.update')
def test_dbqueries_update_score_change_success(update,s_exception,p_exceptions):
    """Tests DBQueries.update_score_change"""
    DBQueries.update_score_change()
    assert update.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.update',
            side_effect=Exception)
def test_dbqueries_update_score_change_exception(update,s_exception,p_exceptions):
    """Tests DBQueries.update_score_change"""
    DBQueries.update_score_change()
    assert update.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.update')
def test_dbqueries_no_score_change_success(update,s_exception,p_exceptions):
    """Tests DBQueries.no_score_change"""
    DBQueries.no_score_change()
    assert update.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('bitsight.database.TheLogs.process_exceptions')
@mock.patch('bitsight.database.TheLogs.sql_exception')
@mock.patch('bitsight.database.BitSightDB.update',
            side_effect=Exception)
def test_dbqueries_no_score_change_exception(update,s_exception,p_exceptions):
    """Tests DBQueries.no_score_change"""
    DBQueries.no_score_change()
    assert update.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 2

if __name__ == '__main__':
    unittest.main()
