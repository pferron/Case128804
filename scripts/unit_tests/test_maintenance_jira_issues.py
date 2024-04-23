'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from maintenance_jira_issues import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch("maintenance_jira_issues.update_all_jira_issues")
@mock.patch("maintenance_jira_issues.General.cmd_processor")
@pytest.mark.parametrize("description,cmd_mock_rv,testargs",
                         [("Run function, no args",[{'function': 'update_all_jira_issues'}],[r'c:\AppSec\scripts\\maintenance_jira_issues.py','update_all_jira_issues']),
                          ("Run function, with args",[{'function': 'update_all_jira_issues','args':'repo'}],[r'c:\AppSec\scripts\\maintenance_jira_issues.py','update_all_jira_issues'])])
def test_main_with_args(cmd_mock,run_mock,
                        description,cmd_mock_rv,testargs):
    '''Tests main'''
    cmd_mock.return_value = cmd_mock_rv
    # arg_cnt = 2
    with mock.patch.object(sys,"argv",testargs):
        main()
        cmd_mock.assert_called_once()
        run_mock.assert_called_once()

@mock.patch('maintenance_jira_issues.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('maintenance_jira_issues.TheLogs.process_exception_count_only')
@mock.patch('maintenance_jira_issues.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

def test_scrvar_update_exception_info():
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info({'FatalCount':5,'ExceptionCount':1})
    assert ScrVar.fe_cnt == 5
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.ScrVar.timed_script_teardown")
@mock.patch("maintenance_jira_issues.add_missing_repos")
@mock.patch("maintenance_jira_issues.reset_ticket_titles")
@mock.patch("maintenance_jira_issues.add_epic_to_closed")
@mock.patch("maintenance_jira_issues.remove_epic_from_cancelled")
@mock.patch("maintenance_jira_issues.cycle_through_all_jira_issues")
@mock.patch("maintenance_jira_issues.check_all_for_moved_tickets")
@mock.patch("maintenance_jira_issues.ScrVar.timed_script_setup")
@mock.patch("maintenance_jira_issues.ScrVar.reset_exception_counts")
@pytest.mark.parametrize("description,cafmt_cnt,run,fe_cnt,ex_cnt",
                         [("Skip cafmt",0,0,0,0),
                          ("Run cafmt",1,1,0,0)])
def test_update_all_jira_issues(rec,tss,cafmt,ctaji,refc,aetc,rtt,amr,tst,
                                description,cafmt_cnt,run,fe_cnt,ex_cnt):
    """Tests update_all_jira_issues"""
    response = update_all_jira_issues(run)
    assert rec.call_count == 1
    assert tss.call_count == 1
    assert cafmt.call_count == cafmt_cnt
    assert ctaji.call_count == 1
    assert refc.call_count == 1
    assert aetc.call_count == 1
    assert rtt.call_count == 1
    assert amr.call_count == 1
    assert tst.call_count == 1
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.reset_ticket_titles")
@mock.patch("maintenance_jira_issues.add_missing_repos")
@mock.patch("maintenance_jira_issues.add_epic_to_closed")
@mock.patch("maintenance_jira_issues.remove_epic_from_cancelled")
@mock.patch("maintenance_jira_issues.cycle_through_all_jira_issues")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_project_key")
@mock.patch("maintenance_jira_issues.ScrVar.reset_exception_counts")
@pytest.mark.parametrize("description,gpk_rv,ctaji_cnt,refc_cnt,aetc_cnt,amr_cnt,rtt_cnt,fe_cnt,ex_cnt,repo",
                         [("gpk_rv = []",[],0,0,0,0,0,0,0,'four'),
                          ("All expected values, repo = four",['FOUR'],1,0,0,1,1,0,0,'four'),
                          ("All expected values, repo != four",['KEY'],1,1,1,1,1,0,0,'repo')])
def test_update_jira_project_tickets(rec,gpk,uei,ctaji,refc,aetc,amr,rtt,
                                     description,gpk_rv,ctaji_cnt,refc_cnt,aetc_cnt,amr_cnt,rtt_cnt,fe_cnt,ex_cnt,repo):
    """Tests update_jira_project_tickets"""
    gpk.return_value = {'FatalCount':0,'ExceptionCount':0,'Results':gpk_rv}
    response = update_jira_project_tickets(repo)
    assert rec.call_count == 1
    assert gpk.call_count == 1
    assert uei.call_count == 1
    assert ctaji.call_count == ctaji_cnt
    assert refc.call_count == refc_cnt
    assert aetc.call_count == aetc_cnt
    assert amr.call_count == amr_cnt
    assert rtt.call_count == rtt_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.cycle_through_all_jira_issues")
@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.DBQueries.insert_multiple")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.get_open_jira_issues")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,log_hl_cnt,goji_se,goji_rv,ex_func_cnt,im_se,im_cnt,um_se,um_cnt,ctaji_cnt,log_ln_cnt,fe_cnt,ex_cnt,repo,start_at,proj_key",
                         [('Exception: goji',1,Exception,None,1,None,0,None,0,0,0,1,0,'All',0,'KEY'),
                          ('Exception: im',1,None,{'Results':{'startAt':0,'total':10,'issueCount':1,'issues':['this is a list of dicts'],'updates':['this is a list of dicts']}},1,Exception,1,None,1,1,0,0,1,'repo',0,'KEY'),
                          ('Exception: um',1,None,{'Results':{'startAt':0,'total':10,'issueCount':1,'issues':['this is a list of dicts'],'updates':['this is a list of dicts']}},1,None,1,Exception,1,1,0,0,1,'repo',0,'KEY'),
                          ('All expected values',1,None,{'Results':{'startAt':0,'total':1,'issueCount':1,'issues':['this is a list of dicts'],'updates':['this is a list of dicts']}},0,None,1,None,1,1,2,0,0,'All',0,'KEY')])
