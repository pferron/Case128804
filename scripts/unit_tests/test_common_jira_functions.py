"""Unit tests for the common.jira_functions script"""

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from datetime import datetime, timedelta
from common.jira_functions import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.jira_functions.TheLogs.sql_exception')
@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt",
                         [("Exception: sql_sel",Exception,None,1,0,1),
                          ("All expected values",None,[(datetime.now(),),],0,0,0)])
def test_generalticketing_get_ticket_due_date(sql_sel,ex_sql,
                                              description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,
                                              ex_cnt):
    """Tests GeneralTicketing.get_ticket_due_date"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    GeneralTicketing.get_ticket_due_date('ticket')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('common.jira_functions.requests.put')
@pytest.mark.parametrize("description,req_put_sc,jira_issue_key,response_rv",
                         [("Incorrect status code",404,'FOUR-1234',False),
                          ("All expected values",204,'KEY-1234',True)])
def test_generalticketing_remove_epic_link(req_put,
                                           description,req_put_sc,jira_issue_key,response_rv):
    """Tests GeneralTicketing.remove_epic_link"""
    resp_mock = mock.Mock(status_code=req_put_sc)
    req_put.return_value = resp_mock
    response = GeneralTicketing.remove_epic_link(jira_issue_key)
    assert req_put.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.requests.get')
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,repo,response_rv",
                         [("Incorrect status code",404,None,'four',False),
                          ("All expected values",200,{'issueLinkTypes':[{'name':'Relates'}]},'repo',True)])
def test_generalticketing_has_related_link_type(req_get,
                                                description,req_get_sc,req_get_rv,repo,response_rv):
    """Tests GeneralTicketing.has_related_link_type"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.has_related_link_type(repo)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.requests.post')
@pytest.mark.parametrize("description,req_pst_sc,req_pst_cnt,jira_issue_key,related_list,response_rv",
                         [("Incorrect status code",404,1,'KEY-123',['KEY-321'],False),
                          ("All expected values",204,2,'FOUR-123',['FOUR-321','FOUR-1234'],True)])
def test_generalticketing_add_related_ticket(req_pst,
                                             description,req_pst_sc,req_pst_cnt,jira_issue_key,
                                             related_list,response_rv):
    """Tests GeneralTicketing.add_related_ticket"""
    resp_mock = mock.Mock(status_code=req_pst_sc)
    req_pst.return_value = resp_mock
    response = GeneralTicketing.add_related_ticket(jira_issue_key,related_list)
    assert req_pst.call_count == req_pst_cnt
    assert response == response_rv

@mock.patch('common.jira_functions.requests.put')
@pytest.mark.parametrize("description,req_put_sc,jira_issue_key,epic,response_rv",
                         [('Incorrect status code',404,'FOUR-1234','FOUR-4321',False),
                          ('All expected values',204,'KEY-123','KEY-321',True)])
def test_generalticketing_add_epic_link(req_put,
                                        description,req_put_sc,jira_issue_key,epic,response_rv):
    """Tests GeneralTicketing.add_epic_link"""
    resp_mock = mock.Mock(status_code=req_put_sc)
    req_put.return_value = resp_mock
    response = GeneralTicketing.add_epic_link(jira_issue_key,epic)
    assert req_put.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.requests.get')
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Incorrect status code",404,None,'FOUR',False),
                          ("All expected values",200,{'issueTypes':[{'name':'Security Finding'}]},'KEY',True)])
def test_generalticketing_verify_security_finding_type(req_get,
                                                       description,req_get_sc,req_get_rv,proj_key,
                                                       response_rv):
    """Tests GeneralTicketing.verify_security_finding_type"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.verify_security_finding_type(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.requests.get')
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Incorrect status code",404,None,'FOUR',None),
                          ("All expected values",200,{'name':'project name'},'KEY','project name')])
def test_generalticketing_get_project_name(req_get,
                                           description,req_get_sc,req_get_rv,proj_key,response_rv):
    """Tests GeneralTicketing.get_project_name"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_project_name(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.GeneralTicketing.cycle_through_project_keys')
def test_generalticketing_get_all_project_keys(ctpk):
    """Tests GeneralTicketing.get_all_project_keys"""
    GeneralTicketing.get_all_project_keys()
    assert ctpk.call_count == 1

@mock.patch('common.jira_functions.GeneralTicketing.get_all_projects_paginated')
def test_generalticketing_cycle_through_project_keys(gapp):
    """Tests GeneralTicketing.cycle_through_project_keys"""
    GeneralTicketing.cycle_through_project_keys()
    assert gapp.call_count == 1

@mock.patch('common.jira_functions.GeneralTicketing.cycle_through_project_keys')
@mock.patch('common.jira_functions.requests.get')
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,ctpk_cnt",
                         [("Incorrect status code",404,None,0),
                          ("All expected values",200,{'nextPage':'yes','values':[{'key':'KEY'}]},1)])
