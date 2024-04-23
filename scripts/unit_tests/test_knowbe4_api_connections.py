'''Unit tests for the nonprodsec_knowbe4 script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from knowbe4.api_connections import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_users_success(g_data,f_except):
    """Tests KB4API.get_users"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'employee_number': 'num','id':'id','first_name': 'fn',
                                    'last_name':'ln','job_title': 'jt','email': 'email',
                                    'location': 'loc', 'division': 'div','organization': 'org',
                                    'department': 'dept','manager_name': 'mn','manager_email':
                                    'me','phish_prone_percentage': 'num','current_risk_score':
                                    'num'}]
    g_data.return_value = resp_mock
    KB4API.get_users(1,'active')
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_users_status_code_failure(g_data,f_except):
    """Tests KB4API.get_users"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = []
    g_data.return_value = resp_mock
    KB4API.get_users(1,'active')
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get",
            side_effect=Exception)
def test_kb4api_get_users_status_exception_gu001(g_data,f_except):
    """Tests KB4API.get_users"""
    KB4API.get_users(1,'active')
    assert g_data.call_count == 1
    assert f_except.call_count == 1

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_user_groups_success(g_data,f_except):
    """Tests KB4API.get_user_groups"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':'id','name': 'name','member_count':'num',
                                    'current_risk_score': 'num'}]
    g_data.return_value = resp_mock
    KB4API.get_user_groups()
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_user_groups_status_code_failure(g_data,f_except):
    """Tests KB4API.get_user_groups"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = []
    g_data.return_value = resp_mock
    KB4API.get_user_groups()
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get",
            side_effect=Exception)
def test_kb4api_get_user_groups_exception_gug001(g_data,f_except):
    """Tests KB4API.get_user_groups"""
    KB4API.get_user_groups()
    assert g_data.call_count == 1
    assert f_except.call_count == 1

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_training_campaigns_success(g_data,f_except):
    """Tests KB4API.get_training_campaigns"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'campaign_id':'id','name':'name','status':'status',
                                    'duration_type':'type','start_date': '2023-07-31T12:12:12.121',
                                    'end_date': '2023-07-31T12:12:12.121','relative_duration':'dur',
                                    'auto_enroll':'ae','allow_multiple_enrollments':'ame',
                                    'completion_percentage':'pct'}]
    g_data.return_value = resp_mock
    KB4API.get_training_campaigns()
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_training_campaigns_status_code_failure(g_data,f_except):
    """Tests KB4API.get_training_campaigns"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = []
    g_data.return_value = resp_mock
    KB4API.get_training_campaigns()
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get",
            side_effect=Exception)
def test_kb4api_get_training_campaigns_exception_gtc001(g_data,f_except):
    """Tests KB4API.get_training_campaigns"""
    KB4API.get_training_campaigns()
    assert g_data.call_count == 1
    assert f_except.call_count == 1

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.KB4API.get_campaign_stats",
            return_value={'Results':{'scheduled_count':1,'delivered_count':2,'opened_count':3,
                                    'clicked_count':4,'replied_count':5,'attachment_open_count':6,
                                    'macro_enabled_count':7,'data_entered_count':8,
                                    'reported_count':9,'bounced_count':10}})
@mock.patch("knowbe4.api_connections.requests.get")
@mock.patch("knowbe4.api_connections.time.sleep")
def test_kb4api_get_phishing_campaigns_success(slp,g_data,g_stats,f_except):
    """Tests KB4API.get_phishing_campaigns"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'campaign_id':'id',
                                    'name':'name','groups':[{'name':'name'}],
                                    'last_run':'2023-07-31T12:12:12.121',
                                    'last_phish_prone_percentage':'pct','status':'status',
                                    'hidden':'hidden','psts_count':'cnt','send_duration':'dur',
                                    'track_duration':'dur','frequency':'frequency','create_date':
                                    '2023-07-31T12:12:12.121','difficulty_filter':['diff'],
                                    'psts':[{'pst_id':'id'}]}]
    g_data.return_value = resp_mock
    KB4API.get_phishing_campaigns()
    assert g_data.call_count == 1
    assert g_stats.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.KB4API.get_campaign_stats")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_phishing_campaigns_status_code_failure(g_data,g_stats,f_except):
    """Tests KB4API.get_phishing_campaigns"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = []
    g_data.return_value = resp_mock
    KB4API.get_phishing_campaigns()
    assert g_data.call_count == 1
    assert g_stats.call_count == 0
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.KB4API.get_campaign_stats")
@mock.patch("knowbe4.api_connections.requests.get",
            side_effect=Exception)
def test_kb4api_get_phishing_campaigns_exception_gpc001(g_data,g_stats,f_except):
    """Tests KB4API.get_phishing_campaigns"""
    KB4API.get_phishing_campaigns()
    assert g_data.call_count == 1
    assert g_stats.call_count == 0
    assert f_except.call_count == 1

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_campaign_stats_success(g_data,f_except):
    """Tests KB4API.get_campaign_stats"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'scheduled_count':1,'delivered_count':2,'opened_count':3,
                                    'clicked_count':4,'replied_count':5,'attachment_open_count':6,
                                    'macro_enabled_count':7,'data_entered_count':8,
                                    'reported_count':9,'bounced_count':10}
    g_data.return_value = resp_mock
    KB4API.get_campaign_stats(1)
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get")
def test_kb4api_get_campaign_stats_status_code_failure(g_data,f_except):
    """Tests KB4API.get_campaign_stats"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = []
    g_data.return_value = resp_mock
    KB4API.get_campaign_stats(1)
    assert g_data.call_count == 1
    assert f_except.call_count == 0

@mock.patch("knowbe4.api_connections.TheLogs.function_exception")
@mock.patch("knowbe4.api_connections.requests.get",
            side_effect=Exception)
def test_kb4api_get_campaign_stats_exception_gpc001(g_data,f_except):
    """Tests KB4API.get_campaign_stats"""
    KB4API.get_campaign_stats(1)
    assert g_data.call_count == 1
    assert f_except.call_count == 1

if __name__ == '__main__':
    unittest.main()
