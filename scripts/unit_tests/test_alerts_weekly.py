'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from alerts_weekly import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('alerts_weekly.verify_sf_exists')
@mock.patch('alerts_weekly.General.cmd_processor',
            return_value=[{'function':'verify_sf_exists'}])
def test_main_function_only(proc_cmd,all_updates):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_weekly.py','verify_sf_exists']
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

@mock.patch('alerts_weekly.Misc.start_timer')
def tests_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('alerts_weekly.Misc.end_timer')
@mock.patch('alerts_weekly.TheLogs.process_exception_count_only')
def tests_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('alerts_weekly.ScrVar.timed_script_teardown')
@mock.patch('alerts_weekly.overdue_cx_baseline_scans')
@mock.patch('alerts_weekly.missing_cx_baseline_scans')
@mock.patch('alerts_weekly.missing_sf_ticket_type')
@mock.patch('alerts_weekly.missing_jira_info')
@mock.patch('alerts_weekly.ScrVar.timed_script_setup')
def test_weeklyalerts_process_all_alerts(tss,mji,mstt,mcbs,ocbs,tst):
    """Tests WeeklyAlerts.process_all_alerts"""
    WeeklyAlerts.process_all_alerts()
    assert tss.call_count == 1
    assert mji.call_count == 1
    assert mstt.call_count == 1
    assert mcbs.call_count == 1
    assert ocbs.call_count == 1
    assert tst.call_count == 1

@mock.patch('alerts_weekly.TheLogs.log_info')
@mock.patch('alerts_weekly.DBQueries.update_multiple')
@mock.patch('alerts_weekly.TheLogs.function_exception')
@mock.patch('alerts_weekly.GeneralTicketing.has_sf_ticket_type')
@mock.patch('alerts_weekly.ScrVar.update_exception_info')
@mock.patch('alerts_weekly.WADatabase.get_unique_jira_keys')
@mock.patch('alerts_weekly.TheLogs.log_headline')
@pytest.mark.parametrize("description,gujk_rv,hstt_se,hstt_rv,hstt_cnt,ex_func_cnt,um_se,fe_cnt,ex_cnt",
                         [("All values expected",{'Results':['KEY']},None,1,1,0,None,0,0),
                          ("Exception: hstt",{'Results':['KEY']},Exception,None,1,1,None,0,1),
                          ("Exception: um",{'Results':['KEY']},None,1,1,2,Exception,0,2)])
def test_verify_sf_exists(log_hl,gujk,uei,hstt,ex_func,um,log_ln,
                          description,gujk_rv,hstt_se,hstt_rv,hstt_cnt,ex_func_cnt,um_se,fe_cnt,
                          ex_cnt):
    """Tests verify_sf_exists"""
    gujk.return_value = gujk_rv
    hstt.side_effect = hstt_se
    hstt.return_value = hstt_rv
    um.side_effect = um_se
    verify_sf_exists()
    assert log_hl.call_count == 1
    assert gujk.call_count == 1
    assert uei.call_count == 1
    assert hstt.call_count == hstt_cnt
    assert ex_func.call_count == ex_func_cnt
    assert um.call_count == 2
    assert log_ln.call_count == 2
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('alerts_weekly.TheLogs.function_exception')
@mock.patch('alerts_weekly.Alerts.manual_alert')
@mock.patch('alerts_weekly.TheLogs.log_info')
@mock.patch('alerts_weekly.ScrVar.update_exception_info')
@mock.patch('alerts_weekly.WADatabase.get_repos_missing_jira_info')
@mock.patch('alerts_weekly.TheLogs.log_headline')
@pytest.mark.parametrize("description,grmji_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("All expected values",{'Results':['repo']},1,None,1,1,0,0,0),
                          ("grmji_rv['Results'] = []",{'Results':[]},1,None,None,0,0,0,0),
                          ("ma_rv = 0",{'Results':['repo']},0,None,0,1,1,1,0),
                          ("Exception: ma",{'Results':['repo']},0,Exception,None,1,1,1,0)])
def test_missing_jira_info(log_hl,grmji,uei,log_ln,ma,ex_func,
                           description,grmji_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,
                           ex_cnt):
    """Tests missing_jira_info"""
    grmji.return_value = grmji_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    missing_jira_info()
    assert log_hl.call_count == 1
    assert grmji.call_count == 1
    assert uei.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('alerts_weekly.TheLogs.function_exception')
