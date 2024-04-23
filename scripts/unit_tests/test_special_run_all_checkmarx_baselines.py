'''Unit tests for the special_run_all_checkmarx_baselines script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from special_run_all_checkmarx_baselines import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('special_run_all_checkmarx_baselines.kick_off_all_scans')
@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'kick_off_all_scans',
                                                          'args': 'appsec-ops'}])
def test_main(cmd_mock,run_mock):
    """Tests the main() function"""
    testargs = [r'c:\AppSec\scripts\special_run_all_checkmarx_baselines.py',
                'kick_off_all_scans(appsec-ops)']
    with mock.patch.object(sys, "argv", testargs):
        main()
        assert cmd_mock.call_count == 1
        assert run_mock.call_count == 1

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_all_repos_scan_success(s_timer,cx_avail,headline,bl_data,g_scans,s_launch,
                                              log_line,s_alert,e_timer,p_exceptions,s_except,
                                              f_except):
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 2
    assert bl_data.call_count == 1
    assert g_scans.call_count == 1
    assert s_launch.call_count == 1
    assert log_line.call_count == 1
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 0

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_one_repo_scan_success(s_timer,cx_avail,headline,bl_data,g_scans,s_launch,
                                              log_line,s_alert,e_timer,p_exceptions,s_except,
                                              f_except):
    kick_off_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 2
    assert bl_data.call_count == 1
    assert g_scans.call_count == 1
    assert s_launch.call_count == 1
    assert log_line.call_count == 1
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 0

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=False)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_all_repos_scan_failed(s_timer,cx_avail,headline,bl_data,g_scans,s_launch,
                                              log_line,s_alert,e_timer,p_exceptions,s_except,
                                              f_except):
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 2
    assert bl_data.call_count == 1
    assert g_scans.call_count == 1
    assert s_launch.call_count == 1
    assert log_line.call_count == 1
    assert s_alert.call_count == 1
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 0

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=False)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_exception_001(s_timer,cx_avail,headline,bl_data,g_scans,s_launch,
                                              log_line,s_alert,e_timer,p_exceptions,s_except,
                                              f_except):
    ScrVar.f_array = []
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert bl_data.call_count == 0
    assert g_scans.call_count == 0
    assert s_launch.call_count == 0
    assert log_line.call_count == 0
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates',
            side_effect=Exception)
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_exception_002(s_timer,cx_avail,headline,bl_data,g_scans,
                                                    s_launch,log_line,s_alert,e_timer,p_exceptions,
                                                    s_except,f_except):
    ScrVar.fe_cnt = 0
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert bl_data.call_count == 1
    assert g_scans.call_count == 0
    assert s_launch.call_count == 0
    assert log_line.call_count == 0
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates',
            side_effect=Exception)
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_exception_003(s_timer,cx_avail,headline,bl_data,g_scans,
                                                   s_launch,log_line,s_alert,e_timer,p_exceptions,
                                                   s_except,f_except):
    ScrVar.fe_cnt = 0
    kick_off_all_scans('appsec-ops')
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert bl_data.call_count == 1
    assert g_scans.call_count == 0
    assert s_launch.call_count == 0
    assert log_line.call_count == 0
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            return_value=False)
@mock.patch('special_run_all_checkmarx_baselines.select',
            side_effect=Exception)
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_exception_004(s_timer,cx_avail,headline,bl_data,g_scans,
                                                    s_launch,log_line,s_alert,e_timer,p_exceptions,
                                                    s_except,f_except):
    ScrVar.fe_cnt = 0
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 1
    assert bl_data.call_count == 1
    assert g_scans.call_count == 1
    assert s_launch.call_count == 0
    assert log_line.call_count == 0
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 1
    assert f_except.call_count == 0

@mock.patch('special_run_all_checkmarx_baselines.TheLogs.function_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.sql_exception')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.process_exceptions')
@mock.patch('special_run_all_checkmarx_baselines.Misc.end_timer')
@mock.patch('special_run_all_checkmarx_baselines.Alerts.manual_alert')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_info')
@mock.patch('special_run_all_checkmarx_baselines.CxAPI.launch_cx_scan',
            side_effect=Exception)
@mock.patch('special_run_all_checkmarx_baselines.select',
            return_value=[('Repo',1,'2021-12-26')])
@mock.patch('special_run_all_checkmarx_baselines.CxMaint.base_sastprojects_updates')
@mock.patch('special_run_all_checkmarx_baselines.TheLogs.log_headline')
@mock.patch('special_run_all_checkmarx_baselines.ToolCx.get_cx_availability',
            return_value=True)
@mock.patch('special_run_all_checkmarx_baselines.Misc.start_timer')
def test_kick_off_all_scans_exception_005(s_timer,cx_avail,headline,bl_data,g_scans,
                                                    s_launch,log_line,s_alert,e_timer,p_exceptions,
                                                    s_except,f_except):
    ScrVar.fe_cnt = 0
    kick_off_all_scans(None)
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert headline.call_count == 2
    assert bl_data.call_count == 1
    assert g_scans.call_count == 1
    assert s_launch.call_count == 1
    assert log_line.call_count == 0
    assert s_alert.call_count == 0
    assert e_timer.call_count == 1
    assert p_exceptions.call_count == 2
    assert s_except.call_count == 0
    assert f_except.call_count == 1

if __name__ == '__main__':
    unittest.main()
