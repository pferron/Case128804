'''Unit tests for the common.logging script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from datetime import datetime
from common.logging import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_LogFilter():
    """Tests LogFilter"""
    LogFilter(logging.INFO)

def test_thelogs_set_alert_source():
    """Tests TheLogs.set_alert_source"""
    source = TheLogs.set_alert_source("c:\\appsec\\scripts\\misc","test.py")
    assert source == "misc-test.py"

def test_thelogs_set_log_file():
    """Tests TheLogs.set_log_file"""
    file = TheLogs.set_log_file("test.py")
    assert file == f'C:\\AppSec\\logs\\{datetime.now().strftime("%Y-%m-%d")}-test.log'

def test_thelogs_set_exceptions_log_file():
    """Tests TheLogs.set_exceptions_log_file"""
    file = TheLogs.set_exceptions_log_file("test.py")
    assert file == f'C:\\AppSec\\logs\\{datetime.now().strftime("%Y-%m-%d")}-test_exceptions.log'

def test_thelogs_exception_headline():
    """Tests TheLogs.exception_headline"""
    headline = TheLogs.exception_headline('Hello World')
    test = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Hello World  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
    assert headline == test

def test_thelogs_setup_logging():
    """Tests TheLogs.setup_logging"""
    TheLogs.setup_logging('C:\\AppSec\\logs\\file.log')

@pytest.mark.parametrize("description,symbol",
                         [("Testing with a symbol","*"),
                          ("Testing without a symbol",None)])
def test_thelogs_log_headline(description,symbol):
    """Tests TheLogs.log_headline"""
    temp_log = logging.getLogger('common.logging')
    with mock.patch.object(temp_log,'info') as main_log:
        TheLogs.log_headline('Test',1,symbol,main_log)

@pytest.mark.parametrize("symbol",[("*"),(None)])
def test_thelogs_log_info(symbol):
    """Tests TheLogs.log_info"""
    temp_log = logging.getLogger('common.logging')
    with mock.patch.object(temp_log,'info') as main_log:
        TheLogs.log_info('Test',1,symbol,main_log)

@mock.patch('common.logging.TheLogs.exception_headline')
@pytest.mark.parametrize("description,custom_message,exception_code,log_file,source_file,parent_function,stack_trace,notes",
                         [('All fields provided','custom_message','exception_code','log_file',
                           'source_file','parent_function','stack_trace','notes')])
def test_thelogs_exception(eh,description,custom_message,exception_code,log_file,source_file,
                           parent_function,stack_trace,notes):
    """Tests TheLogs.exception"""
    temp_main = logging.getLogger('common.logging')
    with mock.patch.object(temp_main,'info') as temp_log:
        TheLogs.exception(custom_message,exception_code,temp_log,temp_log,log_file,source_file,
                          parent_function,stack_trace,notes)
        assert eh.call_count == 1

@mock.patch('common.logging.TheLogs.exception_headline')
@pytest.mark.parametrize("description,source_file,parent_function,exception_details,stack_trace,sql",
                         [('All fields have values','test.py','parent_function','Details','trace','some sql'),
                          ('No fields have values',None,None,None,None,None)])
def test_thelogs_sql_exception(eh,description,source_file,parent_function,exception_details,stack_trace,sql):
    """Tests TheLogs.sql_exception"""
    temp_main = logging.getLogger('common.logging')
    with mock.patch.object(temp_main,'info') as temp_log:
        TheLogs.sql_exception(sql,'Ex-123',exception_details,temp_log,temp_log,'file.log',
                              source_file,parent_function,stack_trace,'notes')
        assert eh.call_count == 1

@mock.patch('common.logging.TheLogs.exception_headline')
@pytest.mark.parametrize("description,source_file,parent_function,exception_details,stack_trace,function",
                         [('All fields have values','test.py','parent_function','Details','trace','some function'),
                          ('No fields have values',None,None,None,None,None)])
def test_thelogs_function_exception(eh,description,source_file,parent_function,exception_details,stack_trace,
                                    function):
    """Tests TheLogs.function_exception"""
    temp_main = logging.getLogger('common.logging')
    with mock.patch.object(temp_main,'info') as temp_log:
        TheLogs.function_exception(function,'Ex-123',exception_details,temp_log,temp_log,
                                   'file.log',source_file,parent_function,stack_trace,'notes')
        assert eh.call_count == 1

@mock.patch('common.logging.Alerts.manual_alert')
@pytest.mark.parametrize("description,ma_rv,ma_cnt,exception_array,alert_source,slack_url,alert_id,log_file,manual_message,response_rv",
                         [("exception_array = []",None,0,[],'alert_source','slack_url',26,'log_file','manual_message',0),
                          ("exception_array = {}",None,0,{},'alert_source','slack_url',26,'log_file','manual_message',0),
                          ("exception_array = str",None,0,'str','alert_source','slack_url',26,'log_file','manual_message',0),
                          ("exception_array dict with values",1,1,{'key1':'value1','key2':'value2'},'alert_source','slack_url',26,'log_file','manual_message',1),
                          ("exception_array list with values",1,1,['value1','value2'],'alert_source','slack_url',26,'log_file','manual_message',1),
                          ("slack_url = None",None,0,['value1','value2'],'alert_source',None,26,'log_file','manual_message',0),
                          ("alert_id = None",None,0,['value1','value2'],'alert_source','slack_url',None,'log_file','manual_message',0)])
def test_thelogs_process_exceptions(ma,description,ma_rv,ma_cnt,exception_array,alert_source,
                                    slack_url,alert_id,log_file,manual_message,response_rv):
    """Tests process_exceptions"""
    ma.return_value = ma_rv
    response = TheLogs.process_exceptions(exception_array=exception_array,alert_source=alert_source,
                                          slack_url=slack_url,alert_id=alert_id,log_file=log_file,
                                          manual_message=manual_message)
    assert ma.call_count == ma_cnt
    assert response == response_rv

@mock.patch('common.logging.Alerts.manual_alert')
@pytest.mark.parametrize("description,ma_rv,ma_cnt,exception_count,alert_id,alert_source,slack_url,log_file,response_rv",
                         [("exception_count = 0",None,0,0,26,'alert_source','slack_url','log_file',0),
                          ("alert_id = None",None,0,1,None,'alert_source','slack_url','log_file',0),
                          ("alert_id = str",None,0,0,'str','alert_source','slack_url','log_file',0),
                          ("slack_url = None",None,0,0,26,'alert_source',None,'log_file',0),
                          ("All values provided",1,1,1,26,'alert_source','slack_url','log_file',1)])
def test_process_exception_count_only(ma,description,ma_rv,ma_cnt,exception_count,alert_id,alert_source,slack_url,log_file,response_rv):
    """tests process_exception_count_only"""
    ma.return_value = ma_rv
    response = TheLogs.process_exception_count_only(exception_count=exception_count,
                                                    alert_id=alert_id,alert_source=alert_source,
                                                    slack_url=slack_url,log_file=log_file)
    assert ma.call_count == ma_cnt
    assert response == response_rv

if __name__ == '__main__':
    unittest.main()
