'''Unit tests for the maintenance_jira_issues script'''

import unittest
from unittest import mock
import sys
import os
import pytest
from bitsight.api_connections import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts",
            return_value=[{'guid':'guid','custom_id':'custom_id','name':'name',
                                    'shortname':'shortname','network_size_v4':'network_size_v4',
                                    'rating':'rating','rating_date':'rating_date',
                                    'date_added':'date_added','industry':'industry',
                                    'sub_industry':'sub_industry','sub_industry_slug':
                                    'sub_industry_slug','type':'type','external_id':'external_id',
                                    'subscription_type':'subscription_type',
                                    'subscription_type_key':'subscription_type_key',
                                    'primary_domain':'primary_domain'}])
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_companies_success(g_data,c_array):
    """Tests BitSightAPI.fetch_companies"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'companies':[{'guid':'guid','custom_id':'custom_id','name':
                                                'name','shortname':'shortname','network_size_v4':
                                                'network_size_v4','rating':'rating','rating_date':
                                                'rating_date','date_added':'date_added',
                                                'industry':'industry','sub_industry':
                                                'sub_industry','sub_industry_slug':
                                                'sub_industry_slug','type':'type','external_id':
                                                'external_id','subscription_type':
                                                'subscription_type','subscription_type_key':
                                                'subscription_type_key','primary_domain':
                                                'primary_domain'}]}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_companies()
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_companies_failure(g_data,c_array):
    """Tests BitSightAPI.fetch_companies"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_companies()
    assert g_data.call_count == 1
    assert c_array.call_count == 0

@mock.patch("bitsight.api_connections.General.replace_blanks_in_dict",
            return_value=[{'current_score':'score','current_score_date':'date','guid':'guid',
                           'name':'name'}])
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_current_scores_success(g_data,c_array):
    """Tests BitSightAPI.fetch_current_scores"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'companies':[{'rating':'score','rating_date':'date',
                                                 'guid':'guid','name':'name'}]}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_current_scores()
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_dict")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_current_scores_failure(g_data,c_array):
    """Tests BitSightAPI.fetch_current_scores"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_current_scores()
    assert g_data.call_count == 1
    assert c_array.call_count == 0

