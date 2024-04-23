'''Unit tests for the maintenance_checkmarx_license_check script'''

import unittest
from unittest import mock
from datetime import time,datetime
import sys
import os
import pytest
from maintenance_checkmarx_license_check import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('maintenance_checkmarx_license_check.verify_checkmarx_license')
@mock.patch('maintenance_checkmarx_license_check.General.cmd_processor')
@pytest.mark.parametrize("description,cp_rv,run_func",
                         [('Function with args',[{'function':'verify_checkmarx_license','args':[1]}],"verify_checkmarx_license(1)"),
                          ('Function without args',[{'function':'verify_checkmarx_license'}],"verify_checkmarx_license")])
def test_main(cp,vcl,description,cp_rv,run_func):
    '''Tests main'''
    testargs = [r'c:\AppSec\scripts\\maintenance_checkmarx_license_check.py',run_func]
    with mock.patch.object(sys, "argv", testargs):
        cp.return_value = cp_rv
        main()
        assert cp.call_count == 1
        assert vcl.call_count == 1

@pytest.mark.parametrize("description,dictionary,fe_cnt,ex_cnt",
                         [('dictionary with FatalCount = 1, ExceptionCount = 2',{'FatalCount':1,'ExceptionCount':2},1,2),
                          ('dictionary with FatalCount = 1, ExceptionCount = 0',{'FatalCount':1,'ExceptionCount':0},1,0),
                          ('dictionary with FatalCount = 0, ExceptionCount = 2',{'FatalCount':0,'ExceptionCount':2},0,2),
                          ('dictionary with no FatalCount and no ExceptionCount',{},0,0)])
def test_scrvar_update_exception_info(description,dictionary,fe_cnt,ex_cnt):
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info(dictionary)
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('maintenance_checkmarx_license_check.Misc.start_timer')
def test_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('maintenance_checkmarx_license_check.Misc.end_timer')
@mock.patch('maintenance_checkmarx_license_check.TheLogs.process_exception_count_only')
def test_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('maintenance_checkmarx_license_check.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx_license_check.ScrVar.update_exception_info')
@mock.patch('maintenance_checkmarx_license_check.copy_from_cx_server')
@pytest.mark.parametrize("description,cfcs_se,response_rv,cfcs_rv,uei_cnt,ex_func_cnt,fe_cnt",
                         [('cfcs is True',None,True,{'FatalCount':0,'ExceptionCount':0,'IsCopied':True},1,0,0),
                          ('cfcs is False',None,False,{'FatalCount':0,'ExceptionCount':0,'IsCopied':False},1,0,0),
                          ('Exception: cfcs',Exception,False,None,0,1,1)])
def test_scriptsteps_copy_hid_and_license(cfcs,uei,ex_func,description,
                                          cfcs_se,response_rv,cfcs_rv,uei_cnt,ex_func_cnt,fe_cnt):
    """Tests ScriptSteps.copy_hid_and_license"""
    cfcs.side_effect = cfcs_se
    cfcs.return_value = cfcs_rv
    response = ScriptSteps.copy_hid_and_license()
    assert cfcs.call_count == 1
    assert uei.call_count == uei_cnt
    assert ex_func.call_count == ex_func_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_checkmarx_license_check.TheLogs.function_exception')
@mock.patch('maintenance_checkmarx_license_check.ScrVar.update_exception_info')
@mock.patch('maintenance_checkmarx_license_check.checkmarx_license_check')
@pytest.mark.parametrize("description,clc_se,response_rv,clc_rv,uei_cnt,ex_func_cnt,fe_cnt",
                         [('License match success',None,True,{'FatalCount':0,'ExceptionCount':0,'Success':True},1,0,0),
                          ('License match failure',None,False,{'FatalCount':0,'ExceptionCount':0,'Success':False},1,0,0),
                          ('Exception: clc',Exception,False,None,0,1,1)])
def test_scriptsteps_hid_and_license_comparison(clc,uei,ex_func,description,
                                                clc_se,response_rv,clc_rv,uei_cnt,ex_func_cnt,fe_cnt):
    """Tests ScriptSteps.hid_and_license_comparison"""
    clc.side_effect = clc_se
    clc.return_value = clc_rv
    response = ScriptSteps.hid_and_license_comparison()
    assert clc.call_count == 1
    assert uei.call_count == uei_cnt
    assert ex_func.call_count == ex_func_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    ScrVar.fe_cnt = 0

@mock.patch('maintenance_checkmarx_license_check.ScrVar.timed_script_teardown')
@mock.patch('maintenance_checkmarx_license_check.ScriptSteps.hid_and_license_comparison')
@mock.patch('maintenance_checkmarx_license_check.ScriptSteps.copy_hid_and_license')
@mock.patch('maintenance_checkmarx_license_check.ScrVar.timed_script_setup')
@pytest.mark.parametrize("description,chal_rv,halc_cnt",
                         [('chal is False',False,0),
                          ('chal is True',True,1)])
def test_verify_checkmarx_license(tss,chal,halc,tst,description,chal_rv,halc_cnt):
    """Test verify_checkmarx_license"""
    chal.return_value = chal_rv
    response = verify_checkmarx_license()
    assert tss.call_count == 1
    assert chal.call_count == 1
    assert halc.call_count == halc_cnt
    assert tst.call_count == 1
    assert response == {'FatalCount':0,'ExceptionCount':0}

if __name__ == '__main__':
    unittest.main()
