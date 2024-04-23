'''Unit tests for the maintenance_checkmarx script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maint.checkmarx_maintenance import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    """Tests ScrVar.reset_exception_counts"""
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

def test_scrvar_update_exception_info():
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_maintenance.update_sastprojects_by_project_type')
@mock.patch('maint.checkmarx_maintenance.ScrVar.update_exception_info')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.set_all_sastprojects_inactive')
@mock.patch('maint.checkmarx_maintenance.ScrVar.reset_exception_counts')
@pytest.mark.parametrize("sasi_rv,uspt_cnt",
                         [(1,0),
                          (0,2)])
def test_cxmaint_base_sastprojects_updates(ex_res,sasi,uei,uspt,sasi_rv,uspt_cnt):
    """Tests CxMaint.base_sastprojects_updates"""
    sasi.return_value = {'FatalCount':sasi_rv}
    CxMaint.base_sastprojects_updates()
    assert ex_res.call_count == 1
    assert sasi.call_count == 1
    assert uei.call_count == 1
    assert uspt.call_count == uspt_cnt
    ScrVar.fe_cnt = 0

@mock.patch('maint.checkmarx_maintenance.update_project_data_sastprojects')
@mock.patch('maint.checkmarx_maintenance.ScrVar.reset_exception_counts')
def test_update_sastprojects_details(ex_res,upds):
    """Tests CxMaint.update_sastprojects_details"""
    CxMaint.update_sastprojects_details()
    assert ex_res.call_count == 1
    assert upds.call_count == 2

@mock.patch('maint.checkmarx_maintenance.update_project_data_sastprojects')
@mock.patch('maint.checkmarx_maintenance.update_sastprojects_by_project_type')
@mock.patch('maint.checkmarx_maintenance.ScrVar.update_exception_info')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.set_all_sastprojects_inactive')
@mock.patch('maint.checkmarx_maintenance.ScrVar.reset_exception_counts')
@pytest.mark.parametrize("sasi_rv,other_cnt",
                         [(1,0),
                          (0,1)])
def test_cxmaint_update_created_baseline_projects(ex_res,sasi,uei,usbpt,upds,sasi_rv,other_cnt):
    """Tests CxMaint.update_created_baseline_projects"""
    sasi.return_value = {'FatalCount':sasi_rv}
    CxMaint.update_created_baseline_projects()
    assert ex_res.call_count == 1
    assert sasi.call_count == 1
    assert uei.call_count == 1
    assert usbpt.call_count == other_cnt
    assert usbpt.call_count == other_cnt

@mock.patch('maint.checkmarx_maintenance.update_appsec_data_table')
@mock.patch('maint.checkmarx_maintenance.ScrVar.update_exception_info')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.get_baselines_from_sastprojects',
            return_value={'Results':['a list']})
@mock.patch('maint.checkmarx_maintenance.ScrVar.reset_exception_counts')
def tests_cxmaint_update_baseline_projects(ex_res,gbfs,uei,uadt):
    """Tests CxMaint.update_baseline_projects"""
    CxMaint.update_baseline_projects()
    assert ex_res.call_count == 1
    assert gbfs.call_count == 1
    assert uei.call_count == 1
    assert uadt.call_count == 2

@mock.patch('maint.checkmarx_maintenance.update_cxbaselineprojectdetails_for_project',
            return_value={'updated':1,'added':1})
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.get_baselines_from_sastprojects',
            return_value={'Results':[{'cxProjectId':123456789}]})
@mock.patch('maint.checkmarx_maintenance.TheLogs.log_info')
@mock.patch('maint.checkmarx_maintenance.TheLogs.log_headline')
@mock.patch('maint.checkmarx_maintenance.ScrVar.reset_exception_counts')
def test_cxmaint_update_project_details(ex_res,log_hl,log_ln,gbfa,ucfp):
    """Tests CxMaint.update_project_details"""
    CxMaint.update_project_details()
    assert ex_res.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 3
    assert gbfa.call_count == 1
    assert ucfp.call_count == 1

@mock.patch('maint.checkmarx_maintenance.TheLogs.log_info')
@mock.patch('maint.checkmarx_maintenance.TheLogs.function_exception')
@mock.patch('maint.checkmarx_maintenance.DBQueries.update_multiple')
@mock.patch('maint.checkmarx_maintenance.CxAPI.get_project_data',
            return_value={'Results':{'cxTeamId':1234,'cxProjectName':'Name','LastScanDate':
                                     '2023-12-12','BranchedFrom':123,'BranchedFromExists':1,
                                     'CrossRepoBranching':0,'cxBaselineRepoSet':False,
                                     'cxProjectId':123456789}})
@mock.patch('maint.checkmarx_maintenance.ScrVar.update_exception_info')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.sastprojects_to_update',
            return_value={'Results':[{'cxProjectId':123456789,'Repo':'repo'}]})
@mock.patch('maint.checkmarx_maintenance.TheLogs.log_headline')
@pytest.mark.parametrize("proj_type,umit_se,ex_func_cnt",
                         [('baseline',None,0),
                          ('pipeline',Exception,1)])
def test_update_project_data_sastprojects(log_hl,stu,uei,gpd,umit,ex_func,log_ln,proj_type,
                                          umit_se,ex_func_cnt):
    """Tests update_project_data_sastprojects"""
    umit.side_effect = umit_se
    update_project_data_sastprojects(proj_type)
    assert log_hl.call_count == 1
    assert stu.call_count == 1
    assert uei.call_count == 2
    assert gpd.call_count == 1
    assert umit.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1

@mock.patch('maint.checkmarx_maintenance.TheLogs.log_info')
@mock.patch('maint.checkmarx_maintenance.DBQueries.insert_multiple')
@mock.patch('maint.checkmarx_maintenance.DBQueries.update_multiple')
@mock.patch('maint.checkmarx_maintenance.TheLogs.function_exception')
@mock.patch('maint.checkmarx_maintenance.CxAPI.get_checkmarx_projects')
@mock.patch('maint.checkmarx_maintenance.TheLogs.log_headline')
@pytest.mark.parametrize("proj_type,gcp_se,gcp_rv,umit_se,imit_se,ex_func_cnt,umit_cnt,imit_cnt",
                         [('baseline',None,[{'repo':'repo','id':12345}],None,None,0,1,1),
                          ('pipeline',Exception,None,None,None,1,0,0),
                          ('baseline',None,[{'repo':'repo','id':12345}],Exception,None,1,1,1),
                          ('baseline',None,[{'repo':'repo','id':12345}],None,Exception,1,1,1)])
def test_update_sastprojects_by_project_type(log_hl,gcp,ex_func,umit,imit,log_ln,
                                             proj_type,gcp_se,gcp_rv,umit_se,imit_se,
                                             ex_func_cnt,umit_cnt,imit_cnt):
    """Tests update_sastprojects_by_project_type"""
    gcp.side_effect = gcp_se
    gcp.return_value = gcp_rv
    umit.side_effect = umit_se
    imit.side_effect = imit_se
    update_sastprojects_by_project_type(proj_type)
    assert log_hl.call_count == 1
    assert gcp.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert umit.call_count == umit_cnt
    assert imit.call_count == imit_cnt
    assert log_ln.call_count == 2

@mock.patch('maint.checkmarx_maintenance.TheLogs.log_info')
@mock.patch('maint.checkmarx_maintenance.DBQueries.insert_multiple')
@mock.patch('maint.checkmarx_maintenance.TheLogs.function_exception')
@mock.patch('maint.checkmarx_maintenance.DBQueries.update_multiple')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.clear_checkmarx_data_from_applications')
@mock.patch('maint.checkmarx_maintenance.ScrVar.update_exception_info')
@mock.patch('maint.checkmarx_maintenance.CxASDatabase.clear_checkmarx_data_from_aa')
@mock.patch('maint.checkmarx_maintenance.TheLogs.log_headline')
@pytest.mark.parametrize("table,ccdfaa_rv,ccdfap_rv,umit_se,imit_se,ex_func_cnt,ccdfaa_cnt,ccdfap_cnt",
                         [('ApplicationAutomation',{'Results':True},None,None,None,0,1,0),
                          ('Applications',None,{'Results':True},None,None,0,0,1),
                          ('ApplicationAutomation',{'Results':False},None,Exception,Exception,2,1,0)])
def test_update_appsec_data_table(log_hl,ccdfaa,uei,ccdfap,umit,ex_func,imit,log_ln,
                                  table,ccdfaa_rv,ccdfap_rv,umit_se,imit_se,
                                  ex_func_cnt,ccdfaa_cnt,ccdfap_cnt):
    """Tests update_appsec_data_table"""
    ccdfaa.return_value = ccdfaa_rv
    ccdfap.return_value = ccdfap_rv
    umit.side_effect = umit_se
    imit.side_effect = imit_se
    update_appsec_data_table(table,[{'Repo':'repo','cxProjectId':1234,'cxActive':1,'cxTeam':53,'CxProjectName':'repo','cxLastScanDate':'2023-01-01'}])
    assert log_hl.call_count == 1
    assert ccdfaa.call_count == ccdfaa_cnt
    assert uei.call_count == 1
    assert ccdfap.call_count == ccdfap_cnt
    assert ex_func.call_count == ex_func_cnt
    assert umit.call_count == 1
    assert imit.call_count ==1
    assert log_ln.call_count == 2

@mock.patch('maint.checkmarx_maintenance.DBQueries.update_multiple')
@mock.patch('maint.checkmarx_maintenance.TheLogs.function_exception')
@mock.patch('maint.checkmarx_maintenance.DBQueries.insert_multiple')
@mock.patch('maint.checkmarx_maintenance.CxAPI.get_project_details',
            return_value = {'LastDataSync':'lds','cxProjectName':'name','cxRelatedProjects':'rp',
                            'branchScanned':'branch','cxLastScanId':'lsid','cxScannedDate':'date',
                            'cxFilesCount':'cnt','cxLinesOfCode':'cnt','Apex':0,'ASP':0,'Cobol':0,
                            'Common':0,'CPP':0,'CSharp':0,'Dart':0,'Go':0,'Groovy':0,'Java':0,
                            'JavaScript':0,'Kotlin':0,'Objc':0,'Perl':0,'PHP':0,'PLSQL':0,
                            'Python':1,'RPG':0,'Ruby':0,'Scala':0,'Swift':0,'VB6':0,'VbNet':0,
                            'VbScript':0,'Unknown':0,'Repo':'repo'})
@pytest.mark.parametrize("imit_se,imit_rv,umit_se,umit_cnt,ex_func_cnt",
                         [(None,1,None,0,0),
                          (None,0,None,1,0),
                          (Exception,None,None,0,1),
                          (None,0,Exception,1,1)])
def test_update_cxbaselineprojectdetails_for_project(gpd,imit,ex_func,umit,
                                                     imit_se,imit_rv,umit_se,umit_cnt,ex_func_cnt):
    """Tests update_cxbaselineprojectdetails_for_project"""
    imit.side_effect = imit_se
    imit.return_value = imit_rv
    umit.side_effect = umit_se
    update_cxbaselineprojectdetails_for_project(12345)
    assert gpd.call_count == 1
    assert imit.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert umit.call_count == umit_cnt

if __name__ == '__main__':
    unittest.main()
