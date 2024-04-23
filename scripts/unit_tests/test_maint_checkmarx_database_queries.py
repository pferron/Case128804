'''Unit tests for the maintenance_checkmarx script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maint.checkmarx_database_queries import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update")
def test_cxasdatabase_clear_checkmarx_data_from_aa_success(update,s_except):
    '''Tests clear_checkmarx_data_from_aa'''
    CxASDatabase.clear_checkmarx_data_from_aa()
    assert update.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update",side_effect=Exception)
def test_cxasdatabase_clear_checkmarx_data_from_aa_exception(update,s_except):
    '''Tests clear_checkmarx_data_from_aa'''
    CxASDatabase.clear_checkmarx_data_from_aa()
    assert update.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update")
def test_cxasdatabase_clear_checkmarx_data_from_applications_success(update,s_except):
    '''Tests clear_checkmarx_data_from_applications'''
    CxASDatabase.clear_checkmarx_data_from_applications()
    assert update.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update",side_effect=Exception)
def test_cxasdatabase_clear_checkmarx_data_from_applications_exception(update,s_except):
    '''Tests clear_checkmarx_data_from_applications'''
    CxASDatabase.clear_checkmarx_data_from_applications()
    assert update.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.function_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.delete_row")
def test_cxasdatabase_clear_data_from_baselineprojectdetails_delete_single_repo_success(del_row,
                                                                                        s_except):
    '''Tests clear_data_from_baselineprojectdetails'''
    CxASDatabase.clear_data_from_baselineprojectdetails('repo')
    assert del_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.delete_row")
def test_cxasdatabase_clear_data_from_baselineprojectdetails_all_repos_success(del_row,s_except):
    '''Tests clear_data_from_baselineprojectdetails'''
    CxASDatabase.clear_data_from_baselineprojectdetails(None)
    assert del_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.delete_row",side_effect=Exception)
def test_cxasdatabase_clear_data_from_baselineprojectdetails_exception(del_row,s_except):
    '''Tests clear_data_from_baselineprojectdetails'''
    CxASDatabase.clear_data_from_baselineprojectdetails(None)
    assert del_row.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.delete_row")
def test_cxasdatabase_clear_data_from_sastprojects_success(del_row,s_except):
    '''Tests clear_data_from_sastprojects'''
    CxASDatabase.clear_data_from_sastprojects()
    assert del_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.delete_row",side_effect=Exception)
def test_cxasdatabase_clear_data_from_sastprojects_exception(del_row,s_except):
    '''Tests clear_data_from_sastprojects'''
    CxASDatabase.clear_data_from_sastprojects()
    assert del_row.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('test-1',),('test-1',)])
def test_cxasdatabase_get_active_repos_success(sel_row,s_except):
    '''Tests get_active_repos'''
    CxASDatabase.get_active_repos()
    assert sel_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",side_effect=Exception)
def test_cxasdatabase_get_active_repos_exception(sel_row,s_except):
    '''Tests get_active_repos'''
    CxASDatabase.get_active_repos()
    assert sel_row.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('test-1','test-1',)])
def test_cxasdatabase_get_repo_and_project_id_success(sel_row,s_except):
    '''Tests get_repo_and_project_id'''
    CxASDatabase.get_repo_and_project_id('appsec-ops')
    assert sel_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('test-1','test-1',)])
def test_cxasdatabase_get_repo_and_project_id_success_no_repo_specified(sel_row,s_except):
    '''Tests get_repo_and_project_id'''
    CxASDatabase.get_repo_and_project_id(None)
    assert sel_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",side_effect=Exception)
def test_cxasdatabase_get_repo_and_project_id_exception(sel_row,s_except):
    '''Tests get_repo_and_project_id'''
    CxASDatabase.get_repo_and_project_id('appsec-ops')
    assert sel_row.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('test-1',),('test-1',)])
def test_cxasdatabase_get_results_to_confirm_success(sel_row,s_except):
    '''Tests get_results_to_confirm'''
    CxASDatabase.get_results_to_confirm(10519)
    assert sel_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",side_effect=Exception)
def test_cxasdatabase_get_results_to_confirm_exception(sel_row,s_except):
    '''Tests get_results_to_confirm'''
    CxASDatabase.get_results_to_confirm(1234)
    assert sel_row.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update")
def test_cxasdatabase_update_branching_stats(sel_row,s_except):
    '''Tests update_branching_stats'''
    CxASDatabase.update_branching_stats()
    assert sel_row.call_count == 1
    assert s_except.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update",side_effect=Exception)
def test_cxasdatabase_update_branching_stats_exception(update,s_except):
    '''Tests update_branching_stats'''
    CxASDatabase.update_branching_stats()
    assert update.call_count == 1
    assert s_except.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('repo',1,12345,53,'repo (type)','2023-12-31')])
def test_cxasdatabase_get_baselines_from_sastprojects(sql_sel,ex_sql):
    """Tests CxASDatabase.get_baselines_from_sastprojects"""
    CxASDatabase.get_baselines_from_sastprojects()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",side_effect=Exception)
def test_cxasdatabase_get_baselines_from_sastprojects_ex_001(sql_sel,ex_sql):
    """Tests CxASDatabase.get_baselines_from_sastprojects"""
    CxASDatabase.get_baselines_from_sastprojects()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update")
def test_cxasdatabase_set_all_sastprojects_inactive(sql_upd,ex_sql):
    """Tests CxASDatabase.set_all_sastprojects_inactive"""
    CxASDatabase.set_all_sastprojects_inactive()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.update",side_effect=Exception)
def test_cxasdatabase_set_all_sastprojects_inactive_ex_001(sql_upd,ex_sql):
    """Tests CxASDatabase.set_all_sastprojects_inactive"""
    CxASDatabase.set_all_sastprojects_inactive()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('repo',)])
def test_cxasdatabase_check_cross_repo(sql_sel,ex_sql):
    """Tests CxASDatabase.check_cross_repo"""
    CxASDatabase.check_cross_repo('repo',12345)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",side_effect=Exception)
def test_cxasdatabase_check_cross_repo_ex_001(sql_sel,ex_sql):
    """Tests CxASDatabase.check_cross_repo"""
    CxASDatabase.check_cross_repo('repo',12345)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.exception')
@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('repo',12345)])
def test_cxasdatabase_sastprojects_to_update_baseline(sql_sel,ex_sql,ex_fatal):
    """Tests CxASDatabase.sastprojects_to_update"""
    CxASDatabase.sastprojects_to_update('baseline')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert ex_fatal.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.exception')
@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            return_value=[('repo',12345)])
def test_cxasdatabase_sastprojects_to_update_pipeline(sql_sel,ex_sql,ex_fatal):
    """Tests CxASDatabase.sastprojects_to_update"""
    CxASDatabase.sastprojects_to_update('pipeline')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert ex_fatal.call_count == 0

@mock.patch('maint.checkmarx_database_queries.TheLogs.exception')
@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select")
def test_cxasdatabase_sastprojects_to_update_ex_001(sql_sel,ex_sql,ex_fatal):
    """Tests CxASDatabase.sastprojects_to_update"""
    CxASDatabase.sastprojects_to_update('invalid_type')
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert ex_fatal.call_count == 1

@mock.patch('maint.checkmarx_database_queries.TheLogs.exception')
@mock.patch('maint.checkmarx_database_queries.TheLogs.sql_exception')
@mock.patch("maint.checkmarx_database_queries.DBQueries.select",
            side_effect=Exception)
def test_cxasdatabase_sastprojects_to_update_ex_002(sql_sel,ex_sql,ex_fatal):
    """Tests CxASDatabase.sastprojects_to_update"""
    CxASDatabase.sastprojects_to_update('baseline')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ex_fatal.call_count == 0

if __name__ == '__main__':
    unittest.main()
