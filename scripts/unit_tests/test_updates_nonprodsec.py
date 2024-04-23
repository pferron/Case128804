'''Unit tests for the updates_nonprodsec script'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from updates_nonprodsec import *

@mock.patch('updates_nonprodsec.ScrVar.run_nonprodsec_updates')
def test_main(rnu):
    """Tests the main() function"""
    main()
    assert rnu.call_count == 1

@mock.patch('updates_nonprodsec.ScrVar.timed_script_teardown')
@mock.patch('updates_nonprodsec.update_knowbe4_database')
@mock.patch('updates_nonprodsec.update_bitsight_database')
@mock.patch('updates_nonprodsec.update_infosecdashboard_database')
@mock.patch('updates_nonprodsec.ScrVar.timed_script_setup')
def test_scrvar_run_nonprodsec_updates(tdd,uid,ubd,ukd,tst):
    """Tests ScrVar.run_nonprodsec_updates"""
    ScrVar.run_nonprodsec_updates()
    assert tdd.call_count == 1
    assert uid.call_count == 1
    assert ubd.call_count == 1
    assert ukd.call_count == 1
    assert tst.call_count == 1

@pytest.mark.parametrize("response_rv,fatal_count,exception_count",
                         [('Updates were successful',0,0),
                          ('Updates failed due to 1 exception(s)',1,0),
                          ('Updates failed due to 1 exception(s) and an additional 1 exception(s) occurred',1,1),
                          ('Updates were successful, but 1 exception(s) occurred',0,1)])
def test_scrvar_get_message(response_rv,fatal_count,exception_count):
    """Tests ScrVar.get_message"""
    response = ScrVar.get_message(fatal_count,exception_count)
    assert response == response_rv

@mock.patch('updates_nonprodsec.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('updates_nonprodsec.Misc.end_timer')
def test_scrvar_timed_script_teardown(et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert et.call_count == 1

@mock.patch('updates_nonprodsec.TheLogs.log_info')
@mock.patch('updates_nonprodsec.ScrVar.get_message')
@mock.patch('updates_nonprodsec.infosecdashboard_updates')
@mock.patch('updates_nonprodsec.TheLogs.log_headline')
def test_update_infosecdashboard_database(log_hl,iu,gm,log_ln):
    """Tests update_infosecdashboard_database"""
    update_infosecdashboard_database()
    assert log_hl.call_count == 1
    assert iu.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_nonprodsec.TheLogs.log_info')
@mock.patch('updates_nonprodsec.ScrVar.get_message')
@mock.patch('updates_nonprodsec.BitSight.update_all_bitsight')
@mock.patch('updates_nonprodsec.TheLogs.log_headline')
def test_update_bitsight_database(log_hl,uab,gm,log_ln):
    """Tests update_bitsight_database"""
    update_bitsight_database()
    assert log_hl.call_count == 1
    assert uab.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('updates_nonprodsec.TheLogs.log_info')
@mock.patch('updates_nonprodsec.ScrVar.get_message')
@mock.patch('updates_nonprodsec.process_knowbe4_updates')
@mock.patch('updates_nonprodsec.TheLogs.log_headline')
def test_update_knowbe4_database(log_hl,pku,gm,log_ln):
    """Tests update_knowbe4_database"""
    update_knowbe4_database()
    assert log_hl.call_count == 1
    assert pku.call_count == 1
    assert gm.call_count == 1
    assert log_ln.call_count == 1

if __name__ == '__main__':
    unittest.main()