def test_generalticketing_get_all_projects_paginated(req_get,ctpk,
                                                     description,req_get_sc,req_get_rv,ctpk_cnt):
    """Tests GeneralTicketing.get_all_projects_paginated"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    GeneralTicketing.get_all_projects_paginated(0)
    assert req_get.call_count == 1
    assert ctpk.call_count == ctpk_cnt

@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,repo,tool,response_rv",
                         [("Exception: sql_sel",Exception,None,'repo','Checkmarx',None),
                          ("All expected values",None,[('some_fields_here',),],'repo','Mend OS',[('some_fields_here',),])])
def test_generalticketing_get_jira_info(sql_sel,
                                        description,sql_sel_se,sql_sel_rv,repo,tool,response_rv):
    """Tests GeneralTicketing.get_jira_info"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.get_jira_info(repo,tool)
    assert sql_sel.call_count == 1
    assert response == response_rv

@pytest.mark.parametrize("description,severity,td_boarded",
                         [("Tech debt not boarded",'Critical',0),
                          ("Tech debt boarded: Critical",'Critical',1),
                          ("Tech debt boarded: High",'High',1),
                          ("Tech debt boarded: Medium",'Medium',1),
                          ("Tech debt boarded: Low",'Low',1)])
def test_generalticketing_set_due_date(description,severity,td_boarded):
    """Tests GeneralTicketing.set_due_date"""
    GeneralTicketing.set_due_date(severity,td_boarded)

@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_rv,response_rv",
                         [('Not past due',[],False),
                          ('Past Due',['KEY-123'],True)])
def test_generalticketing_check_past_due(sql_sel,description,sql_sel_rv,response_rv):
    """Tests GeneralTicketing.check_past_due"""
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.check_past_due('KEY-123')
    assert sql_sel.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_rv,response_rv",
                         [('No exception',[],False),
                          ('Has exception',['KEY-123'],True)])
def test_generalticketing_check_exceptions(sql_sel,description,sql_sel_rv,response_rv):
    """Tests GeneralTicketing.check_exceptions"""
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.check_exceptions('KEY-123')
    assert sql_sel.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_rv,response_rv",
                         [('Is not tech debt',[],False),
                          ('Is tech debt',['KEY-123'],True)])
def test_generalticketing_check_tech_debt(sql_sel,description,sql_sel_rv,response_rv):
    """Tests GeneralTicketing.check_tech_debt"""
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.check_tech_debt('KEY-123')
    assert sql_sel.call_count == 1
    assert response == response_rv

@mock.patch('common.jira_functions.JiraDB.insert_multiple_into_table')
@mock.patch('common.jira_functions.update')
@mock.patch('common.jira_functions.GeneralTicketing.remove_epic_link')
@mock.patch('common.jira_functions.requests.post')
@mock.patch('common.jira_functions.get_ticket_transitions')
@mock.patch('common.jira_functions.jira_connection')
@pytest.mark.parametrize("description,jc_se,jc_cnt,gtt_rv,gtt_cnt,req_pst_sc,req_pst_cnt,rel_cnt,sql_upd_cnt,imit_cnt,repo,jira_issue_key,response_rv",
                         [("Cancel ticket for Four",None,1,None,0,None,0,0,1,0,'four','FOUR-123',True),
                          ("Exception on closure",Exception,1,[{'to':{'statusCategory':{'key':'Done'}},'id':'trans_id','name':'Cancelled'}],1,200,1,0,0,1,'repo','KEY-123',False),
                          ("Incorrect status code",None,1,[{'to':{'statusCategory':{'key':'Done'}},'id':'trans_id','name':'Cancelled'}],1,200,1,1,1,0,'repo','KEY-123',True),
                          ("All expected values",None,0,[{'to':{'statusCategory':{'key':'Done'}},'id':'trans_id','name':'Cancelled'}],1,201,1,1,1,0,'repo','KEY-123',True)])
def test_generalticketing_cancel_jira_ticket(jc,gtt,req_pst,rel,sql_upd,imit,description,jc_se,jc_cnt,
                                             gtt_rv,gtt_cnt,req_pst_sc,req_pst_cnt,rel_cnt,sql_upd_cnt,
                                             imit_cnt,repo,jira_issue_key,response_rv):
    """Tests GeneralTicketing.cancel_jira_ticket"""
    jc.side_effect = jc_se
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.transition_issue.return_value
    jc_mock.connection.add_comment.return_value
    gtt.return_value = gtt_rv
    resp_mock = mock.Mock(status_code=req_pst_sc)
    req_pst.return_value = resp_mock
    response = GeneralTicketing.cancel_jira_ticket(repo,jira_issue_key,'has comment')
    assert jc.call_count == jc_cnt
    assert gtt.call_count == gtt_cnt
    assert req_pst.call_count == req_pst_cnt
    assert rel.call_count == rel_cnt
    assert sql_upd.call_count == sql_upd_cnt
    assert imit.call_count == imit_cnt
    assert response == response_rv