def test_cycle_through_all_jira_issues(log_hl,goji,ex_func,im,um,ctaji,log_ln,
                                       description,log_hl_cnt,goji_se,goji_rv,ex_func_cnt,im_se,
                                       im_cnt,um_se,um_cnt,ctaji_cnt,log_ln_cnt,
                                       fe_cnt,ex_cnt,repo,start_at,proj_key):
    """Tests cycle_through_all_jira_issues"""
    goji.side_effect = goji_se
    goji.return_value = goji_rv
    im.side_effect = im_se
    um.side_effect = um_se
    cycle_through_all_jira_issues(repo,50,start_at,proj_key)
    assert log_hl.call_count == log_hl_cnt
    assert goji.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert im.call_count == im_cnt
    assert um.call_count == um_cnt
    assert ctaji.call_count == ctaji_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.GeneralTicketing.remove_epic_link")
@mock.patch("maintenance_jira_issues.JIDatabase.get_ticket_current_epic")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_cancelled_tickets")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,gct_rv,uei_cnt,gtce_rv,gtce_cnt,rel_se,rel_rv,rel_cnt,ex_func_cnt,um_se,um_cnt,fe_cnt,ex_cnt,repo,response_rv",
                         [("gct_rv = {'Results':[]}",[],1,None,0,None,None,0,0,None,0,0,0,'All',0),
                          ("gtce_rv = {'Results':[]}",['KEY-123'],2,[],1,None,None,0,0,None,0,0,0,'repo',0),
                          ("All expected values",['KEY-123'],2,{'Epic':'KEY-123','ProjectKey':'KEY'},1,None,True,1,0,None,1,0,0,'repo',1),
                          ("Exception: rel",['KEY-123'],2,{'Epic':'KEY-123','ProjectKey':'KEY'},1,Exception,None,1,1,None,0,0,1,'repo',0),
                          ("Exception: um",['KEY-123'],2,{'Epic':'KEY-123','ProjectKey':'KEY'},1,None,True,1,1,Exception,1,0,1,'repo',0)])
