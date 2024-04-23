'''Unit tests for mend.ticket_creation_and_closure '''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from mend.ticket_creation_and_closure import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.fe_cnt = 1
    ScrVar.ex_cnt = 1
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

@mock.patch('mend.ticket_creation_and_closure.create_and_update_tickets')
@mock.patch('mend.ticket_creation_and_closure.close_jira_tickets')
@mock.patch('mend.ticket_creation_and_closure.process_closed_tickets')
@mock.patch('mend.ticket_creation_and_closure.project_on_hold',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.do_not_ticket',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.ScrVar.reset_exception_counts')
def test_mendtickets_single_repo_ticketing(ex_reset,log_hl,u_ji,ct,dnt,poh,proc_closed,
                                           close_tkts,create_tkts):
    '''Tests MendTickets.single_repo_ticketing'''
    MendTickets.single_repo_ticketing('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert u_ji.call_count == 1
    assert ct.call_count == 1
    assert dnt.call_count == 1
    assert poh.call_count == 1
    assert proc_closed.call_count == 1
    assert close_tkts.call_count == 1
    assert create_tkts.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.create_and_update_tickets')
@mock.patch('mend.ticket_creation_and_closure.close_jira_tickets')
@mock.patch('mend.ticket_creation_and_closure.process_closed_tickets')
@mock.patch('mend.ticket_creation_and_closure.project_on_hold',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.do_not_ticket',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.ScrVar.reset_exception_counts')
def test_mendtickets_single_repo_ticketing_do_not_process(ex_reset,log_hl,u_ji,ct,dnt,poh,
                                                          proc_closed,close_tkts,create_tkts):
    '''Tests MendTickets.single_repo_ticketing'''
    MendTickets.single_repo_ticketing('appsec-ops')
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert u_ji.call_count == 1
    assert ct.call_count == 1
    assert dnt.call_count == 1
    assert poh.call_count == 1
    assert proc_closed.call_count == 0
    assert close_tkts.call_count == 0
    assert create_tkts.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS',),])
def test_update_jiraissues(sql_sel,ex_sql,log_hl,u_ji,log_ln):
    '''Tests update_jiraissues'''
    update_jiraissues('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert log_hl.call_count == 1
    assert u_ji.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_update_jiraissues_ex_uji_001(sql_sel,ex_sql,log_hl,u_ji,log_ln):
    '''Tests update_jiraissues'''
    update_jiraissues('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert log_hl.call_count == 0
    assert u_ji.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_cannot_osfindings',
            return_value=1)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value='appsec-ops')
def test_cannot_ticket(sql_sel,ex_sql,uco,log_hl,log_ln):
    '''Tests cannot_ticket'''
    cannot_ticket('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert uco.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_cannot_osfindings')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_cannot_ticket_ex_ct_001(sql_sel,ex_sql,uco,log_hl,log_ln):
    '''Tests cannot_ticket'''
    cannot_ticket('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert uco.call_count == 0
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            return_value=1)
def test_update_cannot_osfindings(sql_upd,ex_sql):
    '''Tests update_cannot_osfindings'''
    update_cannot_osfindings('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
def test_update_cannot_osfindings_ex_uco_001(sql_upd,ex_sql):
    '''Tests update_cannot_osfindings'''
    update_cannot_osfindings('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_dont_ticket',
            return_value=1)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value='appsec-ops')
def test_do_not_ticket(sql_sel,ex_sql,uco,log_hl,log_ln):
    '''Tests do_not_ticket'''
    do_not_ticket('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert uco.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_dont_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_do_not_ticket_ex_dnt_001(sql_sel,ex_sql,uco,log_hl,log_ln):
    '''Tests do_not_ticket'''
    do_not_ticket('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert uco.call_count == 0
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            return_value=1)
def test_update_osfindings_dont_ticket(sql_upd,ex_sql):
    '''Tests update_osfindings_dont_ticket'''
    update_osfindings_dont_ticket('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
def test_update_osfindings_dont_ticket_ex_uodt_001(sql_upd,ex_sql):
    '''Tests update_osfindings_dont_ticket'''
    update_osfindings_dont_ticket('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_poh',
            return_value = 1)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value='appsec-ops')
def test_project_on_hold(sql_sel,ex_sql,u_poh,log_hl,log_ln):
    '''Tests project_on_hold'''
    project_on_hold('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert u_poh.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_poh')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_project_on_hold_ex_poh_001(sql_sel,ex_sql,u_poh,log_hl,log_ln):
    '''Tests project_on_hold'''
    project_on_hold('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert u_poh.call_count == 0
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            return_value=1)
def test_update_osfindings_poh(sql_upd,ex_sql):
    '''Tests update_osfindings_poh'''
    update_osfindings_poh('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
def test_update_osfindings_poh_ex_uopoh_001(sql_upd,ex_sql):
    '''Tests update_osfindings_poh'''
    update_osfindings_poh('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.get_project_key',
            return_value='AS')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','Not Exploitable',),('AS-1235','No Fix Available',),])
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
def test_close_jira_tickets(log_hl,sql_sel,ex_sql,close_tkt,ex_func,sql_upd,g_pk,u_ji,log_ln):
    '''Tests close_jira_tickets'''
    close_jira_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert close_tkt.call_count == 2
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 2
    assert g_pk.call_count == 1
    assert u_ji.call_count == 1
    assert log_ln.call_count == 3

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.get_project_key')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.close_or_cancel_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
def test_close_jira_tickets_ex_cjt_001(log_hl,sql_sel,ex_sql,close_tkt,ex_func,sql_upd,g_pk,u_ji,log_ln):
    '''Tests close_jira_tickets'''
    close_jira_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert close_tkt.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert g_pk.call_count == 0
    assert u_ji.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.get_project_key',
            return_value='AS')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.close_or_cancel_jira_ticket',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','To Close',),])
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
def test_close_jira_tickets_ex_cjt_002(log_hl,sql_sel,ex_sql,close_tkt,ex_func,sql_upd,g_pk,u_ji,log_ln):
    '''Tests close_jira_tickets'''
    close_jira_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert close_tkt.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert g_pk.call_count == 1
    assert u_ji.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.get_project_key',
            return_value='AS')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','To Close',),])
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
def test_close_jira_tickets_ex_cjt_003(log_hl,sql_sel,ex_sql,close_tkt,ex_func,sql_upd,g_pk,u_ji,log_ln):
    '''Tests close_jira_tickets'''
    close_jira_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert close_tkt.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert g_pk.call_count == 1
    assert u_ji.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS',),])