@mock.patch("bitsight.api_connections.General.replace_blanks_in_dict",
            return_value=[{'previous_score':'previous_score_date','date':'date','guid':'guid',
                           'name':'name'}])
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_previous_scores_success(g_data,c_array):
    """Tests BitSightAPI.fetch_previous_scores"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'companies':[{'rating':'score','rating_date':'date',
                                                 'guid':'guid','name':'name'}]}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_previous_scores()
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_dict")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_previous_scores_failure(g_data,c_array):
    """Tests BitSightAPI.fetch_previous_scores"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_previous_scores()
    assert g_data.call_count == 1
    assert c_array.call_count == 0

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts",
            return_value=[{'guid':'guid','name':'name','bitsight_score':'score','score_updated':
                           'score_date','botnet_infections':'big','spam_propagation':'spg',
                           'malware_servers':'msg','unsolicited_communications':'ucg',
                           'potentially_exploited':'peg','spf':'spfg','dkim':'dkimg',
                           'ssl_certificates':'sslcertg','ssl_configurations':'sslcong',
                           'open_ports':'opg','web_application_headers':'asg',
                           'patching_cadence':'pcg','insecure_systems':'isg','server_software':
                           'ssg','desktop_software':'dsg','mobile_software':'mosg','dnssec':'dnsg',
                           'mobile_application_security':'masg','file_sharing':'fsg',
                           'security_incidents':'dbg'}])
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_ratings_details_success(g_data,c_array):
    """Tests BitSightAPI.fetch_ratings_details"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'ratings':[{'rating':'score','rating_date':'score_date'}],
                                   'guid':'guid','name':'name','industry':'industry','homepage':
                                   'homepage','primary_domain':'primary_domain',
                                   'rating_details':{'botnet_infections':{'grade':'big',
                                                                          'grade_color':'bic'},
                                            'spam_propagation':{'grade':'spg','grade_color':'spc'},
                                            'malware_servers':{'grade':'msg','grade_color':'msc'},
                                            'unsolicited_comm':{'grade':'ucg','grade_color':'ucc'},
                                            'potentially_exploited':{'grade':'peg','grade_color':
                                                                     'pec'},
                                            'spf':{'grade':'spfg','grade_color':'spfc'},
                                            'dkim':{'grade':'dkimg','grade_color':'dkimc'},
                                            'ssl_certificates':{'grade':'sslcertg','grade_color':
                                                                'sslcertc'},
                                            'ssl_configurations':{'grade':'sslcong','grade_color':
                                                                  'sslconc'},
                                            'open_ports':{'grade':'opg','grade_color':'opc'},
                                            'application_security':{'grade':'asg','grade_color':
                                                                    'asc'},
                                            'patching_cadence':{'grade':'pcg','grade_color':'pcc'},
                                            'insecure_systems':{'grade':'isg','grade_color':'isc'},
                                            'server_software':{'grade':'ssg','grade_color':'ssc'},
                                            'desktop_software':{'grade':'dsg','grade_color':'dsc'},
                                            'mobile_software':{'grade':'mosg','grade_color':
                                                               'mosc'},
                                            'dnssec':{'grade':'dnsg','grade_color':'dnsc'},
                                            'mobile_application_security':{'grade':'masg',
                                                                           'grade_color':'masc'},
                                            'file_sharing':{'grade':'fsg','grade_color':'fsc'},
                                            'data_breaches':{'grade':'dbg','grade_color':'dbc'}}}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_ratings_details(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_ratings_details_failure(g_data,c_array):
    """Tests BitSightAPI.fetch_ratings_details"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_ratings_details(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_ratings_details_empty(g_data,c_array):
    """Tests BitSightAPI.fetch_ratings_details"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_ratings_details(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts",
            return_value=[{'guid':'guid','name':'name','bitsight_score':'score','score_updated':
                           'score_date','botnet_infections':'big','spam_propagation':'spg',
                           'malware_servers':'msg','unsolicited_communications':'ucg',
                           'potentially_exploited':'peg','spf':'spfg','dkim':'dkimg',
                           'ssl_certificates':'sslcertg','ssl_configurations':'sslcong',
                           'open_ports':'opg','web_application_headers':'asg',
                           'patching_cadence':'pcg','insecure_systems':'isg','server_software':
                           'ssg','desktop_software':'dsg','mobile_software':'mosg','dnssec':'dnsg',
                           'mobile_application_security':'masg','file_sharing':'fsg',
                           'security_incidents':'dbg'}])
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_prog_holdings_success(g_data,c_array):
    """Tests BitSightAPI.fetch_prog_holdings"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'ratings':[{'rating':'score','rating_date':'score_date'}],
                                   'guid':'guid','name':'name','industry':'industry','homepage':
                                   'homepage','primary_domain':'primary_domain',
                                   'rating_details':{'botnet_infections':{'grade':'big',
                                                                          'grade_color':'bic'},
                                            'spam_propagation':{'grade':'spg','grade_color':'spc'},
                                            'malware_servers':{'grade':'msg','grade_color':'msc'},
                                            'unsolicited_comm':{'grade':'ucg','grade_color':'ucc'},
                                            'potentially_exploited':{'grade':'peg','grade_color':
                                                                     'pec'},
                                            'spf':{'grade':'spfg','grade_color':'spfc'},
                                            'dkim':{'grade':'dkimg','grade_color':'dkimc'},
                                            'ssl_certificates':{'grade':'sslcertg','grade_color':
                                                                'sslcertc'},
                                            'ssl_configurations':{'grade':'sslcong','grade_color':
                                                                  'sslconc'},
                                            'open_ports':{'grade':'opg','grade_color':'opc'},
                                            'application_security':{'grade':'asg','grade_color':
                                                                    'asc'},
                                            'patching_cadence':{'grade':'pcg','grade_color':'pcc'},
                                            'insecure_systems':{'grade':'isg','grade_color':'isc'},
                                            'server_software':{'grade':'ssg','grade_color':'ssc'},
                                            'desktop_software':{'grade':'dsg','grade_color':'dsc'},
                                            'mobile_software':{'grade':'mosg','grade_color':
                                                               'mosc'},
                                            'dnssec':{'grade':'dnsg','grade_color':'dnsc'},
                                            'mobile_application_security':{'grade':'masg',
                                                                           'grade_color':'masc'},
                                            'file_sharing':{'grade':'fsg','grade_color':'fsc'},
                                            'data_breaches':{'grade':'dbg','grade_color':'dbc'}}}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_prog_holdings(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_prog_holdings_failure(g_data,c_array):
    """Tests BitSightAPI.fetch_prog_holdings"""
    resp_mock = mock.Mock(status_code=500)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_prog_holdings(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

@mock.patch("bitsight.api_connections.General.replace_blanks_in_list_of_dicts")
@mock.patch("bitsight.api_connections.requests.get")
def test_bitsightapi_fetch_prog_holdings_empty(g_data,c_array):
    """Tests BitSightAPI.fetch_prog_holdings"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {}
    g_data.return_value = resp_mock
    BitSightAPI.fetch_prog_holdings(['guid'])
    assert g_data.call_count == 1
    assert c_array.call_count == 1

if __name__ == '__main__':
    unittest.main()
