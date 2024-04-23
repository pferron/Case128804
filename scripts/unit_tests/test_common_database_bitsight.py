'''Unit tests for common\database_bitsight.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from common.database_bitsight import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.database_bitsight.pyodbc.connect')
def test_database_connection(connect):
    '''Tests database_connection'''
    BitSightDB.database_connection()
    assert connect.call_count == 1

@mock.patch('common.database_bitsight.pyodbc.connect')
def test_database_connection_exists(connect):
    '''Tests database_connection'''
    appsec_connection = 'something'
    BitSightDB.database_connection()
    assert connect.call_count == 0

@mock.patch('common.database_bitsight.BitSightDB.database_connection')
def test_select(db_connect):
    '''Tests select'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = ['returned']
    BitSightDB.select('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_bitsight.BitSightDB.database_connection')
def test_insert(db_connect):
    '''Tests insert'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    BitSightDB.insert('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_bitsight.BitSightDB.database_connection')
def test_update(db_connect):
    '''Tests update'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    BitSightDB.update('sql')
    assert db_connect.call_count == 1

@mock.patch('common.database_bitsight.BitSightDB.database_connection')
def test_delete_row(db_connect):
    '''Tests delete_row'''
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = 1
    BitSightDB.delete_row('sql')
    assert db_connect.call_count == 1

if __name__ == '__main__':
    unittest.main()
