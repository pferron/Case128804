'''Unit tests for mend\deleted_project_handling.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from mend.deleted_project_handling import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('mend.deleted_project_handling.deleted_project_ticket_update')
@mock.patch('mend.deleted_project_handling.DBQueries.update_multiple')
@mock.patch('mend.deleted_project_handling.set_findings_to_close')
@mock.patch('mend.deleted_project_handling.open_tickets_to_add_comment')
@mock.patch('mend.deleted_project_handling.TheLogs.function_exception')
@mock.patch('mend.deleted_project_handling.GeneralTicketing.cancel_jira_ticket')
@mock.patch('mend.deleted_project_handling.get_deleted_project_names_for_ticket')
@mock.patch('mend.deleted_project_handling.get_tickets_to_cancel')
@mock.patch('mend.deleted_project_handling.get_deleted_project_list')
@mock.patch('mend.deleted_project_handling.TheLogs.log_info')
@mock.patch('mend.deleted_project_handling.get_deleted_products')
@mock.patch('mend.deleted_project_handling.TheLogs.log_headline')
@pytest.mark.parametrize("description,gdp_rv,log_ln_cnt,gdpl_rv,gdpl_cnt,gttc_rv,gttc_cnt,gdpnft_rv,gdpnft_cnt,cjt_se,cjt_rv,cjt_cnt,ex_func_cnt,ottac_rv,ottac_cnt,sftc_rv,sftc_cnt,um_se,um_cnt,dptu_cnt,fe_cnt,ex_cnt",
                         [("gdp_rv = []",[],1,None,0,None,0,None,0,None,None,0,0,None,0,None,0,None,0,0,0,0),
                          ("All expected values",[('ProductName',),],10,{'ProjectNames':['ProjectName'],'ProjectIds':['ProjectId']},1,[('KEY-123',),],1,[('ProjectName',),],2,None,True,1,0,[('KEY-124',),],1,True,1,None,4,1,0,0),
                          ("All expected values, no tickets to cancel",[('ProductName',),],10,{'ProjectNames':['ProjectName'],'ProjectIds':['ProjectId']},1,[],1,[('ProjectName',),],1,None,None,0,0,[('KEY-124',),],1,True,1,None,4,1,0,0),
                          ("All expected values, no tickets to update",[('ProductName',),],10,{'ProjectNames':['ProjectName'],'ProjectIds':['ProjectId']},1,[('KEY-123',),],1,[('ProjectName',),],1,None,True,1,0,[],1,None,0,None,3,0,0,0),
                          ("Exception: cjt",[('ProductName',),],9,{'ProjectNames':['ProjectName'],'ProjectIds':['ProjectId']},1,[('KEY-123',),],1,[('ProjectName',),],2,Exception,None,1,1,[('KEY-124',),],1,True,1,None,4,1,0,1),
                          ("Exception: um",[('ProductName',),],10,{'ProjectNames':['ProjectName'],'ProjectIds':['ProjectId']},1,[('KEY-123',),],1,[('ProjectName',),],2,None,True,1,4,[('KEY-124',),],1,True,1,Exception,4,1,0,4)])
def test_deletedprojects_cancel_tickets_for_deleted_projects(log_hl,gdp,log_ln,gdpl,gttc,gdpnft,
                                                             cjt,ex_func,ottac,sftc,um,dptu,
                                                             description,gdp_rv,log_ln_cnt,gdpl_rv,
                                                             gdpl_cnt,gttc_rv,gttc_cnt,gdpnft_rv,
                                                             gdpnft_cnt,cjt_se,cjt_rv,cjt_cnt,
                                                             ex_func_cnt,ottac_rv,ottac_cnt,
                                                             sftc_rv,sftc_cnt,um_se,um_cnt,
                                                             dptu_cnt,fe_cnt,ex_cnt):
    """Tests DeletedProjects.cancel_tickets_for_deleted_projects"""
    gdp.return_value = gdp_rv
    gdpl.return_value = gdpl_rv
    gttc.return_value = gttc_rv
    gdpnft.return_value = gdpnft_rv
    cjt.side_effect = cjt_se
    cjt.return_value = cjt_rv
    ottac.return_value = ottac_rv
    sftc.return_value = sftc_rv
    um.side_effect = um_se
    response = DeletedProjects.cancel_tickets_for_deleted_projects()
    assert log_hl.call_count == 1
    assert gdp.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert gdpl.call_count == gdpl_cnt
    assert gttc.call_count == gttc_cnt
    assert gdpnft.call_count == gdpnft_cnt
    assert cjt.call_count == cjt_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ottac.call_count == ottac_cnt
    assert sftc.call_count == sftc_cnt
    assert um.call_count == um_cnt
    assert dptu.call_count == dptu_cnt
    assert response == {'FatalCount':fe_cnt,'ExceptionCount':ex_cnt}
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("Exception: sql_sel",Exception,None,1,0,1,[]),
                          ("All expected values",None,[('ProductName',),],0,0,0,[('ProductName',),])])
def test_get_deleted_products(sql_sel,ex_sql,
                              description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                              fe_cnt,ex_cnt,response_rv):
    """Tests get_deleted_products"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_deleted_products()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,[('ProjectName','ProjectId',),],0,0,0,{'ProjectNames':['ProjectName'],'ProjectIds':'ProjectId'}),
                          ("Exception: sql_sel",Exception,None,1,0,1,{'ProjectNames':[],'ProjectIds':''})])
def test_get_deleted_project_list(sql_sel,ex_sql,
                                  description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                  fe_cnt,ex_cnt,response_rv):
    """Tests get_deleted_project_list"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_deleted_project_list('repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,[('KEY-123',),],0,0,0,[('KEY-123',),]),
                          ("Exception: sql_sel",Exception,None,1,0,1,[])])
def test_get_tickets_to_cancel(sql_sel,ex_sql,
                               description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                               fe_cnt,ex_cnt,response_rv):
    """Tests get_tickets_to_cancel"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_tickets_to_cancel('repo','ProjectId1,ProjectId2')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,[('KEY-123',),],0,0,0,[('KEY-123',),]),
                          ("Exception: sql_sel",Exception,None,1,0,1,[])])
def test_open_tickets_to_add_comment(sql_sel,ex_sql,
                                     description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                     fe_cnt,ex_cnt,response_rv):
    """Tests open_tickets_to_add_comment"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = open_tickets_to_add_comment('repo','ProjectId1,ProjectId2')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,[('ProjectName',),],0,0,0,[('ProjectName',),]),
                          ("Exception: sql_sel",Exception,None,1,0,1,[])])
def test_get_deleted_project_names_for_ticket(sql_sel,ex_sql,
                                              description,sql_sel_se,sql_sel_rv,ex_sql_cnt,
                                              fe_cnt,ex_cnt,response_rv):
    """Tests get_deleted_project_names_for_ticket"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_deleted_project_names_for_ticket('KEY-123')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,0,0,0,True),
                          ("Exception: sql_upd",Exception,1,0,1,False)])
def test_set_findings_to_close(sql_upd,ex_sql,
                               description,sql_upd_se,ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests set_findings_to_close"""
    sql_upd.side_effect = sql_upd_se
    response = set_findings_to_close('KEY-123','ProjectId1,ProjectId2')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('mend.deleted_project_handling.GeneralTicketing.add_comment_to_ticket')
@mock.patch('mend.deleted_project_handling.update_jira_description')
@mock.patch('mend.deleted_project_handling.MendTicketing.create_jira_descriptions')
@mock.patch('mend.deleted_project_handling.get_group_and_finding_type')
@pytest.mark.parametrize("description,ggaft_rv,cjd_rv,cjd_cnt,ujd_cnt,actt_cnt",
                         [("ggaft_rv = []",[],None,0,0,0),
                          ("cjd_rv = []",[{'GroupId':'group_id','FindingType':'type'}],[],1,0,0),
                          ("All expected values",[{'GroupId':'group_id','FindingType':'type'}],[{'Description':'the description'}],1,1,1)])
def test_deleted_project_ticket_update(ggaft,cjd,ujd,actt,
                                       description,ggaft_rv,cjd_rv,cjd_cnt,ujd_cnt,actt_cnt):
    """Tests deleted_project_ticket_update"""
    ggaft.return_value = ggaft_rv
    cjd.return_value = cjd_rv
    deleted_project_ticket_update('repo','KEY-123','comment')
    assert ggaft.call_count == 1
    assert cjd.call_count == cjd_cnt
    assert ujd.call_count == ujd_cnt
    assert actt.call_count == actt_cnt

@mock.patch('mend.deleted_project_handling.TheLogs.sql_exception')
@mock.patch('mend.deleted_project_handling.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv",
                         [("All expected values",None,[('group_id','type',),],0,0,0,[{'GroupId':'group_id','FindingType':'type'}]),
                          ("Exception: sql_upd",Exception,None,1,0,1,[])])
def test_get_group_and_finding_type(sql_sel,ex_sql,
                                    description,sql_sel_se,sql_sel_rv,ex_sql_cnt,fe_cnt,ex_cnt,response_rv):
    """Tests get_group_and_finding_type"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_group_and_finding_type('KEY-123')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()