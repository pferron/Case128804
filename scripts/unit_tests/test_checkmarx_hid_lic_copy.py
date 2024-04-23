"Unit tests for the checkmarx.hid_lic_copy script"

import unittest
from unittest import mock
from datetime import time,datetime
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from checkmarx.hid_lic_copy import *

@mock.patch('checkmarx.hid_lic_copy.TheLogs.function_exception')
@mock.patch('checkmarx.hid_lic_copy.TheLogs.log_info')
@mock.patch('checkmarx.hid_lic_copy.smbclient.shutil.copyfile')
@pytest.mark.parametrize("cf_se,response_rv,log_ln_cnt,ex_func_cnt,fe_cnt",
                         [(None,'success',1,0,0),
                          (Exception,'fail',0,1,1)])
def test_copy_file(cf,log_ln,ex_func,cf_se,response_rv,log_ln_cnt,ex_func_cnt,fe_cnt):
    cf.side_effect = cf_se
    response = copy_file('source', 'destination')
    assert cf.call_count == 1
    assert log_ln.call_count == log_ln_cnt
    assert ex_func.call_count == ex_func_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert response == response_rv
    ScrVar.fe_cnt = 0

@mock.patch('checkmarx.hid_lic_copy.copy_file')
@mock.patch('checkmarx.hid_lic_copy.TheLogs.log_headline')
@pytest.mark.parametrize("cf_rv",
                         [('success'),
                          ('fail')])
def test_copy_from_cx_server(log_hl,cf,cf_rv):
    """Tests copy_from_cx_server"""
    cf.return_value = cf_rv
    copy_from_cx_server()
    assert log_hl.call_count == 2
    assert cf.call_count == 2