def test_remove_epic_from_cancelled(log_hl,gct,uei,gtce,rel,ex_func,um,log_ln,
                                    description,gct_rv,uei_cnt,gtce_rv,gtce_cnt,rel_se,rel_rv,
                                    rel_cnt,ex_func_cnt,um_se,um_cnt,fe_cnt,ex_cnt,repo,
                                    response_rv):
    """Tests remove_epic_from_cancelled"""
    gct.return_value = {'Results':gct_rv}
    gtce.return_value = {'Results':gtce_rv}
    rel.side_effect = rel_se
    rel.return_value = rel_rv
    um.side_effect = um_se
    response = remove_epic_from_cancelled(repo)
    assert log_hl.call_count == 1
    assert gct.call_count == 1
    assert uei.call_count == uei_cnt
    assert gtce.call_count == gtce_cnt
    assert rel.call_count == rel_cnt
    assert ex_func.call_count == ex_func_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == 1
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.GeneralTicketing.add_epic_link")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_original_epic")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,goe_rv,ael_se,ael_rv,ael_cnt,ex_func_cnt,um_se,um_cnt,fe_cnt,ex_cnt,repo,response_rv",
                         [("goe_rv = []",[],None,None,0,0,None,0,0,0,'All',0),
                          ("All expected values",[{'OriginalEpic':'KEY-321','JiraIssueKey':'KEY-123'}],None,True,1,0,None,1,0,0,'repo',1),
                          ("Exception: ael",[{'OriginalEpic':'KEY-321','JiraIssueKey':'KEY-123'}],Exception,None,1,1,None,0,0,1,'repo',0),
                          ("Exception: um",[{'OriginalEpic':'KEY-321','JiraIssueKey':'KEY-123'}],None,True,1,1,Exception,1,0,1,'repo',0)])
def test_add_epic_to_closed(log_hl,goe,uei,ael,ex_func,um,log_ln,
                            description,goe_rv,ael_se,ael_rv,ael_cnt,ex_func_cnt,um_se,um_cnt,
                            fe_cnt,ex_cnt,repo,response_rv):
    """Tests add_epic_to_closed"""
    goe.return_value = {'Results':goe_rv}
    ael.side_effect = ael_se
    ael.return_value = ael_rv
    um.side_effect = um_se
    response = add_epic_to_closed(repo)
    assert log_hl.call_count == 1
    assert goe.call_count == 1
    assert uei.call_count == 1
    assert ael.call_count == ael_cnt
    assert ex_func.call_count == ex_func_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == 1
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_tickets_with_missing_repos")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,gtwmr_rv,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("gtwmr_rv = []",[],None,0,0,0,0),
                          ("All expected values",[{'SET':{'Repo':'repo'},'WHERE_EQUAL':{'JiraIssueKey':'KEY-123'}}],None,1,0,0,0),
                          ("Exception: um",[{'SET':{'Repo':'repo'},'WHERE_EQUAL':{'JiraIssueKey':'KEY-123'}}],Exception,1,1,0,1)])
def test_add_missing_repos(log_hl,gtwmr,uei,um,ex_func,log_ln,
                           description,gtwmr_rv,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt):
    """Tests add_missing_repos"""
    gtwmr.return_value = {'Results':gtwmr_rv}
    um.side_effect = um_se
    add_missing_repos()
    assert log_hl.call_count == 1
    assert gtwmr.call_count == 1
    assert uei.call_count == 1
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.update_tool_tickets")
@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.check_moved_issue")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_all_jira_issues")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,gaji_rv,cmi_cnt",
                         [("gaji_rv = []",[],0),
                          ("All expected values",[('KEY-1','KEY-2','KEY-3','KEY-4','KEY-5')],1)])
def test_check_all_for_moved_tickets(log_hl,gaji,uei,cmi,log_ln,utt,
                                     description,gaji_rv,cmi_cnt):
    """Tests check_all_for_moved_tickets"""
    gaji.return_value = {'Results':gaji_rv}
    check_all_for_moved_tickets()
    assert log_hl.call_count == 1
    assert gaji.call_count == 1
    assert uei.call_count == 1
    assert cmi.call_count == cmi_cnt
    assert log_ln.call_count == 1
    assert utt.call_count == 2

@mock.patch("maintenance_jira_issues.update_tool_tickets")
@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.check_moved_issue")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.get_repo_jira_issues")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,grji_rv,cmi_cnt",
                         [("grji_rv = []",[],0),
                          ("All expected values",[('KEY-1','KEY-2','KEY-3','KEY-4','KEY-5')],1)])
def test_check_repo_for_moved_tickets(log_hl,grji,uei,cmi,log_ln,utt,
                                     description,grji_rv,cmi_cnt):
    """Tests check_repo_for_moved_tickets"""
    grji.return_value = {'Results':grji_rv}
    check_repo_for_moved_tickets('repo')
    assert log_hl.call_count == 1
    assert grji.call_count == 1
    assert uei.call_count == 1
    assert cmi.call_count == cmi_cnt
    assert log_ln.call_count == 1
    assert utt.call_count == 2

