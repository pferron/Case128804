'''Unit tests for the maint.jira_issues_database_queries script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maint.jira_issues_database_queries import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.fe_cnt = 1
    ScrVar.ex_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.update")
@pytest.mark.parametrize("description,sql_sel_se,ex_sql_cnt,fe_cnt,ex_cnt",
                         [("Exception: sql_sel",Exception,1,0,1),
                          ("All expected values",None,0,0,0)])
def test_jidatabase_update_jirasummary(sql_sel,ex_sql,
                                       description,sql_sel_se,
                                       ex_sql_cnt,fe_cnt,ex_cnt):
    """Tests JIDatabase.update_jirasummary"""
    sql_sel.side_effect = sql_sel_se
    response = JIDatabase.update_jirasummary('repo','jira_ticket','title')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@mock.patch("maint.jira_issues_database_queries.TheLogs.function_exception")
@pytest.mark.parametrize("description,ex_func_cnt,sql_sel_se,sql_sel_rv,sql_sel_cnt,ex_sql_cnt,fe_cnt,ex_cnt,repo,source,response_rv",
                         [("Exception: Invalid source",1,None,None,0,0,0,1,'repo','invalid source',[]),
                          ("Exception: sql_sel",0,Exception,None,1,1,0,1,'repo','Checkmarx',[]),
                          ("All expected values",0,None,[('KEY-123','repo',),],1,0,0,0,'repo','Mend OS',[{'Ticket':'KEY-123','Repo':'repo'}])])
def test_jidatabase_ticket_titles_to_fix(ex_func,sql_sel,ex_sql,
                                         description,ex_func_cnt,sql_sel_se,sql_sel_rv,sql_sel_cnt,
                                         ex_sql_cnt,fe_cnt,ex_cnt,repo,source,response_rv):
    """Tests JIDatabase.ticket_titles_to_fix"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.ticket_titles_to_fix(repo,source)
    assert ex_func.call_count == ex_func_cnt
    assert sql_sel.call_count == sql_sel_cnt
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,[]),
                          ("All expected values",None,[('KEY-123','YEK-321',),],0,0,0,[{'NewTicket':'KEY-123','OldTicket':'YEK-321'}])])
def test_jidatabase_tool_tickets_to_update(sql_sel,ex_sql,
                                           description,sql_sel_se,sql_sel_rv,
                                           ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.tool_tickets_to_update"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.tool_tickets_to_update('table')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,None),
                          ("All expected values",None,[('repo','c_epic','ce_pk','JIK','JPK',),],0,0,0,[('repo','c_epic','ce_pk','JIK','JPK',),])])
def test_jidatabase_get_all_jira_issues(sql_sel,ex_sql,
                                        description,sql_sel_se,sql_sel_rv,
                                        ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_all_jira_issues()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,None),
                          ("All expected values",None,[('repo','c_epic','ce_pk','JIK','JPK',),],0,0,0,[('repo','c_epic','ce_pk','JIK','JPK',),])])
def test_jidatabase_get_repo_jira_issues(sql_sel,ex_sql,
                                         description,sql_sel_se,sql_sel_rv,
                                         ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.get_repo_jira_issues"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_repo_jira_issues('repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.log_info")
@mock.patch("maint.jira_issues_database_queries.TheLogs.function_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.update_multiple")
@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@mock.patch("maint.jira_issues_database_queries.JIDatabase.get_tool_tickets")
@mock.patch("maint.jira_issues_database_queries.TheLogs.log_headline")
@pytest.mark.parametrize("description,gtt_rv,sql_sel_se,sql_sel_rv,sql_sel_cnt,ex_sql_cnt,um_se,um_rv,um_cnt,ex_func_cnt,fe_cnt,ex_cnt,repo,tool",
                         [('gtt_rv = []',[],None,None,0,0,None,None,0,0,0,0,'All','All'),
                          ('Exception: sql_sel',[('KEY-123',),],Exception,None,2,2,None,0,1,0,0,2,'repo','Checkmarx'),
                          ('Exception: um',[('KEY-123',),],None,[('value',)],2,0,Exception,2,1,1,0,1,'repo','Mend OS'),
                          ('All expected values',[('KEY-123',),],None,[('value',)],2,0,None,2,1,0,0,0,'repo','Mend OS')])
def test_jidatabase_update_missing_ji_data(log_hl,gtt,sql_sel,ex_sql,um,ex_func,log_ln,
                                           description,gtt_rv,sql_sel_se,sql_sel_rv,sql_sel_cnt,
                                           ex_sql_cnt,um_se,um_rv,um_cnt,ex_func_cnt,
                                           fe_cnt,ex_cnt,repo,tool):
    """Tests JIDatabase.update_missing_ji_data"""
    gtt.return_value = gtt_rv
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    um.side_effect = um_se
    um.return_value = um_rv
    response = JIDatabase.update_missing_ji_data(repo,tool)
    assert log_hl.call_count == 1
    assert gtt.call_count == 1
    assert sql_sel.call_count == sql_sel_cnt
    assert ex_sql.call_count == ex_sql_cnt
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,sql_sel_cnt,ex_sql_cnt,fe_cnt,ex_cnt,empty_fields,response_rv",
                         [('empty_fields = None',None,None,0,0,0,0,None,[]),
                          ('Exception: sql_sel',Exception,None,1,1,0,1,'(field_name IS NULL)',[]),
                          ('All expected values',None,[('KEY-123',),],1,0,0,0,'(field_name IS NULL)',[('KEY-123',),])])
def test_jidatabase_get_tool_tickets(sql_sel,ex_sql,
                                         description,sql_sel_se,sql_sel_rv,sql_sel_cnt,
                                         ex_sql_cnt,fe_cnt,ex_cnt,empty_fields,response_rv):
    """Tests JIDatabase.get_tool_tickets"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_tool_tickets('Mend OS',empty_fields,'repo','table_name')
    assert sql_sel.call_count == sql_sel_cnt
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,False),
                          ("All expected values",None,[('KEY-123',),],0,0,0,True)])
def test_jidatabase_check_for_jira_issue(sql_sel,ex_sql,
                                         description,sql_sel_se,sql_sel_rv,
                                         ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.check_for_jira_issue"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.check_for_jira_issue('KEY-123')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.log_info")
@mock.patch("maint.jira_issues_database_queries.TheLogs.function_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.update_multiple")
@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@mock.patch("maint.jira_issues_database_queries.TheLogs.log_headline")
@pytest.mark.parametrize("description,log_hl_cnt,sql_sel_se,sql_sel_rv,sql_sel_cnt,ex_sql_cnt,um_se,um_rv,um_cnt,log_ln_cnt,ex_func_cnt,fe_cnt,ex_cnt,repo,tool",
                         [('Results for four',0,None,None,0,0,None,None,0,0,0,0,0,'four','Mend OS'),
                          ('All expected values',1,None,[('KEY-123','YEK-321',),],1,0,None,1,1,1,0,0,0,'repo','Checkmarx'),
                          ('Exception: sql_sel',1,Exception,None,1,1,None,None,0,0,0,0,1,'repo','Mend OS'),
                          ('Exception: um',1,None,[('KEY-123','YEK-321',),],1,0,Exception,None,1,1,1,0,1,'repo','Mend OS'),
                          ('Exception: Invalid tool',1,None,None,0,0,None,None,0,1,1,1,0,'repo','tool')])
def test_jidatabase_update_moved_tool_tickets(log_hl,sql_sel,ex_sql,um,ex_func,log_ln,
                                              description,log_hl_cnt,sql_sel_se,sql_sel_rv,
                                              sql_sel_cnt,ex_sql_cnt,um_se,um_rv,um_cnt,log_ln_cnt,
                                              ex_func_cnt,fe_cnt,ex_cnt,repo,tool):
    """Tests JIDatabase.update_moved_tool_tickets"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    um.side_effect = um_se
    um.return_value = um_rv
    response = JIDatabase.update_moved_tool_tickets(repo,tool)
    assert log_hl.call_count == log_hl_cnt
    assert sql_sel.call_count == sql_sel_cnt
    assert ex_sql.call_count == ex_sql_cnt
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == log_ln_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,[]),
                          ('All expected values',None,[('KEY',),],0,0,0,['KEY'])])
def test_jidatabase_get_project_key(sql_sel,ex_sql,
                                    description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                    fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.get_project_key"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_project_key('repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,repo,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,'repo',[]),
                          ('All expected values - single repo',None,[('KEY-123',),],0,0,0,'repo',['KEY-123']),
                          ('All expected values - all repos',None,[('KEY-123',),],0,0,0,'All',['KEY-123'])])
def test_jidatabase_get_cancelled_tickets(sql_sel,ex_sql,
                                          description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                          fe_cnt,ex_cnt,repo,response_rv):
    """Tests JIDatabase.get_cancelled_tickets"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_cancelled_tickets(repo)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,repo,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,'repo',[]),
                          ('All expected values - single repo',None,[('KEY-100','KEY-123',),],0,0,0,'repo',[{'OriginalEpic':'KEY-100','JiraIssueKey':'KEY-123'}]),
                          ('All expected values - all repos',None,[('KEY-100','KEY-123',),],0,0,0,'All',[{'OriginalEpic':'KEY-100','JiraIssueKey':'KEY-123'}])])
def test_jidatabase_get_original_epic(sql_sel,ex_sql,
                                      description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                      fe_cnt,ex_cnt,repo,response_rv):
    """Tests JIDatabase.get_original_epic"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_original_epic(repo)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,[]),
                          ('All expected values',None,[('KEY-123','Summary - repo',),],0,0,0,[{'SET':{'Repo':'repo'},'WHERE_EQUAL':{'JiraIssueKey':'KEY-123'}}])])
def test_jidatabase_get_tickets_with_missing_repos(sql_sel,ex_sql,
                                                   description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                                   fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.get_tickets_with_missing_repos"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_tickets_with_missing_repos()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maint.jira_issues_database_queries.TheLogs.sql_exception")
@mock.patch("maint.jira_issues_database_queries.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,{}),
                          ('All expected values',None,[('KEY-100','KEY',),],0,0,0,{'Epic':'KEY-100','ProjectKey':'KEY'})])
def test_jidatabase_get_ticket_current_epic(sql_sel,ex_sql,
                                            description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                            fe_cnt,ex_cnt,response_rv):
    """Tests JIDatabase.get_ticket_current_epic"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = JIDatabase.get_ticket_current_epic("KEY-123")
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt,'Results':response_rv}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
