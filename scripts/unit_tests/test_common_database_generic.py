'''Unit tests for common\database_generic.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from common.database_generic import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.database_generic.pyodbc.connect')
def test_dbqueries_database_connection(connect):
    '''Tests DBQueries.database_connection'''
    DBQueries.database_connection('AppSec')
    assert connect.call_count == 1

@mock.patch('common.database_generic.pyodbc.connect')
def test_dbqueries_database_connection_exists(connect):
    '''Tests DBQueries.database_connection'''
    appsec_connection = 'something'
    DBQueries.database_connection('AppSec')
    assert connect.call_count == 0

@mock.patch('common.database_generic.DBQueries.database_connection')
def test_dbqueries_select(db_connect):
    '''Tests DBQueries.select'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = ['returned']
    DBQueries.select('sql','database')
    assert db_connect.call_count == 1

@mock.patch('common.database_generic.DBQueries.database_connection')
def test_dbqueries_insert(db_connect):
    '''Tests DBQueries.insert'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    DBQueries.insert('sql','database')
    assert db_connect.call_count == 1

@mock.patch('common.database_generic.DBQueries.database_connection')
def test_dbqueries_update(db_connect):
    '''Tests DBQueries.update'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    DBQueries.update('sql','database')
    assert db_connect.call_count == 1

@mock.patch('common.database_generic.DBQueries.database_connection')
def test_dbqueries_delete_row(db_connect):
    '''Tests DBQueries.delete_row'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    DBQueries.delete_row('sql','database')
    assert db_connect.call_count == 1

@mock.patch('common.database_generic.DBQueries.insert')
@pytest.mark.parametrize("table_name,array,database,level,verify_on,custom_filter,show_progress",
                         [('table',{'test':'value','test2':None},'AppSec',1,['test','test2'],
                          "AND Something != 'Nothing'",True),
                          ('table',{'test':'value','test2':None},'AppSec',1,[],
                          None,True)
                         ])
def test_dbqueries_insert_multiple(insert,table_name,array,database,level,verify_on,custom_filter,
                                   show_progress):
    '''Tests DBQueries.insert_multiple'''
    insert.return_value = 1
    DBQueries.insert_multiple(table_name,array,database,level,verify_on,custom_filter,show_progress)
    assert insert.call_count == 1

@mock.patch('common.database_generic.DBQueries.update')
def test_dbqueries_update_multiple(update):
    '''Tests DBQueries.update_multiple'''
    DBQueries.update_multiple('TestTable',{'SET':{'TestColumn':'TestValue','TC1':None},
                                          'WHERE_EQUAL':{'TestColumn':None,'TC2':'value''s'},
                                          'WHERE_NOT':{'TC':'value''s','TestColumn':None},
                                          'WHERE_LIKE':{'TC':'value''s','TestColumn':None},
                                          'WHERE_NOT_LIKE':{'TC':'value''s','TestColumn':None},
                                          'WHERE_NOT_IN':{'TC':'value''s','TestColumn':None},
                                          'WHERE_IN':{'TC':'value''s','TestColumn':None},
                                          'CUSTOM_AND':['TestColumn IS NOT NULL','TC1 IS NULL'],
                                          'CUSTOM_OR':['TestColumn IS NOT NULL','TC1 IS NULL'],
                                          'WHERE_OR_VALUES_AND':{'TestColumn':None,
                                                                 'TC2':'value''s'}},'database',
                                                                 show_progress=True)
    assert update.call_count == 1

if __name__ == '__main__':
    unittest.main()
