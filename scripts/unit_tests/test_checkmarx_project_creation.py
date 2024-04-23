'''Unit tests for checkmarx.project_creation'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from checkmarx.project_creation import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_update_exception_info():
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.project_creation.TheLogs.log_info')
@mock.patch('checkmarx.project_creation.Alerts.manual_alert')
@mock.patch('checkmarx.project_creation.CxCreate.baseline_create',
            return_value={'ProjectCreated':True,'repo_is_set':True})
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            return_value=[('repo',None,12345,)])
def test_cxcreate_run_all(sql_sel,ex_sql,b_create,al_man,log_ln):
    """Tests CxCreate.run_all"""
    CxCreate.run_all()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert b_create.call_count == 1
    assert al_man.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.project_creation.TheLogs.log_info')
@mock.patch('checkmarx.project_creation.Alerts.manual_alert')
@mock.patch('checkmarx.project_creation.CxCreate.baseline_create')
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            side_effect=Exception)
def test_cxcreate_run_all_ex_001(sql_sel,ex_sql,b_create,al_man,log_ln):
    """Tests CxCreate.run_all"""
    CxCreate.run_all()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert b_create.call_count == 0
    assert al_man.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_repo',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            return_value=[('main')])
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket',
            return_value={'FatalCount':0,'ExceptionCount':0,'UpdatedRepos':1,'AddedRepos':['repo']})
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,ex_sql,
                                  p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 2
    assert p_branch.call_count == 1
    assert ex_func.call_count == 0
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 1
    assert sv_uei.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 1
    assert lau_scan.call_count == 1

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan')
@mock.patch('checkmarx.project_creation.CxAPI.set_repo')
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select')
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket')
@mock.patch('checkmarx.project_creation.CxAPI.set_policy')
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team')
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_001(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 0
    assert p_sp.call_count == 0
    assert u_bb.call_count == 0
    assert sv_uei.call_count == 0
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 0
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan')
@mock.patch('checkmarx.project_creation.CxAPI.set_repo')
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select')
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket')
@mock.patch('checkmarx.project_creation.CxAPI.set_policy')
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_002(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 1
    assert p_sp.call_count == 0
    assert u_bb.call_count == 0
    assert sv_uei.call_count == 0
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 0
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan')
@mock.patch('checkmarx.project_creation.CxAPI.set_repo')
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select')
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket')
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_003(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 0
    assert sv_uei.call_count == 0
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 0
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_repo',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket',
            return_value={'FatalCount':0,'ExceptionCount':0,'UpdatedRepos':1,'AddedRepos':['repo']})
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_004(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 0
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 1
    assert sv_uei.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert p_sr.call_count == 0
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_repo',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            return_value=[(None)])
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket',
            return_value={'FatalCount':0,'ExceptionCount':0,'UpdatedRepos':1,'AddedRepos':['repo']})
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_005a(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 1
    assert sv_uei.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 1
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_repo',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            return_value=[('main')])
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket',
            return_value={'FatalCount':0,'ExceptionCount':0,'UpdatedRepos':1,'AddedRepos':['repo']})
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_005b(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 1
    assert sv_uei.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 1
    assert lau_scan.call_count == 0

@mock.patch('checkmarx.project_creation.CxAPI.launch_cx_scan',
            side_effect=Exception)
@mock.patch('checkmarx.project_creation.CxAPI.set_repo',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.sql_exception')
@mock.patch('checkmarx.project_creation.select',
            return_value=[('main')])
@mock.patch('checkmarx.project_creation.ScrVar.update_exception_info')
@mock.patch('checkmarx.project_creation.BitBucket.update_bitbucket',
            return_value={'FatalCount':0,'ExceptionCount':0,'UpdatedRepos':1,'AddedRepos':['repo']})
@mock.patch('checkmarx.project_creation.CxAPI.set_policy',
            return_value=True)
@mock.patch('checkmarx.project_creation.CxAPI.set_project_team',
            return_value=True)
@mock.patch('checkmarx.project_creation.TheLogs.function_exception')
@mock.patch('checkmarx.project_creation.CxAPI.branch_project',
            return_value=987654321)
@mock.patch('checkmarx.project_creation.TheLogs.log_info')
def test_cxcreate_baseline_create_ex_006(log_ln,p_branch,ex_func,p_spt,p_sp,u_bb,sv_uei,sql_sel,
                                         ex_sql,p_sr,lau_scan):
    """Tests CxCreate.baseline_create"""
    CxCreate.baseline_create('repo',123456789)
    assert log_ln.call_count == 1
    assert p_branch.call_count == 1
    assert ex_func.call_count == 1
    assert p_spt.call_count == 1
    assert p_sp.call_count == 1
    assert u_bb.call_count == 1
    assert sv_uei.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert p_sr.call_count == 1
    assert lau_scan.call_count == 1
