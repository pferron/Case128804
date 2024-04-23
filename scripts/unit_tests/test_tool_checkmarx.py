'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
from tool_checkmarx import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('tool_checkmarx.all_cx_updates')
def test_main_function_only(all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\tool_checkmarx.py','all_cx_updates']
    with mock.patch.object(sys, "argv", testargs):
        main()
        assert all_updates.call_count == 1

@mock.patch('tool_checkmarx.single_project_updates')
def test_main_function_with_vars(all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\tool_checkmarx.py',"single_project_updates(appsec-ops,10915)"]
    with mock.patch.object(sys, "argv", testargs):
        main()
        assert all_updates.call_count == 1

def test_scrvar_update_exception_info():
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info({'FatalCount':5,'ExceptionCount':1})
    assert ScrVar.fe_cnt == 5
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.ScrVar.get_cx_availability',
            return_value=True)
@mock.patch('tool_checkmarx.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer,cx_avail,l_hl,ex_func):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 0
    assert ex_func.call_count == 0

@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.ScrVar.get_cx_availability',
            return_value=False)
@mock.patch('tool_checkmarx.Misc.start_timer')
def test_scrvar_timed_script_setup_cx_down(s_timer,cx_avail,l_hl,ex_func):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('tool_checkmarx.TheLogs.process_exception_count_only')
@mock.patch('tool_checkmarx.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.CxAPI.checkmarx_availability',return_value=True)
def test_scrvar_get_cx_availability(cx_avail,ex_func,log_hl):
    '''Tests ScrVar.get_cx_availability'''
    result = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 0
    assert result is True

@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.CxAPI.checkmarx_availability',return_value=False)
def test_scrvar_get_cx_availability_connection_failure(cx_avail,ex_func,log_hl):
    '''Tests ScrVar.get_cx_availability'''
    result = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert result is False

@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.CxAPI.checkmarx_availability',side_effect=Exception)
def test_scrvar_get_cx_availability_ex_gca_002(cx_avail,ex_func,log_hl):
    '''Tests ScrVar.get_cx_availability'''
    result = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 0
    assert result is False

@mock.patch('tool_checkmarx.TheLogs.process_exception_count_only')
@mock.patch('tool_checkmarx.CxPipelines.sync_findings_to_pipeline')
@mock.patch('tool_checkmarx.CxTicketing.close_or_cancel_tickets')
@mock.patch('tool_checkmarx.CxTicketing.add_tickets_to_cx')
@mock.patch('tool_checkmarx.CxTicketing.create_and_update_tickets')
@mock.patch('tool_checkmarx.CxTicketing.create_and_update_tickets_by_query_src_and_dest')
@mock.patch('tool_checkmarx.CxTicketing.close_or_cancel_not_exploitable')
@mock.patch('tool_checkmarx.CxTicketing.can_ticket',return_value={'Results':True})
@mock.patch('tool_checkmarx.CxReports.update_all_baseline_states')
@mock.patch('tool_checkmarx.CxReports.update_finding_statuses')
@mock.patch('tool_checkmarx.CxReports.update_results')
@mock.patch('tool_checkmarx.ScrVar.update_exception_info')
@mock.patch('tool_checkmarx.update_jira_project_tickets')
def test_single_project_updates(u_jiraissues,u_ex_info,u_results,u_statuses,u_states,can_tkt,
                                close_cancel_ne,c_u_four,c_u_other,tkt_cx,close_cancel_other,
                                pl_sync,proc_ex):
    '''Tests single_project_updates'''
    single_project_updates('appsec-ops',10915,1)
    assert u_jiraissues.call_count == 2
    assert u_ex_info.call_count == 11
    assert u_results.call_count == 1
    assert u_statuses.call_count == 1
    assert u_states.call_count == 1
    assert can_tkt.call_count == 1
    assert close_cancel_ne.call_count == 1
    assert c_u_four.call_count == 0
    assert c_u_other.call_count == 1
    assert tkt_cx.call_count == 1
    assert close_cancel_other.call_count == 1
    assert pl_sync.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('tool_checkmarx.TheLogs.process_exception_count_only')
@mock.patch('tool_checkmarx.CxPipelines.sync_findings_to_pipeline')
@mock.patch('tool_checkmarx.CxTicketing.close_or_cancel_tickets')
@mock.patch('tool_checkmarx.CxTicketing.add_tickets_to_cx')
@mock.patch('tool_checkmarx.CxTicketing.create_and_update_tickets')
@mock.patch('tool_checkmarx.CxTicketing.create_and_update_tickets_by_query_src_and_dest')
@mock.patch('tool_checkmarx.CxTicketing.close_or_cancel_not_exploitable')
@mock.patch('tool_checkmarx.CxTicketing.can_ticket',return_value={'Results':True})
@mock.patch('tool_checkmarx.CxReports.update_all_baseline_states')
@mock.patch('tool_checkmarx.CxReports.update_finding_statuses')
@mock.patch('tool_checkmarx.CxReports.update_results')
@mock.patch('tool_checkmarx.ScrVar.update_exception_info')
@mock.patch('tool_checkmarx.update_jira_project_tickets')
def test_single_project_updates_four(u_jiraissues,u_ex_info,u_results,u_statuses,u_states,can_tkt,
                                close_cancel_ne,c_u_four,c_u_other,tkt_cx,close_cancel_other,
                                pl_sync,proc_ex):
    '''Tests single_project_updates'''
    single_project_updates('four',10519,1)
    assert u_jiraissues.call_count == 2
    assert u_ex_info.call_count == 11
    assert u_results.call_count == 1
    assert u_statuses.call_count == 1
    assert u_states.call_count == 1
    assert can_tkt.call_count == 1
    assert close_cancel_ne.call_count == 1
    assert c_u_four.call_count == 1
    assert c_u_other.call_count == 0
    assert tkt_cx.call_count == 1
    assert close_cancel_other.call_count == 1
    assert pl_sync.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('tool_checkmarx.TheLogs.process_exceptions')
@mock.patch('tool_checkmarx.ScrVar.update_exception_info')
@mock.patch('tool_checkmarx.CxReports.alert_on_findings_needing_manual_review')
@mock.patch('tool_checkmarx.single_project_updates',return_value={'missing_similarity_ids':10915})
@mock.patch('tool_checkmarx.TheLogs.sql_exception')
@mock.patch('tool_checkmarx.select',return_value=[('10915','appsec-ops',),])
@mock.patch('tool_checkmarx.TheLogs.log_info')
@mock.patch('tool_checkmarx.ScrVar.timed_script_teardown')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.ScrVar.get_cx_availability')
@mock.patch('tool_checkmarx.ScrVar.timed_script_setup')
def test_all_cx_updates(timer_s,cx_avail,log_hl,ex_func,timer_e,log_ln,sql_sel,ex_sql,
                        u_proj,alert_man,u_ex_info,ex_proc):
    '''Tests all_cx_updates'''
    all_cx_updates()
    assert timer_s.call_count == 1
    assert cx_avail.call_count == 1
    assert log_hl.call_count == 1
    assert ex_func.call_count == 0
    assert timer_e.call_count == 1
    assert log_ln.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_proj.call_count == 1
    assert alert_man.call_count == 1
    assert u_ex_info.call_count == 1
    assert ex_proc.call_count == 1

@mock.patch('tool_checkmarx.TheLogs.process_exceptions')
@mock.patch('tool_checkmarx.ScrVar.update_exception_info')
@mock.patch('tool_checkmarx.CxReports.alert_on_findings_needing_manual_review')
@mock.patch('tool_checkmarx.single_project_updates')
@mock.patch('tool_checkmarx.TheLogs.sql_exception')
@mock.patch('tool_checkmarx.select')
@mock.patch('tool_checkmarx.TheLogs.log_info')
@mock.patch('tool_checkmarx.ScrVar.timed_script_teardown')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.ScrVar.get_cx_availability',return_value=False)
@mock.patch('tool_checkmarx.ScrVar.timed_script_setup')
def test_all_cx_updates_cx_connection_failure(timer_s,cx_avail,log_hl,ex_func,timer_e,log_ln,
                                              sql_sel,ex_sql,u_proj,alert_man,u_ex_info,ex_proc):
    '''Tests all_cx_updates'''
    all_cx_updates()
    assert timer_s.call_count == 1
    assert cx_avail.call_count == 1
    assert log_hl.call_count == 1
    assert ex_func.call_count == 1
    assert timer_e.call_count == 1
    assert log_ln.call_count == 0
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert u_proj.call_count == 0
    assert alert_man.call_count == 0
    assert u_ex_info.call_count == 0
    assert ex_proc.call_count == 0

@mock.patch('tool_checkmarx.TheLogs.process_exceptions')
@mock.patch('tool_checkmarx.ScrVar.update_exception_info')
@mock.patch('tool_checkmarx.CxReports.alert_on_findings_needing_manual_review')
@mock.patch('tool_checkmarx.single_project_updates')
@mock.patch('tool_checkmarx.TheLogs.sql_exception')
@mock.patch('tool_checkmarx.select',side_effect=Exception)
@mock.patch('tool_checkmarx.TheLogs.log_info')
@mock.patch('tool_checkmarx.ScrVar.timed_script_teardown')
@mock.patch('tool_checkmarx.TheLogs.function_exception')
@mock.patch('tool_checkmarx.TheLogs.log_headline')
@mock.patch('tool_checkmarx.ScrVar.get_cx_availability')
@mock.patch('tool_checkmarx.ScrVar.timed_script_setup')
def test_all_cx_updates_ex_acu_002(timer_s,cx_avail,log_hl,ex_func,timer_e,log_ln,
                                   sql_sel,ex_sql,u_proj,alert_man,u_ex_info,ex_proc):
    '''Tests all_cx_updates'''
    all_cx_updates()
    assert timer_s.call_count == 1
    assert cx_avail.call_count == 1
    assert log_hl.call_count == 1
    assert ex_func.call_count == 0
    assert timer_e.call_count == 1
    assert log_ln.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert u_proj.call_count == 0
    assert alert_man.call_count == 0
    assert u_ex_info.call_count == 0
    assert ex_proc.call_count == 0

if __name__ == '__main__':
    unittest.main()