def test_get_project_key(sql_sel,ex_sql):
    '''Tests get_project_key'''
    get_project_key('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_get_project_key_ex_gpk_001(sql_sel,ex_sql):
    '''Tests get_project_key'''
    get_project_key('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.reopen_mend_license_violation_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_status')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.MendAPI.update_alert_status',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.get_jiraissue_data')
@mock.patch('mend.ticket_creation_and_closure.get_project_details')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','RITM1234','1',),])
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@pytest.mark.parametrize("g_proj_data,g_jid_data,u_status_cnt,u_osfs_cnt,g_jid_cnt",
                         [([('wsProjectToken',datetime(2023,9,4,21,5,5),'ProjectName','AlertUuid',
                             'Ignored',1,'License Violation')],
                             [('ABC-123',datetime(2022,10,4,21,5,45).date(),'RITM123',1,0)],0,0,1),
                          ([('wsProjectToken',datetime(2023,9,4,21,5,5),'ProjectName','AlertUuid',
                             'Ignored',1,'Vulnerability')],
                             [('ABC-123',datetime(2022,10,4,21,5,45).date(),None,0,1)],1,1,1),
                          ([('wsProjectToken',datetime(2023,9,4,21,5,5),'ProjectName','AlertUuid',
                             'Ignored',1,'License Violation')],
                             [('ABC-123',datetime(2027,10,4,21,5,45).date(),None,0,1)],0,0,1),
                          ([('wsProjectToken',datetime(2023,10,4,21,5,45),'ProjectName','AlertUuid',
                             'Active',1,'Vulnerability')],None,0,0,0)])
def test_process_closed_tickets(log_hl,sql_sel,ex_sql,g_proj,g_jid,u_status,ex_func,u_osfs,u_ji,
                                log_ln,lv_reopen,g_proj_data,g_jid_data,u_status_cnt,u_osfs_cnt,
                                g_jid_cnt):
    '''Tests process_closed_tickets'''
    g_proj.return_value = g_proj_data
    g_jid.return_value = g_jid_data
    process_closed_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_proj.call_count == 1
    assert g_jid.call_count == g_jid_cnt
    assert u_status.call_count == u_status_cnt
    assert ex_func.call_count == 0
    assert u_osfs.call_count == u_osfs_cnt
    assert u_ji.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.reopen_mend_license_violation_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_status')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.MendAPI.update_alert_status',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.get_jiraissue_data')
