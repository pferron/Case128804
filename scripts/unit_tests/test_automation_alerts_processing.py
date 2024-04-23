'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
import pytest
from automation_alerts.processing import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('automation_alerts.processing.retrieve_functions',
            return_value=[('function')])
@mock.patch('automation_alerts.processing.retrieve_scripts',
            return_value=[('script')])
@mock.patch('automation_alerts.processing.retrieve_batch_files',
            return_value=[('file')])
def test_processautomation_get_missing_runs_success(files,scripts,funcs):
    """Tests ProcessAutomation.get_missing_runs"""
    ProcessAutomation.get_missing_runs('test')
    assert files.call_count == 1
    assert scripts.call_count == 1
    assert funcs.call_count == 1

@mock.patch('automation_alerts.processing.retrieve_functions',
            return_value=[('function')])
@mock.patch('automation_alerts.processing.retrieve_scripts',
            return_value=[('script')])
@mock.patch('automation_alerts.processing.select',
            side_effect=Exception)
def test_processautomation_get_missing_runs_exception_in_batch_files(files,scripts,funcs):
    """Tests ProcessAutomation.get_missing_runs"""
    ProcessAutomation.get_missing_runs('test')
    assert files.call_count == 1
    assert scripts.call_count == 0
    assert funcs.call_count == 0
    ScrVar.fe_cnt = 0

@mock.patch('automation_alerts.processing.retrieve_functions',
            return_value=[('function')])
@mock.patch('automation_alerts.processing.select',
            side_effect=Exception)
@mock.patch('automation_alerts.processing.retrieve_batch_files',
            return_value=[('file')])
def test_processautomation_get_missing_runs_exception_in_scripts(files,scripts,funcs):
    """Tests ProcessAutomation.get_missing_runs"""
    ProcessAutomation.get_missing_runs('test')
    assert files.call_count == 1
    assert scripts.call_count == 1
    assert funcs.call_count == 0
    ScrVar.fe_cnt = 0

@mock.patch('automation_alerts.processing.select',
            side_effect=Exception)
@mock.patch('automation_alerts.processing.retrieve_scripts',
            return_value=[('script')])
@mock.patch('automation_alerts.processing.retrieve_batch_files',
            return_value=[('file')])
def test_processautomation_get_missing_runs_exception_in_functions(files,scripts,funcs):
    """Tests ProcessAutomation.get_missing_runs"""
    ProcessAutomation.get_missing_runs('test')
    assert files.call_count == 1
    assert scripts.call_count == 1
    assert funcs.call_count == 1
    ScrVar.fe_cnt = 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.select',
            return_value=[('file')])
def test_retrieve_batch_files_success(files,s_exception):
    """Tests retrieve_batch_files"""
    retrieve_batch_files('test')
    assert files.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.did_it_run',
            return_value=True)
@mock.patch('automation_alerts.processing.select',
            return_value=[('script')])
@pytest.mark.parametrize("batch,col_name",
                         [('file.bat','Sunday'),
                          ('file.bat','FirstOfMonth'),
                          ('file.bat','Every5Minutes'),
                          ('file.bat','Hourly')])
def test_retrieve_scripts_success_it_ran(scripts,ran,s_exception,batch,col_name):
    """Tests retrieve_scripts"""
    retrieve_scripts(batch,col_name)
    assert scripts.call_count == 1
    assert ran.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.did_it_run',
            return_value=False)
@mock.patch('automation_alerts.processing.select',
            return_value=[('script')])
def test_retrieve_scripts_success_it_did_not_run(scripts,ran,s_exception):
    """Tests retrieve_scripts"""
    retrieve_scripts('test','test')
    assert scripts.call_count == 1
    assert ran.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.did_it_run')
@mock.patch('automation_alerts.processing.select')
@pytest.mark.parametrize("batch,col_name,script,sel_val,dir_val",
                         [('file.bat','Sunday','test_script.py',[('script',)],True),
                          ('file.bat','FirstOfMonth','test_script.py',[('script',)],False),
                          ('file.bat','Every5Minutes','test_script.py',[('script',)],True),
                          ('file.bat','Hourly','test_script.py',[('script',)],False)])
def test_retrieve_functions(sql_sel,dir,ex_sql,batch,col_name,script,sel_val,dir_val):
    """Tests retrieve_functions"""
    sql_sel.return_value = sel_val
    dir.return_value = dir_val
    retrieve_functions(batch,col_name,script)
    assert sql_sel.call_count == 1
    assert dir.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.select',
            return_value=[('script')])
def test_did_it_run_success_generic_script(funcs,s_exception):
    """Tests did_it_run"""
    did_it_run('test',None,'DATEADD(hour,-24,GETDATE())')
    assert funcs.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.select',
            return_value=[('script')])
def test_did_it_run_success_snow_script(funcs,s_exception):
    """Tests did_it_run"""
    did_it_run('maintenance_snow.py','process_all_updates','DATEADD(hour,-24,GETDATE())')
    assert funcs.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.select',
            return_value=[('script')])
def test_did_it_run_success_jenkins_script(funcs,s_exception):
    """Tests did_it_run"""
    did_it_run('maintenance_jenkins.py','something','DATEADD(hour,-24,GETDATE())')
    assert funcs.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('automation_alerts.processing.TheLogs.sql_exception')
@mock.patch('automation_alerts.processing.select',
            side_effect=Exception)
def test_did_it_run_exception(funcs,s_exception):
    """Tests did_it_run"""
    did_it_run('test',None,'DATEADD(hour,-24,GETDATE())')
    assert funcs.call_count == 1
    assert s_exception.call_count == 1

if __name__ == '__main__':
    unittest.main()
