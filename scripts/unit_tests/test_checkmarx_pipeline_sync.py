'''Unit tests for the checkmarx_pipeline_sync script '''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from checkmarx.pipeline_sync import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',side_effect=Exception)
def test_psactions_get_findings_to_sync_exception(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Tech Debt',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_proposed_not_exploitable(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Proposed Not Exploitable',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_urgent(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Urgent',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_confirmed(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Confirmed',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_past_due(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Past Due',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_not_exploitable(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Not Exploitable',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
def test_psactions_get_findings_to_sync_accepted(db_select,except_sql):
    '''tests get_findings_to_sync'''
    PSActions.get_findings_to_sync('Accepted',10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',side_effect=Exception)
def test_psactions_get_pipeline_project_id_exception(db_select,except_sql):
    '''tests get_pipeline_project_id'''
    PSActions.get_pipeline_project_id(10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[(10810, )])
def test_psactions_get_pipeline_project_id(db_select,except_sql):
    '''tests get_pipeline_project_id'''
    PSActions.get_pipeline_project_id(10915)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',side_effect=Exception)
def test_psactions_get_ticket_for_finding_exception(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Tech Debt',10915,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[('AS-1189','03/06/2024',None)])
def test_psactions_get_ticket_for_finding_proposed_not_exploitable(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Proposed Not Exploitable',10519,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[('AS-1189','03/06/2024',None)])
def test_psactions_get_ticket_for_finding_urgent(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Urgent',10915,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[('AS-1189','03/06/2024',None)])
def test_psactions_get_ticket_for_finding_past_due(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Past Due',10915,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[])
def test_psactions_get_ticket_for_finding_not_exploitable(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Not Exploitable',10915,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[('AS-1189','03/06/2024',None)])
def test_psactions_get_ticket_for_finding_accepted(db_select,except_sql):
    '''tests get_ticket_for_finding'''
    PSActions.get_ticket_for_finding('Accepted',10915,1)
    assert db_select.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_path_and_result_state',side_effect=Exception)
def test_psactions_get_pipeline_finding_exception(get_result,except_func):
    '''tests get_pipeline_finding'''
    PSActions.get_pipeline_finding(10810,1)
    assert get_result.call_count == 1
    assert except_func.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_path_and_result_state',return_value={'cxScanId':
                                                                            1118025,'cxPathId':3,
                                                                            'cxStateName':
                                                                            'Not Exploitable'})
def test_psactions_get_pipeline_finding(get_result,except_func):
    '''tests get_pipeline_finding'''
    PSActions.get_pipeline_finding(10810,1)
    assert get_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',side_effect=Exception)
def test_psactions_set_result_state_exception(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Tech Debt',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_proposed_not_exploitable(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Proposed Not Exploitable',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_urgent(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Urgent',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_confirmed(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Confirmed',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_past_due(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Past Due',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_not_exploitable(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Not Exploitable',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.update_res_state',return_value=True)
def test_psactions_set_result_state_accepted(update_result,except_func):
    '''tests set_result_state'''
    PSActions.set_result_state('Accepted',12345,1,'A comment')
    assert update_result.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.add_ticket_to_cx',side_effect=Exception)
def test_psactions_set_ticket_in_checkmarx_exception(add_ticket,except_func):
    '''tests set_ticket_in_checkmarx'''
    PSActions.set_ticket_in_checkmarx('1118025-3','AS-1189')
    assert add_ticket.call_count == 1
    assert except_func.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.add_ticket_to_cx')
def test_psactions_set_ticket_in_checkmarx(add_ticket,except_func):
    '''tests set_ticket_in_checkmarx'''
    PSActions.set_ticket_in_checkmarx('1118025-3','AS-1189')
    assert add_ticket.call_count == 1
    assert except_func.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update',side_effect=Exception)
def test_psactions_set_finding_sync_exception(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Tech Debt',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_proposed_not_exploitable(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Proposed Not Exploitable',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_urgent(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Urgent',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_confirmed(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Confirmed',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_past_due(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Past Due',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_not_exploitable(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Not Exploitable',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.update')
def test_psactions_set_finding_sync_accepted(db_update,except_sql):
    '''tests set_finding_sync'''
    PSActions.set_finding_sync('Accepted',10915,1)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.delete_row',side_effect=Exception)
def test_psactions_delete_old_scan_exception(db_update,except_sql):
    '''tests delete_old_scan'''
    PSActions.delete_old_scan('Baseline',1,10915)
    assert db_update.call_count == 1
    assert except_sql.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.delete_row')
def test_psactions_delete_old_scan(db_update,except_sql):
    '''tests delete_old_scan'''
    PSActions.delete_old_scan('Pipeline',1,10915)
    assert db_update.call_count == 1
    assert except_sql.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',side_effect=Exception)
def test_psactions_baseline_scan_exists_exception_001(get_scan,except_func,db_select,except_sql,
                                                      del_old):
    '''tests baseline_scan_exists'''
    PSActions.baseline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 1
    assert db_select.call_count == 0
    assert except_sql.call_count == 0
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',side_effect=Exception)
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_baseline_scan_exists_exception_002(get_scan,except_func,db_select,except_sql,
                                                      del_old):
    '''tests baseline_scan_exists'''
    PSActions.baseline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 1
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[(12345, )])
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_baseline_scan_exists_true(get_scan,except_func,db_select,except_sql,del_old):
    '''tests baseline_scan_exists'''
    PSActions.baseline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 0
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[])
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_baseline_scan_exists_false(get_scan,except_func,db_select,except_sql,del_old):
    '''tests baseline_scan_exists'''
    PSActions.baseline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 0
    assert del_old.call_count == 1

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select')
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',side_effect=Exception)
def test_psactions_piseline_scan_exists_exception_001(get_scan,except_func,db_select,except_sql,
                                                      del_old):
    '''tests piseline_scan_exists'''
    PSActions.pipeline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 1
    assert db_select.call_count == 0
    assert except_sql.call_count == 0
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',side_effect=Exception)
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_pipeline_scan_exists_exception_002(get_scan,except_func,db_select,except_sql,
                                                      del_old):
    '''tests pipeline_scan_exists'''
    PSActions.pipeline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 1
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[(12345, )])
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_pipeline_scan_exists_true(get_scan,except_func,db_select,except_sql,del_old):
    '''tests pipeline_scan_exists'''
    PSActions.pipeline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 0
    assert del_old.call_count == 0

@mock.patch('checkmarx.pipeline_sync.PSActions.delete_old_scan')
@mock.patch('checkmarx.pipeline_sync.TheLogs.sql_exception')
@mock.patch('checkmarx.pipeline_sync.select',return_value=[])
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.CxAPI.get_last_scan_data',return_value={'ID':1119564,'Type':
                                                                    'Incremental','Finished':
                                                                    '2023-10-02 11:15:36',
                                                                    'Duration':'0:02:00'})
def test_psactions_pipeline_scan_exists_false(get_scan,except_func,db_select,except_sql,del_old):
    '''tests pipeline_scan_exists'''
    PSActions.pipeline_scan_exists(10915,12345)
    assert get_scan.call_count == 1
    assert except_func.call_count == 0
    assert db_select.call_count == 1
    assert except_sql.call_count == 0
    assert del_old.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.insert_multiple_into_table',side_effect=Exception)
@mock.patch('checkmarx.pipeline_sync.PSActions.pipeline_scan_exists',
            return_value={'BaselineProjectID':10915,'PipelineProjectID':10810,'ScanType':
                          'Pipeline','ScanID':1119564,'ScanDate':'2023-10-02 11:15:36'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.baseline_scan_exists',
            return_value={'BaselineProjectID':10915,'ScanType':'Pipeline','ScanID':1119564,
                          'ScanDate':'2023-10-02 11:15:36'})
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_update_scans_exception(log_hl,bl_scan,pl_id,pl_scan,db_insert,except_func,
                                            log_ln):
    '''Tests update_scans'''
    CxPipelines.update_scans(10915)
    assert log_hl.call_count == 1
    assert bl_scan.call_count == 1
    assert pl_id.call_count == 1
    assert pl_scan.call_count == 1
    assert db_insert.call_count == 1
    assert except_func.call_count == 1
    assert log_ln.call_count == 0

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.insert_multiple_into_table')
@mock.patch('checkmarx.pipeline_sync.PSActions.pipeline_scan_exists',
            return_value={'BaselineProjectID':10915,'PipelineProjectID':10810,'ScanType':
                          'Pipeline','ScanID':1119564,'ScanDate':'2023-10-02 11:15:36'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.baseline_scan_exists',
            return_value={'BaselineProjectID':10915,'ScanType':'Pipeline','ScanID':1119564,
                          'ScanDate':'2023-10-02 11:15:36'})
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_update_scans_has_updates(log_hl,bl_scan,pl_id,pl_scan,db_insert,except_func,
                                            log_ln):
    '''Tests update_scans'''
    CxPipelines.update_scans(10915)
    assert log_hl.call_count == 1
    assert bl_scan.call_count == 1
    assert pl_id.call_count == 1
    assert pl_scan.call_count == 1
    assert db_insert.call_count == 1
    assert except_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.TheLogs.function_exception')
@mock.patch('checkmarx.pipeline_sync.insert_multiple_into_table')
@mock.patch('checkmarx.pipeline_sync.PSActions.pipeline_scan_exists',return_value=None)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.baseline_scan_exists',return_value=None)
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_update_scans_no_updates(log_hl,bl_scan,pl_id,pl_scan,db_insert,except_func,
                                            log_ln):
    '''Tests update_scans'''
    CxPipelines.update_scans(10915)
    assert log_hl.call_count == 1
    assert bl_scan.call_count == 1
    assert pl_id.call_count == 1
    assert pl_scan.call_count == 1
    assert db_insert.call_count == 0
    assert except_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.ScrVar.reset_exception_counts')
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
@mock.patch('checkmarx.pipeline_sync.CxPipelines.sync_state_to_pipeline')
@mock.patch('checkmarx.pipeline_sync.CxPipelines.update_scans',return_value=False)
def test_cxpipelines_sync_findings_to_pipeline_no_updates(u_scans,sync_sts,log_hl,log_ln,ex_res):
    '''Tests sync_findings_to_pipeline'''
    CxPipelines.sync_findings_to_pipeline(10915)
    assert u_scans.call_count == 1
    assert sync_sts.call_count == 0
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1
    assert ex_res.call_count == 1

@mock.patch('checkmarx.pipeline_sync.ScrVar.reset_exception_counts')
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
@mock.patch('checkmarx.pipeline_sync.CxPipelines.sync_state_to_pipeline')
@mock.patch('checkmarx.pipeline_sync.CxPipelines.update_scans',return_value=True)
def test_cxpipelines_sync_findings_to_pipeline_has_updates(u_scans,sync_sts,log_hl,log_ln,ex_res):
    '''Tests sync_findings_to_pipeline'''
    CxPipelines.sync_findings_to_pipeline(10915)
    assert u_scans.call_count == 1
    assert sync_sts.call_count == 7
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0
    assert ex_res.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Tech Debt'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_no_updates(log_hl,g_sync,pl_id,g_ticket,pl_finding,
                                                       set_state,set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Tech Debt',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 0
    assert set_ticket.call_count == 0
    assert set_sync.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_tech_debt_has_findings(log_hl,g_sync,pl_id,g_ticket,
                                                                   pl_finding,set_state,set_ticket,
                                                                   set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Tech Debt',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_proposed_not_exploitable(log_hl,g_sync,pl_id,g_ticket,
                                                                     pl_finding,set_state,
                                                                     set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Proposed Not Exploitable',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_urgent(log_hl,g_sync,pl_id,g_ticket,pl_finding,
                                                   set_state,set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Urgent',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'To Verify'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_confirmed(log_hl,g_sync,pl_id,g_ticket,pl_finding,
                                                      set_state,set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Confirmed',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_past_due(log_hl,g_sync,pl_id,g_ticket,pl_finding,
                                                     set_state,set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Past Due',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024','RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_not_exploitable(log_hl,g_sync,pl_id,g_ticket,
                                                            pl_finding,set_state,set_ticket,
                                                            set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Not Exploitable',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':None,'JiraDueDate':None,'RITMTicket':None})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_not_exploitable_no_ticket(log_hl,g_sync,pl_id,g_ticket,
                                                                      pl_finding,set_state,
                                                                      set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Not Exploitable',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.pipeline_sync.TheLogs.log_info')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_finding_sync')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_ticket_in_checkmarx')
@mock.patch('checkmarx.pipeline_sync.PSActions.set_result_state',return_value=True)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_finding',
            return_value={'cxScanId':1118025,'cxPathId':3,'cxStateName':'Confirmed'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_ticket_for_finding',
            return_value={'JiraIssueKey':'AS-1189','JiraDueDate':'03/06/2024',
                          'RITMTicket':'AS-1187'})
@mock.patch('checkmarx.pipeline_sync.PSActions.get_pipeline_project_id',return_value=10810)
@mock.patch('checkmarx.pipeline_sync.PSActions.get_findings_to_sync',
            return_value=[('-1007447064',),])
@mock.patch('checkmarx.pipeline_sync.TheLogs.log_headline')
def test_cxpipelines_sync_state_to_pipeline_accepted(log_hl,g_sync,pl_id,g_ticket,pl_finding,
                                                     set_state,set_ticket,set_sync,log_ln):
    '''Tests sync_state_to_pipeline'''
    CxPipelines.sync_state_to_pipeline('Accepted',10915)
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert pl_id.call_count == 1
    assert g_ticket.call_count == 1
    assert pl_finding.call_count == 1
    assert set_state.call_count == 1
    assert set_ticket.call_count == 1
    assert set_sync.call_count == 1
    assert log_ln.call_count == 1

if __name__ == '__main__':
    unittest.main()