@mock.patch("maintenance_jira_issues.add_epic_to_closed")
@mock.patch("maintenance_jira_issues.remove_epic_from_cancelled")
@mock.patch("maintenance_jira_issues.JIDatabase.update_missing_ji_data")
@mock.patch("maintenance_jira_issues.cycle_through_tool_tickets")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.update_moved_tool_tickets")
@pytest.mark.parametrize("description,refc_cnt,aetc_cnt,repo",
                         [("All expected values, repo = four",0,0,'four'),
                          ("All expected values, repo = not four",1,1,'repo')])
def test_update_jiraissues_for_tool_and_repo(umtt,uei,cttt,umjd,refc,aetc,
                                             description,refc_cnt,aetc_cnt,repo):
    """Tests update_jiraissues_for_tool_and_repo"""
    update_jiraissues_for_tool_and_repo(repo,'tool')
    assert umtt.call_count == 1
    assert uei.call_count == 2
    assert cttt.call_count == 1
    assert umjd.call_count == 1
    assert refc.call_count == refc_cnt
    assert aetc.call_count == aetc_cnt

@mock.patch("maintenance_jira_issues.cycle_through_tool_tickets")
@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.DBQueries.insert_multiple")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.get_open_tool_issues")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,log_hl_cnt,goti_se,goti_rv,ex_func_cnt,im_se,im_cnt,um_se,um_cnt,log_ln_cnt,cttt_cnt,fe_cnt,ex_cnt,repo,start_at",
                         [("goti_rv = {}",1,None,{},0,None,0,None,0,2,1,0,0,'All',0),
                          ("Exception: goti",1,Exception,None,1,None,0,None,0,0,0,1,0,'repo',0),
                          ("All expected values",1,None,{'startAt':0,'total':3,'issueCount':1,'issues':['list of dicts'],'updates':['list of dicts']},0,None,1,None,1,0,1,0,0,'four',0),
                          ("Exception: im",0,None,{'startAt':0,'total':1,'issueCount':1,'issues':['list of dicts'],'updates':['list of dicts']},1,Exception,1,None,1,2,0,0,1,'four',1),
                          ("Exception: um",0,None,{'startAt':0,'total':1,'issueCount':1,'issues':['list of dicts'],'updates':['list of dicts']},1,None,1,Exception,1,2,0,0,1,'repo',1)])
def test_cycle_through_tool_tickets(log_hl,goti,ex_func,im,um,log_ln,cttt,
                                    description,log_hl_cnt,goti_se,goti_rv,ex_func_cnt,im_se,im_cnt,
                                    um_se,um_cnt,log_ln_cnt,cttt_cnt,fe_cnt,ex_cnt,repo,start_at):
    """Tests cycle_through_tool_tickets"""
    goti.side_effect = goti_se
    goti.return_value = {'Results':goti_rv}
    im.side_effect = im_se
    um.side_effect = um_se
    cycle_through_tool_tickets(repo,50,start_at,'tool')
    assert log_hl.call_count == log_hl_cnt
    assert goti.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert im.call_count == im_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == log_ln_cnt
    assert cttt.call_count == cttt_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.DBQueries.update_multiple")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.tool_tickets_to_update")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,log_ln_cnt,ex_func_cnt,tttu_rv,tttu_cnt,uei_cnt,um_se,um_cnt,fe_cnt,ex_cnt,tool",
                         [("Exception: tool is invalid",1,1,None,0,0,None,0,1,0,'invalid tool'),
                          ("All expected values",1,0,[{'NewTicket':'ABC-123','OldTicket':'KEY-123'}],1,1,None,1,0,0,'Checkmarx'),
                          ("Exception: um",0,1,[{'NewTicket':'ABC-123','OldTicket':'KEY-123'}],1,1,Exception,1,1,0,'Mend OS')])
def test_update_tool_tickets(log_hl,log_ln,ex_func,tttu,uei,um,
                             description,log_ln_cnt,ex_func_cnt,tttu_rv,tttu_cnt,uei_cnt,
                             um_se,um_cnt,fe_cnt,ex_cnt,tool):
    """Tests update_tool_tickets"""
    tttu.return_value = {'Results':tttu_rv}
    um.side_effect = um_se
    update_tool_tickets(tool)
    assert log_hl.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ex_func.call_count == ex_func_cnt
    assert tttu.call_count == tttu_cnt
    assert uei.call_count == uei_cnt
    assert um.call_count == um_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.reset_titles_to_default")
