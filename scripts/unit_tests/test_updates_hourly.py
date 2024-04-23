'''Unit tests for the updates_hourly script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from updates_hourly import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('updates_hourly.ScrVar.run_hourly_updates')
def test_main(run_updates):
    """Tests main"""
    main()
    assert run_updates.call_count == 1

@mock.patch('updates_hourly.ScrVar.timed_script_teardown')
@mock.patch('updates_hourly.send_slack_alerts_for_failed_runs')
@mock.patch('updates_hourly.run_snow_maintenance')
@mock.patch('updates_hourly.update_security_exceptions')
@mock.patch('updates_hourly.ScrVar.timed_script_setup')
def test_scrvar_run_hourly_updates(t_setup,use,rsm,ssaffr,t_teardown):
    """Tests ScrVar.run_hourly_updates"""
    ScrVar.run_hourly_updates()
    assert t_setup.call_count == 1
    assert use.call_count == 1
    assert rsm.call_count == 1
    assert ssaffr.call_count == 1
    assert t_teardown.call_count == 1

def test_scrvar_update_exception_info():
    """Tests update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('updates_hourly.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('updates_hourly.Misc.end_timer')
@mock.patch('updates_hourly.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(ex_proc,e_timer):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert ex_proc.call_count == 2
    assert e_timer.call_count == 1

@mock.patch('updates_hourly.update_all_snow_exceptions')
def test_update_security_exceptions(uase):
    """Tests update_security_exceptions"""
    update_security_exceptions()
    assert uase.call_count == 1

@mock.patch('updates_hourly.TheLogs.function_exception')
@mock.patch('updates_hourly.process_all_updates')
def test_run_snow_maintenance(pau,ex_func):
    """Tests run_snow_maintenance"""
    run_snow_maintenance()
    assert pau.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_hourly.TheLogs.function_exception')
@mock.patch('updates_hourly.process_all_updates',
            side_effect=Exception)
def test_run_snow_maintenance_ex_pau(pau,ex_func):
    """Tests run_snow_maintenance"""
    run_snow_maintenance()
    assert pau.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('updates_hourly.TheLogs.function_exception')
@mock.patch('updates_hourly.alert_on_failed_runs')
def test_send_slack_alerts_for_failed_runs(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_hourly.TheLogs.function_exception')
@mock.patch('updates_hourly.alert_on_failed_runs',
            side_effect=Exception)
def test_send_slack_alerts_for_failed_runs_ex_aofr(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
