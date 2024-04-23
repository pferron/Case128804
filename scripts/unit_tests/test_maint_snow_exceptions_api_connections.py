'''Unit tests for maint\snow_exceptions_api_connections.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from maint.snow_exceptions_api_connections import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    """Tests ScrVar.reset_exception_counts"""
    ScrVar.ex_cnt = 1
    ScrVar.fe_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.ex_cnt == 0
    assert ScrVar.fe_cnt == 0

def test_scrvar_update_exception_info():
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':2,'ExceptionCount':2})
    assert ScrVar.ex_cnt == 2
    assert ScrVar.fe_cnt == 2
    ScrVar.ex_cnt = 0
    ScrVar.fe_cnt = 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.mark_approvers_inactive')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_update_snow_approvers(ex_reset,req_get,ex_func,u_approvers,ex_upd,
                                       mlti_upd,mlti_ins,g_approvers,log_ln):
    """Tests SNowAPI.update_snow_approvers"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result':[{'user':{'display_value':'Test User'}}]}
    req_get.return_value = resp_mock
    SNowAPI.update_snow_approvers()
    assert ex_reset.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 0
    assert u_approvers.call_count == 1
    assert ex_upd.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert g_approvers.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.mark_approvers_inactive')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_update_snow_approvers_400_status_code(ex_reset,req_get,ex_func,u_approvers,ex_upd,
                                                       mlti_upd,mlti_ins,g_approvers,log_ln):
    """Tests SNowAPI.update_snow_approvers"""
    resp_mock = mock.Mock(status_code=400)
    req_get.return_value = resp_mock
    SNowAPI.update_snow_approvers()
    assert ex_reset.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 0
    assert u_approvers.call_count == 0
    assert ex_upd.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0
    assert g_approvers.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.mark_approvers_inactive')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_update_snow_approvers_ex_req_get(ex_reset,req_get,ex_func,u_approvers,ex_upd,
                                                  mlti_upd,mlti_ins,g_approvers,log_ln):
    """Tests SNowAPI.update_snow_approvers"""
    SNowAPI.update_snow_approvers()
    assert ex_reset.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 1
    assert u_approvers.call_count == 0
    assert ex_upd.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0
    assert g_approvers.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.mark_approvers_inactive')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_update_snow_approvers_ex_mlti_upd_and_mlti_ins(ex_reset,req_get,ex_func,
                                                                u_approvers,ex_upd,mlti_upd,
                                                                mlti_ins,g_approvers,log_ln):
    """Tests SNowAPI.update_snow_approvers"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result':[{'user':{'display_value':'Test User'}}]}
    req_get.return_value = resp_mock
    SNowAPI.update_snow_approvers()
    assert ex_reset.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 2
    assert u_approvers.call_count == 1
    assert ex_upd.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert g_approvers.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.get_exception_approval_records',
            return_value={'ApprovedByName':'Approver Name','ApprovedDate':'2023-11-27 10:14:59'})
@mock.patch('maint.snow_exceptions_api_connections.get_fields_for_exception_ticket',
            return_value={'Length of time for which exception is required':5,
'Standard or procedure document number & version for which the exception is requested':'IS18.01 Txt',
                          'Date exception expires':'2024-02-03','JiraTickets':'ABC-4321'})
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_ritms',
            return_value={'Results':{'JiraSet':['RITM1234567890'],
                                     'JiraNotSet':['RITM0987654321']}})
@mock.patch('maint.snow_exceptions_api_connections.security_approvers',
            return_value=['Approver Name'])
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
@pytest.mark.parametrize("period,ritmticket",[(None,'RITM123456'),('all',None),('hourly',None),
                                              ('past_24_hours',None),('past_week',None),
                                              ('past_month',None),('past_quarter',None),
                                              ('past_6_months',None),('past_12_months',None),
                                              ('past_15_minutes',None)])
def test_snowapi_process_exception_requests(ex_reset,sec_app,g_ritms,req_get,ex_func,
                                            g_fields,g_app_rec,mlti_ins,mlti_upd,period,ritmticket):
    """Tests SNowAPI.process_exception_requests"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result': [{'sys_id':'sys_id1','task_effective_number':
                                               'RITM0987654321','assignment_group':
                                               'group1','opened_at':'2023-11-24 00:00:05',
                                               'sys_updated_on':'2023-11-24 09:15:23','due_date':
                                               '2023-11-30 00:00:00','closed_at':
                                               '2023-11-27 10:27:14','active':'true','opened_by':
                                               'Some Person','u_requested_for':'Another Person',
                                               'state':'state','stage':'stage','escalation':
                                               'escalated','configuration_item':'item','approval':
                                               'approval_status'},
                                               {'sys_id':'sys_id1','task_effective_number':
                                               'RITM1234567890','assignment_group':
                                               'group1','opened_at':'2023-11-24 00:00:05',
                                               'sys_updated_on':'2023-11-24 09:15:23','due_date':
                                               '2023-11-30 00:00:00','closed_at':
                                               '2023-11-27 10:27:14','active':'true','opened_by':
                                               'Some Person','u_requested_for':'Another Person',
                                               'state':'state','stage':'stage','escalation':
                                               'escalated','configuration_item':'item','approval':
                                               'approval_status'},
                                               {'sys_id':'sys_id1','task_effective_number':
                                               'RITM1234567891','assignment_group':
                                               'group1','opened_at':'2023-11-24 00:00:05',
                                               'sys_updated_on':'2023-11-24 09:15:23','due_date':
                                               '2023-11-30 00:00:00','closed_at':
                                               '2023-11-27 10:27:14','active':'true','opened_by':
                                               'Some Person','u_requested_for':'Another Person',
                                               'state':'state','stage':'stage','escalation':
                                               'escalated','configuration_item':'item','approval':
                                               'approval_status'}]}
    req_get.return_value = resp_mock
    ScrVar.get_approvers = []
    SNowAPI.process_exception_requests(period,ritm_ticket=ritmticket)
    assert ex_reset.call_count == 1
    assert sec_app.call_count == 1
    assert g_ritms.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 0
    assert g_fields.call_count == 3
    assert g_app_rec.call_count == 3
    assert mlti_ins.call_count == 1
    assert mlti_upd.call_count == 2

@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.get_exception_approval_records',
            return_value={'ApprovedByName':'Approver Name','ApprovedDate':'2023-11-27 10:14:59'})
@mock.patch('maint.snow_exceptions_api_connections.get_fields_for_exception_ticket',
            return_value={'Length of time for which exception is required':5,
'Standard or procedure document number & version for which the exception is requested':'IS18.01 Txt',
                          'Date exception expires':'2024-02-03','JiraTickets':'ABC-4321'})
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_ritms',
            return_value={'Results':{'JiraSet':['RITM1234567890'],
                                     'JiraNotSet':['RITM0987654321']}})
@mock.patch('maint.snow_exceptions_api_connections.security_approvers',
            return_value=['Approver Name'])
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_process_exception_requests_ex_mlti_upd_and_mlti_ins(ex_reset,sec_app,g_ritms,
                                                                     req_get,ex_func,g_fields,
                                                                     g_app_rec,mlti_ins,mlti_upd):
    """Tests SNowAPI.process_exception_requests"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'result': [{'sys_id':'sys_id1','task_effective_number':
                                               'RITM1234567890','assignment_group':
                                               'group1','opened_at':'2023-11-24 00:00:05',
                                               'sys_updated_on':'2023-11-24 09:15:23','due_date':
                                               '2023-11-30 00:00:00','closed_at':
                                               '2023-11-27 10:27:14','active':'true','opened_by':
                                               'Some Person','u_requested_for':'Another Person',
                                               'state':'state','stage':'stage','escalation':
                                               'escalated','configuration_item':'item','approval':
                                               'approval_status'},
                                               {'sys_id':'sys_id1','task_effective_number':
                                               'RITM1234567891','assignment_group':
                                               'group1','opened_at':'2023-11-24 00:00:05',
                                               'sys_updated_on':'2023-11-24 09:15:23','due_date':
                                               '2023-11-30 00:00:00','closed_at':
                                               '2023-11-27 10:27:14','active':'true','opened_by':
                                               'Some Person','u_requested_for':'Another Person',
                                               'state':'state','stage':'stage','escalation':
                                               'escalated','configuration_item':'item','approval':
                                               'approval_status'}]}
    req_get.return_value = resp_mock
    ScrVar.get_approvers = []
    SNowAPI.process_exception_requests(None)
    assert ex_reset.call_count == 1
    assert sec_app.call_count == 1
    assert g_ritms.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 2
    assert g_fields.call_count == 2
    assert g_app_rec.call_count == 2
    assert mlti_ins.call_count == 1
    assert mlti_upd.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.get_exception_approval_records')
@mock.patch('maint.snow_exceptions_api_connections.get_fields_for_exception_ticket')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_ritms',
            return_value={'Results':{'JiraSet':['RITM1234567890'],
                                     'JiraNotSet':['RITM0987654321']}})
@mock.patch('maint.snow_exceptions_api_connections.security_approvers',
            return_value=['Approver Name'])
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_process_exception_requests_ex_400_response_req_get(ex_reset,sec_app,g_ritms,req_get,ex_func,
                                            g_fields,g_app_rec,mlti_ins,mlti_upd):
    """Tests SNowAPI.process_exception_requests"""
    resp_mock = mock.Mock(status_code=400)
    req_get.return_value = resp_mock
    ScrVar.get_approvers = []
    SNowAPI.process_exception_requests('hourly')
    assert ex_reset.call_count == 1
    assert sec_app.call_count == 1
    assert g_ritms.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 1
    assert g_fields.call_count == 0
    assert g_app_rec.call_count == 0
    assert mlti_ins.call_count == 0
    assert mlti_upd.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_api_connections.insert_multiple_into_table')
@mock.patch('maint.snow_exceptions_api_connections.get_exception_approval_records')
@mock.patch('maint.snow_exceptions_api_connections.get_fields_for_exception_ticket')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_ritms',
            return_value={'Results':{'JiraSet':['RITM1234567890'],
                                     'JiraNotSet':['RITM0987654321']}})
@mock.patch('maint.snow_exceptions_api_connections.security_approvers',
            return_value=['Approver Name'])
@mock.patch('maint.snow_exceptions_api_connections.ScrVar.reset_exception_counts')
def test_snowapi_process_exception_requests_ex_req_get(ex_reset,sec_app,g_ritms,req_get,ex_func,
                                            g_fields,g_app_rec,mlti_ins,mlti_upd):
    """Tests SNowAPI.process_exception_requests"""
    ScrVar.get_approvers = []
    SNowAPI.process_exception_requests('hourly')
    assert ex_reset.call_count == 1
    assert sec_app.call_count == 1
    assert g_ritms.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 1
    assert g_fields.call_count == 0
    assert g_app_rec.call_count == 0
    assert mlti_ins.call_count == 0
    assert mlti_upd.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.get_exception_field_value',autospec=True)
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_jiraissues',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':['ABC-123','FOUR-321']})
@mock.patch('maint.snow_exceptions_api_connections.GeneralTicketing.get_all_project_keys',
            return_value=['ABC','FOUR'])
@pytest.mark.parametrize('values',[{'sys_id':'a1a3d8061b83b5508049bbbc0a4bcbc6','sys_updated_by':
                                    'system','sys_created_on':'12/12/2023 10:58:35','item_option_new':
                                    'Date exception expires','sys_mod_count':'1','sys_updated_on':
                                    '12/15/2023 08:15:41','sys_tags':'','value':'2024-03-15',
                                    'sys_created_by':'kevin.pl.fry','cart_item':'','order':'16'},
                                    {'sys_id':'25a3d8061b83b5508049bbbc0a4bcbc7','sys_updated_by':
                                     'kevin.pl.fry','sys_created_on':'12/12/2023 10:58:35',
                                     'item_option_new':'Detailed description of the requested exception',
                                     'sys_mod_count':'0','sys_updated_on':'12/12/2023 10:58:35',
                                     'sys_tags':'','value':'ABC-123 something else','sys_created_by':
                                     'kevin.pl.fry','cart_item':'','order':'10'}])
def test_get_fields_for_exception_ticket(g_pks,g_ji,req_get,ex_func,g_fv,values):
    """Tests get_fields_for_exception_ticket"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {"result":[{"sc_item_option":{"link":"a_link"}},
                                             {"sc_item_option":{"link":"b_link"}},
                                             {"sc_item_option":{"link":"c_link"}},
                                             {"sc_item_option":{"link":"d_link"}}]}
    req_get.return_value = resp_mock
    g_fv.return_value = values
    get_fields_for_exception_ticket('a_sys_id')
    assert g_pks.call_count == 1
    assert g_ji.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 0
    assert g_fv.call_count == 4

@mock.patch('maint.snow_exceptions_api_connections.get_exception_field_value')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_jiraissues')
@mock.patch('maint.snow_exceptions_api_connections.GeneralTicketing.get_all_project_keys',
            return_value=['ABC','FOUR'])
def test_get_fields_for_exception_ticket_ex_req_get(g_pks,g_ji,req_get,ex_func,g_fv):
    """Tests get_fields_for_exception_ticket"""
    get_fields_for_exception_ticket('a_sys_id')
    assert g_pks.call_count == 1
    assert g_ji.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 1
    assert g_fv.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.get_exception_field_value')
@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.SNowQueries.get_all_jiraissues')
@mock.patch('maint.snow_exceptions_api_connections.GeneralTicketing.get_all_project_keys',
            return_value=['ABC','FOUR'])
def test_get_fields_for_exception_ticket_ex_400_status_req_get(g_pks,g_ji,req_get,ex_func,g_fv):
    """Tests get_fields_for_exception_ticket"""
    resp_mock = mock.Mock(status_code=400)
    req_get.return_value = resp_mock
    get_fields_for_exception_ticket('a_sys_id')
    assert g_pks.call_count == 1
    assert g_ji.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == 1
    assert g_fv.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
def test_get_exception_field_value(req_get,ex_func):
    """Tests get_exception_field_value"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {"result":[{"sc_item_option":{"link":"a_link"}},
                                             {"sc_item_option":{"link":"b_link"}},
                                             {"sc_item_option":{"link":"c_link"}},
                                             {"sc_item_option":{"link":"d_link"}}]}
    req_get.return_value = resp_mock
    get_exception_field_value('a_url')
    assert req_get.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get',
            side_effect=Exception)
def test_get_exception_field_value_ex_req_get(req_get,ex_func):
    """Tests get_exception_field_value"""
    get_exception_field_value('a_url')
    assert req_get.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
def test_get_exception_field_value_ex_400_status_req_get(req_get,ex_func):
    """Tests get_exception_field_value"""
    resp_mock = mock.Mock(status_code=400)
    req_get.return_value = resp_mock
    get_exception_field_value('a_url')
    assert req_get.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
@pytest.mark.parametrize("response,app_list",[({"result":[{"approver":"The Approver","state":
                                                           "Approved","sys_updated_on":
                                                           "2023-12-19 14:57:43"}]},
                                                           ['The Approver']),([],[])])
def test_get_exception_approval_records(g_approvers,req_get,ex_func,response,app_list):
    """Tests get_exception_approval_records"""
    ScrVar.get_approvers = app_list
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = response
    req_get.return_value = resp_mock
    get_exception_approval_records('a_url')
    if response == []:
        assert g_approvers.call_count == 1
    else:
        assert g_approvers.call_count == 0
    assert req_get.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
def test_get_exception_approval_records_ex_req_get(g_approvers,req_get,ex_func,):
    """Tests get_exception_approval_records"""
    get_exception_approval_records('a_url')
    assert g_approvers.call_count == 0
    assert req_get.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_api_connections.requests.get')
@mock.patch('maint.snow_exceptions_api_connections.security_approvers')
def test_get_exception_approval_records_ex_400_response_req_get(g_approvers,req_get,ex_func,):
    """Tests get_exception_approval_records"""
    resp_mock = mock.Mock(status_code=400)
    req_get.return_value = resp_mock
    get_exception_approval_records('a_url')
    assert g_approvers.call_count == 0
    assert req_get.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_api_connections.select',
            return_value=[('Approver1',),('Approver2',),])
def test_security_approvers(sql_sel,ex_sql):
    """Tests security_approvers"""
    security_approvers()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_api_connections.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_api_connections.select',
            side_effect=Exception)
def test_security_approvers_ex_sql_sel(sql_sel,ex_sql):
    """Tests security_approvers"""
    security_approvers()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

if __name__ == '__main__':
    unittest.main()
