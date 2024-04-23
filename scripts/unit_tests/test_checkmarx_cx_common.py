'''Unit tests for checkmarx\common.py '''

import unittest
from unittest import mock
import sys
import os
import pytest
from checkmarx.cx_common import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

def test_cxcommon_get_severity_id():
    '''Tests CxCommon.get_severity_id'''
    result = CxCommon.get_severity_id('critical')
    assert result == 0
    result = CxCommon.get_severity_id('high')
    assert result == 1
    result = CxCommon.get_severity_id('medium')
    assert result == 2
    result = CxCommon.get_severity_id('low')
    assert result is None

def test_cxcommon_get_result_state_id():
    '''Tests CxCommon.get_result_state_id'''
    result = CxCommon.get_result_state_id('To Verify')
    assert result == 0
    result = CxCommon.get_result_state_id('Not Exploitable')
    assert result == 1
    result = CxCommon.get_result_state_id('Confirmed')
    assert result == 2
    result = CxCommon.get_result_state_id('Urgent')
    assert result == 3
    result = CxCommon.get_result_state_id('Proposed Not Exploitable')
    assert result == 4
    result = CxCommon.get_result_state_id('Tech Debt')
    assert result == 5
    result = CxCommon.get_result_state_id('Unknown')
    assert result is None

@mock.patch('checkmarx.cx_common.TheLogs.sql_exception')
@mock.patch('checkmarx.cx_common.select')
def test_cxcommon_verify_found_in_last_scan(sql_sel,ex_sql):
    '''Tests CxCommon.verify_found_in_last_scan'''
    result = CxCommon.verify_found_in_last_scan(1,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == {'FatalCount':0,'ExceptionCount':0,'Results':1}

@mock.patch('checkmarx.cx_common.TheLogs.sql_exception')
@mock.patch('checkmarx.cx_common.select',
            side_effect=Exception)
def test_cxcommon_verify_found_in_last_scan_ex_vfils_001(sql_sel,ex_sql):
    '''Tests CxCommon.verify_found_in_last_scan'''
    result = CxCommon.verify_found_in_last_scan(1,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    assert result == {'FatalCount':0,'ExceptionCount':1,'Results':0}
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
