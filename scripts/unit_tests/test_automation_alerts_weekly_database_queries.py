'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from automation_alerts.weekly_database_queries import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('automation_alerts.weekly_database_queries.TheLogs.process_exception_count_only')
@mock.patch('automation_alerts.weekly_database_queries.TheLogs.sql_exception')
@mock.patch('automation_alerts.weekly_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,fe_cnt,ex_cnt,response_results",
                         [('All values expected',None,[('KEY',),],0,0,0,0,['KEY']),
                          ('sql_sel_rv = []',None,[],0,0,0,0,[]),
                          ('Exception: sql_sel',Exception,None,1,2,1,0,[])])
def test_wadatabase_get_unique_jira_keys(sql_sel,ex_sql,peco,
                                         description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,
                                         fe_cnt,ex_cnt,response_results):
    """Tests WADatabase.get_unique_jira_keys"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = WADatabase.get_unique_jira_keys()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert peco.call_count == peco_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_results}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('automation_alerts.weekly_database_queries.TheLogs.process_exception_count_only')
@mock.patch('automation_alerts.weekly_database_queries.TheLogs.sql_exception')
@mock.patch('automation_alerts.weekly_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,fe_cnt,ex_cnt,response_results",
                         [('All values expected',None,[('repo',),],0,0,0,0,['repo']),
                          ('sql_sel_rv = []',None,[],0,0,0,0,[]),
                          ('Exception: sql_sel',Exception,None,1,2,1,0,[])])
def test_wadatabase_get_repos_missing_jira_info(sql_sel,ex_sql,peco,
                                         description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,
                                         fe_cnt,ex_cnt,response_results):
    """Tests WADatabase.get_repos_missing_jira_info"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = WADatabase.get_repos_missing_jira_info()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert peco.call_count == peco_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_results}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('automation_alerts.weekly_database_queries.TheLogs.process_exception_count_only')
@mock.patch('automation_alerts.weekly_database_queries.TheLogs.sql_exception')
@mock.patch('automation_alerts.weekly_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,fe_cnt,ex_cnt,response_results",
                         [('All values expected',None,[('repo','KEY'),],0,0,0,0,['repo (KEY)']),
                          ('sql_sel_rv = []',None,[],0,0,0,0,[]),
                          ('Exception: sql_sel',Exception,None,1,2,1,0,[])])
def test_wadatabase_get_projects_missing_security_finding_type(sql_sel,ex_sql,peco,
                                         description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,
                                         fe_cnt,ex_cnt,response_results):
    """Tests WADatabase.get_projects_missing_security_finding_type"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = WADatabase.get_projects_missing_security_finding_type()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert peco.call_count == peco_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_results}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('automation_alerts.weekly_database_queries.TheLogs.process_exception_count_only')
@mock.patch('automation_alerts.weekly_database_queries.TheLogs.sql_exception')
@mock.patch('automation_alerts.weekly_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,fe_cnt,ex_cnt,response_results",
                         [('All values expected',None,[('repo',),],0,0,0,0,['repo']),
                          ('sql_sel_rv = []',None,[],0,0,0,0,[]),
                          ('Exception: sql_sel',Exception,None,1,2,1,0,[])])
def test_wadatabase_get_missing_baseline_scans(sql_sel,ex_sql,peco,
                                         description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,
                                         fe_cnt,ex_cnt,response_results):
    """Tests WADatabase.get_missing_baseline_scans"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = WADatabase.get_missing_baseline_scans()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert peco.call_count == peco_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_results}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('automation_alerts.weekly_database_queries.TheLogs.process_exception_count_only')
@mock.patch('automation_alerts.weekly_database_queries.TheLogs.sql_exception')
@mock.patch('automation_alerts.weekly_database_queries.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,fe_cnt,ex_cnt,response_results,response_count",
                         [('All values expected',None,[('repo','2023-01-01'),],0,0,0,0,'slack_headers:Repo\\Last Scan Date\nrepo\\2023-01-01',1),
                          ('No scans on file',None,[('repo',None),],0,0,0,0,'slack_headers:Repo\\Last Scan Date\nrepo\\Never',1),
                          ('sql_sel_rv = []',None,[],0,0,0,0,None,0),
                          ('Exception: sql_sel',Exception,None,1,2,1,0,None,0)])
def test_wadatabase_get_baselines_with_overdue_scans(sql_sel,ex_sql,peco,
                                         description,sql_sel_se,sql_sel_rv,ex_sql_cnt,peco_cnt,
                                         fe_cnt,ex_cnt,response_results,response_count):
    """Tests WADatabase.get_baselines_with_overdue_scans"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = WADatabase.get_baselines_with_overdue_scans()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert peco.call_count == peco_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,
                        'Results':response_results,'Count':response_count}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