@mock.patch('common.jira_functions.JiraDB.insert_multiple_into_table')
@mock.patch('common.jira_functions.requests.post')
@mock.patch('common.jira_functions.GeneralTicketing.get_closed_transition')
@mock.patch('common.jira_functions.jira_connection')
@pytest.mark.parametrize("description,jc_se,jc_cnt,gct_rv,gct_cnt,req_pst_sc,req_pst_cnt,imit_cnt,repo,jira_issue_key,comment,response_rv",
                         [("Close ticket for four",None,1,None,0,None,0,0,'four','FOUR-1234','has comment',True),
                          ("Exception on closure",Exception,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,1,'repo','KEY-123','has comment',False),
                          ("Incorrect status code, comment = None",None,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,0,'repo','KEY-123',None,True),
                          ("Incorrect status code, comment = 'has comment'",None,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,0,'repo','KEY-123','has comment',True),
                          ("All expected values",None,0,{'ID':'trans_id','Name':'trans_name'},1,204,1,0,'repo','KEY-123','has comment',True)])
def test_generalticketing_close_jira_ticket(jc,gct,req_pst,imit,
                                            description,jc_se,jc_cnt,gct_rv,gct_cnt,req_pst_sc,
                                            req_pst_cnt,imit_cnt,repo,jira_issue_key,comment,
                                            response_rv):
    """Tests GeneralTicketing.close_jira_ticket"""
    jc.side_effect = jc_se
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.transition_issue.return_value
    jc_mock.connection.add_comment.return_value
    gct.return_value = gct_rv
    resp_mock = mock.Mock(status_code=req_pst_sc)
    req_pst.return_value = resp_mock
    response = GeneralTicketing.close_jira_ticket(repo,jira_issue_key,comment)
    assert jc.call_count == jc_cnt
    assert gct.call_count == gct_cnt
    assert req_pst.call_count == req_pst_cnt
    assert imit.call_count == imit_cnt
    assert response == response_rv

@mock.patch('common.jira_functions.JiraDB.insert_multiple_into_table')
@mock.patch('common.jira_functions.requests.post')
@mock.patch('common.jira_functions.GeneralTicketing.get_backlog_transition')
@mock.patch('common.jira_functions.jira_connection')
@pytest.mark.parametrize("description,jc_se,jc_cnt,gbt_rv,gbt_cnt,req_pst_sc,req_pst_cnt,imit_cnt,repo,jira_issue_key,comment,response_rv",
                         [("Close ticket for four",None,1,None,0,None,0,0,'four','FOUR-1234','has comment',True),
                          ("Exception on closure",Exception,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,1,'repo','KEY-123','has comment',False),
                          ("Incorrect status code, comment = None",None,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,0,'repo','KEY-123',None,True),
                          ("Incorrect status code, comment = 'has comment'",None,1,{'ID':'trans_id','Name':'trans_name'},1,200,1,0,'repo','KEY-123','has comment',True),
                          ("All expected values",None,0,{'ID':'trans_id','Name':'trans_name'},1,204,1,0,'repo','KEY-123','has comment',True)])
def test_generalticketing_reopen_mend_license_violation_jira_ticket(jc,gbt,req_pst,imit,
                                                                    description,jc_se,jc_cnt,gbt_rv,
                                                                    gbt_cnt,req_pst_sc,req_pst_cnt,
                                                                    imit_cnt,repo,jira_issue_key,
                                                                    comment,response_rv):
    """Tests GeneralTicketing.reopen_mend_license_violation_jira_ticket"""
    jc.side_effect = jc_se
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.transition_issue.return_value
    jc_mock.connection.add_comment.return_value
    gbt.return_value = gbt_rv
    resp_mock = mock.Mock(status_code=req_pst_sc)
    req_pst.return_value = resp_mock
    response = GeneralTicketing.reopen_mend_license_violation_jira_ticket(repo,jira_issue_key,
                                                                          comment)
    assert jc.call_count == jc_cnt
    assert gbt.call_count == gbt_cnt
    assert req_pst.call_count == req_pst_cnt
    assert imit.call_count == imit_cnt
    assert response == response_rv

@mock.patch("common.jira_functions.jira_connection")
@pytest.mark.parametrize("description,repo,proj_key,summary,desc,severity,labels,due_date,epic",
                         [("Four ticket creation",'four','FOUR','summary','desc','Critical','labels','2025-12-31','FOUR-123'),
                          ("Normal ticket creation",'repo','KEY','summary','desc','High','labels','2025-12-31','KEY-123')])
def test_generalticketing_create_jira_ticket(jc,
                                             description,repo,proj_key,summary,desc,severity,
                                             labels,due_date,epic):
    """Tests GeneralTicketing.create_jira_ticket"""
    jc_mock = Mock()
    jc_mock.connection.create_issue.return_value
    jc_mock.connection.create_issue.key.return_value
    response = GeneralTicketing.create_jira_ticket(repo,proj_key,summary,desc,severity,labels,
                                                   due_date,epic)
    assert jc.call_count == 1

@mock.patch("common.jira_functions.jira_connection")
def test_generalticketing_update_jira_ticket(jc):
    """Tests GeneralTicketing.update_jira_ticket"""
    jc_mock = Mock()
    jc_mock.connection.update.return_value
    GeneralTicketing.update_jira_ticket("KEY-123","repo","description","summary")
    assert jc.call_count == 1

