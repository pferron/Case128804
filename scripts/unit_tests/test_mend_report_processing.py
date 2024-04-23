'''Unit tests for mend.report_processing '''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from mend.report_processing import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

@mock.patch('mend.report_processing.ScrVar.reset_exception_counts')
@mock.patch('mend.report_processing.reactivate_alerts')
@mock.patch('mend.report_processing.findings_to_close')
@mock.patch('mend.report_processing.process_past_due')
@mock.patch('mend.report_processing.process_not_exploitables')
@mock.patch('mend.report_processing.process_false_positives')
@mock.patch('mend.report_processing.process_no_fix_available')
@mock.patch('mend.report_processing.process_tech_debt')
@mock.patch('mend.report_processing.update_missing_data')
@mock.patch('mend.report_processing.sync_alerts_to_findings')
@mock.patch('mend.report_processing.sync_license_violations')
@mock.patch('mend.report_processing.sync_mend_alerts')
@mock.patch('mend.report_processing.mend_vulnerability_report')
@mock.patch('mend.report_processing.MendAPI.apply_product_policies',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.reactivate_manually_ignored_alerts',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.get_product_token',
            return_value='the_token')
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_mendreports_single_repo_updates(log_hl,g_token,react_mi,ex_func,log_ln,apply_plcy,
                                         rep_vuln,sync_alerts,sync_lv,u_findings,u_missing,
                                         p_td,p_nfa,p_fp,p_ne,p_pd,to_close,react_al,ex_reset):
    '''Test MendReports.single_repo_updates'''
    MendReports.single_repo_updates('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 3
    assert g_token.call_count == 1
    assert react_mi.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 2
    assert apply_plcy.call_count == 1
    assert rep_vuln.call_count == 1
    assert sync_alerts.call_count == 1
    assert sync_lv.call_count == 1
    assert u_findings.call_count == 1
    assert u_missing.call_count == 1
    assert p_td.call_count == 1
    assert p_nfa.call_count == 1
    assert p_fp.call_count == 1
    assert p_ne.call_count == 1
    assert p_pd.call_count == 1
    assert to_close.call_count == 1
    assert react_al.call_count == 1

@mock.patch('mend.report_processing.ScrVar.reset_exception_counts')
@mock.patch('mend.report_processing.reactivate_alerts')
@mock.patch('mend.report_processing.findings_to_close')
@mock.patch('mend.report_processing.process_past_due')
@mock.patch('mend.report_processing.process_not_exploitables')
@mock.patch('mend.report_processing.process_false_positives')
@mock.patch('mend.report_processing.process_no_fix_available')
@mock.patch('mend.report_processing.process_tech_debt')
@mock.patch('mend.report_processing.update_missing_data')
@mock.patch('mend.report_processing.sync_alerts_to_findings')
@mock.patch('mend.report_processing.sync_license_violations')
@mock.patch('mend.report_processing.sync_mend_alerts')
@mock.patch('mend.report_processing.mend_vulnerability_report')
@mock.patch('mend.report_processing.MendAPI.apply_product_policies')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.reactivate_manually_ignored_alerts')
@mock.patch('mend.report_processing.ReportQueries.get_product_token',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_mendreports_single_repo_updatesex_sru_001(log_hl,g_token,react_mi,ex_func,log_ln,
                                                   apply_plcy,rep_vuln,sync_alerts,sync_lv,
                                                   u_findings,u_missing,p_td,p_nfa,p_fp,p_ne,p_pd,
                                                   to_close,react_al,ex_reset):
    '''Test MendReports.single_repo_updates'''
    MendReports.single_repo_updates('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_token.call_count == 1
    assert react_mi.call_count == 0
    assert ex_func.call_count == 1
    assert log_ln.call_count == 0
    assert apply_plcy.call_count == 0
    assert rep_vuln.call_count == 0
    assert sync_alerts.call_count == 0
    assert sync_lv.call_count == 0
    assert u_findings.call_count == 0
    assert u_missing.call_count == 0
    assert p_td.call_count == 0
    assert p_nfa.call_count == 0
    assert p_fp.call_count == 0
    assert p_ne.call_count == 0
    assert p_pd.call_count == 0
    assert to_close.call_count == 0
    assert react_al.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.ScrVar.reset_exception_counts')
@mock.patch('mend.report_processing.reactivate_alerts')
@mock.patch('mend.report_processing.findings_to_close')
@mock.patch('mend.report_processing.process_past_due')
@mock.patch('mend.report_processing.process_not_exploitables')
@mock.patch('mend.report_processing.process_false_positives')
@mock.patch('mend.report_processing.process_no_fix_available')
@mock.patch('mend.report_processing.process_tech_debt')
@mock.patch('mend.report_processing.update_missing_data')
@mock.patch('mend.report_processing.sync_alerts_to_findings')
@mock.patch('mend.report_processing.sync_license_violations')
@mock.patch('mend.report_processing.sync_mend_alerts')
@mock.patch('mend.report_processing.mend_vulnerability_report')
@mock.patch('mend.report_processing.MendAPI.apply_product_policies')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.reactivate_manually_ignored_alerts',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.get_product_token',
            return_value='the_token')
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_mendreports_single_repo_updatesex_sru_002(log_hl,g_token,react_mi,ex_func,log_ln,
                                                   apply_plcy,rep_vuln,sync_alerts,sync_lv,
                                                   u_findings,u_missing,p_td,p_nfa,p_fp,p_ne,p_pd,
                                                   to_close,react_al,ex_reset):
    '''Test MendReports.single_repo_updates'''
    MendReports.single_repo_updates('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 2
    assert g_token.call_count == 1
    assert react_mi.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 0
    assert apply_plcy.call_count == 0
    assert rep_vuln.call_count == 0
    assert sync_alerts.call_count == 0
    assert sync_lv.call_count == 0
    assert u_findings.call_count == 0
    assert u_missing.call_count == 0
    assert p_td.call_count == 0
    assert p_nfa.call_count == 0
    assert p_fp.call_count == 0
    assert p_ne.call_count == 0
    assert p_pd.call_count == 0
    assert to_close.call_count == 0
    assert react_al.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.ScrVar.reset_exception_counts')
@mock.patch('mend.report_processing.reactivate_alerts')
@mock.patch('mend.report_processing.findings_to_close')
@mock.patch('mend.report_processing.process_past_due')
@mock.patch('mend.report_processing.process_not_exploitables')
@mock.patch('mend.report_processing.process_false_positives')
@mock.patch('mend.report_processing.process_no_fix_available')
@mock.patch('mend.report_processing.process_tech_debt')
@mock.patch('mend.report_processing.update_missing_data')
@mock.patch('mend.report_processing.sync_alerts_to_findings')
@mock.patch('mend.report_processing.sync_license_violations')
@mock.patch('mend.report_processing.sync_mend_alerts')
@mock.patch('mend.report_processing.mend_vulnerability_report')
@mock.patch('mend.report_processing.MendAPI.apply_product_policies',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.reactivate_manually_ignored_alerts',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.get_product_token',
            return_value='the_token')
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_mendreports_single_repo_updatesex_sru_003(log_hl,g_token,react_mi,ex_func,log_ln,
                                                   apply_plcy,rep_vuln,sync_alerts,sync_lv,
                                                   u_findings,u_missing,p_td,p_nfa,p_fp,p_ne,p_pd,
                                                   to_close,react_al,ex_reset):
    '''Test MendReports.single_repo_updates'''
    MendReports.single_repo_updates('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 3
    assert g_token.call_count == 1
    assert react_mi.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 1
    assert apply_plcy.call_count == 1
    assert rep_vuln.call_count == 0
    assert sync_alerts.call_count == 0
    assert sync_lv.call_count == 0
    assert u_findings.call_count == 0
    assert u_missing.call_count == 0
    assert p_td.call_count == 0
    assert p_nfa.call_count == 0
    assert p_fp.call_count == 0
    assert p_ne.call_count == 0
    assert p_pd.call_count == 0
    assert to_close.call_count == 0
    assert react_al.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=0)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.alert_exists',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.get_alerts',
            return_value=[{'ProjectToken':'token','ProjectName':'name','KeyUuid':'uuid',
                           'AlertUuid':'uuid','DateDetected':'2023-10-10','AlertStatus':'status',
                           'InOSFindings':1,'JiraIssueKey':'AS-1234','Comments':'comments',
                           'ProjectId':'id','Library':'library','Severity':'severity',
                           'PolicyViolated':'policy'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_mend_alerts_update(log_hl,g_alerts,ex_func,exists,mlti_upd,log_ln,mlti_ins):
    '''Tests sync_mend_alerts'''
    sync_mend_alerts('appsec-ops','the_token')
    assert log_hl.call_count == 1
    assert g_alerts.call_count == 1
    assert ex_func.call_count == 0
    assert exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=1)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=0)
@mock.patch('mend.report_processing.ReportQueries.alert_exists',
            return_value=False)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.get_alerts',
            return_value=[{'ProjectToken':'token','ProjectName':'name','KeyUuid':'uuid',
                           'AlertUuid':'uuid','DateDetected':'2023-10-10','AlertStatus':'status',
                           'InOSFindings':1,'JiraIssueKey':'AS-1234','Comments':'comments',
                           'ProjectId':'id','Library':'library','Severity':'severity',
                           'PolicyViolated':'policy'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_mend_alerts_insert(log_hl,g_alerts,ex_func,exists,mlti_upd,log_ln,mlti_ins):
    '''Tests sync_mend_alerts'''
    sync_mend_alerts('appsec-ops','the_token')
    assert log_hl.call_count == 1
    assert g_alerts.call_count == 1
    assert ex_func.call_count == 0
    assert exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1

@mock.patch('mend.report_processing.insert_multiple_into_table')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.ReportQueries.alert_exists')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.get_alerts',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_mend_alerts_ex_sma_001(log_hl,g_alerts,ex_func,exists,mlti_upd,log_ln,mlti_ins):
    '''Tests sync_mend_alerts'''
    sync_mend_alerts('appsec-ops','the_token')
    assert log_hl.call_count == 1
    assert g_alerts.call_count == 1
    assert ex_func.call_count == 1
    assert exists.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert mlti_ins.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.alert_exists',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.MendAPI.get_alerts',
            return_value=[{'ProjectToken':'token','ProjectName':'name','KeyUuid':'uuid',
                           'AlertUuid':'uuid','DateDetected':'2023-10-10','AlertStatus':'status',
                           'InOSFindings':1,'JiraIssueKey':'AS-1234','Comments':'comments',
                           'ProjectId':'id','Library':'library','Severity':'severity',
                           'PolicyViolated':'policy'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_mend_alerts_ex_sma_002_003_004(log_hl,g_alerts,ex_func,exists,mlti_upd,log_ln,
                                             mlti_ins):
    '''Tests sync_mend_alerts'''
    sync_mend_alerts('appsec-ops','the_token')
    assert log_hl.call_count == 1
    assert g_alerts.call_count == 1
    assert ex_func.call_count == 3
    assert exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 3
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_sync',
            return_value=[('ProjectName','KeyUuid','Unapproved Licenses','AlertUuid',
                           'AlertStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_alerts_to_findings(log_hl,g_sync,ex_func,mlti_upd,log_ln):
    '''Tests sync_alerts_to_findings'''
    sync_alerts_to_findings('appsec-ops')
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert ex_func.call_count == 0
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_sync',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_alerts_to_findings_ex_satf_001(log_hl,g_sync,ex_func,mlti_upd,log_ln):
    '''Tests sync_alerts_to_findings'''
    sync_alerts_to_findings('appsec-ops')
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert ex_func.call_count == 1
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_sync',
            return_value=[('ProjectName','KeyUuid','Unapproved Licenses','AlertUuid',
                           'Library removed',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_alerts_to_findings_ex_satf_002(log_hl,g_sync,ex_func,mlti_upd,log_ln):
    '''Tests sync_alerts_to_findings'''
    sync_alerts_to_findings('appsec-ops')
    assert log_hl.call_count == 1
    assert g_sync.call_count == 1
    assert ex_func.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=0)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.get_ticket_by_finding_type',
            return_value=[('AS-1234',),])
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_lv')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_license_violations',
            return_value=[('ProjectName','ProjectId','Severity','Library','KeyUuid','AlertUuid',
                           'AlertStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_license_violations(log_hl,g_lv,ex_func,res_lv,g_tkt,mlti_upd,log_ln,mlti_ins):
    '''Tests sync_license_violations'''
    sync_license_violations('appsec-ops','token')
    assert log_hl.call_count == 1
    assert g_lv.call_count == 1
    assert ex_func.call_count == 0
    assert res_lv.call_count == 1
    assert g_tkt.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('mend.report_processing.insert_multiple_into_table')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.ReportQueries.get_ticket_by_finding_type')
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_lv')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_license_violations',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_license_violations_ex_slv_001(log_hl,g_lv,ex_func,res_lv,g_tkt,mlti_upd,log_ln,
                                            mlti_ins):
    '''Tests sync_license_violations'''
    sync_license_violations('appsec-ops','token')
    assert log_hl.call_count == 1
    assert g_lv.call_count == 1
    assert ex_func.call_count == 1
    assert res_lv.call_count == 0
    assert g_tkt.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert mlti_ins.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.ReportQueries.get_ticket_by_finding_type')
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_lv',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_license_violations',
            return_value=[('ProjectName','ProjectId','Severity','Library','KeyUuid','AlertUuid',
                           'AlertStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_license_violations_ex_slv_002(log_hl,g_lv,ex_func,res_lv,g_tkt,mlti_upd,log_ln,
                                            mlti_ins):
    '''Tests sync_license_violations'''
    sync_license_violations('appsec-ops','token')
    assert log_hl.call_count == 1
    assert g_lv.call_count == 1
    assert ex_func.call_count == 1
    assert res_lv.call_count == 1
    assert g_tkt.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert mlti_ins.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=0)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.get_ticket_by_finding_type',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_lv')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_license_violations',
            return_value=[('ProjectName','ProjectId','Severity','Library','KeyUuid','AlertUuid',
                           'AlertStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_license_violations_ex_slv_003(log_hl,g_lv,ex_func,res_lv,g_tkt,mlti_upd,log_ln,
                                            mlti_ins):
    '''Tests sync_license_violations'''
    sync_license_violations('appsec-ops','token')
    assert log_hl.call_count == 1
    assert g_lv.call_count == 1
    assert ex_func.call_count == 1
    assert res_lv.call_count == 1
    assert g_tkt.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 3
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.get_ticket_by_finding_type',
            return_value=[])
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_lv')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_license_violations',
            return_value=[('ProjectName','ProjectId','Severity','Library','KeyUuid','AlertUuid',
                           'OtherStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_sync_license_violations_ex_slv_004_005_006(log_hl,g_lv,ex_func,res_lv,g_tkt,mlti_upd,
                                                    log_ln,mlti_ins):
    '''Tests sync_license_violations'''
    sync_license_violations('appsec-ops','token')
    assert log_hl.call_count == 1
    assert g_lv.call_count == 1
    assert ex_func.call_count == 3
    assert res_lv.call_count == 1
    assert g_tkt.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 3
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 3
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.get_missing_fields',
            return_value={'GroupId':'group_id','Version':'version',
                          'LicenseViolations':'licenses','LibraryLocations':'locations'})
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_libraries_missing_data',
            return_value=[('wsProjectToken','Library','ProjectName','KeyUuid',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_update_missing_data(log_hl,g_md,ex_func,g_mf,mlti_upd,log_ln):
    '''Tests update_missing_data'''
    update_missing_data('appsec-ops')
    assert log_hl.call_count == 1
    assert g_md.call_count == 1
    assert ex_func.call_count == 0
    assert g_mf.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.get_missing_fields')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_libraries_missing_data',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_update_missing_data_ex_umd_001(log_hl,g_md,ex_func,g_mf,mlti_upd,log_ln):
    '''Tests update_missing_data'''
    update_missing_data('appsec-ops')
    assert log_hl.call_count == 1
    assert g_md.call_count == 1
    assert ex_func.call_count == 1
    assert g_mf.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.get_missing_fields',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_libraries_missing_data',
            return_value=[('wsProjectToken','Library','ProjectName','KeyUuid',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_update_missing_data_ex_umd_002(log_hl,g_md,ex_func,g_mf,mlti_upd,log_ln):
    '''Tests update_missing_data'''
    update_missing_data('appsec-ops')
    assert log_hl.call_count == 1
    assert g_md.call_count == 1
    assert ex_func.call_count == 1
    assert g_mf.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.get_missing_fields',
            return_value={'GroupId':'group_id','Version':'version',
                          'LicenseViolations':'licenses','LibraryLocations':'locations'})
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_libraries_missing_data',
            return_value=[('wsProjectToken','Library','ProjectName','KeyUuid',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_update_missing_data_ex_umd_003_004(log_hl,g_md,ex_func,g_mf,mlti_upd,log_ln):
    '''Tests update_missing_data'''
    update_missing_data('appsec-ops')
    assert log_hl.call_count == 1
    assert g_md.call_count == 1
    assert ex_func.call_count == 2
    assert g_mf.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=1)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln',
            return_value=True)
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln')
@mock.patch('mend.report_processing.MendAPI.vulnerability_report',
            return_value=[{"Severity":'severity',"SeverityValue":'sev_value',"ProjectName":'pj_n',
                           "ProjectId":'pj_id',"Library":'lib',"GroupId":'g_id',"KeyUuid":
                           'key_uuid',"Version":'version',"VulnPublishDate":'v_date',
                           "Vulnerability":'v_name',"VulnerabilityUrl":'v_url',"Remediation":'fix',
                           "ResultingShield":'shield'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            return_value=[('ProjectName','Token',),])
def test_mend_vulnerability_report(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                   vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 1
    assert vuln_rep.call_count == 1
    assert res_vulns.call_count == 1
    assert vuln_exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1

@mock.patch('mend.report_processing.insert_multiple_into_table')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln')
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln')
@mock.patch('mend.report_processing.MendAPI.vulnerability_report')
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            side_effect=Exception)
def test_mend_vulnerability_report_ex_mvr_001(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                              vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 0
    assert vuln_rep.call_count == 0
    assert res_vulns.call_count == 0
    assert vuln_exists.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert mlti_ins.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln')
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln')
@mock.patch('mend.report_processing.MendAPI.vulnerability_report',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            return_value=[('ProjectName','Token',),])
def test_mend_vulnerability_report_ex_mvr_002(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                              vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert vuln_rep.call_count == 1
    assert res_vulns.call_count == 0
    assert vuln_exists.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert mlti_ins.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=1)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln',
            return_value=False)
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.vulnerability_report',
            return_value=[{"Severity":'severity',"SeverityValue":'sev_value',"ProjectName":'pj_n',
                           "ProjectId":'pj_id',"Library":'lib',"GroupId":'g_id',"KeyUuid":
                           'key_uuid',"Version":'version',"VulnPublishDate":'v_date',
                           "Vulnerability":'v_name',"VulnerabilityUrl":'v_url',"Remediation":'fix',
                           "ResultingShield":'shield'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            return_value=[('ProjectName','Token',),])
def test_mend_vulnerability_report_ex_mvr_003(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                              vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert vuln_rep.call_count == 1
    assert res_vulns.call_count == 1
    assert vuln_exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            return_value=1)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln')
@mock.patch('mend.report_processing.MendAPI.vulnerability_report',
            return_value=[{"Severity":'severity',"SeverityValue":'sev_value',"ProjectName":'pj_n',
                           "ProjectId":'pj_id',"Library":'lib',"GroupId":'g_id',"KeyUuid":
                           'key_uuid',"Version":'version',"VulnPublishDate":'v_date',
                           "Vulnerability":'v_name',"VulnerabilityUrl":'v_url',"Remediation":'fix',
                           "ResultingShield":'shield'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            return_value=[('ProjectName','Token',),])
def test_mend_vulnerability_report_ex_mvr_004(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                              vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert vuln_rep.call_count == 1
    assert res_vulns.call_count == 1
    assert vuln_exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.check_if_finding_exists_vuln',
            return_value=True)
@mock.patch('mend.report_processing.ReportQueries.reset_found_in_last_scan_vuln')
@mock.patch('mend.report_processing.MendAPI.vulnerability_report',
            return_value=[{"Severity":'severity',"SeverityValue":'sev_value',"ProjectName":'pj_n',
                           "ProjectId":'pj_id',"Library":'lib',"GroupId":'g_id',"KeyUuid":
                           'key_uuid',"Version":'version',"VulnPublishDate":'v_date',
                           "Vulnerability":'v_name',"VulnerabilityUrl":'v_url',"Remediation":'fix',
                           "ResultingShield":'shield'}])
@mock.patch('mend.report_processing.TheLogs.log_headline')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_project_info',
            return_value=[('ProjectName','Token',),])
def test_mend_vulnerability_report_ex_mvr_005_006(g_proj,ex_func,log_hl,vuln_rep,res_vulns,
                                                  vuln_exists,mlti_upd,log_ln,mlti_ins):
    '''Tests mend_vulnerability_report'''
    mend_vulnerability_report('appsec-ops','token')
    assert g_proj.call_count == 1
    assert ex_func.call_count == 2
    assert log_hl.call_count == 1
    assert vuln_rep.call_count == 1
    assert res_vulns.call_count == 1
    assert vuln_exists.call_count == 1
    assert mlti_upd.call_count == 1
    assert log_ln.call_count == 2
    assert mlti_ins.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_active_tech_debt',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_tech_debt(log_hl,g_td,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_tech_debt'''
    process_tech_debt('appsec-ops')
    assert log_hl.call_count == 1
    assert g_td.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_active_tech_debt',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_tech_debt_ex_ptd_001(log_hl,g_td,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_tech_debt'''
    process_tech_debt('appsec-ops')
    assert log_hl.call_count == 1
    assert g_td.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_active_tech_debt',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_tech_debt_ex_ptd_002(log_hl,g_td,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_tech_debt'''
    process_tech_debt('appsec-ops')
    assert log_hl.call_count == 1
    assert g_td.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_active_tech_debt',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_tech_debt_ex_ptd_003_004(log_hl,g_td,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_tech_debt'''
    process_tech_debt('appsec-ops')
    assert log_hl.call_count == 1
    assert g_td.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            return_value='AS')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_close_tkt(log_hl,g_nf,ex_func,u_status,tkt_close,
                                            mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert tkt_close.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 1
    assert g_key.call_count == 1
    assert tool_repo_upd.call_count == 1

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            return_value='AS')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket')
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','Closed',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_tkt_already_closed(log_hl,g_nf,ex_func,u_status,tkt_close,
                                                     mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert tkt_close.call_count == 0
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 1
    assert g_key.call_count == 1
    assert tool_repo_upd.call_count == 1

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_ex_pnfa_001(log_hl,g_nf,ex_func,u_status,tkt_close,
                                              mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert tkt_close.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert clear_nf.call_count == 0
    assert g_key.call_count == 0
    assert tool_repo_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            return_value='AS')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=0)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket')
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_ex_pnfa_002(log_hl,g_nf,ex_func,u_status,tkt_close,
                                              mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert tkt_close.call_count == 0
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 0
    assert g_key.call_count == 0
    assert tool_repo_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            return_value='AS')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=0)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_ex_pnfa_003(log_hl,g_nf,ex_func,u_status,tkt_close,
                                              mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert tkt_close.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 0
    assert g_key.call_count == 0
    assert tool_repo_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            return_value='AS')
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available')
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=False)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_ex_pnfa_004_005(log_hl,g_nf,ex_func,u_status,tkt_close,
                                                  mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert tkt_close.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 0
    assert g_key.call_count == 0
    assert tool_repo_upd.call_count == 0
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.report_processing.ReportQueries.get_project_key',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.clear_no_fix_available',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_no_fix_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_no_fix_available_ex_pnfa_006_007(log_hl,g_nf,ex_func,u_status,tkt_close,
                                                  mlti_upd,log_ln,clear_nf,g_key,tool_repo_upd):
    '''Tests process_no_fix_available'''
    process_no_fix_available('appsec-ops')
    assert log_hl.call_count == 1
    assert g_nf.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert tkt_close.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert clear_nf.call_count == 1
    assert g_key.call_count == 1
    assert tool_repo_upd.call_count == 0
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_false_positives_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_false_positives(log_hl,g_fp,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_false_positives'''
    process_false_positives('appsec-ops')
    assert log_hl.call_count == 1
    assert g_fp.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_false_positives_active',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_false_positivesex_pfp_001(log_hl,g_fp,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_false_positives'''
    process_false_positives('appsec-ops')
    assert log_hl.call_count == 1
    assert g_fp.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_false_positives_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_false_positivesex_pfp_002(log_hl,g_fp,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_false_positives'''
    process_false_positives('appsec-ops')
    assert log_hl.call_count == 1
    assert g_fp.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_false_positives_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_false_positivesex_pfp_003_004(log_hl,g_fp,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_false_positives'''
    process_false_positives('appsec-ops')
    assert log_hl.call_count == 1
    assert g_fp.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_not_exploitables_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_not_exploitables(log_hl,g_ne,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_not_exploitables'''
    process_not_exploitables('appsec-ops')
    assert log_hl.call_count == 1
    assert g_ne.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_not_exploitables_active',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_not_exploitables_ex_pne_001(log_hl,g_ne,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_not_exploitables'''
    process_not_exploitables('appsec-ops')
    assert log_hl.call_count == 1
    assert g_ne.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_not_exploitables_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_not_exploitables_ex_pne_002(log_hl,g_ne,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_not_exploitables'''
    process_not_exploitables('appsec-ops')
    assert log_hl.call_count == 1
    assert g_ne.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_not_exploitables_active',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_not_exploitables_ex_pne_003_004(log_hl,g_ne,ex_func,u_status,mlti_upd,log_ln):
    '''Tests process_not_exploitables'''
    process_not_exploitables('appsec-ops')
    assert log_hl.call_count == 1
    assert g_ne.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 0
    assert g_findings.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding',
            return_value=[])
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due_no_reactivate(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 0
    assert g_findings.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due_ex_ppd_001(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 1
    assert g_findings.call_count == 0
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due_ex_ppd_002(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 1
    assert g_findings.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due_ex_ppd_003(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 1
    assert g_findings.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.ReportQueries.get_past_due_finding',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_past_due_tickets',
            return_value=[('AS-1234','2023-10-10',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_process_past_due_ex_ppd_004_005(log_hl,g_pd,ex_func,g_findings,u_status,mlti_upd,log_ln):
    '''Tests process_past_due'''
    process_past_due('appsec-ops')
    assert log_hl.call_count == 1
    assert g_pd.call_count == 1
    assert ex_func.call_count == 2
    assert g_findings.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_reactivate',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_reactivate_alerts(log_hl,g_react,ex_func,u_status,mlti_upd,log_ln):
    '''Tests reactivate_alerts'''
    reactivate_alerts('appsec-ops')
    assert log_hl.call_count == 1
    assert g_react.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_reactivate',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_reactivate_alerts_ex_ra_001(log_hl,g_react,ex_func,u_status,mlti_upd,log_ln):
    '''Tests reactivate_alerts'''
    reactivate_alerts('appsec-ops')
    assert log_hl.call_count == 1
    assert g_react.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_reactivate',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_reactivate_alerts_ex_ra_002(log_hl,g_react,ex_func,u_status,mlti_upd,log_ln):
    '''Tests reactivate_alerts'''
    reactivate_alerts('appsec-ops')
    assert log_hl.call_count == 1
    assert g_react.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_alerts_to_reactivate',
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid',
                           'AlertStatus','JiraIssueKey',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_reactivate_alerts_ex_ra_003_004(log_hl,g_react,ex_func,u_status,mlti_upd,log_ln):
    '''Tests reactivate_alerts'''
    reactivate_alerts('appsec-ops')
    assert log_hl.call_count == 1
    assert g_react.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_findings_to_close',
            return_value=[('ProjectName','wsProjectToken','AlertUuid','AlertStatus',
                           'JiraIssueKey','KeyUuid','FindingType',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_findings_to_close(log_hl,g_tc,ex_func,u_status,mlti_upd,log_ln):
    '''Tests findings_to_close'''
    findings_to_close('appsec-ops')
    assert log_hl.call_count == 1
    assert g_tc.call_count == 1
    assert ex_func.call_count == 0
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table')
@mock.patch('mend.report_processing.MendAPI.update_alert_status')
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_findings_to_close',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_findings_to_close_ex_ftc_001(log_hl,g_tc,ex_func,u_status,mlti_upd,log_ln):
    '''Tests findings_to_close'''
    findings_to_close('appsec-ops')
    assert log_hl.call_count == 1
    assert g_tc.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 0
    assert mlti_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            return_value=1)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_findings_to_close',
            return_value=[('ProjectName','wsProjectToken','AlertUuid','AlertStatus',
                           'JiraIssueKey','KeyUuid','FindingType',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_findings_to_close_ex_ftc_002(log_hl,g_tc,ex_func,u_status,mlti_upd,log_ln):
    '''Tests findings_to_close'''
    findings_to_close('appsec-ops')
    assert log_hl.call_count == 1
    assert g_tc.call_count == 1
    assert ex_func.call_count == 1
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.report_processing.TheLogs.log_info')
@mock.patch('mend.report_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('mend.report_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.report_processing.TheLogs.function_exception')
@mock.patch('mend.report_processing.ReportQueries.get_findings_to_close',
            return_value=[('ProjectName','wsProjectToken','AlertUuid','AlertStatus',
                           'JiraIssueKey','KeyUuid','FindingType',),])
@mock.patch('mend.report_processing.TheLogs.log_headline')
def test_findings_to_close_ex_ftc_003_004(log_hl,g_tc,ex_func,u_status,mlti_upd,log_ln):
    '''Tests findings_to_close'''
    findings_to_close('appsec-ops')
    assert log_hl.call_count == 1
    assert g_tc.call_count == 1
    assert ex_func.call_count == 2
    assert u_status.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