@mock.patch('mend.ticket_creation_and_closure.get_project_details')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','RITM1234','1',),])
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@pytest.mark.parametrize("g_proj_data,g_jid_data,u_status_cnt,u_osfs_cnt,g_jid_cnt",
                         [([('wsProjectToken',datetime(2023,9,4,21,5,5),'ProjectName','AlertUuid',
                             'Ignored',1,'Vulnerability')],
                             [('ABC-123',datetime(2022,10,4,21,5,45).date(),None,0,1)],1,0,1)])
def test_process_closed_tickets_ex_uas(log_hl,sql_sel,ex_sql,g_proj,g_jid,u_status,ex_func,u_osfs,u_ji,
                                log_ln,lv_reopen,g_proj_data,g_jid_data,u_status_cnt,u_osfs_cnt,
                                g_jid_cnt):
    '''Tests process_closed_tickets'''
    g_proj.return_value = g_proj_data
    g_jid.return_value = g_jid_data
    process_closed_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_proj.call_count == 1
    assert g_jid.call_count == g_jid_cnt
    assert u_status.call_count == u_status_cnt
    assert ex_func.call_count == 1
    assert u_osfs.call_count == u_osfs_cnt
    assert u_ji.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_status')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.MendAPI.update_alert_status')
@mock.patch('mend.ticket_creation_and_closure.get_jiraissue_data',)
@mock.patch('mend.ticket_creation_and_closure.get_project_details')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
def test_process_closed_tickets_ex_sql_sel(log_hl,sql_sel,ex_sql,g_proj,g_jid,u_status,ex_func,
                                           u_osfs,u_ji,log_ln):
    '''Tests process_closed_tickets'''
    process_closed_tickets('appsec-ops')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_proj.call_count == 0
    assert g_jid.call_count == 0
    assert u_status.call_count == 0
    assert ex_func.call_count == 0
    assert u_osfs.call_count == 0
    assert u_ji.call_count == 0
    assert log_ln.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('AS-1234','2024-12-31','RITM1234',1,0,),])
def test_get_jiraissue_data(sql_sel,ex_sql):
    '''Tests get_jiraissue_data'''
    get_jiraissue_data('AS-1234')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_get_jiraissue_data_ex_gjid_001(sql_sel,ex_sql):
    '''Tests get_jiraissue_data'''
    get_jiraissue_data('AS-1234')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
def test_update_osfindings_status(sql_upd,ex_sql):
    '''Tests update_osfindings_status'''
    update_osfindings_status('appsec-ops','alert_uuid')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
def test_update_osfindings_status_ex_uosfs_001(sql_upd,ex_sql):
    '''Tests update_osfindings_status'''
    update_osfindings_status('appsec-ops','alert_uuid')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            return_value=[('wsProjectToken','wsLastUpdatedDate','ProjectName','AlertUuid',
                           'AlertStatus','FoundInLastScan',),])
def test_get_project_details(sql_sel,ex_sql):
    '''Tests get_project_details'''
    get_project_details('AS-1234')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.select',
            side_effect=Exception)
