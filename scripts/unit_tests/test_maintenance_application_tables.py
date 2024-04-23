'''Unit tests for the maintenance_application_tables script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maintenance_application_tables import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maintenance_application_tables.update_all_application_tables')
@mock.patch('maintenance_application_tables.General.cmd_processor',
            return_value=[{'function':'update_all_application_tables'}])
def test_main_function_only(proc_cmd,all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_application_tables.py','update_all_application_tables']
    with mock.patch.object(sys,"argv",testargs):
        main()
        assert proc_cmd.call_count == 1
        assert all_updates.call_count == 1

@pytest.mark.parametrize("description,fe_cnt,ex_cnt,dictionary",
                         [("dictionary is None",0,0,None),
                          ("dictionary has FatalCount only",1,0,{'FatalCount':1}),
                          ("dictionary has ExceptionCount only",0,1,{'ExceptionCount':1}),
                          ("dictionary has both FatalCount and ExceptionCount",1,2,{'FatalCount':1,'ExceptionCount':2}),
                          ("dictionary has neither expected key",0,0,{'Key':'Value'})])
def test_scrvar_update_exception_info(description,fe_cnt,ex_cnt,dictionary):
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info(dictionary)
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.Misc.start_timer')
def tests_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('maintenance_application_tables.Misc.end_timer')
@mock.patch('maintenance_application_tables.TheLogs.process_exception_count_only')
def tests_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('maintenance_application_tables.ScrVar.timed_script_teardown')
@mock.patch('maintenance_application_tables.applications_table_sync')
@mock.patch('maintenance_application_tables.progteam_info_sync')
@mock.patch('maintenance_application_tables.set_jira_project_name')
@mock.patch('maintenance_application_tables.set_security_finding_status')
@mock.patch('maintenance_application_tables.get_jira_from_progteams')
@mock.patch('maintenance_application_tables.bitbucket_updates')
@mock.patch('maintenance_application_tables.ScrVar.timed_script_setup')
def test_update_all_application_tables(tss,bu,gjfp,ssfs,sjpn,pis,ats,tst):
    """Tests update_all_application_tables"""
    update_all_application_tables()
    assert tss.call_count == 1
    assert bu.call_count == 1
    assert gjfp.call_count == 1
    assert ssfs.call_count == 1
    assert sjpn.call_count == 1
    assert pis.call_count == 1
    assert ats.call_count == 1
    assert tst.call_count == 1

@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.Alerts.manual_alert')
@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.BitBucket.update_bitbucket')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@pytest.mark.parametrize("description,ub_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("ub_rv['AddedRepos'] = []",{'UpdatedRepos':1,'AddedRepos':[]},2,None,None,0,0,0,0),
                          ("All expected values",{'UpdatedRepos':1,'AddedRepos':['repo']},3,None,1,1,0,0,0),
                          ("Exception: ma_rv = 0",{'UpdatedRepos':1,'AddedRepos':['repo']},3,None,0,1,1,0,1),
                          ("Exception: ma",{'UpdatedRepos':1,'AddedRepos':['repo']},3,Exception,None,1,1,0,1)])
def test_bitbucket_updates(log_hl,ub,uei,log_ln,ma,ex_func,
                           description,ub_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,
                           ex_func_cnt,fe_cnt,ex_cnt):
    """Tests bitbucket_updates"""
    ub.return_value = ub_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    bitbucket_updates()
    assert log_hl.call_count == 1
    assert ub.call_count == 1
    assert uei.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.DBQueries.update_multiple')
@mock.patch('maintenance_application_tables.AppQueries.get_jira_keys_for_team')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.AppQueries.get_available_progteam_jira_updates')
@pytest.mark.parametrize("description,gapju_rv,uei_cnt,log_hl_cnt,gjkft_rv,gjkft_cnt,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("gapju['Results'] = []",{'Results':[]},1,0,None,0,None,0,0,0,0),
                          ("gjkft['Results'] = []",{'Results':[('repo','progteam',),]},2,1,{'Results':[]},1,None,1,0,0,0),
                          ("All expected values",{'Results':[('repo','progteam',),]},2,1,{'Results':[('KEY','KEY-123',),]},1,None,1,0,0,0),
                          ("Exception: um",{'Results':[('repo','progteam',),]},2,1,{'Results':[('KEY','KEY-123',),]},1,Exception,1,1,1,0)])
def test_get_jira_from_progteams(gapju,uei,log_hl,gjkft,um,ex_func,log_ln,
                                 description,gapju_rv,uei_cnt,log_hl_cnt,gjkft_rv,gjkft_cnt,
                                 um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt):
    """Tests get_jira_from_progteams"""
    gapju.return_value = gapju_rv
    gjkft.return_value = gjkft_rv
    um.side_effect = um_se
    get_jira_from_progteams()
    assert gapju.call_count == 1
    assert uei.call_count == uei_cnt
    assert log_hl.call_count == log_hl_cnt
    assert gjkft.call_count == gjkft_cnt
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.GeneralTicketing.verify_security_finding_type')
@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.DBQueries.update_multiple')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.AppQueries.get_applicationautomation_jira_project_keys')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@pytest.mark.parametrize("description,gaajpk_rv,um_se,um_cnt,ex_func_cnt,vsft_se,vsft_rv,vsft_cnt,fe_cnt,ex_cnt",
                         [("gaajpk['Results'] = []",{'Results':[]},None,0,0,None,None,0,0,0),
                          ("vsft = False",{'Results':[('KEY',),]},None,2,0,None,False,1,0,0),
                          ("All expected values",{'Results':[('KEY',),]},None,2,0,None,True,1,0,0),
                          ("Exception: um",{'Results':[('KEY',),]},Exception,2,2,None,True,1,1,1),
                          ("Exception: vsft",{'Results':[('KEY',),]},None,2,1,Exception,None,1,0,1)])
def test_set_security_finding_status(log_hl,gaajpk,uei,um,ex_func,vsft,log_ln,
                                     description,gaajpk_rv,um_se,um_cnt,ex_func_cnt,vsft_se,
                                     vsft_rv,vsft_cnt,fe_cnt,ex_cnt):
    """Tests set_security_finding_status"""
    gaajpk.return_value = gaajpk_rv
    um.side_effect = um_se
    vsft.side_effect = vsft_se
    vsft.return_value = vsft_rv
    set_security_finding_status()
    assert log_hl.call_count == 1
    assert gaajpk.call_count == 1
    assert uei.call_count == 1
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert vsft.call_count == vsft_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.DBQueries.update_multiple')
@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.GeneralTicketing.get_project_name')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.AppQueries.get_applicationautomation_jira_project_keys')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@pytest.mark.parametrize("description,gaajpk_rv,gpn_se,gpn_rv,gpn_cnt,ex_func_cnt,um_se,um_cnt,fe_cnt,ex_cnt",
                         [("gaajpk['Results'] = []",{'Results':[]},None,None,0,0,None,0,0,0),
                          ("gpk = None",{'Results':[('KEY',),]},None,None,1,0,None,1,0,0),
                          ("All expected values",{'Results':[('KEY',),]},None,'proj_name',1,0,None,1,0,0),
                          ("Exception: gpk",{'Results':[('KEY',),]},Exception,None,1,1,None,1,0,1),
                          ("Exception: um",{'Results':[('KEY',),]},None,'proj_name',1,1,Exception,1,1,0)])
def test_set_jira_project_name(log_hl,gaajpk,uei,gpn,ex_func,um,log_ln,
                               description,gaajpk_rv,gpn_se,gpn_rv,gpn_cnt,ex_func_cnt,
                               um_se,um_cnt,fe_cnt,ex_cnt):
    """Tests set_jira_project_name"""
    gaajpk.return_value = gaajpk_rv
    gpn.side_effect = gpn_se
    gpn.return_value = gpn_rv
    um.side_effect = um_se
    set_jira_project_name()
    assert log_hl.call_count == 1
    assert gaajpk.call_count == 1
    assert uei.call_count == 1
    assert gpn.call_count == gpn_cnt
    assert ex_func.call_count == ex_func_cnt
    assert um.call_count == um_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.DBQueries.update_multiple')
@mock.patch('maintenance_application_tables.AppQueries.get_progteams_teams')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.AppQueries.get_applicationautomation_jira_project_keys')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@pytest.mark.parametrize("description,gaajpk_rv,uei_cnt,gpt_rv,gpt_cnt,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("gaajpk['Results'] = []",{'Results':[]},1,None,0,None,0,0,0,0),
                          ("gpt['Results'] = []",{'Results':[('KEY',),]},2,{'Results':[]},1,None,1,0,0,0),
                          ("All expected values",{'Results':[('KEY',),]},2,{'Results':[('name','lead','owner',),]},1,None,1,0,0,0),
                          ("Exception: um",{'Results':[('KEY',),]},2,{'Results':[('name','lead','owner',),]},1,Exception,1,1,1,0)])
def test_progteam_info_sync(log_hl,gaajpk,uei,gpt,um,ex_func,log_ln,
                            description,gaajpk_rv,uei_cnt,gpt_rv,gpt_cnt,um_se,um_cnt,ex_func_cnt,
                            fe_cnt,ex_cnt):
    """Tests progteam_info_sync"""
    gaajpk.return_value = gaajpk_rv
    gpt.return_value = gpt_rv
    um.side_effect = um_se
    progteam_info_sync()
    assert log_hl.call_count == 1
    assert gaajpk.call_count == 1
    assert uei.call_count == uei_cnt
    assert gpt.call_count == gpt_cnt
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_application_tables.TheLogs.log_info')
@mock.patch('maintenance_application_tables.TheLogs.function_exception')
@mock.patch('maintenance_application_tables.DBQueries.update_multiple')
@mock.patch('maintenance_application_tables.ScrVar.update_exception_info')
@mock.patch('maintenance_application_tables.AppQueries.get_applicationautomation_data')
@mock.patch('maintenance_application_tables.TheLogs.log_headline')
@pytest.mark.parametrize("description,gaad_rv,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("gaad['Results'] = []",{'Results':[]},None,0,0,0,0),
                          ("All expected values",{'Results':[('repo','sft','pid','lsi','lsd','tdb','sae','ca','po','tl','wa','wpt','wlu','vtdb','ltdb','wtdb','ret','mr',),]},None,1,0,0,0),
                          ("Exception: um",{'Results':[('repo','sft','pid','lsi','lsd','tdb','sae','ca','po','tl','wa','wpt','wlu','vtdb','ltdb','wtdb','ret','mr',),]},Exception,1,1,1,0)])
def test_applications_table_sync(log_hl,gaad,uei,um,ex_func,log_ln,
                                 description,gaad_rv,um_se,um_cnt,ex_func_cnt,fe_cnt,ex_cnt):
    """Tests applications_table_sync"""
    gaad.return_value = gaad_rv
    um.side_effect = um_se
    applications_table_sync()
    assert log_hl.call_count == 1
    assert gaad.call_count == 1
    assert uei.call_count == 1
    assert um.call_count == um_cnt
    assert ex_func.call_count == ex_func_cnt
    assert log_ln.call_count == 1
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
