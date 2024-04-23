'''Unit tests for the alerts.automation_failures script'''

import unittest
from unittest import mock
import sys
import os
parent = os.path.abspath('.')
sys.path.insert(1,parent)
import pytest
import datetime
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
sys.modules['appsec_secrets'] = mock.MagicMock()
from scripts.alerts_automation_failures import *

@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'alert_on_failed_runs',
                                                          'args': 'Every5Minutes'}])
@mock.patch("scripts.alerts_automation_failures.alert_on_failed_runs")
def test_main_with_args(run_mock,cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_automation_failures.py',
                'alert_on_failed_runs(Every5Minutes)']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()
        run_mock.assert_called_once()

@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'alert_on_failed_runs'}])
@mock.patch("scripts.alerts_automation_failures.alert_on_failed_runs")
def test_main_no_args(run_mock,cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_automation_failures.py',
                'alert_on_failed_runs()']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()
        run_mock.assert_called_once()

@mock.patch('scripts.alerts_automation_failures.TheLogs.log_info')
@mock.patch.object(Alerts,'manual_alert',return_value=1)
@mock.patch.object(ProcessAutomation,'get_missing_runs',
                   return_value={'Results': [{"key 1": "value 1", "items": [{"key A": "value A",
                                                "details": ["list item A1","list item A2"]}]}]})
@mock.patch('scripts.alerts_automation_failures.TheLogs.log_headline')
def test_alert_on_failed_runs(head_mock,miss_mock,alert_mock,info_mock):
    '''Has failed runs'''
    alert_on_failed_runs()
    head_mock.assert_called_once()
    miss_mock.assert_called_once()
    alert_mock.assert_called_once()
    info_mock.assert_called_once()

@mock.patch('scripts.alerts_automation_failures.TheLogs.log_info')
@mock.patch.object(Alerts,'manual_alert',return_value=0)
@mock.patch.object(ProcessAutomation,'get_missing_runs',return_value={})
@mock.patch('scripts.alerts_automation_failures.TheLogs.log_headline')
def test_alert_on_failed_runs_no_failures(head_mock,miss_mock,alert_mock,info_mock):
    '''Has no failed runs'''
    alert_on_failed_runs('Every5Minutes')
    head_mock.assert_called_once()
    miss_mock.assert_called_once()
    alert_mock.not_called()
    info_mock.assert_called_once()

if __name__ == '__main__':
    unittest.main()