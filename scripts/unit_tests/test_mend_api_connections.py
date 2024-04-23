'''Unit tests for the api_connections script in mend'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from datetime import datetime
from mend.api_connections import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch("mend.api_connections.requests.post")
def test_mend_connect_new_token(req_post):
    """Tests mend_connect"""
    resp_mock = mock.Mock(status_code=201)
    resp_mock.json.return_value = {'retVal':{'jwtToken':'jwtToken'}}
    req_post.return_value = resp_mock
    returns = MendAPI.mend_connect()
    assert req_post.call_count == 1
    assert returns == 'jwtToken'
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
def test_mend_connect_reuse_token(req_post):
    """Tests mend_connect"""
    MendAPI.token = 'jwtToken'
    MendAPI.token_created = datetime.now()
    returns = MendAPI.mend_connect()
    assert req_post.call_count == 0
    assert returns == 'jwtToken'
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_forbidden_licenses(connect,req_get):
    """Tests forbidden_licenses"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':{'filter':{'licenses':[{'name':'license name'}]}}}
    req_get.return_value = resp_mock
    returns = MendAPI.forbidden_licenses()
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert returns == ['license name']
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.forbidden_licenses",
            return_value=['forbbidden'])
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_violating_licenses(connect,forbidden,req_get):
    """Tests get_violating_licenses"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'name':'license name'}]}
    req_get.return_value = resp_mock
    returns = MendAPI.get_violating_licenses(1234,'library')
    assert connect.call_count == 1
    assert forbidden.call_count == 1
    assert req_get.call_count == 1
    assert returns == 'license name'
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.forbidden_licenses",
            return_value=['forbbidden'])
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_violating_licenses_no_licenses(connect,forbidden,req_get):
    """Tests get_violating_licenses"""
    MendAPI.token = 'jwtToken'
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[]}
    req_get.return_value = resp_mock
    returns = MendAPI.get_violating_licenses(1234,'library')
    assert connect.call_count == 0
    assert forbidden.call_count == 1
    assert req_get.call_count == 1
    assert returns == None
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.MendAPI.get_violating_licenses",
            return_value='license name')
@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_missing_fields(connect,req_get,g_v_lic):
    """Tests get_missing_fields"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'groupId':'groupId','version':'version',
                                              'locations':[{'localPath':'localPath'}]}]}
    req_get.return_value = resp_mock
    returns = MendAPI.get_missing_fields(1234,'library')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert g_v_lic.call_count == 1
    assert returns == {'GroupId':'groupId','Version':'version','LicenseViolations':'license name',
                       'LibraryLocations':'localPath'}
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.MendAPI.get_violating_licenses",
            return_value='license name')
@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_missing_fields_no_locations(connect,req_get,g_v_lic):
    """Tests get_missing_fields"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'groupId':'groupId','version':'version',
                                              'locations':[]}]}
    req_get.return_value = resp_mock
    returns = MendAPI.get_missing_fields(1234,'library')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert g_v_lic.call_count == 1
    assert returns == {'GroupId':'groupId','Version':'version','LicenseViolations':'license name',
                       'LibraryLocations':None}
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.select",
            return_value=[('value','value',)])
@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_alerts(connect,req_get,select):
    """Tests get_alerts"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'project':{'name':'project release'},
                                              'policyName':'Medium',
                                              'component':{'name':'component name',
                                                           'uuid':'key_uuid'},
                                              'alertInfo':{'detectedAt':'2023-04-01T23:00:00Z',
                                                           'status':'alertStatus',
                                                           'comment':None},
                                              'uuid':'alertUuid'},
                                              {'project':{'name':'project release'},
                                              'policyName':'High',
                                              'component':{'name':'component name',
                                                           'uuid':'key_uuid'},
                                              'alertInfo':{'detectedAt':'2023-04-01T23:00:00Z',
                                                           'status':'alertStatus',
                                                           'comment':None},
                                              'uuid':'alertUuid'},
                                              {'project':{'name':'project release'},
                                               'policyName':'License',
                                              'component':{'name':'component name',
                                                           'uuid':'key_uuid'},
                                              'alertInfo':{'detectedAt':'2023-04-01T23:00:00Z',
                                                           'status':'alertStatus',
                                                           'comment':{'comment':'comment'}},
                                              'uuid':'alertUuid'}]}
    req_get.return_value = resp_mock
    returns = MendAPI.get_alerts(1234,'library')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert select.call_count == 6
    assert returns == [{'AlertStatus':'Alertstatus','AlertUuid':'alertUuid','Comments':None,
                        'DateDetected':'2023-04-01 23:00:00','FindingType':'Vulnerability',
                        'InOSFindings': 1,'JiraIssueKey':'value','KeyUuid':'key_uuid','Library':
                        'component name','PolicyViolated':'Medium','ProjectId':'value',
                        'ProjectName':'project release','ProjectToken':'value','Severity':
                        'Medium'},
                        {'AlertStatus':'Alertstatus','AlertUuid':'alertUuid','Comments':None,
                         'DateDetected':'2023-04-01 23:00:00','FindingType':'Vulnerability',
                         'InOSFindings': 1,'JiraIssueKey':'value','KeyUuid':'key_uuid','Library':
                         'component name','PolicyViolated':'High','ProjectId':'value',
                         'ProjectName':'project release','ProjectToken':'value','Severity':'High'},
                         {'AlertStatus':'Alertstatus','AlertUuid':'alertUuid','Comments':'comment',
                          'DateDetected':'2023-04-01 23:00:00','FindingType':'License Violation',
                          'InOSFindings': 1,'JiraIssueKey':'value','KeyUuid':'key_uuid','Library':
                          'component name','PolicyViolated':'License','ProjectId':'value',
                          'ProjectName':'project release','ProjectToken':'value','Severity':
                          'High'}]
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.MendAPI.reactivate_license_violations",
            return_value=1)
@mock.patch("mend.api_connections.MendAPI.reactivate_vulnerabilities",
            return_value=1)
def test_reactivate_manually_ignored_alerts(r_vulns,r_lvs):
    """Tests reactivate_manually_ignored_alerts"""
    returns = MendAPI.reactivate_manually_ignored_alerts(1234,'token')
    assert r_vulns.call_count == 1
    assert r_lvs.call_count == 1
    assert returns == 2
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.insert_multiple_into_table")
@mock.patch("mend.api_connections.MendAPI.update_alert_status",
            return_value=True)
@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_reactivate_license_violations(connect,req_get,a_status,i_multi):
    """Tests reactivate_license_violations"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'alertInfo':{'status':'Ignored','comment':
                                  {'userEmail':'email','date':'2021-01-01T23:23:23Z4'}},'uuid':
                                  'uuid','type':'type','project':{'uuid':'project_id','name':
                                  'project_name'},'name':'title','component':{'name':'library',
                                  'groupId':'group_id'}}]}
    req_get.return_value = resp_mock
    response = MendAPI.reactivate_license_violations('repo','prod_token','comment')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert a_status.call_count == 1
    assert i_multi.call_count == 1
    assert response == 1
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_org_prod_vitals(connect,req_get):
    """Tests get_org_prod_vitals"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'products':[{'productName':'productName',
                                                'productToken':'productToken'}]}
    req_get.return_value = resp_mock
    response = MendAPI.get_org_prod_vitals()
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == [{'Repo':'productName','wsProductToken':'productToken'}]
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_apply_org_policies(connect,req_get):
    """Tests apply_org_policies"""
    resp_mock = mock.Mock(status_code=200)
    req_get.return_value = resp_mock
    response = MendAPI.apply_org_policies()
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == True
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_apply_product_policies(connect,req_get):
    """Tests apply_product_policies"""
    resp_mock = mock.Mock(status_code=200)
    req_get.return_value = resp_mock
    response = MendAPI.apply_product_policies(1234)
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == True
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.delete")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_delete_product(connect,req_get):
    """Tests delete_product"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'products':[{'productName':'productName',
                                                'productToken':'productToken'}]}
    req_get.return_value = resp_mock
    response = MendAPI.delete_product(1234)
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == True
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.delete")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_delete_product_error(connect,req_get):
    """Tests delete_product"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'errorCode':[{'productName':'productName',
                                                'productToken':'productToken'}]}
    req_get.return_value = resp_mock
    response = MendAPI.delete_product(1234)
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == False
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_get_projects(connect,req_get):
    """Tests get_projects"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'projectVitals':[{'name':'pj_name release','token':'pj_token',
                                                     'id':'pj_id','lastUpdatedDate':
                                                     'last_updated +stuff'}]}
    req_get.return_value = resp_mock
    response = MendAPI.get_projects('repo','prod_token')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == [{'wsProjectName':'pj_name release','wsProjectToken':'pj_token',
                         'wsProjectId':'pj_id','wsLastUpdatedDate':'last_updated'}]
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.select",
            return_value=[('select_value','select_value',)])
@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_vulnerability_report(connect,req_get,select):
    """Tests vulnerability_report"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'vulnerabilities':
                                   [{'cvss3_severity':'Critical','project':'pj_n release',
                                     'library':{'filename':'filename','groupId':'groupId',
                                                'keyUuid':'keyUuid','version':'version',
                                                'resultingShield':'red'},
                                     'publishDate':'publishDate','name':'vuln_name','url':'url',
                                     'topFix':{'fixResolution':'resolution'}},
                                     {'cvss3_severity':'High','project':'pj_n release',
                                     'library':{'filename':'filename','groupId':'groupId',
                                                'keyUuid':'keyUuid','version':'version',
                                                'resultingShield':'red'},
                                     'publishDate':'publishDate','name':'vuln_name','url':'url',
                                     'topFix':{'fixResolution':'resolution'}},
                                     {'cvss3_severity':'Medium','project':'pj_n release',
                                     'library':{'filename':'filename','groupId':'groupId',
                                                'keyUuid':'keyUuid','version':'version',
                                                'resultingShield':'green'},
                                     'publishDate':'publishDate','name':'vuln_name','url':'url',
                                     'topFix':{'fixResolution':'resolution'}}]}
    req_get.return_value = resp_mock
    response = MendAPI.vulnerability_report('repo','prod_token')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert select.call_count == 3
    assert response == [{'Severity':'Critical','SeverityValue':0,'ProjectName':'pj_n release',
                         'ProjectId':'select_value','Library':'filename','GroupId':'groupId',
                         'KeyUuid':'keyUuid','Version':'version','VulnPublishDate':'publishDate',
                         'Vulnerability':'vuln_name','VulnerabilityUrl':'url','Remediation':
                         'resolution','ResultingShield':'Red'},
                         {'Severity':'High','SeverityValue':1,'ProjectName':'pj_n release',
                         'ProjectId':'select_value','Library':'filename','GroupId':'groupId',
                         'KeyUuid':'keyUuid','Version':'version','VulnPublishDate':'publishDate',
                         'Vulnerability':'vuln_name','VulnerabilityUrl':'url','Remediation':
                         'resolution','ResultingShield':'Red'},
                         {'Severity':'Medium','SeverityValue':2,'ProjectName':'pj_n release',
                         'ProjectId':'select_value','Library':'filename','GroupId':'groupId',
                         'KeyUuid':'keyUuid','Version':'version','VulnPublishDate':'publishDate',
                         'Vulnerability':'vuln_name','VulnerabilityUrl':'url','Remediation':
                         'resolution','ResultingShield':'Green'}]
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_update_alert_status(connect,req_get):
    """Tests update_alert_status"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'message':'Successfully set the alert'}
    req_get.return_value = resp_mock
    response = MendAPI.update_alert_status('pj_token','alert_uuid','status','comment')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == True
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.requests.post")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
def test_update_alert_status_failed(connect,req_get):
    """Tests update_alert_status"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'message':'Failed.'}
    req_get.return_value = resp_mock
    response = MendAPI.update_alert_status('pj_token','alert_uuid','status','comment')
    assert connect.call_count == 1
    assert req_get.call_count == 1
    assert response == False
    MendAPI.token = None
    MendAPI.token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

@mock.patch("mend.api_connections.MendAPI.do_not_reactivate_alert")
@mock.patch("mend.api_connections.insert_multiple_into_table")
@mock.patch("mend.api_connections.MendAPI.update_alert_status",
            return_value=True)
@mock.patch("mend.api_connections.requests.get")
@mock.patch("mend.api_connections.MendAPI.mend_connect",
            return_value='jwtToken')
@pytest.mark.parametrize("mc_val,dnra_rv,mc_cnt,uas_cnt,response_val",
                         [(None,True,1,0,0),
                          ('Token is set',False,0,1,1)])
def test_reactivate_vulnerabilities(mc,req_get,uas,imit,dnra,mc_val,dnra_rv,mc_cnt,uas_cnt,
                                    response_val):
    """Tests reactivate_vulnerabilities"""
    dnra.return_value = dnra_rv
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'retVal':[{'alertInfo':{'status':'Ignored','comment':
                                  {'userEmail':'email','date':'2021-01-01T23:23:23Z4'}},'uuid':
                                  'uuid','type':'type','project':{'uuid':'project_id','name':
                                  'project_name'},'name':'title','component':{'name':'library',
                                  'groupId':'group_id'}}]}
    req_get.return_value = resp_mock
    MendAPI.token = mc_val
    response = MendAPI.reactivate_vulnerabilities('repo','prod_token','comment')
    assert mc.call_count == mc_cnt
    assert req_get.call_count == 1
    assert uas.call_count == uas_cnt
    assert imit.call_count == 1
    assert response == response_val

@mock.patch("mend.api_connections.select")
@pytest.mark.parametrize("response_val,sql_sel_rv",
                         [(True,[('Status')]),
                          (False,[])])
def test_mendapi_do_not_reactivate_alert(sql_sel,response_val,sql_sel_rv):
    """Tests MendAPI.do_not_reactivate_alert"""
    sql_sel.return_value = sql_sel_rv
    response = MendAPI.do_not_reactivate_alert('alert_uuid')
    assert sql_sel.call_count == 1
    assert response == response_val

if __name__ == '__main__':
    unittest.main()