@mock.patch("common.jira_functions.jira_connection")
def test_generalticketing_update_jira_summary(jc):
    """Tests GeneralTicketing.update_jira_summary"""
    jc_mock = Mock()
    jc_mock.connection.update.return_value
    GeneralTicketing.update_jira_summary("KEY-123","repo","summary")
    assert jc.call_count == 1

@mock.patch("common.jira_functions.requests.post")
@mock.patch("common.jira_functions.requests.put")
@mock.patch("common.jira_functions.jira_connection")
@pytest.mark.parametrize("description,jc_se,jc_cnt,req_put_se,req_put_sc,req_put_cnt,req_pst_cnt,jira_issue_key,repo,due_date,comment,response_rv",
                         [("Four ticket creation",None,1,None,None,0,0,"FOUR-123",'four','2025-12-24','has comment',True),
                          ("Exception: Four ticket creation",Exception,1,None,None,0,0,"FOUR-123",'four','2025-12-24',None,False),
                          ("Incorrect status code",None,0,None,404,1,0,"KEY-123","repo","2025-12-24",None,False),
                          ("Exception: Normal ticket creation",None,0,Exception,None,1,0,"KEY-123","repo","2025-12-24",None,False),
                          ("Normal ticket creation",None,0,None,204,1,1,"KEY-123","repo","2025-12-24",'has comment',True)])
def test_generalticketing_update_ticket_due(jc,req_put,req_pst,
                                            description,jc_se,jc_cnt,req_put_se,req_put_sc,
                                            req_put_cnt,req_pst_cnt,jira_issue_key,repo,due_date,
                                            comment,response_rv):
    """Tests GeneralTicketing.update_ticket_due"""
    jc.side_effect = jc_se
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.transition_issue.return_value
    jc_mock.connection.add_comment.return_value
    req_put.side_effect = req_put_se
    resp_mock = mock.Mock(status_code=req_put_sc)
    req_put.return_value = resp_mock
    response = GeneralTicketing.update_ticket_due(jira_issue_key,repo,due_date,comment)
    assert jc.call_count == jc_cnt
    assert req_put.call_count == req_put_cnt
    assert req_pst.call_count == req_pst_cnt
    assert response == response_rv

@mock.patch("common.jira_functions.TheLogs.sql_exception")
@mock.patch("common.jira_functions.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,[]),
                          ("All expected values",None,[(1,'Completed',),(2,'Closed',),],0,0,0,['Completed','Closed'])])
def test_generalticketing_get_closed_states(sql_sel,ex_sql,
                                            description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                            fe_cnt,ex_cnt,response_rv):
    """Tests GeneralTicketing.get_closed_states"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.get_closed_states()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("common.jira_functions.GeneralTicketing.get_closed_states")
@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,req_get_cnt,gcs_rv,gcs_cnt,repo,jira_issue_key,response_rv",
                         [("Get transition for four ticket",None,None,0,None,0,'four','FOUR-123',{'ID':'271','Name':'Completed - No Code Updates'}),
                          ("Incorrect status code",404,None,1,None,0,'repo','KEY-123',{}),
                          ("All expected values",200,{'transitions':[{'id':'1234','name':'Resolved','to':{'statusCategory':{'name':'Done'}}}]},1,['Completed','Closed','Done','Resolved','To Close'],1,'repo','KEY-123',{'ID':'1234','Name':'Resolved'})])
def test_generalticketing_get_closed_transition(req_get,gcs,
                                                description,req_get_sc,req_get_rv,req_get_cnt,
                                                gcs_rv,gcs_cnt,repo,jira_issue_key,response_rv):
    """Tests GeneralTicketing.get_closed_transition"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    gcs.return_value = gcs_rv
    response = GeneralTicketing.get_closed_transition(repo,jira_issue_key)
    assert req_get.call_count == req_get_cnt
    assert gcs.call_count == gcs_cnt
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,req_get_cnt,repo,jira_issue_key,response_rv",
                         [("Get transition for four ticket",None,None,0,'four','FOUR-123',{'ID':'11','Name':'Backlog'}),
                          ("Incorrect status code",404,None,1,'repo','KEY-123',{}),
                          ("All expected values",200,{'transitions':[{'id':'1234','name':'Backlog','to':{'statusCategory':{'name':'To Do'}}}]},1,'repo','KEY-123',{'ID':'1234','Name':'Backlog'})])
