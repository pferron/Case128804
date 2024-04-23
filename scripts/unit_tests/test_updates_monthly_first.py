'''Unit tests for the updates_monthly_first script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from updates_monthly_first import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('updates_monthly_first.ScrVar.run_monthly_updates')
def test_main(run_updates):
    """Tests main"""
    main()
    assert run_updates.call_count == 1

@mock.patch('updates_monthly_first.ScrVar.timed_script_teardown')
@mock.patch('updates_monthly_first.send_slack_alerts_for_failed_runs')
@mock.patch('updates_monthly_first.team_notifications')
@mock.patch('updates_monthly_first.ScrVar.timed_script_setup')
def test_scrvar_run_monthly_updates(t_setup,tn,ssaffr,t_teardown):
    """Tests ScrVar.run_monthly_updates"""
    ScrVar.run_monthly_updates()
    assert t_setup.call_count == 1
    assert tn.call_count == 1
    assert ssaffr.call_count == 1
    assert t_teardown.call_count == 1

def test_scrvar_update_exception_info():
    """Tests update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('updates_monthly_first.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('updates_monthly_first.Misc.end_timer')
@mock.patch('updates_monthly_first.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(ex_proc,e_timer):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert ex_proc.call_count == 2
    assert e_timer.call_count == 1

@mock.patch('updates_monthly_first.TheLogs.function_exception')
@mock.patch('updates_monthly_first.class_setup')
def test_team_notifications(cs,ex_func):
    """Tests team_notifications"""
    team_notifications()
    assert cs.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_monthly_first.TheLogs.function_exception')
@mock.patch('updates_monthly_first.class_setup',
            side_effect=Exception)
def test_team_notifications_ex_cs(cs,ex_func):
    """Tests team_notifications"""
    team_notifications()
    assert cs.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('updates_monthly_first.TheLogs.function_exception')
@mock.patch('updates_monthly_first.alert_on_failed_runs')
def test_send_slack_alerts_for_failed_runs(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('updates_monthly_first.TheLogs.function_exception')
@mock.patch('updates_monthly_first.alert_on_failed_runs',
            side_effect=Exception)
def test_send_slack_alerts_for_failed_runs_ex_aofr(aofr,ex_func):
    """Tests send_slack_alerts_for_failed_runs"""
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
