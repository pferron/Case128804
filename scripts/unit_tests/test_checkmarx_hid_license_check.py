from checkmarx.hid_license_check import *
from unittest import mock
import pytest
import sys
import os
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@pytest.fixture(scope="module")
def mock_response_200():
    '''fixture to mock Slack response'''
    response = mock.MagicMock()
    response.status_code = 200
    return response

@pytest.fixture(scope="module")
def mock_response_400():
    '''fixture to mock Slack response'''
    response = mock.MagicMock()
    response.status_code = 400
    response.body = 'response body'
    return response

@mock.patch("checkmarx.hid_license_check.hid_mismatch_slack_send")
@mock.patch("checkmarx.hid_license_check.lic_hid_compare")
@mock.patch("checkmarx.hid_license_check.read_license_file")
@mock.patch("checkmarx.hid_license_check.read_hid_file")
@mock.patch.object(TheLogs, "log_headline")
def test_checkmarx_license_check_no_match(log_mock, read_hid_mock, read_lic_mock, hid_compare_mock, slack_mock):
    '''test hid check when hid and license hid do not match'''
    hid_compare_mock.return_value = False
    checkmarx_license_check()
    assert log_mock.call_count == 2
    read_hid_mock.assert_called_once()
    read_lic_mock.assert_called_once()
    hid_compare_mock.assert_called_once()
    slack_mock.assert_called_once()

@mock.patch("checkmarx.hid_license_check.lic_hid_compare")
@mock.patch("checkmarx.hid_license_check.read_license_file")
@mock.patch("checkmarx.hid_license_check.read_hid_file")
@mock.patch.object(TheLogs, "log_headline")
def test_checkmarx_license_check_matches(log_mock, read_hid_mock, read_lic_mock, hid_compare_mock):
    '''test hid check when hid and license hid match'''
    hid_compare_mock.return_value = True
    checkmarx_license_check()
    assert log_mock.call_count == 2
    read_hid_mock.assert_called_once()
    read_lic_mock.assert_called_once()

@mock.patch("checkmarx.hid_license_check.lic_hid_compare")
@mock.patch("checkmarx.hid_license_check.read_license_file")
@mock.patch("checkmarx.hid_license_check.read_hid_file")
@mock.patch.object(TheLogs, "log_headline")
def test_checkmarx_license_check_matches_with_fe(log_mock, read_hid_mock, read_lic_mock, hid_compare_mock):
    '''test hid check when hid and license hid match'''
    ScrVar.fe_cnt = 1
    hid_compare_mock.return_value = True
    checkmarx_license_check()
    assert log_mock.call_count == 2
    read_hid_mock.assert_called_once()
    read_lic_mock.assert_called_once()
    assert ScrVar.fe_cnt == 1
    ScrVar.fe_cnt = 0

@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="#2962603912311611063739_0000:0000:0000:0000:24576:64:10:10")
def test_read_hid_file(mock_file):
    res = read_hid_file()
    assert open("path/to/open").read() == "#2962603912311611063739_0000:0000:0000:0000:24576:64:10:10"
    mock_file.assert_called_with("path/to/open")
    assert res == "2962603912311611063739"

@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="adfasdf, H I D = # 2 9 6 2 6 0 3 9 1 2 3 1 1 6 1 1 0 6 3 7 3 8")
def test_read_license_file(mock_file):
    res = read_license_file()
    assert open("path/to/open").read() == "adfasdf, H I D = # 2 9 6 2 6 0 3 9 1 2 3 1 1 6 1 1 0 6 3 7 3 8"
    mock_file.assert_called_with("path/to/open")
    assert res == "2962603912311611063738"

@mock.patch.object(TheLogs, "log_info")
def test_lic_hid_compare_true(log_mock):
    license = '12345'
    hid = '12345'
    res = lic_hid_compare(hid, license)
    log_mock.assert_called_once()
    assert res == True

@mock.patch.object(TheLogs, "log_info")
def test_lic_hid_compare_false(log_mock):
    license = '12345'
    hid = '456789'
    res = lic_hid_compare(hid, license)
    log_mock.assert_called_once()
    assert res == False

@mock.patch("checkmarx.hid_license_check.WebhookClient.send")
@mock.patch.object(TheLogs, "log_info")
def test_hid_mismatch_slack_send_200(log_mock, webhook_client_mock, mock_response_200):
    webhook_client_mock.return_value = mock_response_200
    hid_mismatch_slack_send('hid','license')
    webhook_client_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("checkmarx.hid_license_check.WebhookClient.send")
@mock.patch.object(TheLogs, "function_exception")
def test_hid_mismatch_slack_send_400(log_mock, webhook_client_mock, mock_response_400):
    webhook_client_mock.return_value = mock_response_400
    hid_mismatch_slack_send('hid','license')
    webhook_client_mock.assert_called_once()
    log_mock.assert_called_once()
