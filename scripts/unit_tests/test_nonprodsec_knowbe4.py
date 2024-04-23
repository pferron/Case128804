'''Unit tests for the nonprodsec_knowbe4 script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from nonprodsec_knowbe4 import *

@mock.patch('nonprodsec_knowbe4.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('nonprodsec_knowbe4.Misc.end_timer')
@mock.patch('nonprodsec_knowbe4.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@pytest.mark.parametrize("description,dictionary,fe_cnt,ex_cnt",
                         [('dictionary with FatalCount > 0, ExceptionCount > 0',
                           {'FatalCount':1,'ExceptionCount':2},1,2),
                          ('dictionary with FatalCount > 0, ExceptionCount = 0',
                           {'FatalCount':1,'ExceptionCount':0},1,0),
                          ('dictionary with FatalCount = 0, ExceptionCount > 0',
                           {'FatalCount':0,'ExceptionCount':1},0,1),
                          ('dictionary with FatalCount = 0, ExceptionCount = 0',
                           {'FatalCount':0,'ExceptionCount':0},0,0),
                          ('dictionary missing FatalCount and ExceptionCount',
                           {'SomeKey':'SomeValue'},0,0),
                          ('dictionary with FatalCount only',
                           {'FatalCount':1},1,0),
                          ('dictionary with ExceptionCount only',
                           {'ExceptionCount':2},0,2),
                          ('dictionary with non-int values',
                           {'FatalCount':{},'ExceptionCount':'a string'},0,0),
                          ('dictionary passed through as None',
                           None,0,0),
                          ('dictionary passed through as a str',
                           'A string',0,0),
                          ('dictionary passed through as an int',
                           1,0,0)])
def test_scrvar_update_exception_info(description,dictionary,fe_cnt,ex_cnt):
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info(dictionary)
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.get_all_users')
@pytest.mark.parametrize("description,gau_se,gau_cnt,ex_func_cnt,fe_cnt,ex_cnt,list_of_dicts",
                         [('Successfully runs the function',None,1,0,0,0,[{'function':'get_all_users','args':[2,'active']}]),
                          ('Exception: cmd processing',None,0,1,1,0,[{'fucntion':'get_all_users','args':[2,'active']}])])
def test_scrvar_repeat_function(gau,ex_func,
                    description,gau_se,gau_cnt,ex_func_cnt,fe_cnt,ex_cnt,list_of_dicts):
    """Tests ScrVar.repeat_function"""
    gau.side_effect == gau_se
    ScrVar.repeat_function(list_of_dicts)
    assert gau.call_count == gau_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.TheLogs.log_info')
@mock.patch('nonprodsec_knowbe4.DBQueries.insert_multiple')
@mock.patch('nonprodsec_knowbe4.ScrVar.update_exception_info')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.KB4API.get_user_groups')
@mock.patch('nonprodsec_knowbe4.time.sleep')
@pytest.mark.parametrize("description,gug_se,gug_rv,ex_func_cnt,uei_cnt,im_se,im_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,{'Results':[{'HasResults':True}]},0,1,None,1,1,0,0),
                          ("gug['Results'] = []",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("gug['Results'] = 'not_a_list'",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("Exception: gug",Exception,None,1,0,None,0,0,1,0),
                          ('Exception: im',None,{'Results':[{'HasResults':True}]},1,1,Exception,1,0,1,0)])
def test_kb4updates_get_all_user_groups(sleep,gug,ex_func,uei,im,log_ln,
                                        description,gug_se,gug_rv,ex_func_cnt,uei_cnt,im_se,im_cnt,
                                        log_ln_cnt,fe_cnt,ex_cnt):
    """KB4Updates.get_all_user_groups"""
    gug.side_effect = gug_se
    gug.return_value = gug_rv
    im.side_effect = im_se
    KB4Updates.get_all_user_groups()
    assert sleep.call_count == 1
    assert gug.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert im.call_count == im_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.TheLogs.log_info')
@mock.patch('nonprodsec_knowbe4.DBQueries.insert_multiple')
@mock.patch('nonprodsec_knowbe4.ScrVar.update_exception_info')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.KB4API.get_training_campaigns')
@mock.patch('nonprodsec_knowbe4.time.sleep')
@pytest.mark.parametrize("description,gtc_se,gtc_rv,ex_func_cnt,uei_cnt,im_se,im_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,{'Results':[{'HasResults':True}]},0,1,None,1,1,0,0),
                          ("gtc['Results'] = []",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("gtc['Results'] = 'not_a_list'",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("Exception: gtc",Exception,None,1,0,None,0,0,1,0),
                          ('Exception: im',None,{'Results':[{'HasResults':True}]},1,1,Exception,1,0,1,0)])
def test_kb4updates_get_all_training_campaigns(sleep,gtc,ex_func,uei,im,log_ln,
                                               description,gtc_se,gtc_rv,ex_func_cnt,uei_cnt,im_se,
                                               im_cnt,log_ln_cnt,fe_cnt,ex_cnt):
    """Tests KB4Updates.get_all_training_campaigns"""
    gtc.side_effect = gtc_se
    gtc.return_value = gtc_rv
    im.side_effect = im_se
    KB4Updates.get_all_training_campaigns()
    assert sleep.call_count == 1
    assert gtc.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert im.call_count == im_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.TheLogs.log_info')
@mock.patch('nonprodsec_knowbe4.DBQueries.insert_multiple')
@mock.patch('nonprodsec_knowbe4.ScrVar.update_exception_info')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.KB4API.get_phishing_campaigns')
@mock.patch('nonprodsec_knowbe4.time.sleep')
@pytest.mark.parametrize("description,gpc_se,gpc_rv,ex_func_cnt,uei_cnt,im_se,im_cnt,log_ln_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,{'Results':[{'HasResults':True}]},0,1,None,1,1,0,0),
                          ("gpc['Results'] = []",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("gpc['Results'] = 'not_a_list'",None,{'Results':[]},0,1,None,0,1,0,0),
                          ("Exception: gpc",Exception,None,1,0,None,0,0,1,0),
                          ('Exception: im',None,{'Results':[{'HasResults':True}]},1,1,Exception,1,0,1,0)])
def test_kb4updates_get_all_phishing_campaigns(sleep,gpc,ex_func,uei,im,log_ln,
                                               description,gpc_se,gpc_rv,ex_func_cnt,uei_cnt,im_se,
                                               im_cnt,log_ln_cnt,fe_cnt,ex_cnt):
    """Tests KB4Updates.get_all_phishing_campaigns"""
    gpc.side_effect = gpc_se
    gpc.return_value = gpc_rv
    im.side_effect = im_se
    KB4Updates.get_all_phishing_campaigns()
    assert sleep.call_count == 1
    assert gpc.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert im.call_count == im_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.ScrVar.timed_script_teardown')
@mock.patch('nonprodsec_knowbe4.update_phishing_campaigns')
@mock.patch('nonprodsec_knowbe4.update_training_campaigns')
@mock.patch('nonprodsec_knowbe4.update_user_groups')
@mock.patch('nonprodsec_knowbe4.update_inactive_users')
@mock.patch('nonprodsec_knowbe4.update_active_users')
@mock.patch('nonprodsec_knowbe4.ScrVar.timed_script_setup')
@pytest.mark.parametrize("description,dotw,uiu_cnt",
                         [('Sunday updates:','Sunday',1),
                          ('Monday updates:','Monday',0),
                          ('Tuesday updates:','Tuesday',0),
                          ('Wednesday updates:','Wednesday',0),
                          ('Thursday updates:','Thursday',0),
                          ('Friday updates:','Friday',0),
                          ('Saturday updates:','Saturday',0)])
def test_process_knowbe4_updates(tss,uau,uiu,uug,utc,upc,tst,
                                 description,dotw,uiu_cnt):
    """Tests process_knowbe4_updates"""
    ScrVar.today = dotw
    response = process_knowbe4_updates()
    assert tss.call_count == 1
    assert uau.call_count == 1
    assert uiu.call_count == uiu_cnt
    assert uug.call_count == 1
    assert utc.call_count == 1
    assert upc.call_count == 1
    assert tst.call_count == 1
    assert response == {'FatalCount':0,'ExceptionCount':0}

@mock.patch('nonprodsec_knowbe4.get_all_users')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.DBQueries.clear_table')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_headline')
@pytest.mark.parametrize("description,ct_se,ex_func_cnt,gau_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,0,1,0,0),
                          ('Exception: ct',Exception,1,0,1,0)])
def test_update_active_users(log_hl,ct,ex_func,gau,
                             description,ct_se,ex_func_cnt,gau_cnt,fe_cnt,ex_cnt):
    """Tests update_active_users"""
    ct.side_effect = ct_se
    update_active_users()
    assert log_hl.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gau.call_count == gau_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.get_all_users')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.DBQueries.clear_table')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_headline')
@pytest.mark.parametrize("description,ct_se,ex_func_cnt,gau_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,0,1,0,0),
                          ('Exception: ct',Exception,1,0,1,0)])
def test_update_inactive_users(log_hl,ct,ex_func,gau,
                             description,ct_se,ex_func_cnt,gau_cnt,fe_cnt,ex_cnt):
    """Tests update_inactive_users"""
    ct.side_effect = ct_se
    update_inactive_users()
    assert log_hl.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gau.call_count == gau_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.KB4Updates.get_all_user_groups')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.DBQueries.clear_table')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_headline')
@pytest.mark.parametrize("description,ct_se,ex_func_cnt,gaug_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,0,1,0,0),
                          ('Exception: ct',Exception,1,0,1,0)])
def test_update_user_groups(log_hl,ct,ex_func,gaug,
                             description,ct_se,ex_func_cnt,gaug_cnt,fe_cnt,ex_cnt):
    """Tests update_user_groups"""
    ct.side_effect = ct_se
    update_user_groups()
    assert log_hl.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gaug.call_count == gaug_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.KB4Updates.get_all_training_campaigns')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.DBQueries.clear_table')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_headline')
@pytest.mark.parametrize("description,ct_se,ex_func_cnt,gatc_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,0,1,0,0),
                          ('Exception: ct',Exception,1,0,1,0)])
def test_update_training_campaigns(log_hl,ct,ex_func,gatc,
                             description,ct_se,ex_func_cnt,gatc_cnt,fe_cnt,ex_cnt):
    """Tests update_training_campaigns"""
    ct.side_effect = ct_se
    update_training_campaigns()
    assert log_hl.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gatc.call_count == gatc_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.KB4Updates.get_all_phishing_campaigns')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.DBQueries.clear_table')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_headline')
@pytest.mark.parametrize("description,ct_se,ex_func_cnt,gapc_cnt,fe_cnt,ex_cnt",
                         [('All expected values',None,0,1,0,0),
                          ('Exception: ct',Exception,1,0,1,0)])
def test_update_phishing_campaigns(log_hl,ct,ex_func,gapc,
                             description,ct_se,ex_func_cnt,gapc_cnt,fe_cnt,ex_cnt):
    """Tests update_phishing_campaigns"""
    ct.side_effect = ct_se
    update_phishing_campaigns()
    assert log_hl.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert gapc.call_count == gapc_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('nonprodsec_knowbe4.ScrVar.repeat_function')
@mock.patch('nonprodsec_knowbe4.TheLogs.log_info')
@mock.patch('nonprodsec_knowbe4.DBQueries.insert_multiple')
@mock.patch('nonprodsec_knowbe4.ScrVar.update_exception_info')
@mock.patch('nonprodsec_knowbe4.TheLogs.function_exception')
@mock.patch('nonprodsec_knowbe4.KB4API.get_users')
@mock.patch('nonprodsec_knowbe4.time.sleep')
@pytest.mark.parametrize("description,gu_se,gu_items,ex_func_cnt,uei_cnt,im_se,im_cnt,log_ln_cnt,rf_cnt,fe_cnt,ex_cnt,status",
                         [('All expected values, run rf',None,500,0,1,None,1,0,1,0,0,'active'),
                          ('All expected values, log_info',None,499,0,1,None,1,1,0,0,0,'archived'),
                          ('Exception: gu',Exception,1,1,0,None,0,0,0,1,0,'active'),
                          ('Exception: im',None,1,1,1,Exception,1,0,0,1,0,'archived')])
def test_get_all_users(sleep,gu,ex_func,uei,im,log_ln,rf,
                       description,gu_se,gu_items,ex_func_cnt,uei_cnt,im_se,im_cnt,log_ln_cnt,
                       rf_cnt,fe_cnt,ex_cnt,status):
    """Tests get_all_users"""
    gu_rv = []
    while len(gu_rv) < gu_items:
        gu_rv.append({'key':'value'})
    gu_rv = {'Results':gu_rv,'UserCount':gu_items}
    gu.side_effect = gu_se
    gu.return_value = gu_rv
    im.side_effect = im_se
    get_all_users(1,status)
    assert sleep.call_count == 1
    assert gu.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert uei.call_count == uei_cnt
    assert im.call_count == im_cnt
    assert log_ln.call_count == log_ln_cnt
    assert rf.call_count == rf_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

if __name__ == '__main__':
    unittest.main()
