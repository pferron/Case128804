'''Unit tests for the maintenance_script_stats script'''

import unittest
from unittest import mock
from datetime import time,datetime
import sys
import os
import pytest
from maintenance_script_stats import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maintenance_script_stats.update_overall_stats')
@mock.patch('maintenance_script_stats.get_month_name')
@mock.patch('maintenance_script_stats.General.cmd_processor')
@pytest.mark.parametrize("cp_rv,run_func,gm_cnt,uos_cnt",
                         [([{'function':'get_month_name','args':[1]}],"get_month_name(1)",1,0),
                          ([{'function':'update_overall_stats'}],"update_overall_stats",0,1)])
def test_main(cp,gmn,uos,cp_rv,run_func,gm_cnt,uos_cnt):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_script_stats.py',run_func]
    with mock.patch.object(sys, "argv", testargs):
        cp.return_value = cp_rv
        main()
        assert cp.call_count == 1
        assert gmn.call_count == gm_cnt
        assert uos.call_count == uos_cnt

@pytest.mark.parametrize("dictionary,fe_cnt,ex_cnt",
                         [({'FatalCount':1,'ExceptionCount':2},1,2),
                          ({'FatalCount':1,'ExceptionCount':0},1,0),
                          ({'FatalCount':0,'ExceptionCount':2},0,2),
                          ({},0,0)])
