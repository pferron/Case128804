'''Unit tests for the maint.jira_issues_database_queries script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from mend.data_sync import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('mend.data_sync.TheLogs.log_info')
@mock.patch('mend.data_sync.sync_statuses')
@mock.patch('mend.data_sync.sync_tickets_and_versions')
@mock.patch('mend.data_sync.sync_group_id')
@mock.patch('mend.data_sync.mark_tech_debt_boarded')
@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.select')
@mock.patch('mend.data_sync.TheLogs.log_headline')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,mtdb_cnt,sgi_cnt,stav_cnt,ss_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('Exception: sql_sel',Exception,None,1,0,0,0,0,0,1,0),
                          ('sql_sel_rv = []',None,[],0,0,0,0,0,1,0,0),
                          ('All expected values',None,[('token',),],0,1,1,1,1,0,0,0)])
def test_mendsync_single_repo_updates(log_hl,sql_sel,ex_sql,mtdb,sgi,stav,ss,log_ln,
                                      description,sql_sel_se,sql_sel_rv,ex_sql_cnt,mtdb_cnt,
                                      sgi_cnt,stav_cnt,ss_cnt,log_ln_cnt,fe_cnt,ex_cnt):
    """Tests MendSync.single_repo_updates"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = MendSync.single_repo_updates('repo')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert mtdb.call_count == mtdb_cnt
    assert sgi.call_count == sgi_cnt
    assert stav.call_count == stav_cnt
    assert ss.call_count == ss_cnt
    assert log_ln.call_count == log_ln_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [('Exception: sql_sel',Exception,None,1,0,1,False),
                          ('All expected values',None,[('KEY-123',),],0,0,0,True)])
def test_is_security_exception(sql_sel,ex_sql,
                               description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,
                               response_rv):
    """Tests is_security_exception"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = is_security_exception('ticket')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.log_info')
@mock.patch('mend.data_sync.jiraissues_update')
@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.select')
@mock.patch('mend.data_sync.TheLogs.log_headline')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,ju_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('Exception: sql_sel',Exception,None,1,0,0,0,1),
                          ('All expected values',None,[('KEY-123','summary: group_id - repo',),],0,1,1,0,0)])
def test_sync_group_id(log_hl,sql_sel,ex_sql,ju,log_ln,
                       description,sql_sel_se,sql_sel_rv,ex_sql_cnt,ju_cnt,log_ln_cnt,
                       fe_cnt,ex_cnt):
    """Tests sync_group_id"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    sync_group_id('repo')
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert ju.call_count == ju_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_upd",Exception,None,1,0,1,0),
                          ("All expected values",None,1,0,0,0,1)])
def test_jiraissues_update(sql_upd,ex_sql,
                           description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests jiraissues_update"""
    sql_upd.side_effect = sql_upd_se
    sql_upd.return_value = sql_upd_rv
    response = jiraissues_update('group_id','repo','KEY-123')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.update_wsversion')
@mock.patch('mend.data_sync.get_version_osfindings')
@mock.patch('mend.data_sync.update_reporteddate_osfindings')
@mock.patch('mend.data_sync.TheLogs.log_info')
@mock.patch('mend.data_sync.update_jiraissuekey_osfindings')
@mock.patch('mend.data_sync.TheLogs.log_headline')
@mock.patch('mend.data_sync.get_mend_jira_data')
@pytest.mark.parametrize("description,gmjd_rv,log_hl_cnt,ujo_cnt,log_ln_cnt,uro_cnt,gvo_cnt,uw_cnt",
                         [("gmjd_rv = []",[],0,0,0,0,0,0),
                          ("All expected values (has created datetime",[('KEY-123','wsGroupId','Unapproved Open Source License: group - repo','2023-12-01','2023-12-01 00:00:00','Done')],3,1,3,1,1,1),
                          ("All expected values (has created datetime)",[('KEY-123','wsGroupId','Unapproved Open Source License: group - repo','2023-12-01',None,'Done')],3,1,3,1,1,1)])
def test_sync_tickets_and_versions(gmjd,log_hl,ujo,log_ln,uro,gvo,uw,
                                   description,gmjd_rv,log_hl_cnt,ujo_cnt,log_ln_cnt,uro_cnt,
                                   gvo_cnt,uw_cnt):
    """Tests sync_tickets_and_versions"""
    gmjd.return_value = gmjd_rv
    gvo.return_value = ['1.1','1.5']
    sync_tickets_and_versions('repo')
    assert gmjd.call_count == 1
    assert log_hl.call_count == log_hl_cnt
    assert ujo.call_count == ujo_cnt
    assert log_ln.call_count == log_ln_cnt
    assert uro.call_count == uro_cnt
    assert gvo.call_count == gvo_cnt
    assert uw.call_count == uw_cnt

@mock.patch('mend.data_sync.TheLogs.log_info')
@mock.patch('mend.data_sync.update_statuses_osfindings')
@mock.patch('mend.data_sync.TheLogs.log_headline')
@mock.patch('mend.data_sync.get_mend_jira_data')
@pytest.mark.parametrize("description,gmjd_rv,log_hl_cnt,uso_cnt,log_ln_cnt",
                         [("gmjd_rv = []",[],0,0,0),
                          ("All expected values",[('KEY-123','wsGroupId','Unapproved Open Source License: group - repo','2023-12-01','2023-12-01 00:00:00','Done')],1,1,8)])
def test_sync_statuses(gmjd,log_hl,uso,log_ln,
                       description,gmjd_rv,log_hl_cnt,uso_cnt,log_ln_cnt):
    """Tests sync_statuses"""
    gmjd.return_value = gmjd_rv
    sync_statuses('repo')
    assert gmjd.call_count == 1
    assert log_hl.call_count == log_hl_cnt
    assert uso.call_count == uso_cnt
    assert log_ln.call_count == log_ln_cnt

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt",
                         [("Exception: sql_upd",Exception,None,1,0,1),
                          ("All expected values",None,1,0,0,0)])
def test_mark_tech_debt_boarded(sql_upd,ex_sql,
                                description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt):
    """Tests mark_tech_debt_boarded"""
    sql_upd.side_effect = sql_upd_se
    sql_upd.return_value = sql_upd_rv
    response = mark_tech_debt_boarded('repo')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,[]),
                          ("All expected values",None,[('KEY-123','wsGroupId','JiraSummary','2024-01-01','2021-01-01 00:12:12','Done',),],0,0,0,[('KEY-123','wsGroupId','JiraSummary','2024-01-01','2021-01-01 00:12:12','Done',),])])
def test_get_mend_jira_data(sql_sel,ex_sql,
                            description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                            fe_cnt,ex_cnt,response_rv):
    """Tests get_mend_jira_data"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_mend_jira_data('repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_upd",Exception,None,1,0,1,0),
                          ("All expected values",None,1,0,0,0,1)])
def test_update_jiraissuekey_osfindings(sql_upd,ex_sql,
                                        description,sql_upd_se,sql_upd_rv,ex_sql_cnt,
                                        fe_cnt,ex_cnt,response_rv):
    """Tests update_jiraissuekey_osfindings"""
    sql_upd.side_effect = sql_upd_se
    sql_upd.return_value = sql_upd_rv
    response = update_jiraissuekey_osfindings('KEY-123','repo','group_id','f_type')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@mock.patch('mend.data_sync.is_security_exception')
@pytest.mark.parametrize("description,ise_rv,sql_upd_se,sql_upd_cnt,ex_sql_cnt,fe_cnt,ex_cnt,status",
                         [("All expected values, ise_rv = True, status = In Progress",True,None,2,0,0,0,'In Progress'),
                          ("Exception: sql_upd, ise_rv = True, status = In Progress",True,Exception,2,2,0,2,'In Progress'),
                          ("All expected values, ise_rv = False, status = Done",False,None,3,0,0,0,'Done'),
                          ("Exception: sql_upd, ise_rv = False, status = Done",False,Exception,3,3,0,3,'Done')])
def test_update_statuses_osfindings(ise,sql_upd,ex_sql,
                                    description,ise_rv,sql_upd_se,sql_upd_cnt,ex_sql_cnt,
                                    fe_cnt,ex_cnt,status):
    """Tests update_statuses_osfindings"""
    ise.return_value = ise_rv
    sql_upd.side_effect = sql_upd_se
    update_statuses_osfindings('KEY-123',status,'repo')
    assert ise.call_count == 1
    assert sql_upd.call_count == sql_upd_cnt
    assert ex_sql.call_count == ex_sql_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_upd",Exception,None,1,0,1,0),
                          ("All expected values",None,1,0,0,0,1)])
def test_update_reporteddate_osfindings(sql_upd,ex_sql,
                                        description,sql_upd_se,sql_upd_rv,ex_sql_cnt,
                                        fe_cnt,ex_cnt,response_rv):
    """Tests update_reporteddate_osfindings"""
    sql_upd.side_effect = sql_upd_se
    sql_upd.return_value = sql_upd_rv
    response = update_reporteddate_osfindings('2024-01-01','repo','group_id','f_ype','KEY-123')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0
@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,[]),
                          ("All expected values",None,[('Version',),],0,0,0,[('Version',),])])
def test_get_version_osfindings(sql_sel,ex_sql,
                                description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                fe_cnt,ex_cnt,response_rv):
    """Tests get_version_osfindings"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_version_osfindings('repo','group_id','KEY-124')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.data_sync.TheLogs.sql_exception')
@mock.patch('mend.data_sync.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_upd",Exception,None,1,0,1,0),
                          ("All expected values",None,1,0,0,0,1)])
def test_update_wsversion(sql_upd,ex_sql,
                          description,sql_upd_se,sql_upd_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests update_wsversion"""
    sql_upd.side_effect = sql_upd_se
    sql_upd.return_value = sql_upd_rv
    response = update_wsversion('KEY-123','repo','group_id','f_type')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
