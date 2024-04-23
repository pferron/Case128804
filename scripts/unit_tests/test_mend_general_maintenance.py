'''Unit tests for mend.general_maintenance '''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from mend.general_maintenance import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('appsec-ops',),('ddecore',),])
def test_mendmaint_get_all_mend_repos(sel_sql,ex_sql):
    '''Tests MendMaint.get_all_mend_repos'''
    result = MendMaint.get_all_mend_repos()
    assert sel_sql.call_count == 1
    assert ex_sql.call_count == 0
    assert result == {'FatalCount':0,'ExceptionCount':0,'Results':['appsec-ops','ddecore']}

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_mendmaint_get_all_mend_repos_ec_gamr_001(sel_sql,ex_sql):
    '''Tests MendMaint.get_all_mend_repos'''
    result = MendMaint.get_all_mend_repos()
    assert sel_sql.call_count == 1
    assert ex_sql.call_count == 1
    assert result == {'FatalCount':1,'ExceptionCount':0,'Results':[]}
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.general_maintenance.retire_mend_products')
@mock.patch('mend.general_maintenance.update_projects')
@mock.patch('mend.general_maintenance.update_mend_products')
def test_mendmaint_all_mend_maintenance(u_prods,u_projs,ret_prods):
    '''Tests MendMaint.all_mend_maintenance'''
    MendMaint.all_mend_maintenance('appsec_ops')
    assert u_prods.call_count == 1
    assert u_projs.call_count == 1
    assert ret_prods.call_count == 1

@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.update_tech_debt_boarded')
@mock.patch('mend.general_maintenance.insert_token_into_table')
@mock.patch('mend.general_maintenance.set_token_in_table')
@mock.patch('mend.general_maintenance.repo_exists_in_table',
            return_value=True)
@mock.patch('mend.general_maintenance.zero_out_sca')
@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.get_org_prod_vitals',
            return_value=[{"Repo":'appsec-ops',"wsProductToken":'token'}])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_update_mend_products_updates(log_hl,api_vitals,ex_func,zero_sca,r_exists,set_token,
                              ins_token,tdb_zero,log_ln):
    '''Tests update_mend_products'''
    update_mend_products()
    assert log_hl.call_count == 1
    assert api_vitals.call_count == 1
    assert ex_func.call_count == 0
    assert zero_sca.call_count == 1
    assert r_exists.call_count == 2
    assert set_token.call_count == 2
    assert ins_token.call_count == 0
    assert tdb_zero.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.update_tech_debt_boarded')
@mock.patch('mend.general_maintenance.insert_token_into_table')
@mock.patch('mend.general_maintenance.set_token_in_table')
@mock.patch('mend.general_maintenance.repo_exists_in_table',
            return_value=False)
@mock.patch('mend.general_maintenance.zero_out_sca')
@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.get_org_prod_vitals',
            return_value=[{"Repo":'appsec-ops',"wsProductToken":'token'}])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_update_mend_products_inserts(log_hl,api_vitals,ex_func,zero_sca,r_exists,set_token,
                              ins_token,tdb_zero,log_ln):
    '''Tests update_mend_products'''
    update_mend_products()
    assert log_hl.call_count == 1
    assert api_vitals.call_count == 1
    assert ex_func.call_count == 0
    assert zero_sca.call_count == 1
    assert r_exists.call_count == 2
    assert set_token.call_count == 0
    assert ins_token.call_count == 2
    assert tdb_zero.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.update_tech_debt_boarded')
@mock.patch('mend.general_maintenance.insert_token_into_table')
@mock.patch('mend.general_maintenance.set_token_in_table')
@mock.patch('mend.general_maintenance.repo_exists_in_table',
            return_value=True)
