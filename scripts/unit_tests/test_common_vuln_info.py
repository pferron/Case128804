'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from collections import namedtuple
from common.vuln_info import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

Weakness = namedtuple('Weakness', ['cwe_id','name','description','extended_description'])

@mock.patch('common.vuln_info.TheLogs.process_exceptions')
@mock.patch('common.vuln_info.TheLogs.sql_exception')
@mock.patch('common.vuln_info.TheLogs.function_exception')
@mock.patch('common.vuln_info.select')
@mock.patch('common.vuln_info.Database.get',
            return_value = Weakness('cwe_id','name','','extended_description'))
def test_vulndetails_get_cwe_success_api(db_mock,select,f_exception,s_exception,p_exceptions):
    """Tests VulnDetails.get_cwe"""
    VulnDetails.get_cwe(159)
    assert db_mock.call_count == 1
    assert select.call_count == 0
    assert f_exception.call_count == 0
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 0

@mock.patch('common.vuln_info.TheLogs.process_exceptions')
@mock.patch('common.vuln_info.TheLogs.sql_exception')
@mock.patch('common.vuln_info.TheLogs.function_exception')
@mock.patch('common.vuln_info.select',
            return_value=[('name','description')])
@mock.patch('common.vuln_info.Database.get',
            side_effect=Exception)
def test_vulndetails_get_cwe_exception_api(db_mock,select,f_exception,s_exception,p_exceptions):
    """Tests VulnDetails.get_cwe"""
    VulnDetails.get_cwe(159)
    assert db_mock.call_count == 1
    assert select.call_count == 1
    assert f_exception.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 2

@mock.patch('common.vuln_info.TheLogs.process_exceptions')
@mock.patch('common.vuln_info.TheLogs.sql_exception')
@mock.patch('common.vuln_info.TheLogs.function_exception')
@mock.patch('common.vuln_info.select',
            return_value=[('name','description')])
@mock.patch('common.vuln_info.Database.get',
            side_effect=Exception)
def test_vulndetails_get_cwe_success_sql(db_mock,select,f_exception,s_exception,p_exceptions):
    """Tests VulnDetails.get_cwe"""
    VulnDetails.get_cwe(159)
    assert db_mock.call_count == 1
    assert select.call_count == 1
    assert f_exception.call_count == 1
    assert s_exception.call_count == 0
    assert p_exceptions.call_count == 2

@mock.patch('common.vuln_info.TheLogs.process_exceptions')
@mock.patch('common.vuln_info.TheLogs.sql_exception')
@mock.patch('common.vuln_info.TheLogs.function_exception')
@mock.patch('common.vuln_info.select',
            side_effect=Exception)
@mock.patch('common.vuln_info.Database.get',
            side_effect=Exception)
def test_vulndetails_get_cwe_exception_sql(db_mock,select,f_exception,s_exception,p_exceptions):
    """Tests VulnDetails.get_cwe"""
    VulnDetails.get_cwe(159)
    assert db_mock.call_count == 1
    assert select.call_count == 1
    assert f_exception.call_count == 1
    assert s_exception.call_count == 1
    assert p_exceptions.call_count == 4

if __name__ == '__main__':
    unittest.main()
