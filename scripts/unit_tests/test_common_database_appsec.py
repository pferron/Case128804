'''Unit tests for common\database_appsec.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from common.database_appsec import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.database_appsec.pyodbc.connect')
def test_database_connection(connect):
    '''Tests database_connection'''
    database_connection()
    assert connect.call_count == 1

@mock.patch('common.database_appsec.pyodbc.connect')
def test_database_connection_exists(connect):
    '''Tests database_connection'''
    appsec_connection = 'something'
    database_connection()
    assert connect.call_count == 0

@mock.patch('common.database_appsec.pyodbc.connect')
def test_cx_connection(connect):
    '''Tests cx_connection'''
    cx_connection()
    assert connect.call_count == 1

@mock.patch('common.database_appsec.pyodbc.connect')
def test_cx_connection_exists(connect):
    '''Tests cx_connection'''
    checkmarx_connection  = 'something'
    cx_connection()
    assert connect.call_count == 0

@mock.patch('common.database_appsec.cx_connection')
def test_cx_select(db_connect):
    '''Tests cx_select'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = ['returned']
    cx_select('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_appsec.database_connection')
def test_select(db_connect):
    '''Tests select'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = ['returned']
    select('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_appsec.database_connection')
def test_insert(db_connect):
    '''Tests insert'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    insert('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_appsec.database_connection')
def test_update(db_connect):
    '''Tests update'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    update('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_appsec.database_connection')
def test_delete_row(db_connect):
    '''Tests delete_row'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    delete_row('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_appsec.insert')
def test_insert_multiple_into_table(insert):
    '''Tests insert_multiple_into_table'''
    insert_multiple_into_table('TestTable',{'TestColumn':'TestValue','TC1':None},1,
                               ['TestColumn','TC1'],' OR TestColumn IS NULL',
                               show_progress=True)
    insert_multiple_into_table('TestTable',[{'TestColumn':'TestValue','TC1':None},
                                            {'TestColumn':'TestValue2','TC1':2}],
                               show_progress=False)
    assert insert.call_count == 3

@mock.patch('common.database_appsec.update')
def test_update_multiple_in_table(update):
    '''Tests update_multiple_in_table'''
    update_multiple_in_table('TestTable',{'SET':{'TestColumn':'TestValue','TC1':None},
                                          'WHERE_EQUAL':{'TestColumn':None,'TC2':'value''s'},
                                          'WHERE_NOT':{'TC':'value''s','TestColumn':None},
                                          'WHERE_LIKE':{'TC':'value''s','TestColumn':None},
                                          'WHERE_NOT_LIKE':{'TC':'value''s','TestColumn':None},
                                          'WHERE_NOT_IN':{'TC':'value''s','TestColumn':None},
                                          'WHERE_IN':{'TC':'value''s','TestColumn':None},
                                          'CUSTOM_AND':['TestColumn IS NOT NULL','TC1 IS NULL'],
                                          'CUSTOM_OR':['TestColumn IS NOT NULL','TC1 IS NULL'],
                                          'WHERE_OR_VALUES_AND':{'TestColumn':None,
                                                                 'TC2':'value''s'}},
                             show_progress=True)
    assert update.call_count == 1

if __name__ == '__main__':
    unittest.main()