@mock.patch('mend.general_maintenance.zero_out_sca')
@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.get_org_prod_vitals',
            side_effect=Exception)
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_update_mend_products_ex_ump_001(log_hl,api_vitals,ex_func,zero_sca,r_exists,set_token,
                              ins_token,tdb_zero,log_ln):
    '''Tests update_mend_products'''
    update_mend_products()
    assert log_hl.call_count == 1
    assert api_vitals.call_count == 1
    assert ex_func.call_count == 1
    assert zero_sca.call_count == 0
    assert r_exists.call_count == 0
    assert set_token.call_count == 0
    assert ins_token.call_count == 0
    assert tdb_zero.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('appsec-ops',),])
def test_repo_exists_in_table(sql_sel,ex_sql):
    '''Tests repo_exists_in_table'''
    result = repo_exists_in_table('appsec-ops','ApplicationAutomation')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result is True

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_repo_exists_in_table_ex_reit_001(sql_sel,ex_sql):
    '''Tests repo_exists_in_table'''
    result = repo_exists_in_table('appsec-ops','ApplicationAutomation')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result is None
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_set_token_in_table(sql_upd,ex_sql):
    '''Tests set_token_in_table'''
    set_token_in_table('appsec-ops','the_token','ApplicationAutomation')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    set_token_in_table('appsec-ops','the_token','Applications')
    assert sql_upd.call_count == 2
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_set_token_in_table_ex_stit_001(sql_upd,ex_sql):
    '''Tests set_token_in_table'''
    set_token_in_table('appsec-ops','the_token','ApplicationAutomation')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.insert')
def test_insert_token_into_table(sql_ins,ex_sql):
    '''Test insert_token_into_table'''
    insert_token_into_table('appsec-ops','the_token','ApplicationAutomation')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 0
    insert_token_into_table('appsec-ops','the_token','Applications')
    assert sql_ins.call_count == 2
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.insert',
            side_effect=Exception)
def test_insert_token_into_table_ex_itit_001(sql_ins,ex_sql):
    '''Test insert_token_into_table'''
    insert_token_into_table('appsec-ops','the_token','ApplicationAutomation')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_zero_out_sca(sql_upd,ex_sql):
    '''Tests zero_out_sca'''
    zero_out_sca()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_zero_out_sca_ex_zos_001(sql_upd,ex_sql):
    '''Tests zero_out_sca'''
    zero_out_sca()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_update_tech_debt_boarded(sql_upd,ex_sql):
    '''Tests update_tech_debt_boarded'''
    update_tech_debt_boarded()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_update_tech_debt_boarded_ex_stz_001(sql_upd,ex_sql):
    '''Tests update_tech_debt_boarded'''
    update_tech_debt_boarded()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.cancel_jira_tickets',
            return_value=True)
@mock.patch('mend.general_maintenance.get_jira_to_retire',
            return_value=[('AS-1234',),])
@mock.patch('mend.general_maintenance.deactivate_mend')
@mock.patch('mend.general_maintenance.update_osprojs_retired')
@mock.patch('mend.general_maintenance.delete_product',
            return_value=True)
@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.retire_repo_osprojects')
@mock.patch('mend.general_maintenance.check_osprojects',
            return_value=True)
@mock.patch('mend.general_maintenance.get_retire_repo',
            return_value=[('appsec-ops','the_token',),])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_retire_mend_products(log_hl,g_rr,c_osp,ret_osp,log_ln,del_prod,u_osp,d_mend,g_tkts,cancel_tkts):
    '''Tests retire_mend_products'''
    retire_mend_products('appsec-ops')
    assert log_hl.call_count == 2
    assert g_rr.call_count == 1
    assert c_osp.call_count == 1
    assert ret_osp.call_count == 1
    assert log_ln.call_count == 3
    assert del_prod.call_count == 1
    assert u_osp.call_count == 1
    assert d_mend.call_count == 1
    assert g_tkts.call_count == 1
    assert cancel_tkts.call_count == 1

@mock.patch('mend.general_maintenance.cancel_jira_tickets',
            return_value=True)
