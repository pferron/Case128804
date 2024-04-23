'''Unit tests for the maint.application_tables_database_queries script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maint.application_tables_database_queries import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maint.application_tables_database_queries.TheLogs.process_exception_count_only')
@mock.patch('maint.application_tables_database_queries.TheLogs.function_exception')
@mock.patch('maint.application_tables_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,fe_cnt,ex_cnt",
                         [("All expected values",None,[('repo','team',)],0,0,0,0),
                          ("Exception: sql_sel",Exception,[],1,2,1,0)])
def test_appqueries_get_available_progteam_jira_updates(sql_sel,ex_func,peco,
                                                        description,sql_sel_se,sql_sel_rv,
                                                        ex_func_cnt,peco_cnt,fe_cnt,ex_cnt):
    """Tests AppQueries.get_available_progteam_jira_updates"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = AppQueries.get_available_progteam_jira_updates()
    assert sql_sel.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert peco.call_count == peco_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':sql_sel_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.application_tables_database_queries.TheLogs.process_exception_count_only')
@mock.patch('maint.application_tables_database_queries.TheLogs.function_exception')
@mock.patch('maint.application_tables_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,fe_cnt,ex_cnt",
                         [("All expected values",None,[('KEY','KEY-123',)],0,0,0,0),
                          ("Exception: sql_sel",Exception,[],1,2,1,0)])
def test_appqueries_get_jira_keys_for_team(sql_sel,ex_func,peco,
                                           description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,
                                           fe_cnt,ex_cnt):
    """Tests AppQueries.get_jira_keys_for_team"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = AppQueries.get_jira_keys_for_team('team')
    assert sql_sel.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert peco.call_count == peco_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':sql_sel_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.application_tables_database_queries.TheLogs.process_exception_count_only')
@mock.patch('maint.application_tables_database_queries.TheLogs.function_exception')
@mock.patch('maint.application_tables_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,fe_cnt,ex_cnt",
                         [("All expected values",None,[('repo','team',)],0,0,0,0),
                          ("Exception: sql_sel",Exception,[],1,2,1,0)])
def test_appqueries_get_applicationautomation_jira_project_keys(sql_sel,ex_func,peco,
                                                                description,sql_sel_se,sql_sel_rv,
                                                                ex_func_cnt,peco_cnt,fe_cnt,ex_cnt):
    """Tests AppQueries.get_applicationautomation_jira_project_keys"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = AppQueries.get_applicationautomation_jira_project_keys()
    assert sql_sel.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert peco.call_count == peco_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':sql_sel_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.application_tables_database_queries.TheLogs.process_exception_count_only')
@mock.patch('maint.application_tables_database_queries.TheLogs.function_exception')
@mock.patch('maint.application_tables_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,fe_cnt,ex_cnt",
                         [("All expected values",None,[('team','lead','manager',)],0,0,0,0),
                          ("Exception: sql_sel",Exception,[],1,2,1,0)])
def test_appqueries_get_progteams_teams(sql_sel,ex_func,peco,
                                        description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,
                                        fe_cnt,ex_cnt):
    """Tests AppQueries.get_progteams_teams"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = AppQueries.get_progteams_teams('KEY')
    assert sql_sel.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert peco.call_count == peco_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':sql_sel_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.application_tables_database_queries.TheLogs.process_exception_count_only')
@mock.patch('maint.application_tables_database_queries.TheLogs.function_exception')
@mock.patch('maint.application_tables_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_func_cnt,peco_cnt,fe_cnt,ex_cnt",
                         [("All expected values",None,[('has_sf','pid','sid','sd',)],0,0,0,0),
                          ("Exception: sql_sel",Exception,[],1,2,1,0)])
def test_appqueries_get_applicationautomation_data(sql_sel,ex_func,peco,
                                                                description,sql_sel_se,sql_sel_rv,
                                                                ex_func_cnt,peco_cnt,fe_cnt,ex_cnt):
    """Tests AppQueries.get_applicationautomation_data"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = AppQueries.get_applicationautomation_data()
    assert sql_sel.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert peco.call_count == peco_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':sql_sel_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
