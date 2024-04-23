'''Unit tests for the nightly_updates script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from updates_nightly import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.run_nightly_updates')
def test_main(log_mock,run_mock):
    """Tests the main() function"""
    main()
    assert log_mock.call_count == 1
    assert run_mock.call_count == 1

@mock.patch('updates_nightly.ScrVar.timed_script_teardown')
@mock.patch('updates_nightly.send_slack_alerts_for_failed_runs')
@mock.patch('updates_nightly.process_os_reports_and_tickets')
@mock.patch('updates_nightly.process_sast_reports_and_tickets')
@mock.patch('updates_nightly.update_sastprojects')
@mock.patch('updates_nightly.update_jiraissues_table')
@mock.patch('updates_nightly.backup_the_database')
@mock.patch('updates_nightly.ScrVar.timed_script_setup')
@pytest.mark.parametrize("hostname,btd_rv,ujt_rv,us_rv,btd_cnt,ujt_cnt,us_cnt,psrat_cnt,porat_cnt,ssaffr_cnt",
                         [('slc-prdappcmx01',False,None,None,1,0,0,0,0,0),
                          ('slc-prdappcmx01',True,True,0,1,2,1,1,1,1),
                          ('slc-prdappcmx01',True,False,None,1,1,0,0,0,0),
                          ('slc-prdappcmx01',True,True,1,1,2,1,0,1,1)])
def test_scrvar_run_nightly_updates(tss,btd,ujt,us,psrat,porat,ssaffr,tst,hostname,btd_rv,ujt_rv,
                                    us_rv,btd_cnt,ujt_cnt,us_cnt,psrat_cnt,porat_cnt,ssaffr_cnt):
    """Tests run_nightly_updates"""
    btd.return_value = btd_rv
    ujt.return_value = ujt_rv
    us.return_value = us_rv
    with mock.patch("socket.gethostname",return_value=hostname):
        ScrVar.run_nightly_updates( )
    assert tss.call_count == 1
    assert btd.call_count == btd_cnt
    assert ujt.call_count == ujt_cnt
    assert us.call_count == us_cnt
    assert psrat.call_count == psrat_cnt
    assert porat.call_count == porat_cnt
    assert ssaffr.call_count == ssaffr_cnt
    assert tst.call_count == 1

@pytest.mark.parametrize("fatal_count,exception_count,step,msg_expected",
                         [(0,0,1,"Database backups were successful"),
                          (0,1,1,"Database backups were successful, but 1 exception(s) occurred"),
                          (1,1,1,"Database backups failed due to 1 fatal exception(s)"),
                          (0,0,2,"JiraIssues successfully updated"),
                          (0,1,2,"JiraIssues successfully updated, but 1 exception(s) occurred"),
                          (1,1,2,"Updates to JiraIssues failed due to 1 fatal exception(s)"),
                          (0,0,3,"Checkmarx maintenance successfully completed"),
                          (0,1,3,"Checkmarx maintenance successfully completed, but 1 exception(s) occurred"),
                          (1,1,3,"Checkmarx maintenance failed due to 1 fatal exception(s)"),
                          (0,0,4,"SAST findings successfully processed"),
                          (0,1,4,"SAST findings successfully processed, but 1 exception(s) occurred"),
                          (1,1,4,"Processing of SAST findings failed due to 1 fatal exception(s)"),
                          (0,0,5,"Open source findings successfully processed"),
                          (0,1,5,"Open source findings successfully processed, but 1 exception(s) occurred"),
                          (1,1,5,"Processing of open source findings failed due to 1 fatal exception(s)")])
def test_scrvar_get_message(fatal_count,exception_count,step,msg_expected):
    """Tests ScrVar.get_message"""
    response = ScrVar.get_message(fatal_count,exception_count,step)
    assert response == msg_expected

@pytest.mark.parametrize("dictionary,fe_cnt,ex_cnt",
                         [({'FatalCount':1,'ExceptionCount':2},1,2),
                          ({},0,0)])
def tests_scrvar_update_exception_info(dictionary,fe_cnt,ex_cnt):
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info(dictionary)
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('updates_nightly.Misc.start_timer')
def tests_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('updates_nightly.Misc.end_timer')
@mock.patch('updates_nightly.TheLogs.process_exception_count_only')
def tests_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.get_message')
@mock.patch('updates_nightly.ScrVar.update_exception_info')
@mock.patch('updates_nightly.backup_databases')
@mock.patch('updates_nightly.TheLogs.log_headline')
@pytest.mark.parametrize("bd_rv,response",
                         [({'FatalCount':0,'ExceptionCount':0},True),
                          ({'FatalCount':1,'ExceptionCount':0},False)])
def test_backup_the_database(log_hl,bd,uei,gm,log_ln,bd_rv,response):
    """Tests backup_the_database"""
    bd.return_value = bd_rv
    response = backup_the_database()
    assert log_hl.call_count == 1
    assert bd.call_count == 1
    assert uei.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count ==1
    assert response == response

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.get_message')
@mock.patch('updates_nightly.ScrVar.update_exception_info')
@mock.patch('updates_nightly.update_all_jira_issues')
@mock.patch('updates_nightly.TheLogs.log_headline')
@pytest.mark.parametrize("uaji_rv,response",
                         [({'FatalCount':0,'ExceptionCount':0},True),
                          ({'FatalCount':1,'ExceptionCount':0},False)])
def test_update_jiraissues_table(log_hl,uaji,uei,gm,log_ln,uaji_rv,response):
    """Tests update_jiraissues_table"""
    uaji.return_value = uaji_rv
    response = update_jiraissues_table()
    assert log_hl.call_count == 1
    assert uaji.call_count == 1
    assert uei.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count ==1
    assert response == response

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.get_message')
@mock.patch('updates_nightly.ScrVar.update_exception_info')
@mock.patch('updates_nightly.run_checkmarx_maintenance')
@mock.patch('updates_nightly.TheLogs.log_headline')
@pytest.mark.parametrize("rcm_rv,response",
                         [({'FatalCount':0,'ExceptionCount':0},0),
                          ({'FatalCount':1,'ExceptionCount':0},1)])
def test_update_sastprojects(log_hl,rcm,uei,gm,log_ln,rcm_rv,response):
    """Tests update_sastprojects"""
    rcm.return_value = rcm_rv
    response = update_sastprojects()
    assert log_hl.call_count == 1
    assert rcm.call_count == 1
    assert uei.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count ==1
    assert response == response

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.get_message')
@mock.patch('updates_nightly.ScrVar.update_exception_info')
@mock.patch('updates_nightly.all_cx_updates')
@mock.patch('updates_nightly.TheLogs.log_headline')
def test_process_sast_reports_and_tickets(log_hl,acu,uei,gm,log_ln):
    """Tests process_sast_reports_and_tickets"""
    process_sast_reports_and_tickets()
    assert log_hl.call_count == 1
    assert acu.call_count == 1
    assert uei.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_nightly.TheLogs.log_info')
@mock.patch('updates_nightly.ScrVar.get_message')
@mock.patch('updates_nightly.ScrVar.update_exception_info')
@mock.patch('updates_nightly.MendRepos.run_all_mend')
@mock.patch('updates_nightly.TheLogs.log_headline')
def test_process_os_reports_and_tickets(log_hl,ram,uei,gm,log_ln):
    """Tests process_os_reports_and_tickets"""
    process_os_reports_and_tickets()
    assert log_hl.call_count == 1
    assert ram.call_count == 1
    assert uei.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_nightly.TheLogs.function_exception')
@mock.patch('updates_nightly.alert_on_failed_runs')
@pytest.mark.parametrize("aofr_se,ex_func_cnt",
                         [(None,0),
                          (Exception,1)])
def test_send_slack_alerts_for_failed_runs(aofr,ex_func,aofr_se,ex_func_cnt):
    """Tests send_slack_alerts_for_failed_runs"""
    aofr.side_effect = aofr_se
    send_slack_alerts_for_failed_runs()
    assert aofr.call_count == 1
    assert ex_func.call_count == ex_func_cnt

if __name__ == '__main__':
    unittest.main()