@mock.patch('alerts_weekly.Alerts.manual_alert')
@mock.patch('alerts_weekly.TheLogs.log_info')
@mock.patch('alerts_weekly.ScrVar.update_exception_info')
@mock.patch('alerts_weekly.WADatabase.get_projects_missing_security_finding_type')
@mock.patch('alerts_weekly.TheLogs.log_headline')
@mock.patch('alerts_weekly.verify_sf_exists')
@pytest.mark.parametrize("description,gpmsft_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("All expected values",{'Results':['repo (KEY)']},1,None,1,1,0,0,0),
                          ("grmji_rv['Results'] = []",{'Results':[]},1,None,None,0,0,0,0),
                          ("ma_rv = 0",{'Results':['repo (KEY)']},0,None,0,1,1,1,0),
                          ("Exception: ma",{'Results':['repo (KEY)']},0,Exception,None,1,1,1,0)])
def test_missing_sf_ticket_type(vse,log_hl,gpmsft,uei,log_ln,ma,ex_func,
                                description,gpmsft_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,
                                fe_cnt,ex_cnt):
    """Tests missing_sf_ticket_type"""
    gpmsft.return_value = gpmsft_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    missing_sf_ticket_type()
    assert vse.call_count == 1
    assert log_hl.call_count == 1
    assert gpmsft.call_count == 1
    assert uei.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('alerts_weekly.TheLogs.function_exception')
@mock.patch('alerts_weekly.Alerts.manual_alert')
@mock.patch('alerts_weekly.TheLogs.log_info')
@mock.patch('alerts_weekly.ScrVar.update_exception_info')
@mock.patch('alerts_weekly.WADatabase.get_missing_baseline_scans')
@mock.patch('alerts_weekly.TheLogs.log_headline')
@pytest.mark.parametrize("description,gmbs_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("All expected values",{'Results':['repo']},1,None,1,1,0,0,0),
                          ("gmbs_rv['Results'] = []",{'Results':[]},1,None,None,0,0,0,0),
                          ("ma_rv = 0",{'Results':['repo']},0,None,0,1,1,1,0),
                          ("Exception: ma",{'Results':['repo']},0,Exception,None,1,1,1,0)])
def test_missing_cx_baseline_scans(log_hl,gmbs,uei,log_ln,ma,ex_func,
                           description,gmbs_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,
                           ex_cnt):
    """Tests missing_cx_baseline_scans"""
    gmbs.return_value = gmbs_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    missing_cx_baseline_scans()
    assert log_hl.call_count == 1
    assert gmbs.call_count == 1
    assert uei.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('alerts_weekly.TheLogs.function_exception')
@mock.patch('alerts_weekly.Alerts.manual_alert')
@mock.patch('alerts_weekly.TheLogs.log_info')
@mock.patch('alerts_weekly.ScrVar.update_exception_info')
@mock.patch('alerts_weekly.WADatabase.get_baselines_with_overdue_scans')
@mock.patch('alerts_weekly.TheLogs.log_headline')
@pytest.mark.parametrize("description,gbwos_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,ex_cnt",
                         [("All expected values",{'Results':'slack_headers:Repo\\Last Scan Date\n...','Count':1},1,None,1,1,0,0,0),
                          ("grmji_rv['Results'] = []",{'Results':None},1,None,None,0,0,0,0),
                          ("ma_rv = 0",{'Results':'slack_headers:Repo\\Last Scan Date\n...','Count':1},0,None,0,1,1,1,0),
                          ("Exception: ma",{'Results':'slack_headers:Repo\\Last Scan Date\n...','Count':1},0,Exception,None,1,1,1,0)])
def test_overdue_cx_baseline_scans(log_hl,gbwos,uei,log_ln,ma,ex_func,
                           description,gbwos_rv,log_ln_cnt,ma_se,ma_rv,ma_cnt,ex_func_cnt,fe_cnt,
                           ex_cnt):
    """Tests overdue_cx_baseline_scans"""
    gbwos.return_value = gbwos_rv
    ma.side_effect = ma_se
    ma.return_value = ma_rv
    overdue_cx_baseline_scans()
    assert log_hl.call_count == 1
    assert gbwos.call_count == 1
    assert uei.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ma.call_count == ma_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
