'''Unit tests for the maintenance_checkmarx script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from maintenance_checkmarx import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch.object(General,'cmd_processor',
                   return_value=[{'function': 'run_checkmarx_maintenance'}])
@mock.patch("maintenance_checkmarx.run_checkmarx_maintenance")
def test_main_with_args(cmd_mock,run_mock):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_checkmarx.py',
                'run_checkmarx_maintenance']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        assert cmd_mock.call_count == 1
        assert run_mock.call_count == 1

def test_scrvar_update_exception_info():
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_checkmarx.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.CxAPI.checkmarx_availability',
            return_value=True)
def test_scrvar_get_cx_availability(cx_avail,l_hl,ex_func):
    """Tests ScrVar.get_cx_availability"""
    avail = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 0
    assert ex_func.call_count == 0
    assert avail is True

@mock.patch('maintenance_checkmarx.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.CxAPI.checkmarx_availability',
            side_effect=Exception)
def test_scrvar_get_cx_availability_ex_001(cx_avail,l_hl,ex_func):
    """Tests ScrVar.get_cx_availability"""
    avail = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 0
    assert ex_func.call_count == 1
    assert ScrVar.fe_cnt == 1
    assert avail is False
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_checkmarx.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.CxAPI.checkmarx_availability',
            return_value=False)
def test_scrvar_get_cx_availability_ex_002(cx_avail,l_hl,ex_func):
    """Tests ScrVar.get_cx_availability"""
    avail = ScrVar.get_cx_availability('appsec-ops',10915)
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 1
    assert ex_func.call_count == 1
    assert ScrVar.fe_cnt == 1
    assert avail is False
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_checkmarx.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.ScrVar.get_cx_availability',
            return_value=True)
@mock.patch('maintenance_checkmarx.Misc.start_timer')
def test_scrvar_timed_script_setup(s_timer,cx_avail,l_hl,ex_func):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 0
    assert ex_func.call_count == 0

@mock.patch('maintenance_checkmarx.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.ScrVar.get_cx_availability',
            return_value=False)
@mock.patch('maintenance_checkmarx.Misc.start_timer')
def test_scrvar_timed_script_setup_cx_down(s_timer,cx_avail,l_hl,ex_func):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert s_timer.call_count == 1
    assert cx_avail.call_count == 1
    assert l_hl.call_count == 1
    assert ex_func.call_count == 1

@mock.patch('maintenance_checkmarx.TheLogs.process_exception_count_only')
@mock.patch('maintenance_checkmarx.Misc.end_timer')
def test_scrvar_timed_script_teardown(e_timer,proc_ex):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert e_timer.call_count == 1
    assert proc_ex.call_count == 2

@mock.patch('maintenance_checkmarx.CxMaint.update_project_details',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('maintenance_checkmarx.CxMaint.update_baseline_projects',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('maintenance_checkmarx.CxMaint.update_sastprojects_details',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('maintenance_checkmarx.CxMaint.update_created_baseline_projects',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':True})
@mock.patch('maintenance_checkmarx.CxCreate.run_all',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':['slug']})
@mock.patch('maintenance_checkmarx.ScrVar.timed_script_teardown')
@mock.patch('maintenance_checkmarx.ScrVar.update_exception_info')
@mock.patch('maintenance_checkmarx.CxMaint.base_sastprojects_updates',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':True})
@mock.patch('maintenance_checkmarx.TheLogs.log_headline')
@mock.patch('maintenance_checkmarx.ScrVar.timed_script_setup')
def test_run_checkmarx_maintenance(s_timer,l_hl,u_base,u_ex_info,e_timer,create,u_created,u_sast,
                                   u_blp,u_pd):
    """Tests run_checkmarx_maintenance"""
    response = run_checkmarx_maintenance()
    assert s_timer.call_count == 1
    assert l_hl.call_count == 4
    assert u_base.call_count == 1
    assert u_ex_info.call_count == 6
    assert e_timer.call_count == 1
    assert create.call_count == 1
    assert u_created.call_count == 1
    assert u_sast.call_count == 1
    assert u_blp.call_count == 1
    assert u_pd.call_count == 1

if __name__ == '__main__':
    unittest.main()