def test_generalticketing_get_backlog_transition(req_get,
                                                description,req_get_sc,req_get_rv,req_get_cnt,
                                                repo,jira_issue_key,response_rv):
    """Tests GeneralTicketing.get_backlog_transition"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_backlog_transition(repo,jira_issue_key)
    assert req_get.call_count == req_get_cnt
    assert response == response_rv

@mock.patch('common.jira_functions.select')
def test_generalticketing_get_ticket_status(sql_sel):
    """Tests GeneralTicketing.get_ticket_status"""
    sql_sel.return_value = [('Done',),]
    response = GeneralTicketing.get_ticket_status('KEY-123')
    assert sql_sel.call_count == 1
    assert response == 'Done'

@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_rv,sql_sel_cnt,tool,jira_issue_key,response_rv",
                         [("Invalid tool",None,0,'invalid tool','KEY-123',True),
                          ("Checkmarx: No open items",[],1,'Checkmarx','KEY-123',False),
                          ("Mend OS: No open items",[('KEY-123',),],1,'Mend OS','KEY-123',True)])
def test_generalticketing_leave_ticket_open(sql_sel,
                                            description,sql_sel_rv,sql_sel_cnt,tool,jira_issue_key,
                                            response_rv):
    """Tests GeneralTicketing.leave_ticket_open"""
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.leave_ticket_open(tool,jira_issue_key)
    assert sql_sel.call_count == sql_sel_cnt
    assert response == response_rv

@mock.patch("common.jira_functions.jira_connection")
def test_generalticketing_add_comment_to_ticket(jc):
    """Tests GeneralTicketing.add_comment_to_ticket"""
    jc_mock = Mock()
    jc_mock.connection.add_comment.return_value
    GeneralTicketing.add_comment_to_ticket("KEY-123","repo","comment")
    assert jc.call_count == 1

@mock.patch('common.jira_functions.TheLogs.sql_exception')
@mock.patch('common.jira_functions.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,{'RITMTicket':None,'Standard':None,'ApprovedDate':None,'Duration':None,'Due':None}),
                          ("All expected values",None,[('RITMTicket','Standard','Approved','Duration','Due'),],0,0,0,{'RITMTicket':'RITMTicket','Standard':'Standard','ApprovedDate':'Approved','Duration':'Duration','Due':'Due'})])
def test_generalticketing_has_repo_exceptions(sql_sel,ex_sql,
                                              description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                              fe_cnt,ex_cnt,response_rv):
    """Tests GeneralTicketing.has_repo_exceptions"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = GeneralTicketing.has_repo_exceptions('repo','2024-01-01')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('common.jira_functions.GeneralTicketing.close_jira_ticket')
