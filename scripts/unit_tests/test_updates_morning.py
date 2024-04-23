'''Unit tests for the updates_morning script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from updates_morning import *

@mock.patch('updates_morning.ScrVar.run_morning_updates')
def test_main(rmu):
    """Tests the main() function"""
    main()
    assert rmu.call_count == 1

@mock.patch('updates_morning.ScrVar.timed_script_teardown')
@mock.patch('updates_morning.TheLogs.log_headline')
@mock.patch('updates_morning.ScrVar.run_day_of_the_week_scripts')
@mock.patch('updates_morning.update_script_runtime_stats')
@mock.patch('updates_morning.checkmarx_hid_license_check')
@mock.patch('updates_morning.new_ticket_slack_notifications')
@mock.patch('updates_morning.ScrVar.timed_script_setup')
def test_scrvar_run_morning_updates(tss,ntsn,chlc,usrs,rdotws,log_hl,tst):
    """Tests ScrVar.run_morning_updates"""
    ScrVar.run_morning_updates()
    assert tss.call_count == 1
    assert ntsn.call_count == 1
    assert chlc.call_count == 1
    assert usrs.call_count == 1
    assert rdotws.call_count == 1
    assert log_hl.call_count == 1
    assert tst.call_count == 1

@pytest.mark.parametrize("fatal_exceptions,exception_count,message",
                         [(0,0,"Step was run successfully"),
                          (1,0,"Step failed due to 1 fatal exception(s)"),
                          (0,1,"Step was run successfully, but 1 exception(s) occurred")])
def test_scrvar_get_message(fatal_exceptions,exception_count,message):
    """Tests ScrVar.get_message"""
    response = ScrVar.get_message(fatal_exceptions,exception_count)
    assert response == message

@mock.patch('updates_morning.LogCleanup.all_maintenance')
@mock.patch('updates_morning.WeeklyAlerts.process_all_alerts')
@mock.patch('updates_morning.TheLogs.log_headline')
@mock.patch('updates_morning.new_ticket_slack_notifications')
@pytest.mark.parametrize("day_name,ntsn_cnt,log_hl_cnt,paa_cnt,am_cnt",
                         [('Sunday',0,0,0,0),
                          ('Monday',1,1,1,0),
                          ('Tuesday',0,0,0,0),
                          ('Wednesday',0,0,0,0),
                          ('Thursday',0,1,0,1),
                          ('Friday',0,0,0,0),
                          ('Saturday',0,0,0,0)])
def test_scrvar_run_day_of_the_week_scripts(ntsn,log_hl,paa,am,day_name,ntsn_cnt,log_hl_cnt,paa_cnt,am_cnt):
    """Tests ScrVar.run_day_of_the_week_scripts"""
    ScrVar.run_day_of_the_week_scripts(day_name,4)
    assert ntsn.call_count == ntsn_cnt
    assert log_hl.call_count == log_hl_cnt
    assert paa.call_count == paa_cnt
    assert am.call_count == am_cnt

@mock.patch('updates_morning.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('updates_morning.Misc.end_timer')
@mock.patch('updates_morning.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('updates_morning.TheLogs.log_info')
@mock.patch('updates_morning.ScrVar.get_message')
@mock.patch('updates_morning.TheLogs.function_exception')
@mock.patch('updates_morning.class_setup')
@mock.patch('updates_morning.TheLogs.log_headline')
@pytest.mark.parametrize("cs_se,ex_func_cnt",
                         [(None,0),
                          (Exception,1)])
def test_new_ticket_slack_notifications(log_hl,cs,ex_func,gm,log_ln,cs_se,ex_func_cnt):
    """Tests new_ticket_slack_notifications"""
    cs.side_effect = cs_se
    new_ticket_slack_notifications()
    assert log_hl.call_count == 1
    assert cs.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_morning.TheLogs.log_info')
@mock.patch('updates_morning.ScrVar.get_message')
@mock.patch('updates_morning.TheLogs.function_exception')
@mock.patch('updates_morning.verify_checkmarx_license')
@mock.patch('updates_morning.TheLogs.log_headline')
@pytest.mark.parametrize("clc_se,ex_func_cnt",
                         [(None,0),
                          (Exception,1)])
def test_checkmarx_hid_license_check(log_hl,clc,ex_func,gm,log_ln,clc_se,ex_func_cnt):
    """Tests checkmarx_hid_license_check"""
    clc.side_effect = clc_se
    checkmarx_hid_license_check()
    assert log_hl.call_count == 1
    assert clc.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_morning.TheLogs.log_info')
@mock.patch('updates_morning.ScrVar.get_message')
@mock.patch('updates_morning.ScriptStats.update_run_times')
@mock.patch('updates_morning.TheLogs.log_headline')
def test_update_script_runtime_stats(log_hl,urt,gm,log_ln):
    """Tests update_script_runtime_stats"""
    update_script_runtime_stats()
    assert log_hl.call_count == 1
    assert urt.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

if __name__ == '__main__':
    unittest.main()
