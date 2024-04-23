'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
from maint.mend_user_cleanup import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_ScrVar_reset_exception_counts():
    '''Resets exception counts'''
    ScrVar.fe_cnt = 1
    ScrVar.ex_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_is_user_active(connect_mend,req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result':[{'active':'true'}]}
    req.return_value = resp_mock
    results = MendUsers.is_user_active('stacy.castleton@progleasing.com')
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert results is True
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_is_user_active_bad_status_code(connect_mend,req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=403)
    resp_mock.json.return_value = {}
    req.return_value = resp_mock
    results = MendUsers.is_user_active('stacy.castleton@progleasing.com')
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is None
    assert ScrVar.ex_cnt == 1
    assert ScrVar.fe_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_is_user_active_exception(connect_mend,req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=0)
    resp_mock.json.return_value = {}
    req.return_value = resp_mock
    results = MendUsers.is_user_active('stacy.castleton@progleasing.com')
    connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert ScrVar.ex_cnt == 1
    assert ScrVar.fe_cnt == 0
    assert results is None
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table')
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table',return_value=1)
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=True)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_update(log_hl,connect_mend,req,except_func,
                                                  log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    connect_mend.token = 'token'
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert in_db.call_count == 1
    assert sql_update.call_count == 1
    assert sql_insert.call_count == 0
    assert log_ln.call_count == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table',return_value=1)
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table')
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_insert(log_hl,connect_mend,req,except_func,
                                                  log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert in_db.call_count == 1
    assert sql_update.call_count == 0
    assert sql_insert.call_count == 1
    assert log_ln.call_count == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table',return_value=1)
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table')
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_req_exception(log_hl,connect_mend,req,except_func,
                                                         log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert in_db.call_count == 0
    assert sql_update.call_count == 0
    assert sql_insert.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table',return_value=1)
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table')
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_req_bad_status_code(log_hl,connect_mend,req,except_func,
                                                               log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert in_db.call_count == 0
    assert sql_update.call_count == 0
    assert sql_insert.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table',return_value=1)
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=True)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_update_exception(log_hl,connect_mend,req,except_func,
                                                            log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert in_db.call_count == 1
    assert sql_update.call_count == 1
    assert sql_insert.call_count == 0
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.insert_multiple_into_table',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.update_multiple_in_table')
@mock.patch('maint.mend_user_cleanup.MendUsers.service_account_in_db',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
def test_mendusers_update_service_accounts_insert_exception(log_hl,connect_mend,req,except_func,
                                                            log_ln,in_db,sql_update,sql_insert):
    '''Tests update_service_accounts'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},
                                   'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378",
                                              "name":"CircleCI_WS","email":
                                              "circleci_ws@progleasing.com","userType":"SERVICE",
                                              "accountStatus":"ACTIVE"}],
                                              'supportToken':
                                              '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    MendUsers.update_service_accounts()
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert in_db.call_count == 1
    assert sql_update.call_count == 0
    assert sql_insert.call_count == 1
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.mend_user_cleanup.select',return_value=[('1',)])
def test_mendusers_service_account_in_db(sql_select,except_sql):
    '''Tests service_account_in_db'''
    results = MendUsers.service_account_in_db(1)
    assert sql_select.call_count == 1
    assert except_sql.call_count == 0
    assert results is True

@mock.patch('maint.mend_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.mend_user_cleanup.select',side_effect=Exception)
def test_mendusers_service_account_in_db_sql_exception(sql_select,except_sql):
    '''Tests service_account_in_db'''
    results = MendUsers.service_account_in_db(1)
    assert sql_select.call_count == 1
    assert except_sql.call_count == 1
    assert results is None
    assert ScrVar.ex_cnt == 1
    assert ScrVar.fe_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.MendUsers.delete_mend_account',return_value=True)
@mock.patch('maint.mend_user_cleanup.MendUsers.is_user_active',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.mend_user_cleanup.MendUsers.update_service_accounts')
@mock.patch('maint.mend_user_cleanup.ScrVar.reset_exception_counts')
def test_mendusers_remove_deactivated_users_account_deleted(exception_reset,sa_update,log_hl,
                                                            connect_mend,req,except_func,log_ln,
                                                            is_active,del_account):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},'retVal':
                                   [{'uuid':'0ec3794f-7d6f-452d-8342-3359ccb9b199','name':
                                     'John McCutchen','email':'john.mccutchen@progleasing.com',
                                     'userType':'REGULAR','accountStatus':'ACTIVE'}],
                                     'supportToken':
                                     '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    results = MendUsers.remove_deactivated_users()
    assert exception_reset.call_count == 1
    assert sa_update.call_count == 1
    assert log_hl.call_count == 2
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert log_ln.call_count == 2
    assert is_active.call_count == 1
    assert del_account.call_count == 1
    assert results == {'FatalCount':0,'ExceptionCount':0,'Results':[]}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.MendUsers.delete_mend_account',return_value=False)
@mock.patch('maint.mend_user_cleanup.MendUsers.is_user_active',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.mend_user_cleanup.MendUsers.update_service_accounts')
@mock.patch('maint.mend_user_cleanup.ScrVar.reset_exception_counts')
def test_mendusers_remove_deactivated_users_account_not_deleted(exception_reset,sa_update,log_hl,
                                                                connect_mend,req,except_func,
                                                                log_ln,is_active,del_account):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},'retVal':
                                   [{'uuid':'0ec3794f-7d6f-452d-8342-3359ccb9b199','name':
                                     'John McCutchen','email':'john.mccutchen@progleasing.com',
                                     'userType':'REGULAR','accountStatus':'ACTIVE'}],
                                     'supportToken':
                                     '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    results = MendUsers.remove_deactivated_users()
    assert exception_reset.call_count == 1
    assert sa_update.call_count == 1
    assert log_hl.call_count == 2
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert log_ln.call_count == 3
    assert is_active.call_count == 1
    assert del_account.call_count == 1
    assert results == {'FatalCount':0,'ExceptionCount':0,
                       'Results':['john.mccutchen@progleasing.com']}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.MendUsers.delete_mend_account',return_value=True)
@mock.patch('maint.mend_user_cleanup.MendUsers.is_user_active',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.mend_user_cleanup.MendUsers.update_service_accounts')
@mock.patch('maint.mend_user_cleanup.ScrVar.reset_exception_counts')
def test_mendusers_remove_deactivated_users_req_exception(exception_reset,sa_update,log_hl,
                                                          connect_mend,req,except_func,log_ln,
                                                          is_active,del_account):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},'retVal':
                                   [{'uuid':'0ec3794f-7d6f-452d-8342-3359ccb9b199','name':
                                     'John McCutchen','email':'john.mccutchen@progleasing.com',
                                     'userType':'REGULAR','accountStatus':'ACTIVE'}],
                                     'supportToken':
                                     '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    results = MendUsers.remove_deactivated_users()
    assert exception_reset.call_count == 1
    assert sa_update.call_count == 1
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert log_ln.call_count == 0
    assert is_active.call_count == 0
    assert del_account.call_count == 0
    assert results == {'FatalCount':1,'ExceptionCount':0,'Results':[]}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.MendUsers.delete_mend_account',return_value=True)
@mock.patch('maint.mend_user_cleanup.MendUsers.is_user_active',return_value=False)
@mock.patch('maint.mend_user_cleanup.TheLogs.log_info')
@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.get')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
@mock.patch('maint.mend_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.mend_user_cleanup.MendUsers.update_service_accounts')
@mock.patch('maint.mend_user_cleanup.ScrVar.reset_exception_counts')
def test_mendusers_remove_deactivated_users_req_bad_status_code(exception_reset,sa_update,log_hl,
                                                                connect_mend,req,except_func,
                                                                log_ln,is_active,del_account):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = {'additionalData':{'totalItems':40,'isLastPage':True},'retVal':
                                   [{'uuid':'0ec3794f-7d6f-452d-8342-3359ccb9b199','name':
                                     'John McCutchen','email':'john.mccutchen@progleasing.com',
                                     'userType':'REGULAR','accountStatus':'ACTIVE'}],
                                     'supportToken':
                                     '2eac3073a25d04fe4ab4003993ac945af1695847861538'}
    req.return_value = resp_mock
    results = MendUsers.remove_deactivated_users()
    assert exception_reset.call_count == 1
    assert sa_update.call_count == 1
    assert log_hl.call_count == 1
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert log_ln.call_count == 1
    assert is_active.call_count == 0
    assert del_account.call_count == 0
    assert results == {'FatalCount':1,'ExceptionCount':0,'Results':[]}
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.delete')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_delete_mend_account(connect_mend,req,except_func):
    '''Tests delete_mend_account'''
    resp_mock = mock.Mock(status_code=200)
    req.return_value = resp_mock
    results = MendUsers.delete_mend_account(123456)
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    assert results is True
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.delete',side_effect=Exception)
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_delete_mend_account_req_exception(connect_mend,req,except_func):
    '''Tests delete_mend_account'''
    resp_mock = mock.Mock(status_code=200)
    req.return_value = resp_mock
    results = MendUsers.delete_mend_account(123456)
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    assert results is False
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

@mock.patch('maint.mend_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.mend_user_cleanup.requests.delete')
@mock.patch('maint.mend_user_cleanup.MendAPI.mend_connect')
def test_mendusers_delete_mend_account_req_bad_status_code(connect_mend,req,except_func):
    '''Tests delete_mend_account'''
    resp_mock = mock.Mock(status_code=400)
    req.return_value = resp_mock
    results = MendUsers.delete_mend_account(123456)
    assert connect_mend.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    assert results is False
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
    MendAPI.token = None

if __name__ == '__main__':
    unittest.main()
