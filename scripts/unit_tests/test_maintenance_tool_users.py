'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
import sys
import os
from maintenance_tool_users import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_update_exception_info():
    '''Tests updating exception information'''
    test_data = {'FatalCount':1,'ExceptionCount':3}
    remove_none = ScrVar.update_exception_info(test_data)
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 3
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_tool_users.remove_mend_users')
@mock.patch.object(General,'cmd_processor',return_value=[{'function':'remove_mend_users'}])
def test_main_no_args(func_mock,cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_tool_users.py','remove_mend_users']
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.call_count == 1
        func_mock.call_count == 1

@mock.patch('maintenance_tool_users.Misc.end_timer')
@mock.patch('maintenance_tool_users.TheLogs.log_info')
@mock.patch('maintenance_tool_users.TheLogs.log_headline')
@mock.patch('maintenance_tool_users.TheLogs.process_exceptions')
@mock.patch('maintenance_tool_users.remove_checkmarx_users')
@mock.patch('maintenance_tool_users.remove_mend_users')
@mock.patch('maintenance_tool_users.Misc.start_timer',
            return_value=['10:10:10','12/12/2022 10:10:10'])
def test_perform_user_maintenance(timer_start,mend_maint,cx_maint,except_processing,log_hl,log_ln,
                                  timer_end):
    '''tests perform_user_maintenance'''
    funct = perform_user_maintenance()
    assert timer_start.call_count == 1
    assert mend_maint.call_count == 1
    assert cx_maint.call_count == 1
    assert except_processing.call_count == 2
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert timer_end.call_count == 1
    assert funct == {'FatalCount':0,'ExceptionCount':0}

@mock.patch('maintenance_tool_users.TheLogs.function_exception')
@mock.patch('maintenance_tool_users.Alerts.manual_alert')
@mock.patch('maintenance_tool_users.ScrVar.update_exception_info')
@mock.patch('maintenance_tool_users.MendUsers.remove_deactivated_users')
@mock.patch('maintenance_tool_users.TheLogs.log_headline')
def test_remove_mend_users(log_hl,remove_users,ex_update,send_alert,except_func):
    '''tests remove_mend_users'''
    funct = remove_mend_users()
    assert log_hl.call_count == 1
    assert remove_users.call_count == 1
    assert ex_update.call_count == 1
    assert send_alert.call_count == 1
    assert except_func.call_count == 0

@mock.patch('maintenance_tool_users.TheLogs.function_exception')
@mock.patch('maintenance_tool_users.Alerts.manual_alert',side_effect=Exception)
@mock.patch('maintenance_tool_users.ScrVar.update_exception_info')
@mock.patch('maintenance_tool_users.MendUsers.remove_deactivated_users')
@mock.patch('maintenance_tool_users.TheLogs.log_headline')
def test_remove_mend_users_exception(log_hl,remove_users,ex_update,send_alert,except_func):
    '''tests remove_mend_users'''
    funct = remove_mend_users()
    assert log_hl.call_count == 1
    assert remove_users.call_count == 1
    assert ex_update.call_count == 1
    assert send_alert.call_count == 1
    assert except_func.call_count == 1

@mock.patch('maintenance_tool_users.TheLogs.function_exception')
@mock.patch('maintenance_tool_users.Alerts.manual_alert')
@mock.patch('maintenance_tool_users.ScrVar.update_exception_info')
@mock.patch('maintenance_tool_users.CxUsers.remove_deactivated_users')
@mock.patch('maintenance_tool_users.TheLogs.log_headline')
def test_remove_checkmarx_users(log_hl,remove_users,ex_update,send_alert,except_func):
    '''tests remove_checkmarx_users'''
    funct = remove_checkmarx_users()
    assert log_hl.call_count == 1
    assert remove_users.call_count == 1
    assert ex_update.call_count == 1
    assert send_alert.call_count == 1
    assert except_func.call_count == 0

@mock.patch('maintenance_tool_users.TheLogs.function_exception')
@mock.patch('maintenance_tool_users.Alerts.manual_alert',side_effect=Exception)
@mock.patch('maintenance_tool_users.ScrVar.update_exception_info')
@mock.patch('maintenance_tool_users.CxUsers.remove_deactivated_users')
@mock.patch('maintenance_tool_users.TheLogs.log_headline')
def test_remove_checkmarx_users_exception(log_hl,remove_users,ex_update,send_alert,except_func):
    '''tests remove_checkmarx_users'''
    funct = remove_checkmarx_users()
    assert log_hl.call_count == 1
    assert remove_users.call_count == 1
    assert ex_update.call_count == 1
    assert send_alert.call_count == 1
    assert except_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
