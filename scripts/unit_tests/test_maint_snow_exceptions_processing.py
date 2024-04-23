'''Unit tests for maint\snow_exceptions_processing.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from maint.snow_exceptions_processing import *
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
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0
    ScrVar.fe_cnt = 0

@mock.patch('maint.snow_exceptions_processing.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_processing.DBQueries.update_multiple')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.Alerts.manual_alert')
@mock.patch('maint.snow_exceptions_processing.General.do_script_query',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':[('RITM12345','RITSysId',
                                                                        'Normal',
                                                                        str('2021-08-21 16:10:16'),
                                                                        'First Last')]})
@mock.patch('maint.snow_exceptions_processing.ScrVar.reset_exception_counts')
def test_snowproc_alerts_for_pending_approvals(ex_reset,sql_do,alert_man,ex_func,log_ln,mlti_upd,
                                               ex_upd):
    """Tests SNowProc.alerts_for_pending_approvals"""
    SNowProc.alerts_for_pending_approvals()
    assert ex_reset.call_count == 1
    assert sql_do.call_count == 1
    assert alert_man.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 2
    assert mlti_upd.call_count == 1
    assert ex_upd.call_count == 1

@mock.patch('maint.snow_exceptions_processing.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_processing.DBQueries.update_multiple')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.Alerts.manual_alert',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.General.do_script_query',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':[('RITM12345','RITSysId',
                                                                        'Normal',
                                                                        str('2021-08-21 16:10:16'),
                                                                        'First Last')]})
@mock.patch('maint.snow_exceptions_processing.ScrVar.reset_exception_counts')
def test_snowproc_alerts_for_pending_approvals_ex_alert_man(ex_reset,sql_do,alert_man,ex_func,
                                                            log_ln,mlti_upd,ex_upd):
    """Tests SNowProc.alerts_for_pending_approvals"""
    SNowProc.alerts_for_pending_approvals()
    assert ex_reset.call_count == 1
    assert sql_do.call_count == 1
    assert alert_man.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 0
    assert mlti_upd.call_count == 0
    assert ex_upd.call_count == 1

@mock.patch('maint.snow_exceptions_processing.remove_non_appsec_ritms')
@mock.patch('maint.snow_exceptions_processing.sync_ritms_from_jiraissues_to_snowsecurityexceptions')
@mock.patch('maint.snow_exceptions_processing.sync_ritms_from_snowsecurityexceptions_to_jiraissues')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_headline')
@mock.patch('maint.snow_exceptions_processing.ScrVar.reset_exception_counts')
def test_snowproc_sync_with_jiraissues(ex_reset,log_hl,sse_to_ji,ji_to_sse,rem_non_appsec):
    """Tests SNowProc.sync_with_jiraissues"""
    SNowProc.sync_with_jiraissues()
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 3
    assert sse_to_ji.call_count == 1
    assert ji_to_sse.call_count == 1
    assert rem_non_appsec.call_count == 1

@mock.patch('maint.snow_exceptions_processing.update_unprocessed_exceptions')
@mock.patch('maint.snow_exceptions_processing.ScrVar.reset_exception_counts')
def test_snowproc_update_tool_and_jira_exceptions(ex_reset,upd_unproc):
    """Tool SNowProc.update_tool_and_jira_exceptions"""
    SNowProc.update_tool_and_jira_exceptions()
    assert ex_reset.call_count == 1
    assert upd_unproc.call_count == 2

@mock.patch('maint.snow_exceptions_processing.ritm_sse_by_type_sync')
def test_sync_ritms_from_snowsecurityexceptions_to_jiraissues(sse_type_sync):
    """Tests sync_ritms_from_snowsecurityexceptions_to_jiraissues"""
    sync_ritms_from_snowsecurityexceptions_to_jiraissues()
    assert sse_type_sync.call_count == 2

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@pytest.mark.parametrize("type,sel_val,expect_upd",[("ticket",[('RITMTicket','Value,Value2',
                                                                'IS18.01','Approver Name')],2),
                                                    ("repo",[('RITMTicket','Value','IS18.01',
                                                              'Approver Name')],1),
                                                    ("repo",[('RITMTicket','Value,Value2',
                                                                'IS18.01','Approver Name')],2),
                                                    ("ticket",[('RITMTicket','Value','IS18.01',
                                                              'Approver Name')],1)])
def test_ritm_sse_by_type_sync(ex_func,sql_sel,ex_sql,sql_upd,log_ln,type,sel_val,expect_upd):
    """Tests ritm_sse_by_type_sync"""
    sql_sel.return_value = sel_val
    ritm_sse_by_type_sync(type)
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert sql_upd.call_count == expect_upd
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
def test_ritm_sse_by_type_sync_ex_type(ex_func,sql_sel,ex_sql,sql_upd,log_ln):
    """Tests ritm_sse_by_type_sync"""
    ritm_sse_by_type_sync('invalid_type')
    assert ex_func.call_count == 1
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('maint.snow_exceptions_processing.ritm_sse_by_type_sync')
def test_sync_ritms_from_snowsecurityexceptions_to_jiraissues(sse_type_sync):
    """Tests sync_ritms_from_snowsecurityexceptions_to_jiraissues"""
    sync_ritms_from_snowsecurityexceptions_to_jiraissues()
    assert sse_type_sync.call_count == 2

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
def test_ritm_sse_by_type_sync_ex_sql_sel(ex_func,sql_sel,ex_sql,sql_upd,log_ln):
    """Tests ritm_sse_by_type_sync"""
    ritm_sse_by_type_sync('repo')
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('maint.snow_exceptions_processing.ritm_sse_by_type_sync')
def test_sync_ritms_from_snowsecurityexceptions_to_jiraissues(sse_type_sync):
    """Tests sync_ritms_from_snowsecurityexceptions_to_jiraissues"""
    sync_ritms_from_snowsecurityexceptions_to_jiraissues()
    assert sse_type_sync.call_count == 2

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@pytest.mark.parametrize("type,sel_val,expect_upd",[("repo",[('RITMTicket','Value','IS18.01',
                                                              'Approver Name')],1),
                                                    ("ticket",[('RITMTicket','Value','IS18.01',
                                                              'Approver Name')],1)])
def test_ritm_sse_by_type_sync_ex_sql_upd(ex_func,sql_sel,ex_sql,sql_upd,log_ln,type,sel_val,
                                          expect_upd):
    """Tests ritm_sse_by_type_sync"""
    sql_sel.return_value = sel_val
    ritm_sse_by_type_sync(type)
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == expect_upd
    assert sql_upd.call_count == expect_upd
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update')
@mock.patch('maint.snow_exceptions_processing.ritm_jira_tickets',
            return_value = 'ABC-123')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            return_value=[('RITM12345')])
def test_sync_ritms_from_jiraissues_to_snowsecurityexceptions(sql_sel,ex_sql,rjt,sql_upd,log_ln):
    """Tests sync_ritms_from_jiraissues_to_snowsecurityexceptions"""
    sync_ritms_from_jiraissues_to_snowsecurityexceptions()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert rjt.call_count == 1
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update')
@mock.patch('maint.snow_exceptions_processing.ritm_jira_tickets')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            side_effect=Exception)
def test_sync_ritms_from_jiraissues_to_snowsecurityexceptions_ex_sql_sel(sql_sel,ex_sql,rjt,
                                                                         sql_upd,log_ln):
    """Tests sync_ritms_from_jiraissues_to_snowsecurityexceptions"""
    sync_ritms_from_jiraissues_to_snowsecurityexceptions()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert rjt.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.ritm_jira_tickets',
            return_value = 'ABC-123')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            return_value=[('RITM12345')])
def test_sync_ritms_from_jiraissues_to_snowsecurityexceptions_ex_sql_upd(sql_sel,ex_sql,rjt,
                                                                         sql_upd,log_ln):
    """Tests sync_ritms_from_jiraissues_to_snowsecurityexceptions"""
    sync_ritms_from_jiraissues_to_snowsecurityexceptions()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert rjt.call_count == 1
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.delete_row')
def test_remove_non_appsec_ritms(sql_del,ex_sql,log_ln):
    """Test remove_non_appsec_ritms"""
    remove_non_appsec_ritms()
    assert sql_del.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.delete_row',
            side_effect=Exception)
def test_remove_non_appsec_ritms_ex_sql_del(sql_del,ex_sql,log_ln):
    """Test remove_non_appsec_ritms"""
    remove_non_appsec_ritms()
    assert sql_del.call_count == 1
    assert ex_sql.call_count == 1
    assert log_ln.call_count == 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            return_value=[('ABC-123','CBA-321',),])
def test_get_all_jiraissues(sql_sel,ex_sql):
    """Tests get_all_jiraissues"""
    get_all_jiraissues()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            side_effect=Exception)
def test_get_all_jiraissues_ex_sql_sel(sql_sel,ex_sql):
    """Tests get_all_jiraissues"""
    get_all_jiraissues()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            return_value=[('ABC-123',),])
def test_ritm_jira_tickets(sql_sel,ex_sql):
    """Tests ritm_jira_tickets"""
    ritm_jira_tickets('RITM12345')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            side_effect=Exception)
def test_ritm_jira_tickets_ex_sql_sel(sql_sel,ex_sql):
    """Tests ritm_jira_tickets"""
    ritm_jira_tickets('RITM12345')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('maint.snow_exceptions_processing.process_mend_exceptions')
@mock.patch('maint.snow_exceptions_processing.process_checkmarx_exceptions')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_headline')
@pytest.mark.parametrize("tool,ret_sel,pce_cnt,pme_cnt",
                         [('checkmarx',[('repo','2023-10-12','RITM1234','2024-01-01','IS.1803','3',
                                         '2023-12-01','ABC-123',
                                         '1','status','cxState','cxProjId','12345-67')],1,0),
                          ('mend os',[('repo','2023-10-12','RITM1234','2024-01-01',
                                                'IS.1803','3','2023-12-01','ABC-123',
                                                'Vulnerability','mStatus','mAlert','Status',
                                                'JiraStatus','ProjToken')],0,1)])
def test_update_unprocessed_exceptions(log_hl,ex_func,sql_sel,ex_sql,pce,pme,
                                       tool,ret_sel,pce_cnt,pme_cnt):
    """Tests update_unprocessed_exceptions"""
    sql_sel.return_value = ret_sel
    update_unprocessed_exceptions(tool)
    assert log_hl.call_count == 1
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert pce.call_count == pce_cnt
    assert pme.call_count == pme_cnt

@mock.patch('maint.snow_exceptions_processing.process_mend_exceptions')
@mock.patch('maint.snow_exceptions_processing.process_checkmarx_exceptions')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_headline')
def test_update_unprocessed_exceptions_ex_tool(log_hl,ex_func,sql_sel,ex_sql,pce,pme):
    """Tests update_unprocessed_exceptions"""
    update_unprocessed_exceptions('invalid tool')
    assert log_hl.call_count == 1
    assert ex_func.call_count == 1
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert pce.call_count == 0
    assert pme.call_count == 0

@mock.patch('maint.snow_exceptions_processing.process_mend_exceptions')
@mock.patch('maint.snow_exceptions_processing.process_checkmarx_exceptions')
@mock.patch('maint.snow_exceptions_processing.TheLogs.sql_exception')
@mock.patch('maint.snow_exceptions_processing.select',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_headline')
def test_update_unprocessed_exceptions_ex_sql_sel(log_hl,ex_func,sql_sel,ex_sql,pce,pme):
    """Tests update_unprocessed_exceptions"""
    update_unprocessed_exceptions('checkmarx')
    assert log_hl.call_count == 1
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert pce.call_count == 0
    assert pme.call_count == 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_processing.CxPipelines.sync_state_to_pipeline')
@mock.patch('maint.snow_exceptions_processing.CxAPI.update_res_state')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due')
def test_process_checkmarx_exceptions(u_td,ex_func,u_rs,sstp,mlti_upd,log_ln):
    """Tests process_checkmarx_exceptions"""
    process_checkmarx_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                                   'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                                   'ExDuration':'12','ApprovedDate':'2023-12-20',
                                   'JiraTicket':'ABC-123','PipelineSync':1,'Status':'Status',
                                   'cxState':'cxstate','cxProjectID':'12345',
                                   'cxScanId':'987654321','cxPathId':'367'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 0
    assert u_rs.call_count == 1
    assert sstp.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 4

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_processing.CxPipelines.sync_state_to_pipeline')
@mock.patch('maint.snow_exceptions_processing.CxAPI.update_res_state')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due',
            side_effect=Exception)
def test_process_checkmarx_exceptions_ex_u_td(u_td,ex_func,u_rs,sstp,mlti_upd,log_ln):
    """Tests process_checkmarx_exceptions"""
    process_checkmarx_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                                   'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                                   'ExDuration':'12','ApprovedDate':'2023-12-20',
                                   'JiraTicket':'ABC-123','PipelineSync':1,'Status':'Status',
                                   'cxState':'cxstate','cxProjectID':'12345',
                                   'cxScanId':'987654321','cxPathId':'367'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 1
    assert u_rs.call_count == 1
    assert sstp.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 4

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_processing.CxPipelines.sync_state_to_pipeline')
@mock.patch('maint.snow_exceptions_processing.CxAPI.update_res_state',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due')
def test_process_checkmarx_exceptions_ex_u_rs(u_td,ex_func,u_rs,sstp,mlti_upd,log_ln):
    """Tests process_checkmarx_exceptions"""
    process_checkmarx_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                                   'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                                   'ExDuration':'12','ApprovedDate':'2023-12-20',
                                   'JiraTicket':'ABC-123','PipelineSync':1,'Status':'Status',
                                   'cxState':'cxstate','cxProjectID':'12345',
                                   'cxScanId':'987654321','cxPathId':'367'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 1
    assert u_rs.call_count == 1
    assert sstp.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 4

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_processing.CxPipelines.sync_state_to_pipeline',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.CxAPI.update_res_state')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due')
def test_process_checkmarx_exceptions_ex_sstp(u_td,ex_func,u_rs,sstp,mlti_upd,log_ln):
    """Tests process_checkmarx_exceptions"""
    process_checkmarx_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                                   'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                                   'ExDuration':'12','ApprovedDate':'2023-12-20',
                                   'JiraTicket':'ABC-123','PipelineSync':1,'Status':'Status',
                                   'cxState':'cxstate','cxProjectID':'12345',
                                   'cxScanId':'987654321','cxPathId':'367'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 1
    assert u_rs.call_count == 1
    assert sstp.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 4

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.CxPipelines.sync_state_to_pipeline')
@mock.patch('maint.snow_exceptions_processing.CxAPI.update_res_state')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due')
def test_process_checkmarx_exceptions_ex_mlti_upd(u_td,ex_func,u_rs,sstp,mlti_upd,log_ln):
    """Tests process_checkmarx_exceptions"""
    process_checkmarx_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                                   'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                                   'ExDuration':'12','ApprovedDate':'2023-12-20',
                                   'JiraTicket':'ABC-123','PipelineSync':1,'Status':'Status',
                                   'cxState':'cxstate','cxProjectID':'12345',
                                   'cxScanId':'987654321','cxPathId':'367'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 2
    assert u_rs.call_count == 1
    assert sstp.call_count == 1
    assert mlti_upd.call_count == 2
    assert log_ln.call_count == 4

@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.close_jira_ticket',
            return_value=True)
@mock.patch('maint.snow_exceptions_processing.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_processing.update_jira_project_tickets',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table')
@mock.patch('maint.snow_exceptions_processing.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due')
def test_process_mend_exceptions(u_td,ex_func,u_uas,mlti_upd,log_ln,ujpt,ex_upd,c_tkt):
    """Tests process_mend_exceptions"""
    process_mend_exceptions([{'RITMTicket':'RITM12354','Repo':'repo','JiraDue':'2023-10-22',
                              'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                              'ExDuration':'12','ApprovedDate':'2023-12-20','JiraTicket':'ABC-123',
                              'Type':'License Violation','mStatus':'Status','mAlert':'alert',
                              'Status':'Status','JiraStatus':'jirastatus','ProjectToken':'token'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 0
    assert u_uas.call_count == 1
    assert mlti_upd.call_count == 3
    assert log_ln.call_count == 5
    assert ujpt.call_count == 1
    assert ex_upd.call_count == 1
    assert c_tkt.call_count == 1

@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.close_jira_ticket',
            return_value=True)
@mock.patch('maint.snow_exceptions_processing.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_processing.update_jira_project_tickets',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.GeneralTicketing.update_ticket_due',
            side_effect=Exception)
def test_process_mend_exceptions_ex_all(u_td,ex_func,u_uas,mlti_upd,log_ln,ujpt,ex_upd,c_tkt):
    """Tests process_mend_exceptions"""
    process_mend_exceptions([{'Repo':'repo','JiraDue':'2023-10-22','RITMTicket':'RITM1234',
                              'ExceptionDue':'2024-12-20','ExStandard':'IS18.05',
                              'ExDuration':'12','ApprovedDate':'2023-12-20','JiraTicket':'ABC-123',
                              'Type':'License Violation','mStatus':'Status','mAlert':'alert',
                              'Status':'Status','JiraStatus':'jirastatus','ProjectToken':'token'}])
    assert u_td.call_count == 1
    assert ex_func.call_count == 5
    assert u_uas.call_count == 1
    assert mlti_upd.call_count == 3
    assert log_ln.call_count == 5
    assert ujpt.call_count == 0
    assert ex_upd.call_count == 0
    assert c_tkt.call_count == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maint.snow_exceptions_processing.TheLogs.log_info')
@mock.patch('maint.snow_exceptions_processing.DBQueries.update_multiple')
@mock.patch('maint.snow_exceptions_processing.TheLogs.function_exception')
@mock.patch('maint.snow_exceptions_processing.Alerts.manual_alert')
@mock.patch('maint.snow_exceptions_processing.ScrVar.update_exception_info')
@mock.patch('maint.snow_exceptions_processing.General.do_script_query')
@pytest.mark.parametrize("description,dsq_rv,ma_se,ma_rv,ma_cnt,ex_func_cnt,um_se,um_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('dsq_rv = []',{'FatalCount':0,'ExceptionCount':0,'Results':[]},None,None,0,0,None,0,1,0,0),
                          ('All expected values',{'FatalCount':0,'ExceptionCount':0,'Results':[('RITMTicket','SysId','Awaiting Approval','Name','Name',),]},None,1,1,0,None,1,2,0,0),
                          ('Exception: ma',{'FatalCount':0,'ExceptionCount':0,'Results':[('RITMTicket','SysId','Awaiting Approval','Name','Name',),]},Exception,None,1,1,None,0,0,0,1),
                          ('Exception: um',{'FatalCount':0,'ExceptionCount':0,'Results':[('RITMTicket','SysId','Awaiting Approval','Name','Name',),]},None,1,1,1,Exception,1,2,0,1)])
def test_snowproc_alerts_for_missing_jira_tickets(dsq,uei,ma,ex_func,um,log_ln,
                                                  description,dsq_rv,ma_se,ma_rv,ma_cnt,
                                                  ex_func_cnt,um_se,um_cnt,log_ln_cnt,fe_cnt,ex_cnt):
    """Tests SNowProc.alerts_for_missing_jira_tickets"""
    dsq.return_value = dsq_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    um.side_effect = um_se
    response = SNowProc.alerts_for_missing_jira_tickets()
    assert dsq.call_count == 1
    assert uei.call_count == 1
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == log_ln_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
