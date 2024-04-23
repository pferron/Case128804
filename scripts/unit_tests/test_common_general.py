'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from common.general import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    ScrVar.fe_cnt = 1
    ScrVar.ex_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

def test_general_replace_blanks_in_dict():
    '''Tests General.database_connection'''
    test_data = {'Key':'','Key2':'value'}
    remove_none = General.replace_blanks_in_dict(test_data)
    assert remove_none == {'Key':None,'Key2':'value'}

def test_general_replace_blanks_in_list_of_dicts():
    '''Tests General.database_connection'''
    test_data = [{'Key':'value','Key2':''},{'Key':'value','Key2':'None'}]
    remove_none = General.replace_blanks_in_list_of_dicts(test_data)
    assert remove_none == [{'Key':'value','Key2':None},{'Key':'value','Key2':None}]

def test_general_combine_dictionaries_in_list_of_dictionaries():
    '''Tests General.combine_dictionaries_in_list_of_dictionaries'''
    remove_none = General.combine_dictionaries_in_list_of_dictionaries([{'name':'name','Key2':
                                                                         'value'}],
                                                                       [{'Key2':None,'name':'name',
                                                                         'Key3':'value'}])
    assert remove_none == [{'name':'name','Key2':'value','Key3':'value'}]

def test_general_cmd_processor_with_args():
    '''Tests General.cmd_processor'''
    test = General.cmd_processor(['file_name.py','test_function(value,value,value)'])
    assert test == [{'function':'test_function','args':['value','value','value']}]

def test_general_cmd_processor_no_args():
    '''Tests General.cmd_processor'''
    test = General.cmd_processor(['file_name.py','test_function'])
    assert test == [{'function':'test_function'}]

@mock.patch('common.general.do_dbquery',
            return_value=[('something')])
@mock.patch('common.general.TheLogs.function_exception')
@mock.patch('common.general.DBQueries.select',
            return_value=[('database','full_query')])
def test_general_do_script_query(sql_sel,ex_func,dbq):
    """Tests General.do_script_query"""
    General.do_script_query(1)
    assert sql_sel.call_count == 1
    assert ex_func.call_count == 0
    assert dbq.call_count == 1

@mock.patch('common.general.do_dbquery')
@mock.patch('common.general.TheLogs.function_exception')
@mock.patch('common.general.DBQueries.select',
            side_effect=Exception)
def test_general_do_script_query_ex_sql_sel(sql_sel,ex_func,dbq):
    """Tests General.do_script_query"""
    General.do_script_query(1)
    assert sql_sel.call_count == 1
    assert ex_func.call_count == 1
    assert dbq.call_count == 0

@mock.patch('common.general.TheLogs.function_exception')
@mock.patch('common.general.DBQueries.select',
            return_value=[('something')])
def test_do_dbquery(sql_sel,ex_func):
    """Tests do_dbquery"""
    do_dbquery('sql','database')
    assert sql_sel.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('common.general.TheLogs.function_exception')
@mock.patch('common.general.DBQueries.select',
            side_effect=Exception)
def test_do_dbquery_ex_sql_sel(sql_sel,ex_func):
    """Tests do_dbquery"""
    do_dbquery('sql','database')
    assert sql_sel.call_count == 1
    assert ex_func.call_count == 1

if __name__ == '__main__':
    unittest.main()