@mock.patch('common.jira_functions.GeneralTicketing.cancel_jira_ticket')
@mock.patch('common.jira_functions.GeneralTicketing.get_accounting_and_compliance')
@mock.patch('common.jira_functions.jira_connection')
@mock.patch('common.jira_functions.GeneralTicketing.leave_ticket_open')
@mock.patch('common.jira_functions.GeneralTicketing.get_ticket_status')
@pytest.mark.parametrize("description,gts_rv,lto_rv,lto_cnt,jc_cnt,gaac_rv,gaac_cnt,cajt_rv,cajt_cnt,cljt_rv,cljt_cnt,repo,response_rv",
                         [("Ticket is already closed","Done",None,0,0,None,0,None,0,None,0,'repo',True),
                          ("gts returns None",None,None,0,0,None,0,None,0,None,0,'repo',False),
                          ("Ticket should be left open","To Do",True,1,0,None,0,None,0,None,0,'repo',False),
                          ("Close ticket for four","To Do",False,1,1,None,0,None,0,None,0,'four',True),
                          ("gaac returns {}","To Do",False,1,0,{},1,None,0,None,0,'repo',False),
                          ("Cancel ticket in To Do status","To Do",False,1,0,{'AccountingDemo':'Passed','ComplianceDemo':'Passed','StatusCategory':'To Do'},1,True,1,None,0,'repo',True),
                          ("Close ticket in In Progress status, passing demo fields","In Progress",False,1,0,{'AccountingDemo':'Passed','ComplianceDemo':'Passed','StatusCategory':'In Progress'},1,None,0,True,1,'repo',True),
                          ("Close ticket in In Progress status, no demo fields","In Progress",False,1,0,{'AccountingDemo':None,'ComplianceDemo':None,'StatusCategory':'In Progress'},1,None,0,True,1,'repo',True),
                          ("Comment on ticket in In Progress status, demo fields are not set","In Progress",False,1,1,{'AccountingDemo':'Not Set','ComplianceDemo':'Not Set','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, demo fields in undesireable state","In Progress",False,1,1,{'AccountingDemo':'Pending','ComplianceDemo':'Pending','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo = Not Set, ComplianceDemo desireable","In Progress",False,1,1,{'AccountingDemo':'Not Set','ComplianceDemo':'Passed','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo desireable, ComplianceDemo = Not Set","In Progress",False,1,1,{'AccountingDemo':'Passed','ComplianceDemo':'Not Set','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo desireable, ComplianceDemo undesireable","In Progress",False,1,1,{'AccountingDemo':'Passed','ComplianceDemo':'Pending','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo undesireable, ComplianceDemo desireable","In Progress",False,1,1,{'AccountingDemo':'Pending','ComplianceDemo':'Passed','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo missing, ComplianceDemo undesireable","In Progress",False,1,1,{'AccountingDemo':None,'ComplianceDemo':'Pending','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo undesireable, ComplianceDemo missing","In Progress",False,1,1,{'AccountingDemo':'Pending','ComplianceDemo':None,'StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo missing, ComplianceDemo desireable","In Progress",False,1,1,{'AccountingDemo':None,'ComplianceDemo':'Passed','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo desireable, ComplianceDemo missing","In Progress",False,1,1,{'AccountingDemo':'Passed','ComplianceDemo':None,'StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo missing, ComplianceDemo = Not Set","In Progress",False,1,1,{'AccountingDemo':None,'ComplianceDemo':'Not Set','StatusCategory':'In Progress'},1,None,0,None,0,'repo',True),
                          ("Comment on ticket in In Progress status, AccountingDemo = Not Set, ComplianceDemo missing","In Progress",False,1,1,{'AccountingDemo':'Not Set','ComplianceDemo':None,'StatusCategory':'In Progress'},1,None,0,None,0,'repo',True)])
def test_generalticketing_close_or_cancel_jira_ticket(gts,lto,jc,gaac,cajt,cljt,
                                                      description,gts_rv,lto_rv,lto_cnt,jc_cnt,
                                                      gaac_rv,gaac_cnt,cajt_rv,cajt_cnt,
                                                      cljt_rv,cljt_cnt,repo,response_rv):
    """Tests GeneralTicketing.close_or_cancel_jira_ticket"""
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.transition_issue.return_value
    jc_mock.connection.add_comment.return_value
    gts.return_value = gts_rv
    lto.return_value = lto_rv
    gaac.return_value = gaac_rv
    cajt.return_value = cajt_rv
    cljt.return_value = cljt_rv
    response = GeneralTicketing.close_or_cancel_jira_ticket(repo,'KEY-123','comment','tool')
    assert gts.call_count == 1
    assert lto.call_count == lto_cnt
    assert jc.call_count == jc_cnt
    assert gaac.call_count == gaac_cnt
    assert cajt.call_count == cajt_cnt
    assert cljt.call_count == cljt_cnt
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,repo,jira_issue_key,response_rv",
                         [("Get fields for four, incorrect status code",404,None,'four','FOUR-1234',{}),
                          ("All expected values",200,{'issues':[{'fields':{'customfield_14906':{'value':'Passed'},'customfield_14908':{'value':'Passed'},'status':{'statusCategory':{'name':'In Progress'}}}}]},'repo','KEY-123',{'AccountingDemo':'Passed','ComplianceDemo':'Passed','StatusCategory':'In Progress'})])
def test_generalticketing_get_accounting_and_compliance(req_get,
                                                        description,req_get_sc,req_get_rv,
                                                        repo,jira_issue_key,response_rv):
    """Tests GeneralTicketing.get_accounting_and_compliance"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_accounting_and_compliance(repo,jira_issue_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Get child programs for four, incorrect status code",404,None,'FOUR',[]),
                          ("All expected values: no labels",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Program'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':None,'priority':{'name':'high'},'status':{'name':'status','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Program','ProgramName':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':None,'Priority':'high','State':'status','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}]),
                          ("All expected values",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Program'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':['label'],'priority':{'name':'high'},'status':{'name':'status','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Program','ProgramName':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':'label','Priority':'high','State':'status','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}])])
def test_generalticketing_get_child_programs(req_get,
                                             description,req_get_sc,req_get_rv,proj_key,
                                             response_rv):
    """Test GeneralTicketing.get_child_programs"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_child_programs(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Get child projects for four, incorrect status code",404,None,'FOUR',[]),
                          ("All expected values: no labels",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Project'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':None,'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Project','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':None,'Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}]),
                          ("All expected values",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Project'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':['label'],'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Project','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':'label','Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}])])
def test_generalticketing_get_child_projects(req_get,
                                             description,req_get_sc,req_get_rv,proj_key,
                                             response_rv):
    """Test GeneralTicketing.get_child_projects"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_child_projects(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Get child epics for four, incorrect status code",404,None,'FOUR',[]),
                          ("All expected values: no labels",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Epic'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':None,'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Epic','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':None,'Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}]),
                          ("All expected values",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Epic'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':['label'],'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',[{'IssueKey':'AS-123','IssueType':'Epic','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':'label','Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}])])
def test_generalticketing_get_child_epics(req_get,
                                             description,req_get_sc,req_get_rv,proj_key,
                                             response_rv):
    """Test GeneralTicketing.get_child_epics"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_child_epics(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,start_at,response_rv",
                         [("Get child issues for four, incorrect status code",404,None,'FOUR',0,[]),
                          ("All expected values: no labels",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Issue'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':None,'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',1,[{'IssueKey':'AS-123','IssueType':'Issue','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':None,'Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}]),
                          ("All expected values",200,{'issues':[{'key':'AS-123','fields':{'issuetype':{'name':'Issue'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':['label'],'priority':{'name':'high'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','duedate':'2025-01-01','updated':'2024-01-02T00:10:00','resolutiondate':'2024-01-02T00:00:00','customfield_14841':'2024-01-01T00:01:34','reporter':{'displayName':'reporter'}}}]},'AS',2,[{'IssueKey':'AS-123','IssueType':'Issue','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':'label','Priority':'high','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','DueDate':'2025-01-01','UpdatedDate':'2024-01-02','ResolutionDate':'2024-01-02','StartDate':'2024-01-01'}])])
def test_generalticketing_get_child_issues(req_get,
                                             description,req_get_sc,req_get_rv,proj_key,
                                             start_at,response_rv):
    """Test GeneralTicketing.get_child_issues"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_child_issues(proj_key,start_at)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,issue_key,response_rv",
                         [("Incorrect status code",404,None,'FOUR-1234',{}),
                          ("Success, no labels",200,{'issues':[{'key':'KEY-123','fields':{'issuetype':{'name':'Story'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':None,'priority':{'name':'High'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'reporter':{'displayName':'reporter'},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','updated':'2024-01-03T05:05:05','duedate':'2025-12-31T00:00:00','resolutiondate':'2024-01-02T12:31:15','customfield_14841':'2024-01-02T00:0:00'}}]},'KEY-123',{'IssueKey':'KEY-123','IssueType':'Story','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':None,'Priority':'High','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','UpdatedDate':'2024-01-03','DueDate':'2025-12-31','ResolutionDate':'2024-01-02','StartDate':'2024-01-02'}),
                          ("All expected values",200,{'issues':[{'key':'KEY-123','fields':{'issuetype':{'name':'Story'},'subtasks':[{'key':'ABC-123'}],'summary':'summary','labels':['label'],'priority':{'name':'High'},'status':{'name':'Done','statusCategory':{'name':'Done'}},'reporter':{'displayName':'reporter'},'assignee':{'displayName':'assignee'},'created':'2024-01-01T00:00:00','updated':'2024-01-03T05:05:05','duedate':'2025-12-31T00:00:00','resolutiondate':'2024-01-02T12:31:15','customfield_14841':'2024-01-02T00:0:00'}}]},'KEY-123',{'IssueKey':'KEY-123','IssueType':'Story','Summary':'summary','SubtaskCount':1,'Subtasks':['ABC-123'],'Labels':'label','Priority':'High','State':'Done','JiraStatusCategory':'Done','Reporter':'reporter','Assignee':'assignee','CreatedDate':'2024-01-01','UpdatedDate':'2024-01-03','DueDate':'2025-12-31','ResolutionDate':'2024-01-02','StartDate':'2024-01-02'})])
def test_generalticketing_get_task_json(req_get,
                                        description,req_get_sc,req_get_rv,issue_key,response_rv):
    """Tests GeneralTicketing.get_task_json"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.get_task_json(issue_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,proj_key,response_rv",
                         [("Incorrect status code",404,None,'FOUR',0),
                          ("All expected values",200,{'issueTypes':[{'name':'Security Finding'}]},'KEY',1)])
def test_generalticketing_has_sf_ticket_type(req_get,
                                             description,req_get_sc,req_get_rv,
                                             proj_key,response_rv):
    """Tests GeneralTicketing.has_sf_ticket_type"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = GeneralTicketing.has_sf_ticket_type(proj_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.JIRA")
@pytest.mark.parametrize("description,the_repo",
                         [("Test four connection","four"),
                          ("Test normal connection","repo")])
def test_jira_connection(api_call,
                         description,the_repo):
    """Tests jira_connection"""
    info = jira_connection(the_repo)
    assert api_call.call_count == 1

@mock.patch("common.jira_functions.JIDatabase.check_for_jira_issue")
@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,cfji_rv,cfji_cnt,repo,max_results,start_at,jira_project_key,response_rv",
                         [("Incorrect status code",404,None,None,0,'four',50,0,'FOUR',{'FatalCount':0,'ExceptionCount':0,'Results':{}}),
                          ("Specific repo four",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'Pen Test','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':False},1,'four',50,51,'FOUR-123',{'FatalCount':0,'ExceptionCount':0,'Results':{'CurrentEpic':'ABC-123','CurrentEpicProjectKey':'ABC','JiraProjectKey':'ABC','JiraSummary':'Pen Test','JiraPriority':'High','JiraDueDate':'2024-01-01','JiraStatus':'Done','JiraStatusCategory':'Done','TechDebt':1,'JiraCreated':'2023-01-01','JiraResolutionDate':'2023-12-31','Source':'Pen Test'}}),
                          ("All repos (non-four only)",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'Open Source','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':True},1,'All',50,0,'All',{'FatalCount':0,'ExceptionCount':0,'Results':{'CurrentEpic':'ABC-123','CurrentEpicProjectKey':'ABC','JiraProjectKey':'ABC','JiraSummary':'Open Source','JiraPriority':'High','JiraDueDate':'2024-01-01','JiraStatus':'Done','JiraStatusCategory':'Done','TechDebt':1,'JiraCreated':'2023-01-01','JiraResolutionDate':'2023-12-31','Source':'Mend OS'}}),
                          ("Single (non-four) repo only",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'SAST Finding','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':True},1,'repo',50,0,'KEY-123',{'FatalCount':0,'ExceptionCount':0,'Results':{'CurrentEpic':'ABC-123','CurrentEpicProjectKey':'ABC','JiraProjectKey':'ABC','JiraSummary':'SAST Finding','JiraPriority':'High','JiraDueDate':'2024-01-01','JiraStatus':'Done','JiraStatusCategory':'Done','TechDebt':1,'JiraCreated':'2023-01-01','JiraResolutionDate':'2023-12-31','Source':'Checkmarx'}})])
def test_get_open_jira_issues(req_get,cfji,
                              description,req_get_sc,req_get_rv,cfji_rv,cfji_cnt,
                              repo,max_results,start_at,jira_project_key,response_rv):
    """Tests get_open_jira_issues"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    cfji.return_value = cfji_rv
    get_open_jira_issues(repo,max_results,start_at,jira_project_key)
    assert req_get.call_count == 1
    assert cfji.call_count == cfji_cnt

@mock.patch("common.jira_functions.TheLogs.function_exception")
@mock.patch("common.jira_functions.update_multiple_in_table")
@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,req_get_cnt,umit_sc,umit_rv,umit_cnt,ex_func_cnt,fe_cnt,ex_cnt,repo,current_epic,current_epic_project_key,jira_issue_key,jira_project_key,response_rv",
                         [("Check four issue",None,None,0,None,None,0,0,0,0,'four','FOUR-123','FOUR','FOUR-1234','FOUR',0),
                          ("Incorrect status code",404,None,1,None,None,0,0,0,0,'repo','KEY-123','KEY','KEY-1234','KEY',0),
                          ("All expected values",200,{'issues':[{'key':'ABC-123','fields':{'parent':{'key':'ABC-100'}}}]},1,None,1,1,0,0,0,'repo','KEY-123','KEY','KEY-1234','KEY',1),
                          ("Exception: umit",200,{'issues':[{'key':'ABC-123','fields':{'parent':{'key':'ABC-100'}}}]},1,Exception,None,1,1,0,1,'repo',None,None,'KEY-1234','KEY',0)])
def test_check_moved_issue(req_get,umit,ex_func,
                           description,req_get_sc,req_get_rv,req_get_cnt,umit_sc,umit_rv,umit_cnt,
                           ex_func_cnt,fe_cnt,ex_cnt,repo,current_epic,current_epic_project_key,
                           jira_issue_key,jira_project_key,response_rv):
    """Tests check_moved_issue"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    umit.status_code = umit_sc
    umit.return_value = umit_rv
    response = check_moved_issue(repo,current_epic,current_epic_project_key,jira_issue_key,jira_project_key)
    assert req_get.call_count == req_get_cnt
    assert umit.call_count == umit_cnt
    assert ex_func.call_count == ex_func_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("common.jira_functions.JIDatabase.check_for_jira_issue")
@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,cfji_rv,cfji_cnt,repo,max_results,start_at,tool",
                         [("Incorrect status code",404,None,None,0,'four',50,0,'Checkmarx'),
                          ("Specific repo four",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'Pen Test','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':False},1,'four',50,51,'Checkmarx'),
                          ("All repos (non-four only)",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'Open Source','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':True},1,'All',50,0,'Mend OS'),
                          ("Single (non-four) repo only",200,{'startAt':0,'total':1,'issues':[{'key':'ABC-123','fields':{'customfield_10035':'2024-01-01','statuscategorychangedate':'2023-12-31T09:13:00','resolutiondate':'2023-12-31T09:13:00','created':'2023-01-01T00:00:00','priority':{'name':'High'},'duedate':'2024-01-01','parent':{'key':'ABC-100'},'summary':'SAST Finding','status':{'name':'Done','statusCategory':{'name':'Done'}},'labels':['tech_debt']}}]},{'Results':True},1,'repo',50,0,'Mend OS')])
def test_get_open_tool_issues(req_get,cfji,
                              description,req_get_sc,req_get_rv,cfji_rv,cfji_cnt,
                              repo,max_results,start_at,tool):
    """Tests get_open_tool_issues"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    cfji.return_value = cfji_rv
    get_open_tool_issues(repo,max_results,start_at,tool)
    assert req_get.call_count == 1
    assert cfji.call_count == cfji_cnt

@mock.patch("common.jira_functions.requests.get")
@pytest.mark.parametrize("description,req_get_sc,req_get_rv,repo,jira_issue_key,response_rv",
                         [("Incorrect status code",404,None,'four','FOUR-123',None),
                          ("All expected values",200,{'transitions':['list_of_dicts']},'repo','KEY-123',['list_of_dicts'])])
def test_get_ticket_transitions(req_get,
                                description,req_get_sc,req_get_rv,repo,jira_issue_key,response_rv):
    """Tests get_ticket_transitions"""
    resp_mock = mock.Mock(status_code=req_get_sc)
    resp_mock.json.return_value = req_get_rv
    req_get.return_value = resp_mock
    response = get_ticket_transitions(repo,jira_issue_key)
    assert req_get.call_count == 1
    assert response == response_rv

@mock.patch("common.jira_functions.jira_connection")
def test_update_jira_description(jc):
    """Tests update_jira_description"""
    jc_mock = Mock()
    jc_mock.connection.issue.return_value
    jc_mock.connection.update.return_value
    update_jira_description("KEY-123","repo","new_description")
    assert jc.call_count == 1

if __name__ == '__main__':
    unittest.main()
