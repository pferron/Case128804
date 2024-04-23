'''Unit tests for the updates_every_5_minutes script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from updates_every_5_minutes import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('updates_every_5_minutes.ScrVar.run_updates_every_5_minutes')
def test_main(run_updates):
    """Tests main"""
    main()
    assert run_updates.call_count == 1

@mock.patch('updates_every_5_minutes.ScrVar.timed_script_teardown')
@mock.patch('updates_every_5_minutes.send_slack_alerts_for_failed_runs')
@mock.patch('updates_every_5_minutes.ccsx_updates')
@mock.patch('updates_every_5_minutes.jenkins_updates')
@mock.patch('updates_every_5_minutes.ScrVar.timed_script_setup')
def test_scrvar_run_updates_every_5_minutes(t_setup,ju,cu,ssaffr,t_teardown):
    """Tests ScrVar.run_updates_every_5_minutes"""
    ScrVar.run_updates_every_5_minutes()
    assert t_setup.call_count == 1
    assert ju.call_count == 1
    assert cu.call_count == 1
    assert ssaffr.call_count == 1
    assert t_teardown.call_count == 1

def test_scrvar_update_exception_info():
    """Tests update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('updates_every_5_minutes.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('updates_every_5_minutes.Misc.end_timer')
@mock.patch('updates_every_5_minutes.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(ex_proc,e_timer):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert ex_proc.call_count == 2
    assert e_timer.call_count == 1

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.appsecjenkins')
def test_jenkins_updates(asj,ex_func):
    """Tests jenkins_updates"""
    jenkins_updates()
    assert asj.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.appsecjenkins',
            side_effect=Exception)
def test_jenkins_updates_ex_asj(asj,ex_func):
    """Tests jenkins_updates"""
    jenkins_updates()
    assert asj.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.every_5_minutes')
def test_ccsx_updates(e5m,ex_func):
    """Tests ccsx_updates"""
    ccsx_updates()
    assert e5m.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.every_5_minutes',
            side_effect=Exception)
def test_ccsx_updates_ex_e5m(e5m,ex_func):
    """Tests ccsx_updates"""
    ccsx_updates()
    assert e5m.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.alert_on_failed_runs')
def test_send_slack_alerts_for_failed_runs(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_every_5_minutes.TheLogs.function_exception')
@mock.patch('updates_every_5_minutes.alert_on_failed_runs',
            side_effect=Exception)
def test_send_slack_alerts_for_failed_runs_ex_aofr(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
