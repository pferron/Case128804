"""Unit tests for maintenance_database_backups"""

import pytest
from unittest import mock
import sys
from maintenance_database_backups import *

JIRA_KEY = 'FAKE_KEY_123'
REPO = 'REPO'
MAIN_LOG = mock.MagicMock()

@pytest.fixture()
def scr_var_mock():
    return ScrVar

@mock.patch('maintenance_database_backups.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('maintenance_database_backups.TheLogs.process_exception_count_only')
@mock.patch('maintenance_database_backups.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch("maintenance_database_backups.backup_databases")
@mock.patch.object(General, "cmd_processor")
def test_main(cmd_processor_mock, backup_databases_mock):
    cmd_processor_mock.return_value = [{'args': {'arg_1': 'test'},
                                        'function': 'backup_databases'}]
    main()

@mock.patch("maintenance_database_backups.ScrVar.timed_script_teardown")
@mock.patch("maintenance_database_backups.cleanup_database_backups")
@mock.patch("pyodbc.connect")
@mock.patch("os.makedirs")
@mock.patch("os.path.exists",
            return_value=True)
@mock.patch("maintenance_database_backups.TheLogs.exception")
@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
@mock.patch("maintenance_database_backups.TheLogs.log_info")
@mock.patch("maintenance_database_backups.ScrVar.timed_script_setup")
def test_backup_databases(s_timer,log_ln,log_hl,ex_func,ex_fatal,path_exists,makedirs,conn_pyodbc,
                          r_cdb,e_timer):
    conn_pyodbc.return_value.cursor.return_value.nextset.return_value = False
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    backup_databases(MAIN_LOG)
    assert s_timer.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1
    assert ex_func.call_count == 0
    assert ex_fatal.call_count == 0
    assert makedirs.call_count == 0
    assert r_cdb.call_count == 1
    assert e_timer.call_count == 1

@mock.patch("maintenance_database_backups.ScrVar.timed_script_teardown")
@mock.patch("maintenance_database_backups.cleanup_database_backups")
@mock.patch("pyodbc.connect",
            side_effect=Exception)
@mock.patch("os.makedirs")
@mock.patch("os.path.exists",
            return_value=True)
@mock.patch("maintenance_database_backups.TheLogs.exception")
@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
@mock.patch("maintenance_database_backups.TheLogs.log_info")
@mock.patch("maintenance_database_backups.ScrVar.timed_script_setup")
def test_backup_databases_ex_001(s_timer,log_ln,log_hl,ex_func,ex_fatal,path_exists,makedirs,
                                 conn_pyodbc,r_cdb,e_timer):
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    backup_databases(MAIN_LOG)
    assert s_timer.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 0
    assert ex_func.call_count == 1
    assert ex_fatal.call_count == 0
    assert makedirs.call_count == 0
    assert r_cdb.call_count == 0
    assert e_timer.call_count == 1

@mock.patch("maintenance_database_backups.ScrVar.timed_script_teardown")
@mock.patch("maintenance_database_backups.cleanup_database_backups")
@mock.patch("pyodbc.connect")
@mock.patch("os.makedirs")
@mock.patch("os.path.exists",
            return_value=False)
@mock.patch("maintenance_database_backups.TheLogs.exception")
@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
@mock.patch("maintenance_database_backups.TheLogs.log_info")
@mock.patch("maintenance_database_backups.ScrVar.timed_script_setup")
def test_backup_databases_ex_002(s_timer,log_ln,log_hl,ex_func,ex_fatal,path_exists,makedirs,
                                 conn_pyodbc,r_cdb,e_timer):
    conn_pyodbc.return_value.cursor.return_value.nextset.return_value = False
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    backup_databases(MAIN_LOG)
    assert s_timer.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 0
    assert ex_func.call_count == 0
    assert ex_fatal.call_count == 1
    assert makedirs.call_count == 2
    assert r_cdb.call_count == 0
    assert e_timer.call_count == 1

@mock.patch("maintenance_database_backups.ScrVar.timed_script_teardown")
@mock.patch("maintenance_database_backups.cleanup_database_backups",
            side_effect=Exception)
@mock.patch("pyodbc.connect")
@mock.patch("os.makedirs")
@mock.patch("os.path.exists",
            return_value=True)
@mock.patch("maintenance_database_backups.TheLogs.exception")
@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
@mock.patch("maintenance_database_backups.TheLogs.log_info")
@mock.patch("maintenance_database_backups.ScrVar.timed_script_setup")
def test_backup_databases_ex_003(s_timer,log_ln,log_hl,ex_func,ex_fatal,path_exists,makedirs,
                                 conn_pyodbc,r_cdb,e_timer):
    conn_pyodbc.return_value.cursor.return_value.nextset.return_value = False
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    backup_databases(MAIN_LOG)
    assert s_timer.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1
    assert ex_func.call_count == 1
    assert ex_fatal.call_count == 0
    assert makedirs.call_count == 0
    assert r_cdb.call_count == 1
    assert e_timer.call_count == 1

@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("os.remove")
@mock.patch("os.path.join",
            return_value='rootfile_1')
@mock.patch("os.stat")
@mock.patch("os.walk",
            return_value=[('root','directories',['file_1'])])
@mock.patch("os.chdir")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
def test_cleanup_database_backups(log_hl,o_chdir,o_walk,o_stat,o_pj,o_rem,ex_func):
    """Tests cleanup_database_backups"""
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    cleanup_database_backups()
    assert log_hl.call_count == 1
    assert o_chdir.call_count == 1
    assert o_walk.call_count == 1
    assert o_stat.call_count == 1
    assert o_pj.call_count == 2
    assert o_rem.call_count == 1
    assert ex_func.call_count == 0

@mock.patch("maintenance_database_backups.TheLogs.function_exception")
@mock.patch("os.remove")
@mock.patch("os.path.join",
            return_value='rootfile_1')
@mock.patch("os.stat")
@mock.patch("os.walk",
            side_effect=Exception)
@mock.patch("os.chdir")
@mock.patch("maintenance_database_backups.TheLogs.log_headline")
def test_cleanup_database_backups_ex_001(log_hl,o_chdir,o_walk,o_stat,o_pj,o_rem,ex_func):
    """Tests cleanup_database_backups"""
    ScrVar.databases = [{'databaseName': 'AppSec', 'backupDay': 'All'}]
    cleanup_database_backups()
    assert log_hl.call_count == 1
    assert o_chdir.call_count == 1
    assert o_walk.call_count == 1
    assert o_pj.call_count == 0
    assert o_rem.call_count == 0
    assert ex_func.call_count == 1

