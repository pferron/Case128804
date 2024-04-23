'''Unit tests for the nonprodsec_bitsight script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from nonprodsec_bitsight import *

@mock.patch('nonprodsec_bitsight.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('nonprodsec_bitsight.Misc.end_timer')
@mock.patch('nonprodsec_bitsight.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('nonprodsec_bitsight.ScrVar.timed_script_teardown')
@mock.patch('nonprodsec_bitsight.update_bitsight_progholdings')
@mock.patch('nonprodsec_bitsight.update_bitsight_rating_details')
@mock.patch('nonprodsec_bitsight.update_bitsight_inventory')
@mock.patch('nonprodsec_bitsight.ScrVar.timed_script_setup')
def test_bitsight_update_all_bitsight(tss,ubi,ubrd,ubp,tst):
    """Tests BitSight.update_all_bitsight"""
    BitSight.update_all_bitsight()
    assert tss.call_count == 1
    assert ubi.call_count == 1
    assert ubrd.call_count == 1
    assert ubp.call_count == 1
    assert tst.call_count == 1

@mock.patch('nonprodsec_bitsight.TheLogs.log_info')
@mock.patch('nonprodsec_bitsight.DBQueries.insert_into_table')
@mock.patch('nonprodsec_bitsight.DBQueries.clear_table')
@mock.patch('nonprodsec_bitsight.TheLogs.function_exception')
@mock.patch('nonprodsec_bitsight.BitSightAPI.fetch_companies')
@mock.patch('nonprodsec_bitsight.TheLogs.log_headline')
@pytest.mark.parametrize("description,fc_se,fc_rv,ct_se,ct_rv,ct_cnt,iit_se,iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,fe_cnt",
                         [('All calls successful',None,'a list of dictionaries',None,True,1,None,1,
                           1,0,1,0),
                          ('Exception: BitSightAPI.fetch_companies',Exception,None,None,None,0,
                           None,0,0,1,0,1),
                          ('Exception: DBQueries.clear_table',None,'a list of dictionaries',
                           Exception,None,1,None,0,0,1,0,1),
                          ('Exception: DBQueries.insert_into_table',None,'a list of dictionaries',
                           None,True,1,Exception,None,1,1,0,1)])
def test_update_bitsight_inventory(log_hl,fc,ex_func,ct,iit,log_ln,description,fc_se,fc_rv,ct_se,
                                   ct_rv,ct_cnt,iit_se,iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,
                                   fe_cnt):
    """Tests update_bitsight_inventory"""
    fc.side_effect = fc_se
    fc.return_valut = fc_rv
    ct.side_effect = ct_se
    ct.return_value = ct_rv
    iit.side_effect = iit_se
    iit.return_value = iit_rv
    update_bitsight_inventory()
    assert log_hl.call_count == 1
    assert fc.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert ct.call_count == ct_cnt
    assert iit.call_count == iit_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('nonprodsec_bitsight.TheLogs.log_info')
@mock.patch('nonprodsec_bitsight.DBQueries.insert_into_table')
@mock.patch('nonprodsec_bitsight.BitSightAPI.fetch_ratings_details')
@mock.patch('nonprodsec_bitsight.DBQueries.clear_table')
@mock.patch('nonprodsec_bitsight.TheLogs.function_exception')
@mock.patch('nonprodsec_bitsight.DBQueries.ratings_details_available')
@mock.patch('nonprodsec_bitsight.TheLogs.log_headline')
@pytest.mark.parametrize("description,rda_se,rda_rv,ct_se,ct_rv,ct_cnt,frd_se,frd_rv,frd_cnt,iit_se,iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,fe_cnt",
                         [('All calls successful',None,'rda_rv',None,True,1,None,'frd_rv',1,None,
                           'iit_rv',1,0,1,0),
                          ('Exception: DBQueries.ratings_details_available',Exception,None,None,
                           None,0,None,None,0,None,None,0,1,0,1),
                          ('Exception: DBQueries.clear_table',None,'rda_rv',Exception,None,1,None,
                           None,0,None,None,0,1,0,1),
                          ('DBQueries.clear_table = False',None,'rda_rv',None,False,1,None,None,0,
                           None,None,0,0,1,0),
                          ('Exception: BitSightAPI.fetch_ratings_details',None,'rda_rv',None,True,
                           1,Exception,None,1,None,None,0,1,0,1),
                          ('BitSightAPI.fetch_ratings_details = None',None,'rda_rv',None,True,1,
                           None,None,1,None,None,0,0,1,0),
                          ('Exception: DBQueries.insert_into_table',None,'rda_rv',None,True,1,None,
                           'frd_rv',1,Exception,None,1,1,0,1)])
def test_update_bitsight_rating_details(log_hl,rda,ex_func,ct,frd,iit,log_ln,description,
                                        rda_se,rda_rv,ct_se,ct_rv,ct_cnt,frd_se,frd_rv,frd_cnt,
                                        iit_se,iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,fe_cnt):
    """Tests update_bitsight_rating_details"""
    rda.side_effect = rda_se
    rda.return_value = rda_rv
    ct.side_effect = ct_se
    ct.return_value = ct_rv
    frd.side_effect = frd_se
    frd.return_value = frd_rv
    iit.side_effect = iit_se
    iit.return_value = iit_rv
    update_bitsight_rating_details()
    assert log_hl.call_count == 1
    assert rda.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert ct.call_count == ct_cnt
    assert frd.call_count == frd_cnt
    assert iit.call_count == iit_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('nonprodsec_bitsight.TheLogs.log_info')
@mock.patch('nonprodsec_bitsight.DBQueries.insert_into_table')
@mock.patch('nonprodsec_bitsight.BitSightAPI.fetch_prog_holdings')
@mock.patch('nonprodsec_bitsight.DBQueries.clear_table')
@mock.patch('nonprodsec_bitsight.TheLogs.function_exception')
@mock.patch('nonprodsec_bitsight.DBQueries.get_watchlist')
@mock.patch('nonprodsec_bitsight.TheLogs.log_headline')
@pytest.mark.parametrize("description,gw_se,gw_rv,ct_se,ct_rv,ct_cnt,fph_se,fph_rv,fph_cnt,iit_se,iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,fe_cnt",
                         [('All calls successful',None,'gw_rv',None,True,1,None,'fph_rv',1,None,
                           'iit_rv',1,0,1,0),
                          ('Exception: DBQueries.get_watchlist',Exception,None,None,None,0,None,
                           None,0,None,None,0,1,0,1),
                          ('Exception: DBQueries.clear_table',None,'gw_rv',Exception,None,1,None,
                           None,0,None,None,0,1,0,1),
                          ('Exception: BitSightAPI.fetch_prog_holdings',None,'gw_rv',None,True,1,
                           Exception,None,1,None,None,0,1,0,1),
                          ('Exception: DBQueries.insert_into_table',None,'gw_rv',None,True,1,None,
                           'fph_rv',1,Exception,None,1,1,0,1),
                          ('DBQueries.get_watchlist = None',None,None,None,None,0,None,None,0,None,
                           None,0,0,1,0),
                          ('DBQueries.clear_table = False',None,'gw_rv',None,False,1,None,None,0,
                           None,None,0,0,1,0),
                          ('BitSightAPI.fetch_prog_holdings = None',None,'gw_rv',None,True,1,None,
                           None,1,None,None,0,0,1,0)])
def test_update_bitsight_progholdings(log_hl,gw,ex_func,ct,fph,iit,log_ln,description,
                                      gw_se,gw_rv,ct_se,ct_rv,ct_cnt,fph_se,fph_rv,fph_cnt,iit_se,
                                      iit_rv,iit_cnt,ex_func_cnt,log_ln_cnt,fe_cnt):
    """Tests update_bitsight_progholdings"""
    gw.side_effect = gw_se
    gw.return_value = gw_rv
    ct.side_effect = ct_se
    ct.return_value = ct_rv
    fph.side_effect = fph_se
    fph.return_value = fph_rv
    iit.side_effect = iit_se
    iit.return_value == iit_rv
    update_bitsight_progholdings()
    assert log_hl.call_count == 1
    assert gw.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert ct.call_count == ct_cnt
    assert fph.call_count == fph_cnt
    assert iit.call_count == iit_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('nonprodsec_bitsight.TheLogs.log_info')
@mock.patch('nonprodsec_bitsight.DBQueries.no_score_change')
@mock.patch('nonprodsec_bitsight.DBQueries.update_score_change')
@mock.patch('nonprodsec_bitsight.DBQueries.insert_into_table')
@mock.patch('nonprodsec_bitsight.DBQueries.clear_table')
@mock.patch('nonprodsec_bitsight.General.combine_dictionaries_in_list_of_dictionaries')
@mock.patch('nonprodsec_bitsight.BitSightAPI.fetch_previous_scores')
@mock.patch('nonprodsec_bitsight.TheLogs.function_exception')
@mock.patch('nonprodsec_bitsight.BitSightAPI.fetch_current_scores')
@mock.patch('nonprodsec_bitsight.TheLogs.log_headline')
@pytest.mark.parametrize("description,fcs_se,fcs_rv,fps_se,fps_rv,fps_cnt,cdilod_se,cdilod_rv,cdilod_cnt,ct_se,ct_rv,ct_cnt,iit_se,iit_rv,iit_cnt,usc_se,usc_rv,usc_cnt,nsc_se,nsc_rv,nsc_cnt,ex_func_cnt,log_ln_cnt,fe_cnt",
                         [('BitSightAPI.fetch_current_scores = None',None,None,None,None,0,None,
                           None,0,None,None,0,None,None,0,None,None,0,None,None,0,0,1,0),
                          ('BitSightAPI.fetch_previous_scores = None',None,'fcs_rv',None,None,1,
                           None,None,0,None,None,0,None,None,0,None,None,0,None,None,0,0,1,0),
                          ('General.combine_dictionaries_in_list_of_dictionaries = []',None,
                           'fcs_rv',None,'fps_rv',1,None,[],1,None,None,0,None,None,0,None,None,0,
                           None,None,0,0,1,0),
                          ('clear_table = False',None,'fcs_rv',None,'fps_rv',1,None,'cdilod_rv',1,
                           None,False,1,None,None,0,None,None,0,None,None,0,0,1,0),
                          ('DBQueries.insert_into_table = 0',None,'fcs_rv',None,'fps_rv',1,None,
                           'cdilod_rv',1,None,True,1,None,0,1,None,None,0,None,None,0,0,1,0),
                          ('All calls successful',None,'fcs_rv',None,'fps_rv',1,None,'cdilod_rv',1,
                           None,True,1,None,'iit_rv',1,None,'usc_rv',1,None,'nsc_rv',1,0,1,0),
                          ('Exception: BitSightAPI.fetch_current_scores',Exception,None,None,None,
                           0,None,None,0,None,None,0,None,None,0,None,None,0,None,None,0,1,0,1),
                          ('Exception: BitSightAPI.fetch_previous_scores',None,'fcs_rv',Exception,
                           None,1,None,None,0,None,None,0,None,None,0,None,None,0,None,None,0,1,0,1),
                          ('Exception: General.combine_dictionaries_in_list_of_dictionaries',None,
                           'fcs_rv',None,'fps_rv',1,Exception,None,1,None,None,0,None,None,0,None,
                           None,0,None,None,0,1,0,1),
                          ('Exception: clear_table',None,'fcs_rv',None,'fps_rv',1,None,'cdilod_rv',
                           1,Exception,None,1,None,None,0,None,None,0,None,None,0,1,0,1),
                          ('Exception: DBQueries.insert_into_table',None,'fcs_rv',None,'fps_rv',1,
                           None,'cdilod_rv',1,None,True,1,Exception,None,1,None,None,0,None,None,0,
                           1,0,1),
                          ('Exception: DBQueries.update_score_change',None,'fcs_rv',None,'fps_rv',
                           1,None,'cdilod_rv',1,None,True,1,None,'iit_rv',1,Exception,None,1,None,
                           'nsc_rv',1,1,1,1),
                          ('Exception: DBQueries.no_score_change',None,'fcs_rv',None,'fps_rv',1,
                           None,'cdilod_rv',1,None,True,1,None,'iit_rv',1,None,'usc_rv',1,
                           Exception,None,1,1,1,1)])
def test_update_bitsight_score_changes(log_hl,fcs,ex_func,fps,cdilod,ct,iit,usc,nsc,log_ln,description,
                                       fcs_se,fcs_rv,fps_se,fps_rv,fps_cnt,cdilod_se,cdilod_rv,
                                       cdilod_cnt,ct_se,ct_rv,ct_cnt,iit_se,iit_rv,iit_cnt,usc_se,
                                       usc_rv,usc_cnt,nsc_se,nsc_rv,nsc_cnt,ex_func_cnt,
                                       log_ln_cnt,fe_cnt):
    """Tests update_bitsight_score_changes"""
    fcs.side_effect = fcs_se
    fcs.return_value = fcs_rv
    fps.side_effect = fps_se
    fps.return_value = fps_rv
    cdilod.side_effect = cdilod_se
    cdilod.return_value = cdilod_rv
    ct.side_effect = ct_se
    ct.return_value = ct_rv
    iit.side_effect = iit_se
    iit.return_value = iit_rv
    usc.side_effect = usc_se
    usc.return_value = usc_rv
    nsc.side_effect = nsc_se
    nsc.return_value = nsc_rv
    update_bitsight_score_changes()
    assert log_hl.call_count == 1
    assert fcs.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert fps.call_count == fps_cnt
    assert cdilod.call_count == cdilod_cnt
    assert ct.call_count == ct_cnt
    assert iit.call_count == iit_cnt
    assert usc.call_count == usc_cnt
    assert nsc.call_count == nsc_cnt
    assert log_ln.call_count == log_ln_cnt
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

if __name__ == '__main__':
    unittest.main()
