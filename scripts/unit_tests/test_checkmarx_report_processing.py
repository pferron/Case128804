'''Unit tests for the checkmarx.report_processing script'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from checkmarx.report_processing import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

@mock.patch('checkmarx.report_processing.CxReports.baseline_state_updates')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_all_baseline_states(ex_reset,bl_states):
    '''Tests CxReports.update_all_baseline_states'''
    result = CxReports.update_all_baseline_states(10915)
    assert ex_reset.call_count == 1
    assert bl_states.call_count == 5
    assert result == {'FatalCount':0,'ExceptionCount':0}

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_tech_debt(log_hl,sql_sel,ex_sql,u_res_state,add_tkt,
                                                    mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10519,'Tech Debt')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_past_due(log_hl,sql_sel,ex_sql,u_res_state,add_tkt,
                                                   mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Past Due')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_closed(log_hl,sql_sel,ex_sql,u_res_state,add_tkt,
                                                 mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Closed')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_closed_in_ticket(log_hl,sql_sel,ex_sql,u_res_state,
                                                           add_tkt,mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Closed in Ticket')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_not_exploitable(log_hl,sql_sel,ex_sql,u_res_state,
                                                          add_tkt,mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Not Exploitable')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_ex_bsu_001(log_hl,sql_sel,ex_sql,u_res_state,add_tkt,
                                                         mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Closed in Ticket')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert u_res_state.call_count == 0
    assert add_tkt.call_count == 0
    assert mlti_upd.call_count == 0
    assert ex_func.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','KEY-123','2021-12-13',None,),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_baseline_state_updates_ex_bsu_002(log_hl,sql_sel,ex_sql,u_res_state,add_tkt,
                                                         mlti_upd,ex_func,log_ln):
    '''Tests CxReports.baseline_state_updates'''
    result = CxReports.baseline_state_updates(10915,'Closed in Ticket')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_res_state.call_count == 1
    assert add_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6',),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_auto_confirm_findings(log_hl,sql_sel,ex_sql,u_cx_state,ex_func,mlti_upd,log_ln):
    '''Tests CxReports.auto_confirm_findings'''
    result = CxReports.auto_confirm_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_cx_state.call_count == 1
    assert ex_func.call_count == 0
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            return_value=True)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_auto_confirm_findings_ex_acf_001(log_hl,sql_sel,ex_sql,u_cx_state,ex_func,
                                                    mlti_upd,log_ln):
    '''Tests CxReports.auto_confirm_findings'''
    result = CxReports.auto_confirm_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert u_cx_state.call_count == 0
    assert ex_func.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6',),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_auto_confirm_findings_ex_acf_002_003(log_hl,sql_sel,ex_sql,u_cx_state,ex_func,
                                                        mlti_upd,log_ln):
    '''Tests CxReports.auto_confirm_findings'''
    result = CxReports.auto_confirm_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_cx_state.call_count == 1
    assert ex_func.call_count == 2
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row')
@mock.patch('checkmarx.report_processing.insert')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[{'cxResultState':'To Verify','cxResultStateValue':0,'cxQuery':'cxQuery',
                           'cxResultSeverity':'Critical','cxResultSeverityValue':0,'cxLink':'link',
                           'cxSource':'file_name; Object: object; Line: 1; Column: 2','SourceFile':
                           'file_name','SourceObject':'object',
                           'cxDestination':'file_name; Object: object; Line: 1; Column: 2',
                           'DestinationFile':'file_name','DestinationObject':'object','cxResultID':
                           '12345-6','cxResultDescription':'description','cxDetectionDate':
                           '2023-01-01','cxLastScanID':1,'cxLastScanDate':'2023-10-10 01:15:22',
                           'cxCWEID':1,'cxCWETitle':'cwe_title','cxCWEDescription':
                           'cwe_description','cxCWELink':'cwe_link','cxSimilarityID':33321301029},
                           0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            return_value={'ID':1,'Finished':'2023-10-10 00:59:36'})
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_force_reprocess(ex_reset,log_hl,g_last_scan,ex_func,ck_processed,
                                                  log_ln,run_report,proc_report,up_sf,sql_upd,
                                                  ex_sql,sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,1)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 0
    assert ck_processed.call_count == 0
    assert log_ln.call_count == 2
    assert run_report.call_count == 1
    assert proc_report.call_count == 1
    assert up_sf.call_count == 1
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert sql_ins.call_count == 1
    assert sql_del.call_count == 1
    assert auto_conf.call_count == 1

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row')
@mock.patch('checkmarx.report_processing.insert')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[[],0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            return_value={'ID':1,'Finished':'2023-10-10 00:59:36'})
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_calc_reprocess_no_report(ex_reset,log_hl,g_last_scan,ex_func,
                                                           ck_processed,log_ln,run_report,
                                                           proc_report,up_sf,sql_upd,ex_sql,
                                                           sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,0)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 0
    assert ck_processed.call_count == 1
    assert log_ln.call_count == 2
    assert run_report.call_count == 1
    assert proc_report.call_count == 1
    assert up_sf.call_count == 0
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert sql_ins.call_count == 1
    assert sql_del.call_count == 1
    assert auto_conf.call_count == 1

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row')
@mock.patch('checkmarx.report_processing.insert')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[{'cxResultState':'To Verify','cxResultStateValue':0,'cxQuery':'cxQuery',
                           'cxResultSeverity':'Critical','cxResultSeverityValue':0,'cxLink':'link',
                           'cxSource':'file_name; Object: object; Line: 1; Column: 2','SourceFile':
                           'file_name','SourceObject':'object',
                           'cxDestination':'file_name; Object: object; Line: 1; Column: 2',
                           'DestinationFile':'file_name','DestinationObject':'object','cxResultID':
                           '12345-6','cxResultDescription':'description','cxDetectionDate':
                           '2023-01-01','cxLastScanID':1,'cxLastScanDate':'2023-10-10 01:15:22',
                           'cxCWEID':1,'cxCWETitle':'cwe_title','cxCWEDescription':
                           'cwe_description','cxCWELink':'cwe_link','cxSimilarityID':33321301029},
                           0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            return_value={'ID':None,'Finished':None})
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_no_scan(ex_reset,log_hl,g_last_scan,ex_func,ck_processed,
                                                  log_ln,run_report,proc_report,up_sf,sql_upd,
                                                  ex_sql,sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,1)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 0
    assert ck_processed.call_count == 0
    assert log_ln.call_count == 1
    assert run_report.call_count == 0
    assert proc_report.call_count == 0
    assert up_sf.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert sql_ins.call_count == 0
    assert sql_del.call_count == 0
    assert auto_conf.call_count == 1

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row')
@mock.patch('checkmarx.report_processing.insert')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[{'cxResultState':'To Verify','cxResultStateValue':0,'cxQuery':'cxQuery',
                           'cxResultSeverity':'Critical','cxResultSeverityValue':0,'cxLink':'link',
                           'cxSource':'file_name; Object: object; Line: 1; Column: 2','SourceFile':
                           'file_name','SourceObject':'object',
                           'cxDestination':'file_name; Object: object; Line: 1; Column: 2',
                           'DestinationFile':'file_name','DestinationObject':'object','cxResultID':
                           '12345-6','cxResultDescription':'description','cxDetectionDate':
                           '2023-01-01','cxLastScanID':1,'cxLastScanDate':'2023-10-10 01:15:22',
                           'cxCWEID':1,'cxCWETitle':'cwe_title','cxCWEDescription':
                           'cwe_description','cxCWELink':'cwe_link','cxSimilarityID':33321301029},
                           0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_ex_us_001(ex_reset,log_hl,g_last_scan,ex_func,ck_processed,
                                            log_ln,run_report,proc_report,up_sf,sql_upd,
                                            ex_sql,sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,1)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 1
    assert ck_processed.call_count == 0
    assert log_ln.call_count == 0
    assert run_report.call_count == 0
    assert proc_report.call_count == 0
    assert up_sf.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert sql_ins.call_count == 0
    assert sql_del.call_count == 0
    assert auto_conf.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row')
@mock.patch('checkmarx.report_processing.insert')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[[],0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            return_value={'ID':1,'Finished':'2023-10-10 00:59:36'})
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_ex_ur_002(ex_reset,log_hl,g_last_scan,ex_func,ck_processed,
                                            log_ln,run_report,proc_report,up_sf,sql_upd,ex_sql,
                                            sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,0)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 0
    assert ck_processed.call_count == 1
    assert log_ln.call_count == 2
    assert run_report.call_count == 1
    assert proc_report.call_count == 1
    assert up_sf.call_count == 0
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert sql_ins.call_count == 1
    assert sql_del.call_count == 1
    assert auto_conf.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxReports.auto_confirm_findings')
@mock.patch('checkmarx.report_processing.delete_row',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.insert',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.CxReports.update_sastfindings')
@mock.patch('checkmarx.report_processing.CxReports.scan_report_to_process',
            return_value=[{'cxResultState':'To Verify','cxResultStateValue':0,'cxQuery':'cxQuery',
                           'cxResultSeverity':'Critical','cxResultSeverityValue':0,'cxLink':'link',
                           'cxSource':'file_name; Object: object; Line: 1; Column: 2','SourceFile':
                           'file_name','SourceObject':'object',
                           'cxDestination':'file_name; Object: object; Line: 1; Column: 2',
                           'DestinationFile':'file_name','DestinationObject':'object','cxResultID':
                           '12345-6','cxResultDescription':'description','cxDetectionDate':
                           '2023-01-01','cxLastScanID':1,'cxLastScanDate':'2023-10-10 01:15:22',
                           'cxCWEID':1,'cxCWETitle':'cwe_title','cxCWEDescription':
                           'cwe_description','cxCWELink':'cwe_link','cxSimilarityID':33321301029},
                           0])
@mock.patch('checkmarx.report_processing.CxReports.run_cx_report',
            return_value=99)
@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.CxReports.check_scan_processed',
            return_value=1)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_last_scan_data',
            return_value={'ID':1,'Finished':'2023-10-10 00:59:36'})
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_update_results_ex_ur_003_004(ex_reset,log_hl,g_last_scan,ex_func,ck_processed,
                                                  log_ln,run_report,proc_report,up_sf,sql_upd,
                                                  ex_sql,sql_ins,sql_del,auto_conf):
    '''Tests CxReports.update_results'''
    result = CxReports.update_results(10915,1)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_last_scan.call_count == 1
    assert ex_func.call_count == 0
    assert ck_processed.call_count == 0
    assert log_ln.call_count == 2
    assert run_report.call_count == 1
    assert proc_report.call_count == 1
    assert up_sf.call_count == 1
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 2
    assert sql_ins.call_count == 1
    assert sql_del.call_count == 1
    assert auto_conf.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[(10915,),])
def test_cxreports_check_scan_processed(sql_sel,ex_sql):
    '''Tests CxReports.check_scan_processed'''
    result = CxReports.check_scan_processed(1,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == 0

@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
def test_cxreports_check_scan_processed_ex_csp_001(sql_sel,ex_sql):
    '''Tests CxReports.check_scan_processed'''
    result = CxReports.check_scan_processed(1,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.create_scan_report',
            return_value=12345)
def test_cxreports_run_cx_report(create_report,ex_func):
    '''Tests CxReports.run_cx_report'''
    result = CxReports.run_cx_report(1)
    assert create_report.call_count == 1
    assert ex_func.call_count == 0
    assert result == 12345

@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.create_scan_report',
            side_effect=Exception)
def test_cxreports_run_cx_report(create_report,ex_func):
    '''Tests CxReports.run_cx_report'''
    result = CxReports.run_cx_report(1)
    assert create_report.call_count == 1
    assert ex_func.call_count == 1
    assert result == None
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            return_value={'cxResultStateValue':2,'cxSimilarityID':-102394294,'cxCWEID':1,
                          'cxCWETitle':'title','cxCWEDescription':'cwe_desc','cxCWELink':
                          'cwe_link','cxLastScanDate':'2019-12-12 00:33:22'})
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            return_value='A description of the result.')
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            return_value=[{'SrcFileName':'file_name','Name':'name','Line':1,'Column':2,
                           'DestFileName':'file_name','DestName':'name','DestLine':4,'DestColumn':
                           23,'Link':'/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                           'Result Severity':'High','Result State':'Confirmed',
                           'Query':'query_name','Detection Date':'2023-08-22 00:55:34'}])
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            return_value=True)
def test_cxreports_scan_report_to_process(cx_complete,ex_func,g_scan_report,g_res_desc,det_by_path,
                                          sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 0
    assert g_scan_report.call_count == 1
    assert g_res_desc.call_count == 1
    assert det_by_path.call_count == 1
    assert sev_id.call_count == 1

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            return_value={'cxResultStateValue':2,'cxSimilarityID':-102394294,'cxCWEID':1,
                          'cxCWETitle':'title','cxCWEDescription':'cwe_desc','cxCWELink':
                          'cwe_link','cxLastScanDate':'2019-12-12 00:33:22'})
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            return_value='A description of the result.')
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            return_value=[{'SrcFileName':'file_name','Name':'name','Line':1,'Column':2,
                           'DestFileName':'file_name','DestName':'name','DestLine':4,'DestColumn':
                           23,'Link':'/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                           'Result Severity':'High','Result State':'Confirmed',
                           'Query':'query_name','Detection Date':'2023-08-22 00:55:34'}])
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            side_effect=Exception)
def test_cxreports_scan_report_to_process_ex_srtp_001(cx_complete,ex_func,g_scan_report,g_res_desc,
                                                      det_by_path,sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 1
    assert g_scan_report.call_count == 0
    assert g_res_desc.call_count == 0
    assert det_by_path.call_count == 0
    assert sev_id.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            return_value={'cxResultStateValue':2,'cxSimilarityID':-102394294,'cxCWEID':1,
                          'cxCWETitle':'title','cxCWEDescription':'cwe_desc','cxCWELink':
                          'cwe_link','cxLastScanDate':'2019-12-12 00:33:22'})
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            return_value='A description of the result.')
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            return_value=True)
def test_cxreports_scan_report_to_process_ex_srtp_002(cx_complete,ex_func,g_scan_report,g_res_desc,
                                                      det_by_path,sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 1
    assert g_scan_report.call_count == 1
    assert g_res_desc.call_count == 0
    assert det_by_path.call_count == 0
    assert sev_id.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            return_value={'cxResultStateValue':2,'cxSimilarityID':-102394294,'cxCWEID':1,
                          'cxCWETitle':'title','cxCWEDescription':'cwe_desc','cxCWELink':
                          'cwe_link','cxLastScanDate':'2019-12-12 00:33:22'})
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            return_value=[{'SrcFileName':'file_name','Name':'name','Line':1,'Column':2,
                           'DestFileName':'file_name','DestName':'name','DestLine':4,'DestColumn':
                           23,'Link':'/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                           'Result Severity':'High','Result State':'Confirmed',
                           'Query':'query_name','Detection Date':'2023-08-22 00:55:34'}])
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            return_value=True)
def test_cxreports_scan_report_to_process_ex_srtp_003(cx_complete,ex_func,g_scan_report,g_res_desc,
                                                      det_by_path,sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 1
    assert g_scan_report.call_count == 1
    assert g_res_desc.call_count == 1
    assert det_by_path.call_count == 0
    assert sev_id.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            return_value='A description of the result.')
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            return_value=[{'SrcFileName':'file_name','Name':'name','Line':1,'Column':2,
                           'DestFileName':'file_name','DestName':'name','DestLine':4,'DestColumn':
                           23,'Link':'/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                           'Result Severity':'High','Result State':'Confirmed',
                           'Query':'query_name','Detection Date':'2023-08-22 00:55:34'}])
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            return_value=True)
def test_cxreports_scan_report_to_process_ex_srtp_004(cx_complete,ex_func,g_scan_report,g_res_desc,
                                                      det_by_path,sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 1
    assert g_scan_report.call_count == 1
    assert g_res_desc.call_count == 1
    assert det_by_path.call_count == 1
    assert sev_id.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxCommon.get_severity_id',
            return_value=1)
@mock.patch('checkmarx.report_processing.CxAPI.get_finding_details_by_path',
            return_value={'cxResultStateValue':2,'cxSimilarityID':None,'cxCWEID':1,
                          'cxCWETitle':'title','cxCWEDescription':'cwe_desc','cxCWELink':
                          'cwe_link','cxLastScanDate':'2019-12-12 00:33:22'})
@mock.patch('checkmarx.report_processing.CxAPI.get_result_description',
            return_value='A description of the result.')
@mock.patch('checkmarx.report_processing.CxAPI.get_scan_report',
            return_value=[{'SrcFileName':'file_name','Name':'name','Line':1,'Column':2,
                           'DestFileName':'file_name','DestName':'name','DestLine':4,'DestColumn':
                           23,'Link':'/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                           'Result Severity':'High','Result State':'Confirmed',
                           'Query':'query_name','Detection Date':'2023-08-22 00:55:34'}])
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.scan_report_complete',
            return_value=True)
def test_cxreports_scan_report_to_process_no_simid(cx_complete,ex_func,g_scan_report,g_res_desc,
                                                   det_by_path,sev_id):
    '''Tests CxReports.scan_report_to_process'''
    result = CxReports.scan_report_to_process(12345,10915,1)
    assert cx_complete.call_count == 1
    assert ex_func.call_count == 0
    assert g_scan_report.call_count == 1
    assert g_res_desc.call_count == 1
    assert det_by_path.call_count == 1
    assert sev_id.call_count == 1

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.insert_multiple_into_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','Not Exploitable','KEY-123','Not Exploitable',),])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
def test_cxreports_update_sastfindings_ne(sql_upd,ex_sql,sql_sel,mlti_upd,ex_func,mlti_ins,log_ln):
    '''Tests CxReports.update_sastfindings'''
    result = CxReports.update_sastfindings([{'cxResultState':'Confirmed','cxResultStateValue':3,
                                    'cxQuery':'Query','cxResultSeverity':'Critical',
                                    'cxResultSeverityValue':0,'cxLink':
                                    '/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                                    'cxSource':'source','SourceFile':'src_file','SourceObject':
                                    'src_obj','cxDestination':'destination','DestinationFile':
                                    'dest_file','DestinationObject':'dest_obj','cxResultID':
                                    '12345-6','cxResultDescription':'description',
                                    'cxDetectionDate':'2023-10-10','cxLastScanID':1,
                                    'cxLastScanDate':'2021-09-09 03:32:45','cxCWEID':1,
                                    'cxCWETitle':'title','cxCWEDescription':'cwe_description',
                                    'cxCWELink':'cwe_link','cxSimilarityID':312455}],10915,1,
                                    '2023-10-10')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert sql_sel.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert mlti_ins.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.insert_multiple_into_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','To Ticket',None,'Confirmed',),])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
def test_cxreports_update_sastfindings_to_ticket(sql_upd,ex_sql,sql_sel,mlti_upd,ex_func,mlti_ins,
                                                 log_ln):
    '''Tests CxReports.update_sastfindings'''
    result = CxReports.update_sastfindings([{'cxResultState':'Confirmed','cxResultStateValue':3,
                                    'cxQuery':'Query','cxResultSeverity':'Critical',
                                    'cxResultSeverityValue':0,'cxLink':
                                    '/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                                    'cxSource':'source','SourceFile':'src_file','SourceObject':
                                    'src_obj','cxDestination':'destination','DestinationFile':
                                    'dest_file','DestinationObject':'dest_obj','cxResultID':
                                    '12345-6','cxResultDescription':'description',
                                    'cxDetectionDate':'2023-10-10','cxLastScanID':1,
                                    'cxLastScanDate':'2021-09-09 03:32:45','cxCWEID':1,
                                    'cxCWETitle':'title','cxCWEDescription':'cwe_description',
                                    'cxCWELink':'cwe_link','cxSimilarityID':312455}],10915,1,
                                    '2023-10-10')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert sql_sel.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert mlti_ins.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.insert_multiple_into_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.select',
            return_value=[])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
def test_cxreports_update_sastfindings_insert(sql_upd,ex_sql,sql_sel,mlti_upd,ex_func,mlti_ins,log_ln):
    '''Tests CxReports.update_sastfindings'''
    result = CxReports.update_sastfindings([{'cxResultState':'Confirmed','cxResultStateValue':3,
                                    'cxQuery':'Query','cxResultSeverity':'Critical',
                                    'cxResultSeverityValue':0,'cxLink':
                                    '/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                                    'cxSource':'source','SourceFile':'src_file','SourceObject':
                                    'src_obj','cxDestination':'destination','DestinationFile':
                                    'dest_file','DestinationObject':'dest_obj','cxResultID':
                                    '12345-6','cxResultDescription':'description',
                                    'cxDetectionDate':'2023-10-10','cxLastScanID':1,
                                    'cxLastScanDate':'2021-09-09 03:32:45','cxCWEID':1,
                                    'cxCWETitle':'title','cxCWEDescription':'cwe_description',
                                    'cxCWELink':'cwe_link','cxSimilarityID':312455}],10915,1,
                                    '2023-10-10')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert sql_sel.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 0
    assert mlti_ins.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.insert_multiple_into_table')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('12345-6','Not Exploitable','KEY-123','Not Exploitable',),])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update',
            side_effect=Exception)
def test_cxreports_update_sastfindings_ex_us_001(sql_upd,ex_sql,sql_sel,mlti_upd,ex_func,mlti_ins,
                                                 log_ln):
    '''Tests CxReports.update_sastfindings'''
    result = CxReports.update_sastfindings([{'cxResultState':'Confirmed','cxResultStateValue':3,
                                    'cxQuery':'Query','cxResultSeverity':'Critical',
                                    'cxResultSeverityValue':0,'cxLink':
                                    '/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                                    'cxSource':'source','SourceFile':'src_file','SourceObject':
                                    'src_obj','cxDestination':'destination','DestinationFile':
                                    'dest_file','DestinationObject':'dest_obj','cxResultID':
                                    '12345-6','cxResultDescription':'description',
                                    'cxDetectionDate':'2023-10-10','cxLastScanID':1,
                                    'cxLastScanDate':'2021-09-09 03:32:45','cxCWEID':1,
                                    'cxCWETitle':'title','cxCWEDescription':'cwe_description',
                                    'cxCWELink':'cwe_link','cxSimilarityID':312455}],10915,1,
                                    '2023-10-10')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert sql_sel.call_count == 0
    assert mlti_upd.call_count == 0
    assert ex_func.call_count == 0
    assert mlti_ins.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
def test_cxreports_update_sastfindings_ex_us_002_003_004(sql_upd,ex_sql,sql_sel,mlti_upd,ex_func,
                                                         mlti_ins,log_ln):
    '''Tests CxReports.update_sastfindings'''
    result = CxReports.update_sastfindings([{'cxResultState':'Confirmed','cxResultStateValue':3,
                                    'cxQuery':'Query','cxResultSeverity':'Critical',
                                    'cxResultSeverityValue':0,'cxLink':
                                    '/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',
                                    'cxSource':'source','SourceFile':'src_file','SourceObject':
                                    'src_obj','cxDestination':'destination','DestinationFile':
                                    'dest_file','DestinationObject':'dest_obj','cxResultID':
                                    '12345-6','cxResultDescription':'description',
                                    'cxDetectionDate':'2023-10-10','cxLastScanID':1,
                                    'cxLastScanDate':'2021-09-09 03:32:45','cxCWEID':1,
                                    'cxCWETitle':'title','cxCWEDescription':'cwe_description',
                                    'cxCWELink':'cwe_link','cxSimilarityID':312455}],10915,1,
                                    '2023-10-10')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert sql_sel.call_count == 1
    assert mlti_upd.call_count == 1
    assert ex_func.call_count == 2
    assert mlti_ins.call_count == 1
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 3
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_update_finding_statuses(log_hl,sql_upd,ex_sql,log_ln):
    '''Tests CxReports.update_finding_statuses'''
    result = CxReports.update_finding_statuses(10915)
    assert log_hl.call_count == 1
    assert sql_upd.call_count == 13
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 11

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_update_finding_statuses_exceptions(log_hl,sql_upd,ex_sql,log_ln):
    '''Tests CxReports.update_finding_statuses'''
    result = CxReports.update_finding_statuses(10915)
    assert log_hl.call_count == 1
    assert sql_upd.call_count == 13
    assert ex_sql.call_count == 13
    assert log_ln.call_count == 11
    assert ScrVar.ex_cnt == 13
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_path_and_result_state',
            return_value={'cxPathId':1,'cxStateName':'To Verify'})
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[(213124214,12345,'KEY-123'),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_reset_closed_findings(log_hl,sql_sel,ex_sql,g_path_state,ex_func,u_state,
                                         add_tkt):
    '''Tests CxReports.reset_closed_findings'''
    result = CxReports.reset_closed_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_path_state.call_count == 1
    assert ex_func.call_count == 0
    assert u_state.call_count == 1
    assert add_tkt.call_count == 1

@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_path_and_result_state',
            return_value={'cxPathId':1,'cxStateName':'To Verify'})
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_reset_closed_findings_ex_rcf_001(log_hl,sql_sel,ex_sql,g_path_state,ex_func,
                                                    u_state,add_tkt):
    '''Tests CxReports.reset_closed_findings'''
    result = CxReports.reset_closed_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_path_state.call_count == 0
    assert ex_func.call_count == 0
    assert u_state.call_count == 0
    assert add_tkt.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_path_and_result_state',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[(213124214,12345,'KEY-123'),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_reset_closed_findings_ex_rcf_002(log_hl,sql_sel,ex_sql,g_path_state,ex_func,
                                                    u_state,add_tkt):
    '''Tests CxReports.reset_closed_findings'''
    result = CxReports.reset_closed_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_path_state.call_count == 1
    assert ex_func.call_count == 1
    assert u_state.call_count == 0
    assert add_tkt.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_path_and_result_state',
            return_value={'cxPathId':1,'cxStateName':'To Verify'})
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[(213124214,12345,'KEY-123'),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_reset_closed_findings_ex_rcf_003(log_hl,sql_sel,ex_sql,g_path_state,ex_func,
                                                        u_state,add_tkt):
    '''Tests CxReports.reset_closed_findings'''
    result = CxReports.reset_closed_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_path_state.call_count == 1
    assert ex_func.call_count == 1
    assert u_state.call_count == 1
    assert add_tkt.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.CxAPI.add_ticket_to_cx',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.CxAPI.update_res_state')
@mock.patch('checkmarx.report_processing.TheLogs.function_exception')
@mock.patch('checkmarx.report_processing.CxAPI.get_path_and_result_state',
            return_value={'cxPathId':1,'cxStateName':'To Verify'})
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[(213124214,12345,'KEY-123'),])
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_reset_closed_findings_ex_rcf_004(log_hl,sql_sel,ex_sql,g_path_state,ex_func,
                                                    u_state,add_tkt):
    '''Tests CxReports.reset_closed_findings'''
    result = CxReports.reset_closed_findings(10915)
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_path_state.call_count == 1
    assert ex_func.call_count == 1
    assert u_state.call_count == 1
    assert add_tkt.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update')
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_sync_ticket_closed_status(log_hl,sql_upd,ex_sql,log_ln):
    '''Tests CxReports.sync_ticket_closed_status'''
    result = CxReports.sync_ticket_closed_status(10915)
    assert log_hl.call_count == 2
    assert sql_upd.call_count == 2
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 2

@mock.patch('checkmarx.report_processing.TheLogs.log_info')
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.update',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.TheLogs.log_headline')
def test_cxreports_sync_ticket_closed_status_ex_stcs_001_002(log_hl,sql_upd,ex_sql,log_ln):
    '''Tests CxReports.sync_ticket_closed_status'''
    result = CxReports.sync_ticket_closed_status(None)
    assert log_hl.call_count == 2
    assert sql_upd.call_count == 2
    assert ex_sql.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.Alerts.manual_alert')
@mock.patch('checkmarx.report_processing.CxReports.get_alert_repos',
            return_value=[['repo'],['repo']])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('Query',),])
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_alert_on_findings_needing_manual_review(ex_reset,sql_sel,ex_sql,g_repos,
                                                           man_alert):
    '''Tests CxReports.alert_on_findings_needing_manual_review'''
    result = CxReports.alert_on_findings_needing_manual_review()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_repos.call_count == 1
    assert man_alert.call_count == 1

@mock.patch('checkmarx.report_processing.Alerts.manual_alert')
@mock.patch('checkmarx.report_processing.CxReports.get_alert_repos',
            return_value=[['repo'],['repo']])
@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
@mock.patch('checkmarx.report_processing.ScrVar.reset_exception_counts')
def test_cxreports_alert_on_findings_needing_manual_review_ex_aofnmr_001(ex_reset,sql_sel,ex_sql,
                                                                         g_repos,man_alert):
    '''Tests CxReports.alert_on_findings_needing_manual_review'''
    result = CxReports.alert_on_findings_needing_manual_review()
    assert ex_reset.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_repos.call_count == 0
    assert man_alert.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            return_value=[('appsec-ops')])
def test_cxreports_get_alert_repos(sql_sel,ex_sql):
    '''Tests CxReports.get_alert_repos'''
    CxReports.get_alert_repos('query_name')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('checkmarx.report_processing.TheLogs.sql_exception')
@mock.patch('checkmarx.report_processing.select',
            side_effect=Exception)
def test_cxreports_get_alert_repos_ex_gar_001(sql_sel,ex_sql):
    '''Tests CxReports.get_alert_repos'''
    CxReports.get_alert_repos('query_name')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