@mock.patch('mend.general_maintenance.get_jira_to_retire',
            return_value=[('AS-1234',),])
@mock.patch('mend.general_maintenance.deactivate_mend')
@mock.patch('mend.general_maintenance.update_osprojs_retired')
@mock.patch('mend.general_maintenance.delete_product',
            return_value=True)
@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.retire_repo_osprojects')
@mock.patch('mend.general_maintenance.check_osprojects',
            return_value=False)
@mock.patch('mend.general_maintenance.get_retire_repo',
            return_value=[('appsec-ops','the_token',),])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_retire_mend_products_not_in_osprojects(log_hl,g_rr,c_osp,ret_osp,log_ln,del_prod,u_osp,
                                                d_mend,g_tkts,cancel_tkts):
    '''Tests retire_mend_products'''
    retire_mend_products('appsec-ops')
    assert log_hl.call_count == 2
    assert g_rr.call_count == 1
    assert c_osp.call_count == 1
    assert ret_osp.call_count == 0
    assert log_ln.call_count == 4
    assert del_prod.call_count == 1
    assert u_osp.call_count == 1
    assert d_mend.call_count == 1
    assert g_tkts.call_count == 1
    assert cancel_tkts.call_count == 1

@mock.patch('mend.general_maintenance.cancel_jira_tickets',
            return_value=True)
@mock.patch('mend.general_maintenance.get_jira_to_retire',
            return_value=[('AS-1234',),])
@mock.patch('mend.general_maintenance.deactivate_mend')
@mock.patch('mend.general_maintenance.update_osprojs_retired')
@mock.patch('mend.general_maintenance.delete_product',
            return_value=False)
@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.retire_repo_osprojects')
@mock.patch('mend.general_maintenance.check_osprojects',
            return_value=True)
@mock.patch('mend.general_maintenance.get_retire_repo',
            return_value=[('appsec-ops','the_token',),])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_retire_mend_products_not_deleted(log_hl,g_rr,c_osp,ret_osp,log_ln,del_prod,u_osp,d_mend,
                                          g_tkts,cancel_tkts):
    '''Tests retire_mend_products'''
    retire_mend_products('appsec-ops')
    assert log_hl.call_count == 1
    assert g_rr.call_count == 1
    assert c_osp.call_count == 1
    assert ret_osp.call_count == 1
    assert log_ln.call_count == 1
    assert del_prod.call_count == 1
    assert u_osp.call_count == 0
    assert d_mend.call_count == 0
    assert g_tkts.call_count == 0
    assert cancel_tkts.call_count == 0

@mock.patch('mend.general_maintenance.cancel_jira_tickets')
@mock.patch('mend.general_maintenance.get_jira_to_retire')
@mock.patch('mend.general_maintenance.deactivate_mend')
@mock.patch('mend.general_maintenance.update_osprojs_retired')
@mock.patch('mend.general_maintenance.delete_product')
@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.retire_repo_osprojects')
@mock.patch('mend.general_maintenance.check_osprojects')
@mock.patch('mend.general_maintenance.get_retire_repo',
            return_value=[])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_retire_mend_products_not_retired(log_hl,g_rr,c_osp,ret_osp,log_ln,del_prod,u_osp,d_mend,
                                          g_tkts,cancel_tkts):
    '''Tests retire_mend_products'''
    retire_mend_products('appsec-ops')
    assert log_hl.call_count == 1
    assert g_rr.call_count == 1
    assert c_osp.call_count == 0
    assert ret_osp.call_count == 0
    assert log_ln.call_count == 1
    assert del_prod.call_count == 0
    assert u_osp.call_count == 0
    assert d_mend.call_count == 0
    assert g_tkts.call_count == 0
    assert cancel_tkts.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('appsec-ops',),])