def test_scrvar_update_exception_info(dictionary,fe_cnt,ex_cnt):
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info(dictionary)
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_script_stats.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('maintenance_script_stats.Misc.end_timer')
@mock.patch('maintenance_script_stats.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('maintenance_script_stats.ScrVar.timed_script_teardown')
@mock.patch('maintenance_script_stats.update_overall_stats')
@mock.patch('maintenance_script_stats.cycle_through_execution_months')
@mock.patch('maintenance_script_stats.ScrVar.timed_script_setup')
def test_scriptstats_update_run_times(tss,ctem,uos,tst):
    """Tests ScriptStats.update_run_times"""
    ScriptStats.update_run_times()
    assert tss.call_count == 1
    assert ctem.call_count == 1
    assert uos.call_count == 1
    assert tst.call_count == 1

@mock.patch('maintenance_script_stats.TheLogs.log_info')
@mock.patch('maintenance_script_stats.update_database')
@mock.patch('maintenance_script_stats.get_runs_for_script_and_function')
@mock.patch('maintenance_script_stats.get_list_of_logged_scripts')
@mock.patch('maintenance_script_stats.TheLogs.log_headline')
@mock.patch('maintenance_script_stats.get_month_name')
@pytest.mark.parametrize("gmn_rv,glols_rv,grfsaf_rv,ud_rv,grfsaf_cnt,ud_cnt",
                         [('January',[{'Script':'script_name','FunctionName':'function'}],
                           {'Script':'script_name','FunctionName':'function',
                            'AverageTime':'00:01:10','Executions':5},{'Added':1,'Updates':2},13,
                            13),
                          ('February',[],None,None,0,0)])
def test_cycle_through_execution_months(gmn,log_hl,glols,grfsaf,ud,log_ln,
                                        gmn_rv,glols_rv,grfsaf_rv,ud_rv,grfsaf_cnt,ud_cnt):
    gmn.return_value = gmn_rv
    glols.return_value = glols_rv
    grfsaf.return_value = grfsaf_rv
    ud.return_value = ud_rv
    """Tests cycle_through_execution_months"""
    cycle_through_execution_months()
    assert gmn.call_count == 13
    assert log_hl.call_count == 13
    assert glols.call_count == 13
    assert grfsaf.call_count == grfsaf_cnt
    assert ud.call_count == ud_cnt
    assert log_ln.call_count == 26

@mock.patch('maintenance_script_stats.TheLogs.log_info')
@mock.patch('maintenance_script_stats.update_database')
@mock.patch('maintenance_script_stats.get_runs_for_script_and_function')
@mock.patch('maintenance_script_stats.get_list_of_logged_scripts')
@mock.patch('maintenance_script_stats.TheLogs.log_headline')
@pytest.mark.parametrize("glols_rv,grfsaf_rv,ud_rv,grfsaf_cnt,ud_cnt",
                         [([{'Script':'script_name','FunctionName':'function'}],
                           {'Script':'script_name','FunctionName':'function',
                            'AverageTime':'00:01:10','Executions':5},{'Added':1,'Updates':2},1,
                            1),
                          ([],None,None,0,0)])
def test_update_overall_stats(log_hl,glols,grfsaf,ud,log_ln,
                              glols_rv,grfsaf_rv,ud_rv,grfsaf_cnt,ud_cnt):
    """Tests update_overall_stats"""
    glols.return_value = glols_rv
    grfsaf.return_value = grfsaf_rv
    ud.return_value = ud_rv
    update_overall_stats()
    assert log_hl.call_count == 1
    assert glols.call_count == 1
    assert grfsaf.call_count == grfsaf_cnt
    assert ud.call_count == ud_cnt
    assert log_ln.call_count == 2

@mock.patch('maintenance_script_stats.TheLogs.sql_exception')
@mock.patch('maintenance_script_stats.DBQueries.select')
@pytest.mark.parametrize("sql_sel_se,sql_sel_rv,response_rv,ex_sql_cnt,fe_cnt,month",
                         [(None,[('script','function')],
                           [{'Script':'script','FunctionName':'function'}],0,0,1200),
                          (Exception,[('script','function')],[],1,1,0)])
def test_get_list_of_logged_scripts(sql_sel,ex_sql,sql_sel_se,sql_sel_rv,response_rv,ex_sql_cnt,
                                    fe_cnt,month):
    """Tests get_list_of_logged_scripts"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_list_of_logged_scripts(month)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_script_stats.TheLogs.sql_exception')
@mock.patch('maintenance_script_stats.DBQueries.select')
@pytest.mark.parametrize("sql_sel_se,response_rv,sql_sel_rv,ex_sql_cnt,fe_cnt",
                         [(Exception,{'Script':'script','FunctionName':'function',
                                      'AverageTime':None,'Executions':None},None,1,1),
                          (None,{'Script':'script','FunctionName':'function',
                                 'AverageTime':'01:01:10','Executions':1},
                                 [(time(1,1,10),),],0,0)])
def test_get_runs_for_script_and_function(sql_sel,ex_sql,
                                          sql_sel_se,response_rv,sql_sel_rv,ex_sql_cnt,fe_cnt):
    """Tests get_runs_for_script_and_function"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = get_runs_for_script_and_function('script','function','month')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert response == response_rv
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_script_stats.DBQueries.update_multiple')
@mock.patch('maintenance_script_stats.TheLogs.function_exception')
@mock.patch('maintenance_script_stats.DBQueries.insert_multiple')
@pytest.mark.parametrize("sql_im_se,sql_um_se,response_rv,sql_im_rv,sql_um_rv,ex_func_cnt,ex_cnt,month,data_dict",
                         [(None,None,{'Added':1,'Updates':2},1,2,0,0,1200,
                           {'Script':'script','FunctionName':'function','AverageTime':'00:01:10',
                            'Executions':5}),
                          (Exception,None,{'Added':0,'Updates':2},None,2,1,1,1,
                           {'Script':'script','FunctionName':'function','AverageTime':'00:01:10',
                            'Executions':5}),
                          (None,Exception,{'Added':1,'Updates':0},1,None,1,1,12,
                           {'Script':'script','FunctionName':'function','AverageTime':'00:01:10',
                            'Executions':5})])
def test_update_database(sql_im,ex_func,sql_um,sql_im_se,sql_um_se,response_rv,sql_im_rv,sql_um_rv,
                         ex_func_cnt,ex_cnt,month,data_dict):
    """Tests update_database"""
    sql_im.side_effect = sql_im_se
    sql_im.return_value = sql_im_rv
    sql_um.side_effect = sql_um_se
    sql_um.return_value = sql_um_rv
    response = update_database(month,data_dict)
    assert sql_im.call_count == 1
    assert sql_um.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.ex_cnt == ex_cnt
    assert response == response_rv
    ScrVar.ex_cnt = 0

@pytest.mark.parametrize("the_month",
                         [(0),(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12)])
def test_get_month_name(the_month):
    """Tests get_month_name"""
    months = ['January','February','March','April','May','June','July','August','September',
              'October','November','December']
    response = get_month_name(the_month)
    assert response.capitalize().split(" ",1)[0] in months
    assert datetime.today().year - 1 <= int(response.split(" ",1)[1]) <= datetime.today().year

if __name__ == '__main__':
    unittest.main()