def test_reset_ticket_titles(rttd):
    """Tests reset_ticket_titles"""
    reset_ticket_titles('repo')
    assert rttd.call_count == 2

@mock.patch("maintenance_jira_issues.TheLogs.log_info")
@mock.patch("maintenance_jira_issues.JIDatabase.update_jirasummary")
@mock.patch("maintenance_jira_issues.TheLogs.function_exception")
@mock.patch("maintenance_jira_issues.GeneralTicketing.update_jira_summary")
@mock.patch("maintenance_jira_issues.create_title")
@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.JIDatabase.ticket_titles_to_fix")
@mock.patch("maintenance_jira_issues.TheLogs.log_headline")
@pytest.mark.parametrize("description,tttf_rv,ct_rv,ct_cnt,ujs_se,ujs_cnt,ex_func_cnt,uj_se,uj_cnt,fe_cnt,ex_cnt",
                         [("tttf_rv = []",[],None,0,None,0,0,None,0,0,0),
                          ("All expected values",[{'Repo':'repo','Ticket':'KEY-123'}],'title',1,None,1,0,None,1,0,0),
                          ("Exception: ujs",[{'Repo':'repo','Ticket':'KEY-123'}],'title',1,Exception,1,1,None,0,0,1),
                          ("Exception: uj",[{'Repo':'repo','Ticket':'KEY-123'}],'title',1,None,1,1,Exception,1,0,1)])
def test_reset_titles_to_default(log_hl,tttf,uei,ct,ujs,ex_func,uj,log_ln,
                                 description,tttf_rv,ct_rv,ct_cnt,ujs_se,ujs_cnt,ex_func_cnt,
                                 uj_se,uj_cnt,fe_cnt,ex_cnt):
    """Tests reset_titles_to_default"""
    tttf.return_value = {'Results':tttf_rv}
    ct.return_value = ct_rv
    ujs.side_effect = ujs_se
    uj.side_effect = uj_se
    reset_titles_to_default('repo','source')
    assert log_hl.call_count == 1
    assert uei.call_count == 1
    assert ct.call_count == ct_cnt
    assert ujs.call_count == ujs_cnt
    assert ex_func.call_count == ex_func_cnt
    assert uj.call_count == uj_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("maintenance_jira_issues.ScrVar.update_exception_info")
@mock.patch("maintenance_jira_issues.GeneralTicketing.get_ticket_due_date")
@mock.patch("maintenance_jira_issues.TheLogs.sql_exception")
@mock.patch("maintenance_jira_issues.DBQueries.select")
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,gtdd_rv,gtdd_cnt,uei_cnt,fe_cnt,ex_cnt,ticket,source,response_rv",
                         [("Exception: sql",Exception,None,1,None,0,0,0,1,'KEY-123','Checkmarx',None),
                          ("All expected values, source = Mend OS, Vulnerability title testing",None,[('repo','Vulnerability','group_id')],0,None,0,0,0,0,'KEY-123','Mend OS','Open Source Vulnerability: group_id - repo'),
                          ("All expected values, source = Mend OS, License Violation title testing",None,[('repo','License Violation','group_id')],0,None,0,0,0,0,'KEY-123','Mend OS','Unapproved Open Source License Use: group_id - repo'),
                          ("All expected values, source = Checkmarx, using PROG ticket",None,[('repo','cx_query')],0,'2024-12-31',1,1,0,0,'PROG-123','Checkmarx','SAST Finding: cx_query - repo - 2024-12-31')])
def test_create_title(sql_sel,ex_sql,gtdd,uei,
                      description,sql_sel_se,sql_sel_rv,ex_sql_cnt,gtdd_rv,gtdd_cnt,uei_cnt,
                      fe_cnt,ex_cnt,ticket,source,response_rv):
    """Tests create_title"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    gtdd.return_value = {'Results':gtdd_rv}
    response = create_title(ticket,source)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert gtdd.call_count == gtdd_cnt
    assert uei.call_count == uei_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