def test_check_osprojects(sql_sel,ex_sql):
    '''Tests check_osprojects'''
    result = check_osprojects('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == True

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_check_osprojects_ex_cop_001(sql_sel,ex_sql):
    '''Tests check_osprojects'''
    result = check_osprojects('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == False
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('appsec_ops','the_token',),])
def test_get_retire_repo(sql_sel,ex_sql):
    '''Tests get_retire_repo'''
    get_retire_repo('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_get_retire_repo_ex_grr_001(sql_sel,ex_sql):
    '''Tests get_retire_repo'''
    get_retire_repo()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_retire_repo_osprojects(sql_upd,ex_sql):
    '''Tests retire_repo_osprojects'''
    retire_repo_osprojects('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_retire_repo_osprojects_ex_rrop_001(sql_upd,ex_sql):
    '''Tests retire_repo_osprojects'''
    retire_repo_osprojects('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.delete_product',
            return_value=True)
def test_delete_product(del_prod,ex_func):
    '''Tests delete_product'''
    result = delete_product('the_token')
    assert del_prod.call_count == 1
    assert ex_func.call_count == 0
    assert result is True

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.delete_product',
            side_effect=Exception)
def test_delete_product_ex_dp_001(del_prod,ex_func):
    '''Tests delete_product'''
    result = delete_product('the_token')
    assert del_prod.call_count == 1
    assert ex_func.call_count == 1
    assert result is False
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_deactivate_mend(sql_upd,ex_sql):
    '''Tests deactivate_mend'''
    deactivate_mend('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_deactivate_mend_ex_dm_001(sql_upd,ex_sql):
    '''Tests deactivate_mend'''
    deactivate_mend('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('AS-1234',),])
def test_get_jira_to_retire(sql_sel,ex_sql):
    '''Tests get_jira_to_retire'''
    get_jira_to_retire('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_get_jira_to_retire_ex_gjtr_001(sql_sel,ex_sql):
    '''Tests get_jira_to_retire'''
    get_jira_to_retire('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.GeneralTicketing.cancel_jira_ticket',
            return_value=True)
def test_cancel_jira_tickets(cancel_tkt,ex_func):
    '''Tests cancel_jira_tickets'''
    cancel_jira_tickets('appsec-ops','AS-1234')
    assert cancel_tkt.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.GeneralTicketing.cancel_jira_ticket',
            side_effect=Exception)
def test_cancel_jira_tickets_ex_cjt_001(cancel_tkt,ex_func):
    '''Tests cancel_jira_tickets'''
    cancel_jira_tickets('appsec-ops','AS-1234')
    assert cancel_tkt.call_count == 1
    assert ex_func.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_update_osprojs_retired(sql_upd,ex_sql):
    '''Tests update_osprojs_retired'''
    update_osprojs_retired('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_update_osprojs_retired_ex_uopr_001(sql_upd,ex_sql):
    '''Tests update_osprojs_retired'''
    update_osprojs_retired('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.insert_osprojects')
@mock.patch('mend.general_maintenance.update_osprojects')
@mock.patch('mend.general_maintenance.project_check',
            return_value = True)
@mock.patch('mend.general_maintenance.get_projects',
            return_value=[{'wsProjectName':'appsec-ops','wsProjectToken':'proj_token',
                           'wsProjectId':'proj_id','wsLastUpdatedDate':'2023-10-20'}])
@mock.patch('mend.general_maintenance.zero_active')
@mock.patch('mend.general_maintenance.get_os_projects',
            return_value=[('appsec-ops','the_token',),])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_update_projects(log_hl,g_os_projs,zero_act,g_projs,proj_check,u_osp,i_osp,log_ln):
    '''Tests update_projects'''
    update_projects('appsec-ops')
    assert log_hl.call_count == 1
    assert g_os_projs.call_count == 1
    assert zero_act.call_count == 1
    assert g_projs.call_count == 1
    assert proj_check.call_count == 1
    assert u_osp.call_count == 1
    assert i_osp.call_count == 0
    assert log_ln.call_count == 2

@mock.patch('mend.general_maintenance.TheLogs.log_info')
@mock.patch('mend.general_maintenance.insert_osprojects')
@mock.patch('mend.general_maintenance.update_osprojects')
@mock.patch('mend.general_maintenance.project_check',
            return_value = False)
@mock.patch('mend.general_maintenance.get_projects',
            return_value=[{'wsProjectName':'appsec-ops','wsProjectToken':'proj_token',
                           'wsProjectId':'proj_id','wsLastUpdatedDate':'2023-10-20'}])
@mock.patch('mend.general_maintenance.zero_active')
@mock.patch('mend.general_maintenance.get_os_projects',
            return_value=[('appsec-ops','the_token',),])
@mock.patch('mend.general_maintenance.TheLogs.log_headline')
def test_update_projects_does_not_exist(log_hl,g_os_projs,zero_act,g_projs,proj_check,u_osp,i_osp,
                                        log_ln):
    '''Tests update_projects'''
    update_projects('appsec-ops')
    assert log_hl.call_count == 1
    assert g_os_projs.call_count == 1
    assert zero_act.call_count == 1
    assert g_projs.call_count == 1
    assert proj_check.call_count == 1
    assert u_osp.call_count == 0
    assert i_osp.call_count == 1
    assert log_ln.call_count == 2

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select')
def test_get_os_projects(sql_sel,ex_sql):
    '''Tests get_os_projects'''
    get_os_projects('appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_get_os_projects_ex_gop_001(sql_sel,ex_sql):
    '''Tests get_os_projects'''
    get_os_projects()
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update')
def test_zero_active(sql_upd,ex_sql):
    '''Tests zero_active'''
    zero_active('appsec-ops')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_zero_active_ex_za_001(sql_upd,ex_sql):
    '''Tests zero_active'''
    zero_active()
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.get_projects')
def test_get_projects(api_projs,ex_func):
    '''Tests get_projects'''
    get_projects('appsec-ops','the_token')
    assert api_projs.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.function_exception')
@mock.patch('mend.general_maintenance.MendAPI.get_projects',
            side_effect=Exception)
def test_get_projects_ex_gp_001(api_projs,ex_func):
    '''Tests get_projects'''
    get_projects('appsec-ops','the_token')
    assert api_projs.call_count == 1
    assert ex_func.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            return_value=[('appsec-ops',),])
def test_project_check(sql_sel,ex_sql):
    '''Tests project_check'''
    project_check('appsec-ops','appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.select',
            side_effect=Exception)
def test_project_check_ex_pc_001(sql_sel,ex_sql):
    '''Tests project_check'''
    project_check('appsec-ops','appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            return_value=1)
def test_update_osprojects(sql_upd,ex_sql):
    '''Tests update_osprojects'''
    update_osprojects('appsec-ops','p_token','p_id','2023-10-30','appsec-ops','the_token')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert ScrVar.u_cnt == 1
    ScrVar.u_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.update',
            side_effect=Exception)
def test_update_osprojects_ex_uop_001(sql_upd,ex_sql):
    '''Tests update_osprojects'''
    update_osprojects('appsec-ops','p_token','p_id','2023-10-30','appsec-ops','the_token')
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.u_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.insert',
            return_value=1)
def test_insert_osprojects(sql_ins,ex_sql):
    '''Tests insert_osprojects'''
    insert_osprojects('appsec-ops','p_token','p_id','2023-10-30','appsec-ops','the_token')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 0
    assert ScrVar.a_cnt == 1
    ScrVar.a_cnt = 0

@mock.patch('mend.general_maintenance.TheLogs.sql_exception')
@mock.patch('mend.general_maintenance.insert',
            side_effect=Exception)
def test_insert_osprojects_ex_iop_001(sql_ins,ex_sql):
    '''Tests insert_osprojects'''
    insert_osprojects('appsec-ops','p_token','p_id','2023-10-30','appsec-ops','the_token')
    assert sql_ins.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.a_cnt == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
