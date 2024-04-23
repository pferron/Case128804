'''Unit tests for the nonprodsec_infosecdashboard script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from infosecdashboard.database import *

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('ProjectKey',)])
def test_IFDQueries_check_if_epic_exists_success(select,s_exception):
    """Tests IFDQueries.check_if_epic_exists"""
    IFDQueries.check_if_epic_exists('epic_key')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_epic_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_epic_exists"""
    IFDQueries.check_if_epic_exists('epic_key')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('IssueKey',)])
def test_IFDQueries_check_if_issue_exists_success(select,s_exception):
    """Tests IFDQueries.check_if_issue_exists"""
    IFDQueries.check_if_issue_exists('use_table','issue_key')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_issue_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_issue_exists"""
    IFDQueries.check_if_issue_exists('use_table','issue_key')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('ProjectKey',)])
def test_IFDQueries_check_if_project_exists_success(select,s_exception):
    """Tests IFDQueries.check_if_project_exists"""
    IFDQueries.check_if_project_exists('project_key')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_project_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_project_exists"""
    IFDQueries.check_if_project_exists('project_key')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('ProgramKey',)])
def test_IFDQueries_check_if_program_exists_success(select,s_exception):
    """Tests IFDQueries.check_if_program_exists"""
    IFDQueries.check_if_program_exists('program_key')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_program_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_program_exists"""
    IFDQueries.check_if_program_exists('program_key')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('SubTaskIssueKey',)])
def test_IFDQueries_check_if_subtask_exists_success(select,s_exception):
    """Tests IFDQueries.check_if_subtask_exists"""
    IFDQueries.check_if_subtask_exists('use_table','subtask_key')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_subtask_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_subtask_exists"""
    IFDQueries.check_if_subtask_exists('use_table','subtask_key')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.IFDQueries.create_new_project_table')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('name',)])
def test_IFDQueries_check_if_table_exists_success_exists(select,c_table,s_exception):
    """Tests IFDQueries.check_if_table_exists"""
    IFDQueries.check_if_table_exists('use_table')
    assert select.call_count == 1
    assert c_table.call_count == 0
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.IFDQueries.create_new_project_table')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[])
def test_IFDQueries_check_if_table_exists_success_does_not_exist(select,c_table,s_exception):
    """Tests IFDQueries.check_if_table_exists"""
    IFDQueries.check_if_table_exists('use_table')
    assert select.call_count == 1
    assert c_table.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_check_if_table_exists_failure(select,s_exception):
    """Tests IFDQueries.check_if_table_exists"""
    IFDQueries.check_if_table_exists('use_table')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.update')
def test_IFDQueries_create_new_project_table_success(update,s_exception):
    """Tests IFDQueries.create_new_project_table"""
    IFDQueries.create_new_project_table('use_table')
    assert update.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.update',
            side_effect=Exception)
def test_IFDQueries_create_new_project_table_failure(update,s_exception):
    """Tests IFDQueries.create_new_project_table"""
    IFDQueries.create_new_project_table('use_table')
    assert update.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('EpicKey',)])
def test_IFDQueries_get_epics_for_project_success(select,s_exception):
    """Tests IFDQueries.get_epics_for_project"""
    IFDQueries.get_epics_for_project('project_name')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_get_epics_for_project_failure(select,s_exception):
    """Tests IFDQueries.get_epics_for_project"""
    IFDQueries.get_epics_for_project('project_name')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('JiraProjectKey','JiraProjectName','InfoSecDashboardTable')])
def test_IFDQueries_get_projects_success(select,s_exception):
    """Tests IFDQueries.get_projects"""
    IFDQueries.get_projects()
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_get_projects_failure(select,s_exception):
    """Tests IFDQueries.get_projects"""
    IFDQueries.get_projects('project_name')
    assert select.call_count == 1
    assert s_exception.call_count == 1

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            return_value=[('ProgramKey','ProgramName')])
def test_IFDQueries_get_programs_for_project_success(select,s_exception):
    """Tests IFDQueries.get_programs_for_project"""
    IFDQueries.get_programs_for_project('project_name')
    assert select.call_count == 1
    assert s_exception.call_count == 0

@mock.patch('infosecdashboard.database.TheLogs.sql_exception')
@mock.patch('infosecdashboard.database.DBQueries.select',
            side_effect=Exception)
def test_IFDQueries_get_programs_for_project_failure(select,s_exception):
    """Tests IFDQueries.get_programs_for_project"""
    IFDQueries.get_programs_for_project('project_name')
    assert select.call_count == 1
    assert s_exception.call_count == 1

if __name__ == '__main__':
    unittest.main()
