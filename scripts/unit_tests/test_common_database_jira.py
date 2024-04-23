'''Unit tests for common\database_jira.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from common.database_jira import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.database_jira.pyodbc.connect')
def test_database_connection(connect):
    '''Tests database_connection'''
    JiraDB.database_connection()
    assert connect.call_count == 1

@mock.patch('common.database_jira.pyodbc.connect')
def test_database_connection_exists(connect):
    '''Tests database_connection'''
    appsec_connection = 'something'
    JiraDB.database_connection()
    assert connect.call_count == 0

@mock.patch('common.database_jira.JiraDB.database_connection')
def test_select(db_connect):
    '''Tests select'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = ['returned']
    JiraDB.select('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_jira.JiraDB.database_connection')
def test_insert(db_connect):
    '''Tests insert'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    JiraDB.insert('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_jira.JiraDB.database_connection')
def test_update(db_connect):
    '''Tests update'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    JiraDB.update('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_jira.JiraDB.database_connection')
def test_delete_row(db_connect):
    '''Tests delete_row'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    JiraDB.delete_row('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_jira.JiraDB.insert')
def test_insert_multiple_into_table_w_list(insert):
    '''Tests insert_multiple_into_table'''
    JiraDB.insert_multiple_into_table('TestTable',[{'TestColumn':'TestValue'}])
    assert insert.call_count == 1

@mock.patch('common.database_jira.JiraDB.insert')
def test_insert_multiple_into_table_w_dict(insert):
    '''Tests insert_multiple_into_table'''
    JiraDB.insert_multiple_into_table('TestTable',{'TestColumn':'TestValue'})
    assert insert.call_count == 1

@mock.patch('common.database_jira.JiraDB.insert')
def test_insert_multiple_into_table_empty_list(insert):
    '''Tests insert_multiple_into_table'''
    JiraDB.insert_multiple_into_table('TestTable',[])
    assert insert.call_count == 0

@mock.patch('common.database_jira.JiraDB.insert')
def test_insert_multiple_into_table_empty_dict(insert):
    '''Tests insert_multiple_into_table'''
    JiraDB.insert_multiple_into_table('TestTable',{})
    assert insert.call_count == 0

@mock.patch('common.database_jira.JiraDB.update')
def test_update_multiple_in_table_w_list(update):
    '''Tests update_multiple_in_table'''
    JiraDB.update_multiple_in_table('TestTable',[{'SET':{'TestColumn':None},
                                                  'WHERE_EQUAL':{'TC':None},
                                                  'WHERE_IN':{'TC3':['test','test']},
                                                  'WHERE_NOT':{'TC':None},
                                                  'WHERE_NOT_IN':{'TC2':['test','test']},
                                                  'CUSTOM_AND':['TC1 != 1 OR TC1 IS NULL'],
                                                  'CUSTOM_OR':['TC1 != 1 OR TC1 IS NULL']}])
    assert update.call_count == 1

@mock.patch('common.database_jira.JiraDB.update')
def test_update_multiple_in_table_w_list_null_values(update):
    '''Tests update_multiple_in_table'''
    JiraDB.update_multiple_in_table('TestTable',[{'SET':{'TestColumn':None},
                                                     'WHERE_EQUAL':{'TC':None},
                                                     'WHERE_NOT':{'TC':None}}])
    assert update.call_count == 1

@mock.patch('common.database_jira.JiraDB.update')
def test_update_multiple_in_table_w_dict(update):
    '''Tests update_multiple_in_table'''
    JiraDB.update_multiple_in_table('TestTable',{'SET':{'TestColumn':'TestValue'},
                                                    'WHERE_EQUAL':{'TC':'value'},
                                                    'WHERE_NOT':{'TC':'value''s'}})
    assert update.call_count == 1

if __name__ == '__main__':
    unittest.main()
