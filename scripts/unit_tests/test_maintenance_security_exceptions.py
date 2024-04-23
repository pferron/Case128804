'''Unit tests for maintenance_security_exceptions.py '''

import unittest
from unittest import mock
import sys
import os
import pytest
from maintenance_security_exceptions import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maintenance_security_exceptions.update_all_snow_exceptions')
@mock.patch('maintenance_security_exceptions.General.cmd_processor',
            return_value=[{'function':'update_all_snow_exceptions'}])
def test_main_function_only(proc_cmd,all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_security_exceptions.py','update_all_snow_exceptions']
    with mock.patch.object(sys,"argv",testargs):
        main()
        assert proc_cmd.call_count == 1
        assert all_updates.call_count == 1

@mock.patch('maintenance_security_exceptions.update_all_snow_exceptions')
@mock.patch('maintenance_security_exceptions.General.cmd_processor',
            return_value=[{'function':'update_all_snow_exceptions','args':['hourly']}])
def test_main_function_with_args(proc_cmd,all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_security_exceptions.py',"update_all_snow_exceptions('hourly')"]
    with mock.patch.object(sys,"argv",testargs):
        main()
        assert proc_cmd.call_count == 1
        assert all_updates.call_count == 1

def test_scrvar_update_exception_info():
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':1})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_security_exceptions.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('maintenance_security_exceptions.TheLogs.process_exception_count_only')
@mock.patch('maintenance_security_exceptions.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('maintenance_security_exceptions.ScrVar.timed_script_teardown')
@mock.patch('maintenance_security_exceptions.SNowProc.alerts_for_missing_jira_tickets')
@mock.patch('maintenance_security_exceptions.SNowProc.update_tool_and_jira_exceptions')
@mock.patch('maintenance_security_exceptions.SNowProc.alerts_for_pending_approvals')
@mock.patch('maintenance_security_exceptions.SNowProc.sync_with_jiraissues')
@mock.patch('maintenance_security_exceptions.TheLogs.log_info')
@mock.patch('maintenance_security_exceptions.SNowAPI.process_exception_requests')
@mock.patch('maintenance_security_exceptions.ScrVar.update_exception_info')
@mock.patch('maintenance_security_exceptions.SNowAPI.update_snow_approvers')
@mock.patch('maintenance_security_exceptions.TheLogs.log_headline')
@mock.patch('maintenance_security_exceptions.ScrVar.timed_script_setup')
@pytest.mark.parametrize("period",[('hourly'),
                                   ('past_15_minutes'),
                                   (None)])
def test_update_all_snow_exceptions(tss,log_hl,usa,uei,per,log_ln,swj,afpa,utaje,afmjt,
                                    tst,period):
    """Tests update_all_snow_exceptions"""
    update_all_snow_exceptions(period)
    assert tss.call_count == 1
    assert log_hl.call_count == 7
    assert usa.call_count == 1
    assert uei.call_count == 6
    assert per.call_count == 1
    assert log_ln.call_count == 2
    assert swj.call_count == 1
    assert afpa.call_count == 1
    assert utaje.call_count == 1
    assert afmjt.call_count == 1
    assert tst.call_count == 1

if __name__ == '__main__':
    unittest.main()
