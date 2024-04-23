'''Unit tests for the special_run_after_checkmarx_updates script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from special_run_after_checkmarx_updates import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('special_run_after_checkmarx_updates.update_all_scans')
@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'update_all_scans',
                                                          'args': 'appsec-ops'}])
def test_main(cmd_mock,run_mock):
    """Tests the main() function"""
    testargs = [r'c:\AppSec\scripts\special_run_after_checkmarx_updates.py',
                'update_all_scans(appsec-ops)']
    with mock.patch.object(sys, "argv", testargs):
        main()
        assert cmd_mock.call_count == 1
        assert run_mock.call_count == 1

@mock.patch('special_run_after_checkmarx_updates.TheLogs.function_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.sql_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.process_exceptions')
@mock.patch('special_run_after_checkmarx_updates.Misc.end_timer')
@mock.patch('special_run_after_checkmarx_updates.Alerts.manual_alert')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_info')
@mock.patch('special_run_after_checkmarx_updates.update_multiple_in_table')
@mock.patch('special_run_after_checkmarx_updates.single_project_updates')
@mock.patch('special_run_after_checkmarx_updates.CxAPI.update_res_state')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_results_to_confirm',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'cxScanID': 'scan_id',
                                       'cxPathID': 'path_id'}]})
@mock.patch('special_run_after_checkmarx_updates.update_exception_count')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_repo_and_project_id',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'Repo': 'repo',
                                       'cxProjectID': 'proj_id'}]})
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_headline')
@mock.patch('special_run_after_checkmarx_updates.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_after_checkmarx_updates.Misc.start_timer')
def test_update_all_scans_all_repos_success(s_timer,cx_avail,headline,g_projs,ex_cnt,g_results,
                                            u_results,u_projs,u_table,log_line,man_alert,e_timer,
                                            p_exceptions,s_except,f_except):
    update_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert g_projs.call_count == 1
    assert ex_cnt.call_count == 2
    assert g_results.call_count == 1
    assert u_results.call_count == 1
    assert u_projs.call_count == 1
    assert u_table.call_count == 2
    assert log_line.call_count == 1
    assert man_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 0

@mock.patch('special_run_after_checkmarx_updates.TheLogs.function_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.sql_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.process_exceptions')
@mock.patch('special_run_after_checkmarx_updates.Misc.end_timer')
@mock.patch('special_run_after_checkmarx_updates.Alerts.manual_alert')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_info')
@mock.patch('special_run_after_checkmarx_updates.update_multiple_in_table')
@mock.patch('special_run_after_checkmarx_updates.single_project_updates')
@mock.patch('special_run_after_checkmarx_updates.CxAPI.update_res_state')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_results_to_confirm',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'cxScanID': 'scan_id',
                                       'cxPathID': 'path_id'}]})
@mock.patch('special_run_after_checkmarx_updates.update_exception_count')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_repo_and_project_id',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'Repo': 'repo',
                                       'cxProjectID': 'proj_id'}]})
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_headline')
@mock.patch('special_run_after_checkmarx_updates.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_after_checkmarx_updates.Misc.start_timer')
def test_update_all_scans_one_repo_success(s_timer,cx_avail,headline,g_projs,ex_cnt,g_results,
                                            u_results,u_projs,u_table,log_line,man_alert,e_timer,
                                            p_exceptions,s_except,f_except):
    update_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert g_projs.call_count == 1
    assert ex_cnt.call_count == 2
    assert g_results.call_count == 1
    assert u_results.call_count == 1
    assert u_projs.call_count == 1
    assert u_table.call_count == 2
    assert log_line.call_count == 1
    assert man_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 0

@mock.patch('special_run_after_checkmarx_updates.TheLogs.function_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.sql_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.process_exceptions')
@mock.patch('special_run_after_checkmarx_updates.Misc.end_timer')
@mock.patch('special_run_after_checkmarx_updates.Alerts.manual_alert')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_info')
@mock.patch('special_run_after_checkmarx_updates.update_multiple_in_table')
@mock.patch('special_run_after_checkmarx_updates.single_project_updates')
@mock.patch('special_run_after_checkmarx_updates.CxAPI.update_res_state')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_results_to_confirm',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'cxScanID': 'scan_id',
                                       'cxPathID': 'path_id'}]})
@mock.patch('special_run_after_checkmarx_updates.update_exception_count')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_repo_and_project_id',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'Repo': 'repo',
                                       'cxProjectID': 'proj_id'}]})
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_headline')
@mock.patch('special_run_after_checkmarx_updates.ToolCx.get_cx_availability',
            return_value=False)
@mock.patch('special_run_after_checkmarx_updates.Misc.start_timer')
def test_update_all_scans_exception_001(s_timer,cx_avail,headline,g_projs,ex_cnt,g_results,
                                            u_results,u_projs,u_table,log_line,man_alert,e_timer,
                                            p_exceptions,s_except,f_except):
    update_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert g_projs.call_count == 0
    assert ex_cnt.call_count == 0
    assert g_results.call_count == 0
    assert u_results.call_count == 0
    assert u_projs.call_count == 0
    assert u_table.call_count == 0
    assert log_line.call_count == 1
    assert man_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

@mock.patch('special_run_after_checkmarx_updates.TheLogs.function_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.sql_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.process_exceptions')
@mock.patch('special_run_after_checkmarx_updates.Misc.end_timer')
@mock.patch('special_run_after_checkmarx_updates.Alerts.manual_alert')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_info')
@mock.patch('special_run_after_checkmarx_updates.update_multiple_in_table')
@mock.patch('special_run_after_checkmarx_updates.single_project_updates')
@mock.patch('special_run_after_checkmarx_updates.CxAPI.update_res_state',
            side_effect=Exception)
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_results_to_confirm',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'cxScanID': 'scan_id',
                                       'cxPathID': 'path_id'}]})
@mock.patch('special_run_after_checkmarx_updates.update_exception_count')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_repo_and_project_id',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'Repo': 'repo',
                                       'cxProjectID': 'proj_id'}]})
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_headline')
@mock.patch('special_run_after_checkmarx_updates.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_after_checkmarx_updates.Misc.start_timer')
def test_update_all_scans_exception_002(s_timer,cx_avail,headline,g_projs,ex_cnt,g_results,
                                            u_results,u_projs,u_table,log_line,man_alert,e_timer,
                                            p_exceptions,s_except,f_except):
    update_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert g_projs.call_count == 1
    assert ex_cnt.call_count == 2
    assert g_results.call_count == 1
    assert u_results.call_count == 1
    assert u_projs.call_count == 0
    assert u_table.call_count == 1
    assert log_line.call_count == 1
    assert man_alert.call_count == 1
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

@mock.patch('special_run_after_checkmarx_updates.TheLogs.function_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.sql_exception')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.process_exceptions')
@mock.patch('special_run_after_checkmarx_updates.Misc.end_timer')
@mock.patch('special_run_after_checkmarx_updates.Alerts.manual_alert')
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_info')
@mock.patch('special_run_after_checkmarx_updates.update_multiple_in_table')
@mock.patch('special_run_after_checkmarx_updates.single_project_updates',
            side_effect=Exception)
@mock.patch('special_run_after_checkmarx_updates.CxAPI.update_res_state')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_results_to_confirm',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'cxScanID': 'scan_id',
                                       'cxPathID': 'path_id'}]})
@mock.patch('special_run_after_checkmarx_updates.update_exception_count')
@mock.patch('special_run_after_checkmarx_updates.CxASDatabase.get_repo_and_project_id',
            return_value={'FatalCount': 0,
                          'ExceptionCount': 0,
                          'Results': [{'Repo': 'repo',
                                       'cxProjectID': 'proj_id'}]})
@mock.patch('special_run_after_checkmarx_updates.TheLogs.log_headline')
@mock.patch('special_run_after_checkmarx_updates.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_after_checkmarx_updates.Misc.start_timer')
def test_update_all_scans_exception_003(s_timer,cx_avail,headline,g_projs,ex_cnt,g_results,
                                            u_results,u_projs,u_table,log_line,man_alert,e_timer,
                                            p_exceptions,s_except,f_except):
    ScrVar.f_array = []
    update_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert g_projs.call_count == 1
    assert ex_cnt.call_count == 2
    assert g_results.call_count == 1
    assert u_results.call_count == 1
    assert u_projs.call_count == 1
    assert u_table.call_count == 1
    assert log_line.call_count == 1
    assert man_alert.call_count == 1
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

def test_update_exception_count():
    """Tests update_exception_count"""
    update_exception_count({'FatalCount': 1, 'ExceptionCount': 0})

if __name__ == '__main__':
    unittest.main()
