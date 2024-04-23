'''Unit tests for tool_mend.py '''

import unittest
from unittest import mock
import sys
import os
import pytest
from tool_mend import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('tool_mend.cmd_line_run_all')
@mock.patch('tool_mend.General.cmd_processor',
            return_value=[{'function':'cmd_line_run_all'}])
def test_main_function_only(proc_cmd,all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\tool_mend.py','cmd_line_run_all']
    with mock.patch.object(sys,"argv",testargs):
        main()
        assert proc_cmd.call_count == 1
        assert all_updates.call_count == 1

def test_scrvar_update_exception_info():
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':1})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_mend.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1

@mock.patch('tool_mend.TheLogs.process_exception_count_only')
@mock.patch('tool_mend.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('tool_mend.TheLogs.process_exception_count_only')
@mock.patch('tool_mend.do_mend_cleanup')
@mock.patch('tool_mend.process_mend_tickets')
@mock.patch('tool_mend.process_mend_findings')
@mock.patch('tool_mend.repo_mend_maintenance')
@pytest.mark.parametrize("description,rmm_cnt,peco_cnt,nightly",
                         [("nightly = False",1,2,False),
                          ("nightly = True",0,0,True)])
def test_mendrepos_onboard_single_repo(rmm,pmf,pmt,dmc,peco,
                                       description,rmm_cnt,peco_cnt,nightly):
    """Tests MendRepos.onboard_single_repo"""
    MendRepos.onboard_single_repo('repo',nightly)
    assert rmm.call_count == rmm_cnt
    assert pmf.call_count == 1
    assert pmt.call_count == 1
    assert dmc.call_count == 1
    assert peco.call_count == peco_cnt

@mock.patch('tool_mend.ScrVar.timed_script_teardown')
@mock.patch('tool_mend.MendRepos.onboard_single_repo')
@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.MendMaint.get_all_mend_repos')
@mock.patch('tool_mend.run_all_mend_maintenance')
@mock.patch('tool_mend.ScrVar.timed_script_setup')
@pytest.mark.parametrize("description,gamr_rv,osr_cnt",
                         [("All expected values",{'Results':['repo']},1),
                          ("gamr returns no repos",{'Results':[]},0)])
def test_mendrepos_run_all_mend(tss,ramm,gamr,uei,osr,tst,
                                description,gamr_rv,osr_cnt):
    """Tests MendRepos.run_all_mend"""
    gamr.return_value = gamr_rv
    MendRepos.run_all_mend()
    assert tss.call_count == 1
    assert ramm.call_count == 1
    assert gamr.call_count == 1
    assert uei.call_count ==1
    assert osr.call_count == osr_cnt
    assert tst.call_count == 1

@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.TheLogs.function_exception')
@mock.patch('tool_mend.MendMaint.all_mend_maintenance')
@mock.patch('tool_mend.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,amm_se,amm_rv,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt",
                         [("Exception: amm",1,Exception,None,1,0,1,0),
                          ("All expected values",2,None,{'FatalCount':0,'ExceptionCount':0},0,1,0,0)])
def test_run_all_mend_maintenance(log_hl,amm,ex_func,uei,
                                  description,log_hl_cnt,amm_se,amm_rv,ex_func_cnt,uei_cnt,
                                  fe_cnt,ex_cnt):
    """Tests run_all_mend_maintenance"""
    amm.side_effect = amm_se
    amm.return_value = amm_rv
    run_all_mend_maintenance(1)
    assert log_hl.call_count == log_hl_cnt
    assert amm.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_mend.MendRepos.run_all_mend')
def test_cmd_line_run_all(ram):
    """Tests cmd_line_run_all"""
    cmd_line_run_all()
    assert ram.call_count == 1

@mock.patch('tool_mend.DeletedProjects.cancel_tickets_for_deleted_projects')
@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.TheLogs.function_exception')
@mock.patch('tool_mend.MendMaint.all_mend_maintenance')
@mock.patch('tool_mend.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,amm_se,ex_func_cnt,uei_cnt,ctfdp_cnt,fe_cnt,ex_cnt",
                         [("Exception: amm",1,Exception,1,0,0,1,0),
                          ("All expected values",2,None,0,2,1,0,0)])
def test_repo_mend_maintenance(log_hl,amm,ex_func,uei,ctfdp,
                               description,log_hl_cnt,amm_se,ex_func_cnt,uei_cnt,ctfdp_cnt,
                               fe_cnt,ex_cnt):
    """Tests repo_mend_maintenance"""
    amm.side_effect = amm_se
    repo_mend_maintenance('repo',1)
    assert log_hl.call_count == log_hl_cnt
    assert amm.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert ctfdp.call_count == ctfdp_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.TheLogs.function_exception')
@mock.patch('tool_mend.MendReports.single_repo_updates')
@mock.patch('tool_mend.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,sru_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt",
                         [("Exception: sru",1,Exception,1,0,1,0),
                          ("All expected values",2,None,0,1,0,0)])
def test_process_mend_findings(log_hl,sru,ex_func,uei,
                               description,log_hl_cnt,sru_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt):
    """Tests process_mend_findings"""
    sru.side_effect = sru_se
    process_mend_findings('repo',1)
    assert log_hl.call_count == log_hl_cnt
    assert sru.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.TheLogs.function_exception')
@mock.patch('tool_mend.MendTickets.single_repo_ticketing')
@mock.patch('tool_mend.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,srt_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt",
                         [("Exception: srt",1,Exception,1,0,1,0),
                          ("All expected values",2,None,0,1,0,0)])
def test_process_mend_tickets(log_hl,srt,ex_func,uei,
                              description,log_hl_cnt,srt_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt):
    """Tests process_mend_tickets"""
    srt.side_effect = srt_se
    process_mend_tickets('repo',1)
    assert log_hl.call_count == log_hl_cnt
    assert srt.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('tool_mend.ScrVar.update_exception_info')
@mock.patch('tool_mend.TheLogs.function_exception')
@mock.patch('tool_mend.MendSync.single_repo_updates')
@mock.patch('tool_mend.TheLogs.log_headline')
@pytest.mark.parametrize("description,log_hl_cnt,sru_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt",
                         [("Exception: sru",1,Exception,1,0,1,0),
                          ("All expected values",2,None,0,1,0,0)])
def test_do_mend_cleanup(log_hl,sru,ex_func,uei,
                         description,log_hl_cnt,sru_se,ex_func_cnt,uei_cnt,fe_cnt,ex_cnt):
    """Tests do_mend_cleanup"""
    sru.side_effect = sru_se
    do_mend_cleanup('repo',1)
    assert log_hl.call_count == log_hl_cnt
    assert sru.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
