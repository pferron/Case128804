'''Unit tests for the product_onboarding script '''

import unittest
from unittest import mock
import sys
import os
from scripts.product_onboarding import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()

@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'update_mend',
                                                          'args': 'appsec-ops'},
                                                          {'function': 'update_mend',
                                                          'args': 'appsec-ops'}])
@mock.patch("scripts.product_onboarding.update_mend")
def test_main(mend_mock,cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\product_onboarding.py', 'update_mend(appsec-ops)',
                'update_mend(appsec-ops)']
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()
        assert mend_mock.call_count == 2

@mock.patch.object(General,'cmd_processor',return_value=[])
def test_main_no_args(cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\product_onboarding.py']
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()

@mock.patch("scripts.product_onboarding.update_mend")
@mock.patch("scripts.product_onboarding.update_checkmarx")
def test_update_all(cx_mock, mend_mock):
    '''tests update all'''
    update_all('appsec-ops')
    cx_mock.assert_called_once()
    mend_mock.assert_called_once()

@mock.patch("scripts.product_onboarding.single_project_onboard")
@mock.patch("scripts.product_onboarding.project_id")
@mock.patch("scripts.product_onboarding.project_id_transform")
@mock.patch("scripts.product_onboarding.repo_check_aa")
@mock.patch("scripts.product_onboarding.update_aa_table")
@mock.patch("scripts.product_onboarding.repo_check_app")
@mock.patch("scripts.product_onboarding.update_app_table")
@mock.patch.object(TheLogs, 'log_headline')
def test_update_checkmarx(log_mock, app_update_mock, app_check_mock, aa_update_mock, aa_check_mock, transform_mock, project_id_mock, sp_onboard_mock):
    '''tests update checkmarx'''
    update_checkmarx('repo', main_log=LOG)
    project_id_mock.assert_called_once()
    transform_mock.assert_called_once()
    aa_check_mock.assert_called_once()
    aa_update_mock.assert_called_once()
    app_check_mock.assert_called_once()
    app_update_mock.assert_called_once()
    sp_onboard_mock.assert_called_once()
    assert log_mock.call_count == 2

@mock.patch("product_onboarding.CxAPI.get_repo_project_id",
            return_value=1)
def test_project_id_success(proj_id):
    '''tests getting project id'''
    project_id('appsec')
    assert proj_id.call_count == 1

@mock.patch.object(TheLogs, 'exception')
@mock.patch.object(CxAPI, 'get_repo_project_id', side_effect=Exception())
def test_project_id_except(get_data_mock, log_mock):
    '''tests exception for this function'''
    try:
        project_id('appsec')
        get_data_mock.assert_called_once()
    except Exception:
        log_mock.assert_called_once()

def test_project_id_transform_none():
    '''tests project_id_transform with None results'''
    get_proj_id = None
    res = project_id_transform(get_proj_id)
    assert res == "No or None proj ID"

def test_project_id_transform_empty():
    '''tests project_id_transform with [] result'''
    get_proj_id = []
    res = project_id_transform(get_proj_id)
    assert res == "No or None proj ID"

def test_project_id_transform():
    '''tests successful project_id_transform'''
    get_proj_id = {'cxProjectId': 10915, 'BranchedFrom': 10810}
    res = project_id_transform(get_proj_id)
    assert res == 10915

@mock.patch('scripts.product_onboarding.conn')
def test_repo_check_aa(conn_mock):
    '''tests repo check on ApplicationAutomation table'''
    repo_check_aa('appsec')
    conn_mock.query_with_logs.assert_called_once()

@mock.patch.object(TheLogs, 'log_info')
@mock.patch('scripts.product_onboarding.conn')
def test_update_aa_table(conn_mock, log_mock):
    '''tests repo check on ApplicationAutomation table'''
    conn_mock.query_with_logs.return_value = 1
    res = update_aa_table(12, 'appsec')
    assert res == 1
    log_mock.assert_called_once()

@mock.patch('scripts.product_onboarding.conn')
def test_repo_check_app(conn_mock):
    '''tests repo check on Applications table'''
    conn_mock.query_with_logs.return_value = [('appsec', )]
    res = repo_check_app('appsec')
    assert res == [('appsec', )]

@mock.patch.object(TheLogs, 'log_info')
@mock.patch('scripts.product_onboarding.conn')
def test_update_app_table(conn_mock, log_mock):
    '''tests repo check on Applications table'''
    conn_mock.query_with_logs.return_value = 1
    res = update_app_table(12, 'appsec')
    assert res == 1
    log_mock.assert_called_once()

@mock.patch('scripts.product_onboarding.single_project_updates')
def test_single_project_onboard(update_mock):
    '''tests successful onboard'''
    single_project_onboard('repo', 24, 'log')
    update_mock.assert_called_once()

@mock.patch.object(TheLogs, 'function_exception')
@mock.patch('scripts.product_onboarding.single_project_updates', side_effect=Exception())
def test_single_project_onboard_exception(update_mock, log_mock):
    '''test onboard exception'''
    try:
        single_project_onboard('repo', 24, 'log')
        update_mock.assert_called_once()
    except Exception:
        log_mock.assert_called_once()

@mock.patch.object(MendRepos, 'onboard_single_repo')
@mock.patch('product_onboarding.TheLogs.log_headline')
def test_update_mend(log_mock, single_repo_mock):
    '''tests updating mend'''
    update_mend('appsec')
    single_repo_mock.assert_called_once()
    assert log_mock.call_count == 2

@mock.patch.object(MendRepos, 'onboard_single_repo', side_effect=Exception())
@mock.patch.object(TheLogs, 'exception')
def test_update_mend_exception(log_mock, single_repo_mock):
    '''tests update mend exception'''
    try:
        update_mend('appsec')
        log_mock.assert_called_once()
        single_repo_mock.assert_called_once()
    except Exception:
        log_mock.assert_called_once()

@mock.patch('scripts.product_onboarding.update_all_scans')
def test_checkmarx_update_run(update_mock):
    '''tests checkumarx update run'''
    checkmarx_update_run('repo','log')
    update_mock.assert_called_once()

def test_sql_success_check():
    res = sql_success_check([9, 'SQL-CONNECT-01'])
    assert res == None

if __name__ == '__main__':
    unittest.main()