def test_get_project_details_ex_gpd_001(sql_sel,ex_sql):
    '''Tests get_project_details'''
    get_project_details('AS-1234')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':None,'Severity':'Critical',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'High',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,u_osft,
                                   i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,ex_sql,u_ji_ftar,
                                   has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 1
    assert log_ln.call_count == 6
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 3
    assert u_osft.call_count == 3
    assert i_ji.call_count == 3
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 4
    assert tkt_cmt.call_count == 3

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=False)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':None,'Severity':'Critical',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'High',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(1,'PROG','AS-4321',0,),])
def test_create_and_update_tickets_tech_debt(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                             u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                             ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 1
    assert log_ln.call_count == 6
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 3
    assert u_osft.call_count == 3
    assert i_ji.call_count == 3
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 4
    assert tkt_cmt.call_count == 3

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions')
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(1,'AS',None,0,),])
def test_create_and_update_tickets_no_jira_info(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                                u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                                ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 1
    assert log_ln.call_count == 1
    assert cnt_tkt.call_count == 1
    assert c_desc.call_count == 0
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 0
    assert chk_ex.call_count == 0
    assert chk_td.call_count == 0
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 0
    assert has_repo_ex.call_count == 0
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions')
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            side_effect=Exception)
def test_create_and_update_tickets_ex_caut_001(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 0
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 0
    assert chk_ex.call_count == 0
    assert chk_td.call_count == 0
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 0
    assert has_repo_ex.call_count == 0
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_002(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 0
    assert log_ln.call_count == 0
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 0
    assert chk_ex.call_count == 0
    assert chk_td.call_count == 0
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 0
    assert has_repo_ex.call_count == 0
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':None,'Severity':'Critical',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_003_005(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                                   u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                                   ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 2
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 1
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 0
    assert chk_td.call_count == 0
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 2
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':None,'Severity':'Critical',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'High',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':None,'Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'},
                           {'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_004(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,u_osft,
                                   i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,ex_sql,u_ji_ftar,
                                   has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 3
    assert log_hl.call_count == 1
    assert log_ln.call_count == 6
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 3
    assert u_osft.call_count == 3
    assert i_ji.call_count == 3
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 4
    assert tkt_cmt.call_count == 3

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_006(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 0
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 1
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_007(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 1
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_008(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 1
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 1
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 1
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.has_repo_exceptions')
@mock.patch('mend.ticket_creation_and_closure.update_jiraissues_for_tool_and_repo')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_tech_debt',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.check_exceptions',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.update_jira_ticket',
            return_value=True)
@mock.patch('mend.ticket_creation_and_closure.insert_jiraissues')
@mock.patch('mend.ticket_creation_and_closure.update_osfindings_ticket')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.create_jira_ticket',
            return_value='AS-1234')
@mock.patch('mend.ticket_creation_and_closure.MendTicketing.create_jira_descriptions',
            return_value=[{'ExistingTicket':'AS-1212','Severity':'Medium',
                           'Summary':'Open Source Vulnerability: Issue - repo',
                           'Description':'desc','GroupId':'group_id'}])
@mock.patch('mend.ticket_creation_and_closure.cannot_ticket')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_info')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.log_headline')
@mock.patch('mend.ticket_creation_and_closure.TheLogs.function_exception')
@mock.patch('mend.ticket_creation_and_closure.GeneralTicketing.get_jira_info',
            return_value=[(0,'AS','AS-4321',1,),])
def test_create_and_update_tickets_ex_caut_009(g_ji,ex_func,log_hl,log_ln,cnt_tkt,c_desc,c_tkt,
                                               u_osft,i_ji,u_tkt,chk_ex,chk_td,chk_pd,sql_upd,
                                               ex_sql,u_ji_ftar,has_repo_ex,tkt_cmt):
    '''Tests create_and_update_tickets'''
    create_and_update_tickets('appsec-ops')
    assert g_ji.call_count == 1
    assert ex_func.call_count == 0
    assert log_hl.call_count == 1
    assert log_ln.call_count == 2
    assert cnt_tkt.call_count == 0
    assert c_desc.call_count == 1
    assert c_tkt.call_count == 0
    assert u_osft.call_count == 0
    assert i_ji.call_count == 0
    assert u_tkt.call_count == 1
    assert chk_ex.call_count == 1
    assert chk_td.call_count == 1
    assert chk_pd.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert u_ji_ftar.call_count == 1
    assert has_repo_ex.call_count == 1
    assert tkt_cmt.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            return_value=1)
def test_update_osfindings_ticket(sql_upd,ex_sql):
    '''Tests update_osfindings_ticket'''
    update_osfindings_ticket('AS-1234','Open','2023-10-10','appsec-ops',{'GroupId':'group_id'},
                             'Vulnerability')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.update',
            side_effect=Exception)
def test_update_osfindings_ticket_ex_uosft_001(sql_upd,ex_sql):
    '''Tests update_osfindings_ticket'''
    update_osfindings_ticket('AS-1234','Open','2023-10-10','appsec-ops',{'GroupId':'group_id'},
                             'Vulnerability')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.insert',
            return_value=1)
def test_insert_jiraissues(sql_ins,ex_sql):
    '''Tests insert_jiraissues'''
    insert_jiraissues('repo','epic','proj_key','ticket',{'GroupId':'group_id','Summary':'summary',
                                                         'Severity':'High'},'due_date',
                                                         'created_date','td_status')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.ticket_creation_and_closure.TheLogs.sql_exception')
@mock.patch('mend.ticket_creation_and_closure.insert',
            side_effect=Exception)
def test_insert_jiraissues_ex_iji_001(sql_ins,ex_sql):
    '''Tests insert_jiraissues'''
    insert_jiraissues('repo','epic','proj_key','ticket',{'GroupId':'group_id','Summary':'summary',
                                                         'Severity':'High'},'due_date',
                                                         'created_date','td_status')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 1

if __name__ == '__main__':
    unittest.main()
