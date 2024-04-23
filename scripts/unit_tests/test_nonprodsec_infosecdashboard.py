'''Unit tests for the nonprodsec_infosecdashboard script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from nonprodsec_infosecdashboard import *

@mock.patch('nonprodsec_infosecdashboard.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('nonprodsec_infosecdashboard.Misc.end_timer')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('nonprodsec_infosecdashboard.ScrVar.timed_script_teardown')
@mock.patch('nonprodsec_infosecdashboard.update_tickets_and_tasks')
@mock.patch('nonprodsec_infosecdashboard.update_projects_and_epics')
@mock.patch('nonprodsec_infosecdashboard.update_programs')
@mock.patch('nonprodsec_infosecdashboard.ScrVar.timed_script_setup')
def test_infosecdashboard_updates(tss,up,upae,utat,tst):
    """Tests infosecdashboard_updates"""
    infosecdashboard_updates()
    assert tss.call_count == 1
    assert up.call_count == 1
    assert upae.call_count == 1
    assert utat.call_count == 1
    assert tst.call_count == 1

@mock.patch('nonprodsec_infosecdashboard.DBQueries.insert_multiple')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_info')
@mock.patch('nonprodsec_infosecdashboard.DBQueries.update_multiple')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_program_exists')
@mock.patch('nonprodsec_infosecdashboard.GeneralTicketing.get_child_programs')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.function_exception')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.get_projects')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,gcp_se,gcp_rv,gcp_cnt,cipe_se,cipe_rv,cipe_cnt,um_se,um_rv,um_cnt,log_ln_cnt,im_se,im_rv,im_cnt,fe_cnt,ex_cnt",
                         [('All values expected, cipe = True',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],0,None,[{'IssueKey':'tkt','IssueType':'type','ProgramName':'summary','SubtaskCount':1,'Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,1,1,4,None,1,1,0,0),
                          ('All values expected, cipe = False',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],0,None,[{'IssueKey':'tkt','IssueType':'type','ProgramName':'summary','SubtaskCount':1,'Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,False,1,None,1,1,4,None,1,1,0,0),
                          ('Exception: gp',1,Exception,None,1,None,None,0,None,None,0,None,0,0,0,None,0,0,1,0),
                          ('Exception: gcp',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,Exception,None,1,None,None,0,None,None,0,2,None,None,0,0,1),
                          ('Exception: cipe',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[{'IssueKey':'tkt','IssueType':'type','ProgramName':'summary','SubtaskCount':1,'Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,Exception,None,1,None,1,1,4,None,1,1,0,1),
                          ('Exception: um',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[{'IssueKey':'tkt','IssueType':'type','ProgramName':'summary','SubtaskCount':1,'Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,Exception,None,1,4,None,1,1,0,1),
                          ('Exception: im',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[{'IssueKey':'tkt','IssueType':'type','ProgramName':'summary','SubtaskCount':1,'Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,1,1,4,Exception,None,1,0,1)])
def test_update_programs(log_hl,gp,ex_func,gcp,cipe,um,log_ln,im,
                         description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,gcp_se,gcp_rv,gcp_cnt,
                         cipe_se,cipe_rv,cipe_cnt,um_se,um_rv,um_cnt,log_ln_cnt,im_se,im_rv,im_cnt,
                         fe_cnt,ex_cnt):
    """Tests update_programs"""
    gp.side_effect = gp_se
    gp.return_value = gp_rv
    gcp.side_effect = gcp_se
    gcp.return_value = gcp_rv
    cipe.side_effect = cipe_se
    cipe.return_value = cipe_rv
    um.side_effect = um_se
    um.return_value = um_rv
    im.side_effect = im_se
    im.return_value = im_rv
    update_programs()
    assert log_hl.call_count == log_hl_cnt
    assert gp.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gcp.call_count == gcp_cnt
    assert cipe.call_count == cipe_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == log_ln_cnt
    assert im.call_count == im_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_infosecdashboard.DBQueries.update_multiple')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_info')
@mock.patch('nonprodsec_infosecdashboard.DBQueries.insert_multiple')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_epic_exists')
@mock.patch('nonprodsec_infosecdashboard.GeneralTicketing.get_child_epics')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_project_exists')
@mock.patch('nonprodsec_infosecdashboard.GeneralTicketing.get_child_projects')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.get_programs_for_project')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.function_exception')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.get_projects')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,gpfp_se,gpfp_rv,gpfp_cnt,gcp_se,gcp_rv,gcp_cnt,cipe_se,cipe_rv,cipe_cnt,gce_se,gce_rv,gce_cnt,ciee_se,ciee_rv,ciee_cnt,im_se,im_rv,im_cnt,log_ln_cnt,um_se,um_rv,um_cnt,fe_cnt,ex_cnt",
                         [('All expected values, cipe = True, ciee = True',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],0,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,0,2,8,None,1,2,0,0),
                          ('All expected values, cipe = False, ciee = False',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],0,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,False,1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,False,1,None,0,2,8,None,1,2,0,0),
                          ('Exception: gp',1,Exception,None,1,None,None,0,None,None,0,None,None,0,None,None,0,None,None,0,None,0,0,0,None,None,0,1,0),
                          ('Exception: gpfp',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,Exception,None,1,None,None,0,None,None,0,None,None,0,None,None,0,None,None,0,4,None,None,0,0,1),
                          ('Exception: gcp',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[('ProgramKey','ProgramName')],1,Exception,None,1,None,None,0,None,None,0,None,None,0,None,1,2,8,None,1,2,0,1),
                          ('Exception: cipe',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,Exception,None,1,None,None,0,None,None,0,None,1,2,8,None,1,2,0,1),
                          ('Exception: gce',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,Exception,None,1,None,None,0,None,1,2,8,None,1,2,0,1),
                          ('Exception: ciee',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],1,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,Exception,None,1,None,1,2,8,None,1,2,0,1),
                          ('Exception: im',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],2,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,False,1,Exception,None,2,8,None,1,2,0,2),
                          ('Exception: um',3,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],2,None,[('ProgramKey','ProgramName')],1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,True,1,None,[{'IssueKey':'i_key','IssueType':'i_type','Summary':'summary','SubtaskCount':'subtask_cnt','Subtasks':'subtasks','Labels':'labels','Priority':'priority','State':'state','JiraStatusCategory':'stat_cat','Reporter':'reporter','Assignee':'assignee','CreatedDate':'d_created','DueDate':'d_due','UpdatedDate':'d_updated','ResolutionDate':'d_resolution','StartDate':'d_start'}],1,None,False,1,None,1,2,8,Exception,1,2,0,2)])
def test_update_projects_and_epics(log_hl,gp,ex_func,gpfp,gcp,cipe,gce,ciee,im,log_ln,um,
                                   description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,gpfp_se,gpfp_rv,
                                   gpfp_cnt,gcp_se,gcp_rv,gcp_cnt,cipe_se,cipe_rv,cipe_cnt,gce_se,
                                   gce_rv,gce_cnt,ciee_se,ciee_rv,ciee_cnt,im_se,im_rv,im_cnt,
                                   log_ln_cnt,um_se,um_rv,um_cnt,fe_cnt,ex_cnt):
    """Tests update_projects_and_epics"""
    gp.side_effect = gp_se
    gp.return_value = gp_rv
    gpfp.side_effect = gpfp_se
    gpfp.return_value = gpfp_rv
    gcp.side_effect = gcp_se
    gcp.return_value = gcp_rv
    cipe.side_effect = cipe_se
    cipe.return_value = cipe_rv
    gce.side_effect = gce_se
    gce.return_value = gce_rv
    ciee.side_effect = ciee_se
    ciee.return_value = ciee_rv
    im.side_effect = im_se
    im.return_value = im_rv
    um.side_effect = um_se
    um.return_value = um_rv
    update_projects_and_epics()
    assert log_hl.call_count == log_hl_cnt
    assert gp.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gpfp.call_count == gpfp_cnt
    assert gcp.call_count == gcp_cnt
    assert cipe.call_count == cipe_cnt
    assert gce.call_count == gce_cnt
    assert ciee.call_count == ciee_cnt
    assert im.call_count == im_cnt
    assert log_ln.call_count == log_ln_cnt
    assert um.call_count == um_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_infosecdashboard.DBQueries.insert_multiple')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_info')
@mock.patch('nonprodsec_infosecdashboard.get_jira_issues_for_epic')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.get_epics_for_project')
@mock.patch('nonprodsec_infosecdashboard.DBQueries.update_multiple')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_table_exists')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.function_exception')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.get_projects')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,cite_se,cite_rv,cite_cnt,um_se,um_rv,um_cnt,gefp_se,gefp_rv,gefp_cnt,gjife_se,gjife_cnt,log_ln_cnt,im_se,im_rv,im_cnt,fe_cnt,ex_cnt",
                         [('All expected values, cite = True',3,None,[('JiraProjectKey','JiraProjectName',None)],0,None,True,1,None,1,4,None,[('KEY-123')],1,None,1,8,None,1,2,0,0),
                          ('All expected values, cite = False',2,None,[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')],0,None,False,1,None,1,3,None,None,0,None,0,8,None,1,2,0,0),
                          ('Exception: gp',1,Exception,None,1,None,None,0,None,None,0,None,None,0,None,0,0,None,None,0,1,0),
                          ('Exception: cite',2,None,[('JiraProjectKey','JiraProjectName',None)],1,Exception,None,1,None,None,0,None,None,0,None,0,4,None,None,0,0,1),
                          ('Exception: um, cite = False',2,None,[('JiraProjectKey','JiraProjectName',None)],3,None,False,1,Exception,1,3,None,None,0,None,0,8,None,1,2,0,3),
                          ('Exception: um, cite = True',2,None,[('JiraProjectKey','JiraProjectName',None)],1,None,True,1,Exception,1,1,None,None,0,None,0,4,None,None,0,0,1),
                          ('Exception: gefp',3,None,[('JiraProjectKey','JiraProjectName',None)],1,None,True,1,None,1,1,Exception,None,1,None,0,4,None,None,0,0,1),
                          ('Exception: gjife',3,None,[('JiraProjectKey','JiraProjectName',None)],1,None,True,1,None,1,4,None,[('KEY-123')],1,Exception,1,8,None,1,2,0,1),
                          ('Exception: im, cite = False',2,None,[('JiraProjectKey','JiraProjectName',None)],2,None,False,1,None,1,3,None,None,0,None,0,8,Exception,1,2,0,2)])
def test_update_tickets_and_tasks(log_hl,gp,ex_func,cite,um,gefp,gjife,log_ln,im,
                                  description,log_hl_cnt,gp_se,gp_rv,ex_func_cnt,cite_se,cite_rv,
                                  cite_cnt,um_se,um_rv,um_cnt,gefp_se,gefp_rv,gefp_cnt,gjife_se,
                                  gjife_cnt,log_ln_cnt,im_se,im_rv,im_cnt,fe_cnt,ex_cnt):
    """Tests update_tickets_and_tasks"""
    gp.side_effect = gp_se
    gp.return_value = gp_rv
    cite.side_effect = cite_se
    cite.return_value = cite_rv
    um.side_effect = um_se
    um.return_value = um_rv
    gefp.side_effect = gefp_se
    gefp.return_value = gefp_rv
    gjife.side_effect = gjife_se
    im.side_effect = im_se
    im.return_value = im_rv
    update_tickets_and_tasks()
    assert log_hl.call_count == log_hl_cnt
    assert gp.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert cite.call_count == cite_cnt
    assert um.call_count == um_cnt
    assert gefp.call_count == gefp_cnt
    assert gjife.call_count == gjife_cnt
    assert log_ln.call_count == log_ln_cnt
    assert im.call_count == im_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_infosecdashboard.repeat_function')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_subtask_exists')
@mock.patch('nonprodsec_infosecdashboard.GeneralTicketing.get_task_json')
@mock.patch('nonprodsec_infosecdashboard.IFDQueries.check_if_issue_exists')
@mock.patch('nonprodsec_infosecdashboard.TheLogs.function_exception')
@mock.patch('nonprodsec_infosecdashboard.GeneralTicketing.get_child_issues')
@pytest.mark.parametrize("description,number_of_items,gci_se,ex_func_cnt,ciie_se,ciie_rv,ciie_cnt,gtj_se,gtj_rv,gtj_cnt,cise_se,cise_rv,cise_cnt,rf_cnt,fe_cnt,ex_cnt",
                         [('All expected values, 50 items, ciie = True, cise = False',50,None,0,None,True,1,None,{'EpicIssueKey':'eik','IssueType':'it','Summary':'sum','Labels':'lbs','Priority':'pty','State':'st','JiraStatusCategory':'jsc','Reporter':'rpt','Assignee':'asn','CreatedDate':'cd','DueDate':'dd','StartDate':'sd','UpdatedDate':'ud','ResolutionDate':'rd','IssueKey':'ik','SubTaskIssueKey':'sti'},1,None,False,1,1,0,0),
                          ('All expected values, 50 items, ciie = False, cise = True',50,None,0,None,False,1,None,{'EpicIssueKey':'eik','IssueType':'it','Summary':'sum','Labels':'lbs','Priority':'pty','State':'st','JiraStatusCategory':'jsc','Reporter':'rpt','Assignee':'asn','CreatedDate':'cd','DueDate':'dd','StartDate':'sd','UpdatedDate':'ud','ResolutionDate':'rd','IssueKey':'ik','SubTaskIssueKey':'sti'},1,None,True,1,1,0,0),
                          ('Exception: gci',0,Exception,1,None,None,0,None,None,0,None,None,0,0,1,0),
                          ('Exception: ciie',25,None,25,Exception,None,1,None,None,0,None,None,0,0,0,25),
                          ('Exception: gjt',10,None,10,None,False,1,Exception,None,1,None,None,0,0,0,10),
                          ('Exception: cise',1,None,1,None,True,1,None,{'EpicIssueKey':'eik','IssueType':'it','Summary':'sum','Labels':'lbs','Priority':'pty','State':'st','JiraStatusCategory':'jsc','Reporter':'rpt','Assignee':'asn','CreatedDate':'cd','DueDate':'dd','StartDate':'sd','UpdatedDate':'ud','ResolutionDate':'rd','IssueKey':'ik','SubTaskIssueKey':'sti'},1,Exception,None,1,0,0,1),])
def test_get_jira_issues_for_epic(gci,ex_func,ciie,gtj,cise,rf,
                                  description,number_of_items,gci_se,ex_func_cnt,ciie_se,ciie_rv,
                                  ciie_cnt,gtj_se,gtj_rv,gtj_cnt,cise_se,cise_rv,cise_cnt,rf_cnt,
                                  fe_cnt,ex_cnt):
    """Tests get_jira_issues_for_epic"""
    gci_rv = []
    while len(gci_rv) < number_of_items:
        gci_rv.append({'IssueKey':'ABC-123','IssueType':'it','Summary':'sum','SubtaskCount':1,'Subtasks':['ABC-124'],'Labels':'lab','Priority':'pty','State':'st','JiraStatusCategory':'jsc','Reporter':'rptr','Assignee':'asn','CreatedDate':'2020-04-27','DueDate':'2030-04-27','UpdatedDate':'2023-06-13','ResolutionDate':None,'StartDate': None})
    gci.side_effect = gci_se
    gci.return_value = gci_rv
    ciie.side_effect = ciie_se
    ciie.return_value = ciie_rv
    gtj.side_effect = gtj_se
    gtj.return_value = gtj_rv
    cise.side_effect = cise_se
    cise.return_value = cise_rv
    get_jira_issues_for_epic('ABC-123',1,'ExampleTable')
    assert gci.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert ciie.call_count == ciie_cnt*number_of_items
    assert gtj.call_count == gtj_cnt*number_of_items
    assert cise.call_count == cise_cnt*number_of_items
    assert rf.call_count == rf_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_infosecdashboard.TheLogs.function_exception')
@mock.patch('nonprodsec_infosecdashboard.get_jira_issues_for_epic')
@pytest.mark.parametrize("description,gjife_se,gjife_cnt,ex_func_cnt,fe_cnt,ex_cnt,list_of_dicts",
                         [('Successfully runs the function',None,1,0,0,0,[{'function':'get_jira_issues_for_epic','args':['ABC-123',2,'ExampleTable']}]),
                          ('Exception: cmd processing',None,0,1,1,0,[{'fucntion':'get_jira_issues_for_epic','args':['ABC-123',2,'ExampleTable']}])])
def test_repeat_function(gjife,ex_func,
                    description,gjife_se,gjife_cnt,ex_func_cnt,fe_cnt,ex_cnt,list_of_dicts):
    """Tests repeat_function"""
    gjife.side_effect == gjife_se
    repeat_function(list_of_dicts)
    assert gjife.call_count == gjife_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
