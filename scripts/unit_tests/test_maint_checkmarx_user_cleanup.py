'''Unit tests for the maintenance_jira_issues script '''

import unittest
from unittest import mock
import sys
import os
from maint.checkmarx_user_cleanup import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

def test_mucvar_reset_exception_counts():
    '''Resets exception counts'''
    ScrVar.fe_cnt = 1
    ScrVar.ex_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.requests.post')
def test_cxusers_access_control_connection(req):
    '''Tests access_control_connection'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'access_token':'token'}
    req.return_value = resp_mock
    results = CxUsers.access_control_connection()
    assert req.call_count == 1
    assert results == 'token'
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
def test_cxusers_is_user_active(req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result':[{'active':'true'}]}
    req.return_value = resp_mock
    results = CxUsers.is_user_active('john.mccutcheon@progleasing.com')
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert results is True
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get',side_effect=Exception)
def test_cxusers_is_user_active_req_exception(req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result':[{'active':'true'}]}
    req.return_value = resp_mock
    results = CxUsers.is_user_active('john.mccutcheon@progleasing.com')
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is None
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
def test_cxusers_is_user_active_req_bad_status_code(req,except_func):
    '''Tests is_user_active'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = {'result':[{'active':'true'}]}
    req.return_value = resp_mock
    results = CxUsers.is_user_active('john.mccutcheon@progleasing.com')
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is None
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.delete_user_account',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.is_user_active',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.process_service_account')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.remove_expiration_date',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_service_accounts',return_value=['1','10'])
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.ScrVar.reset_exception_counts')
def test_cxusers_remove_deactivated_users(except_reset,connect_api,log_hl,req,log_ln,get_sa,
                                          rem_exp_date,sa_processing,is_active,del_account,except_func):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':12,'userName':'name','email':'email',
                                    'expirationDate':'2050-12-31'},{'id':10,'userName':'svc_name',
                                                                    'email':'email',
                                                                    'expirationDate':
                                                                '2050-12-31T23:59:59.0598536Z'}]
    req.return_value = resp_mock
    results = CxUsers.remove_deactivated_users()
    assert except_reset.call_count == 1
    assert connect_api.call_count == 1
    assert log_hl.call_count == 3
    assert req.call_count == 1
    assert log_ln.call_count == 3
    assert get_sa.call_count == 2
    assert rem_exp_date.call_count == 1
    assert sa_processing.call_count == 1
    assert is_active.call_count == 1
    assert del_account.call_count == 1
    assert except_func.call_count == 0
    assert results == {'ExceptionCount': 0, 'FatalCount': 0, 'Results': []}
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.delete_user_account',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.is_user_active',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.process_service_account')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.remove_expiration_date')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_service_accounts',return_value=['1','10'])
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.ScrVar.reset_exception_counts')
def test_cxusers_remove_deactivated_users_api_blank(except_reset,connect_api,log_hl,req,log_ln,get_sa,
                                          rem_exp_date,sa_processing,is_active,del_account,except_func):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = []
    req.return_value = resp_mock
    results = CxUsers.remove_deactivated_users()
    assert except_reset.call_count == 1
    assert connect_api.call_count == 1
    assert log_hl.call_count == 1
    assert req.call_count == 1
    assert log_ln.call_count == 1
    assert get_sa.call_count == 0
    assert rem_exp_date.call_count == 0
    assert sa_processing.call_count == 0
    assert is_active.call_count == 0
    assert del_account.call_count == 0
    assert except_func.call_count == 0
    assert results == {'ExceptionCount': 0, 'FatalCount': 0, 'Results': []}
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.delete_user_account',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.is_user_active',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.process_service_account')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.remove_expiration_date',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_service_accounts',return_value=['1','10'])
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.ScrVar.reset_exception_counts')
def test_cxusers_remove_deactivated_users_account_deletion_failure(except_reset,connect_api,log_hl,
                                                                   req,log_ln,get_sa,rem_exp_date,
                                                                   sa_processing,is_active,
                                                                   del_account,except_func):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':12,'userName':'name','email':'email',
                                    'expirationDate':'2050-12-31'},{'id':10,'userName':'svc_name',
                                                                    'email':'email',
                                                                    'expirationDate':
                                                                '2050-12-31T23:59:59.0598536Z'}]
    req.return_value = resp_mock
    results = CxUsers.remove_deactivated_users()
    assert except_reset.call_count == 1
    assert connect_api.call_count == 1
    assert log_hl.call_count == 3
    assert req.call_count == 1
    assert log_ln.call_count == 3
    assert get_sa.call_count == 2
    assert rem_exp_date.call_count == 1
    assert sa_processing.call_count == 1
    assert is_active.call_count == 1
    assert del_account.call_count == 1
    assert except_func.call_count == 0
    assert results == {'ExceptionCount': 0, 'FatalCount': 0, 'Results': ['email']}
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.delete_user_account',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.is_user_active',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.process_service_account')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.remove_expiration_date')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_service_accounts',return_value=['1','10'])
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.requests.get',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.ScrVar.reset_exception_counts')
def test_cxusers_remove_deactivated_users_req_exception(except_reset,connect_api,log_hl,req,log_ln,
                                                        get_sa,rem_exp_date,sa_processing,
                                                        is_active,del_account,except_func):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = []
    req.return_value = resp_mock
    results = CxUsers.remove_deactivated_users()
    assert except_reset.call_count == 1
    assert connect_api.call_count == 1
    assert log_hl.call_count == 1
    assert req.call_count == 1
    assert log_ln.call_count == 0
    assert get_sa.call_count == 0
    assert rem_exp_date.call_count == 0
    assert sa_processing.call_count == 0
    assert is_active.call_count == 0
    assert del_account.call_count == 0
    assert except_func.call_count == 1
    assert results == {'ExceptionCount': 0, 'FatalCount': 1, 'Results': []}
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.delete_user_account',return_value=True)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.is_user_active',return_value=False)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.process_service_account')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.remove_expiration_date')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_service_accounts',return_value=['1','10'])
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_headline')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.ScrVar.reset_exception_counts')
def test_cxusers_remove_deactivated_users_bad_status_code(except_reset,connect_api,log_hl,req,
                                                          log_ln,get_sa,rem_exp_date,sa_processing,
                                                          is_active,del_account,except_func):
    '''Tests remove_deactivated_users'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = []
    req.return_value = resp_mock
    results = CxUsers.remove_deactivated_users()
    assert except_reset.call_count == 1
    assert connect_api.call_count == 1
    assert log_hl.call_count == 1
    assert req.call_count == 1
    assert log_ln.call_count == 0
    assert get_sa.call_count == 0
    assert rem_exp_date.call_count == 0
    assert sa_processing.call_count == 0
    assert is_active.call_count == 0
    assert del_account.call_count == 0
    assert except_func.call_count == 1
    assert results == {'ExceptionCount': 0, 'FatalCount': 1, 'Results': []}
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',return_value=[('1',),('10',)])
def test_cxusers_get_service_accounts(sql_select,except_sql):
    '''Tests get_service_accounts'''
    results = CxUsers.get_service_accounts()
    assert sql_select.call_count == 1
    assert except_sql.call_count == 0
    assert results == ['1','10']
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',side_effect=Exception)
def test_cxusers_get_service_accounts_sql_select_exception(sql_select,except_sql):
    '''Tests get_service_accounts'''
    results = CxUsers.get_service_accounts()
    assert sql_select.call_count == 1
    assert except_sql.call_count == 1
    assert results == None
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',return_value=[])
def test_cxusers_get_service_accounts_no_accounts_returned(sql_select,except_sql):
    '''Tests get_service_accounts'''
    results = CxUsers.get_service_accounts()
    assert sql_select.call_count == 1
    assert except_sql.call_count == 1
    assert results == None
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.delete')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_delete_user_account(connect_api,req,except_func):
    '''Tests delete_user_account'''
    resp_mock = mock.Mock(status_code=204)
    req.return_value = resp_mock
    results = CxUsers.delete_user_account(123456)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert results is True
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.delete',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_delete_user_account_req_exception(connect_api,req,except_func):
    '''Tests delete_user_account'''
    resp_mock = mock.Mock(status_code=204)
    req.return_value = resp_mock
    results = CxUsers.delete_user_account(123456)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is False
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.delete')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_delete_user_account_bad_status_code(connect_api,req,except_func):
    '''Tests delete_user_account'''
    resp_mock = mock.Mock(status_code=400)
    req.return_value = resp_mock
    results = CxUsers.delete_user_account(123456)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is False
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.put')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_user',return_value={'id': 1,'userName':
                                                                'CxAdmin','lastLoginDate':
                                                                '2023-09-27T18:58:51.8831987Z',
                                                                'roleIds':[1,2,6,10,11],'teamIds':
                                                                [1],'authenticationProviderId':1,
                                                                'creationDate':
                                                                '2020-05-06T15:24:49.45Z',
                                                                'twoFAExemption':False,
                                                                'accessToUi':True,'firstName':
                                                                'admin','lastName':'admin','email':
                                                                'admin@cx.com','phoneNumber':'',
                                                                'cellPhoneNumber':'','jobTitle':'',
                                                                'other':'','country':'','active':
                                                                True,'expirationDate':
                                                                '2050-12-31T23:59:59.0598536Z',
                                                                'allowedIpList':[],'localeId':1})
def test_cxusers_remove_expiration_date(get_id,connect_api,req,except_func):
    '''Tests remove_expiration_date'''
    resp_mock = mock.Mock(status_code=204)
    req.return_value = resp_mock
    results = CxUsers.remove_expiration_date(1)
    assert get_id.call_count == 1
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert results is True
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.put',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_user',return_value={'id': 1,'userName':
                                                                'CxAdmin','lastLoginDate':
                                                                '2023-09-27T18:58:51.8831987Z',
                                                                'roleIds':[1,2,6,10,11],'teamIds':
                                                                [1],'authenticationProviderId':1,
                                                                'creationDate':
                                                                '2020-05-06T15:24:49.45Z',
                                                                'twoFAExemption':False,
                                                                'accessToUi':True,'firstName':
                                                                'admin','lastName':'admin','email':
                                                                'admin@cx.com','phoneNumber':'',
                                                                'cellPhoneNumber':'','jobTitle':'',
                                                                'other':'','country':'','active':
                                                                True,'expirationDate':
                                                                '2050-12-31T23:59:59.0598536Z',
                                                                'allowedIpList':[],'localeId':1})
def test_cxusers_remove_expiration_date_req_exception(get_id,connect_api,req,except_func):
    '''Tests remove_expiration_date'''
    resp_mock = mock.Mock(status_code=204)
    req.return_value = resp_mock
    results = CxUsers.remove_expiration_date(1)
    assert get_id.call_count == 1
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is False
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.put')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.get_user',return_value={'id': 1,'userName':
                                                                'CxAdmin','lastLoginDate':
                                                                '2023-09-27T18:58:51.8831987Z',
                                                                'roleIds':[1,2,6,10,11],'teamIds':
                                                                [1],'authenticationProviderId':1,
                                                                'creationDate':
                                                                '2020-05-06T15:24:49.45Z',
                                                                'twoFAExemption':False,
                                                                'accessToUi':True,'firstName':
                                                                'admin','lastName':'admin','email':
                                                                'admin@cx.com','phoneNumber':'',
                                                                'cellPhoneNumber':'','jobTitle':'',
                                                                'other':'','country':'','active':
                                                                True,'expirationDate':
                                                                '2050-12-31T23:59:59.0598536Z',
                                                                'allowedIpList':[],'localeId':1})
def test_cxusers_remove_expiration_date_bad_status_code(get_id,connect_api,req,except_func):
    '''Tests remove_expiration_date'''
    resp_mock = mock.Mock(status_code=400)
    req.return_value = resp_mock
    results = CxUsers.remove_expiration_date(1)
    assert get_id.call_count == 1
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is False
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_get_user(connect_api,req,except_func):
    '''Tests get_user'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'id':1,'userName':'CxAdmin','lastLoginDate':
                                   '2023-09-27T18:58:51.8831987Z','roleIds':[1,2,6,10,11],
                                   'teamIds':[1],'authenticationProviderId':1,'creationDate':
                                   '2020-05-06T15:24:49.45Z','twoFAExemption':False,'accessToUi':
                                   True,'firstName':'admin','lastName':'admin','email':
                                   'admin@cx.com','phoneNumber':'','cellPhoneNumber':'','jobTitle':
                                   '','other':'','country':'','active':True,'expirationDate':
                                   '2050-12-31T23:59:59.0598536Z','allowedIpList':[],'localeId':1}
    req.return_value = resp_mock
    results = CxUsers.get_user(1)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 0
    assert results == {'id':1,'userName':'CxAdmin','lastLoginDate':'2023-09-27T18:58:51.8831987Z',
                       'roleIds':[1,2,6,10,11],'teamIds':[1],'authenticationProviderId':1,
                       'creationDate':'2020-05-06T15:24:49.45Z','twoFAExemption':False,
                       'accessToUi':True,'firstName':'admin','lastName':'admin','email':
                       'admin@cx.com','phoneNumber':'','cellPhoneNumber':'','jobTitle':'','other':
                       '','country':'','active':True,'expirationDate':
                       '2050-12-31T23:59:59.0598536Z','allowedIpList':[],'localeId':1}
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_get_user_req_exception(connect_api,req,except_func):
    '''Tests get_user'''
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'id':1,'userName':'CxAdmin','lastLoginDate':
                                   '2023-09-27T18:58:51.8831987Z','roleIds':[1,2,6,10,11],
                                   'teamIds':[1],'authenticationProviderId':1,'creationDate':
                                   '2020-05-06T15:24:49.45Z','twoFAExemption':False,'accessToUi':
                                   True,'firstName':'admin','lastName':'admin','email':
                                   'admin@cx.com','phoneNumber':'','cellPhoneNumber':'','jobTitle':
                                   '','other':'','country':'','active':True,'expirationDate':
                                   '2050-12-31T23:59:59.0598536Z','allowedIpList':[],'localeId':1}
    req.return_value = resp_mock
    results = CxUsers.get_user(1)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is None
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.requests.get')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.access_control_connection',return_value='token')
def test_cxusers_get_user_bad_status_code(connect_api,req,except_func):
    '''Tests get_user'''
    resp_mock = mock.Mock(status_code=400)
    resp_mock.json.return_value = {}
    req.return_value = resp_mock
    results = CxUsers.get_user(1)
    assert connect_api.call_count == 1
    assert req.call_count == 1
    assert except_func.call_count == 1
    assert results is None
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.insert_multiple_into_table')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.update_multiple_in_table',return_value=1)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.service_account_in_db',return_value=True)
def test_cxusers_process_service_account_update(in_db,sql_update,except_func,log_ln,sql_insert):
    '''Tests process_service_account'''
    CxUsers.process_service_account(1,'CxAdmin','admin@cx.com','2050-12-31T23:59:59.0598536Z')
    assert in_db.call_count == 1
    assert sql_update.call_count == 1
    assert except_func.call_count == 0
    assert log_ln.call_count == 1
    assert sql_insert.call_count == 0
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.insert_multiple_into_table')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.update_multiple_in_table',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.service_account_in_db',return_value=True)
def test_cxusers_process_service_account_update_exception(in_db,sql_update,except_func,log_ln,
                                                          sql_insert):
    '''Tests process_service_account'''
    CxUsers.process_service_account(1,'CxAdmin','admin@cx.com','2050-12-31T23:59:59.0598536Z')
    assert in_db.call_count == 1
    assert sql_update.call_count == 1
    assert except_func.call_count == 1
    assert log_ln.call_count == 0
    assert sql_insert.call_count == 0
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.insert_multiple_into_table',return_value=1)
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.update_multiple_in_table')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.service_account_in_db',return_value=False)
def test_cxusers_process_service_account_insert(in_db,sql_update,except_func,log_ln,sql_insert):
    '''Tests process_service_account'''
    CxUsers.process_service_account(1,'CxAdmin','admin@cx.com','2050-12-31T23:59:59.0598536Z')
    assert in_db.call_count == 1
    assert sql_update.call_count == 0
    assert except_func.call_count == 0
    assert log_ln.call_count == 1
    assert sql_insert.call_count == 1
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.insert_multiple_into_table',side_effect=Exception)
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.log_info')
@mock.patch('maint.checkmarx_user_cleanup.TheLogs.function_exception')
@mock.patch('maint.checkmarx_user_cleanup.update_multiple_in_table')
@mock.patch('maint.checkmarx_user_cleanup.CxUsers.service_account_in_db',return_value=False)
def test_cxusers_process_service_account_insert_exception(in_db,sql_update,except_func,log_ln,
                                                          sql_insert):
    '''Tests process_service_account'''
    CxUsers.process_service_account(1,'CxAdmin','admin@cx.com','2050-12-31T23:59:59.0598536Z')
    assert in_db.call_count == 1
    assert sql_update.call_count == 0
    assert except_func.call_count == 1
    assert log_ln.call_count == 0
    assert sql_insert.call_count == 1
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',return_value=[('1',)])
def test_cxusers_service_account_in_db(sql_select,except_sql):
    '''Tests service_account_in_db'''
    results = CxUsers.service_account_in_db(1)
    assert sql_select.call_count == 1
    assert except_sql.call_count == 0
    assert results is True
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',return_value=[])
def test_cxusers_service_account_in_db_not_found(sql_select,except_sql):
    '''Tests service_account_in_db'''
    results = CxUsers.service_account_in_db(1)
    assert sql_select.call_count == 1
    assert except_sql.call_count == 0
    assert results is False
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.checkmarx_user_cleanup.TheLogs.sql_exception')
@mock.patch('maint.checkmarx_user_cleanup.select',side_effect=Exception)
def test_cxusers_service_account_in_db_sql_exception(sql_select,except_sql):
    '''Tests service_account_in_db'''
    results = CxUsers.service_account_in_db(1)
    assert sql_select.call_count == 1
    assert except_sql.call_count == 1
    assert results is None
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
