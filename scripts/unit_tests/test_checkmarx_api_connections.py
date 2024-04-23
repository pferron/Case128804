'''Unit tests for the api_connections script in mend'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from datetime import date, timedelta
from checkmarx.api_connections import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

GENERIC_DT = datetime.now()

def test_scrvar_update_exception_info():
    """Tests ScrVar.update_exception_info"""
    ScrVar.update_exception_info({'FatalCount':1,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 1
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch("checkmarx.api_connections.requests.post")
def test_cxapi_checkmarx_connection(req_post):
    """Tests CxAPI.checkmarx_connection"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'access_token':'token'}
    req_post.return_value = resp_mock
    response = CxAPI.checkmarx_connection()
    assert req_post.call_count == 1
    assert response == 'token'

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_checkmarx_projects(cx_conn,req_get):
    """Tests CxAPI.get_checkmarx_projects"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':1,'name':'project name','owner':'Project Owner'}]
    req_get.return_value = resp_mock
    response = CxAPI.get_checkmarx_projects(52)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == [{'id':1,'repo':'project','checkmarx_project_owner':'Project Owner'}]

@mock.patch("checkmarx.api_connections.requests.delete")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_cx_delete_project(cx_conn,req_delete):
    """Tests CxAPI.cx_delete_project"""
    resp_mock = mock.Mock(status_code=202)
    req_delete.return_value = resp_mock
    response = CxAPI.cx_delete_project(987654321)
    assert cx_conn.call_count == 1
    assert req_delete.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.patch")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_update_res_state(cx_conn,req_patch):
    """Tests CxAPI.update_res_state"""
    resp_mock = mock.Mock(status_code=200)
    req_patch.return_value = resp_mock
    response = CxAPI.update_res_state(123456789,98765,2,'updated by unit test')
    assert cx_conn.call_count == 1
    assert req_patch.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_last_scan_data(cx_conn,req_get):
    """Tests CxAPI.get_last_scan_data"""
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    today = date.today().strftime("%Y-%m-%d %H:%M:%S")
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'project':{'id':987654321},'id':12345678,
                                    'dateAndTime': {'startedOn': yesterday ,
                                                    'finishedOn': today},
                                    'isIncremental':'False','scanState':{'Contains':'Data'}},
                                    {'project':{'id':987654321},'id':12345678,
                                    'dateAndTime': {'startedOn': yesterday ,
                                                    'finishedOn': today},
                                    'isIncremental':'True','scanState':{'Contains':'Data'}}]
    req_get.return_value = resp_mock
    response = CxAPI.get_last_scan_data(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_checkmarx_availability(cx_conn,req_get):
    """Tests CxAPI.checkmarx_availability"""
    resp_mock = mock.Mock(status_code=200)
    req_get.return_value = resp_mock
    response = CxAPI.checkmarx_availability(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_path_and_result_state(cx_conn,req_get):
    """Tests CxAPI.get_path_and_result_state"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'value':[{'ScanId':55555555,'Id':33333,'StateName':'Confirmed'}]}
    req_get.return_value = resp_mock
    response = CxAPI.get_path_and_result_state(123456789,98765)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == {'cxScanId':55555555,'cxPathId':33333,'cxStateName':'Confirmed'}

@mock.patch("checkmarx.api_connections.CxASDatabase.check_cross_repo",
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':False})
@mock.patch("checkmarx.api_connections.CxAPI.get_project_repo_set",
            return_value={'is_set':True,'branch':'branch_name'})
@mock.patch("checkmarx.api_connections.CxAPI.project_exists",
            return_value=True)
@mock.patch("checkmarx.api_connections.CxAPI.get_last_scan_data",
            return_value={'ID':22222222,'Type':'Full','Finished':datetime.now(),
                          'Duration':'00:07:21'})
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_project_data(cx_conn,req_get,g_ls,g_pe,g_rs,g_cr):
    """Tests CxAPI.get_project_data"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'id':123456789,'name':'project_name (Baseline)',
                                   'originalProjectId':987654321,'teamId':52}
    req_get.return_value = resp_mock
    response = CxAPI.get_project_data(123456789)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_ls.call_count == 1
    assert g_pe.call_count == 1
    assert g_rs.call_count == 1
    assert g_cr.call_count == 1

@mock.patch("checkmarx.api_connections.CxASDatabase.check_cross_repo",
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':False})
@mock.patch("checkmarx.api_connections.CxAPI.get_project_repo_set",
            return_value={'is_set':True,'branch':'branch_name'})
@mock.patch("checkmarx.api_connections.CxAPI.project_exists",
            return_value=True)
@mock.patch("checkmarx.api_connections.CxAPI.get_last_scan_data",
            return_value={'ID':22222222,'Type':'Full','Finished':datetime.now(),
                          'Duration':'00:07:21'})
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_project_data_not_branched(cx_conn,req_get,g_ls,g_pe,g_rs,g_cr):
    """Tests CxAPI.get_project_data"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'id':123456789,'name':'project_name (Baseline)',
                                   'originalProjectId':'','teamId':52}
    req_get.return_value = resp_mock
    response = CxAPI.get_project_data(123456789)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_ls.call_count == 1
    assert g_pe.call_count == 0
    assert g_rs.call_count == 1
    assert g_cr.call_count == 0

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_project_repo_set(cx_conn,req_get):
    """Tests CxAPI.get_project_repo_set"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'branch':'/testing/path/branch_name'}
    req_get.return_value = resp_mock
    response = CxAPI.get_project_repo_set(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == {'is_set':True,'branch':'branch_name'}

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_project_exists(cx_conn,req_get):
    """Tests CxAPI.project_exists"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'id':987654321}
    req_get.return_value = resp_mock
    response = CxAPI.project_exists(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_repo_project_id(cx_conn,req_get):
    """Tests CxAPI.get_repo_project_id"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':987654321}]
    req_get.return_value = resp_mock
    response = CxAPI.get_repo_project_id(987654321,'baseline')
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == {'cxProjectId':987654321}

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_repo_project_id_pipeline(cx_conn,req_get):
    """Tests CxAPI.get_repo_project_id"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = [{'id':987654321}]
    req_get.return_value = resp_mock
    response = CxAPI.get_repo_project_id(987654321,'pipeline')
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == {'cxProjectId':987654321}

@mock.patch("checkmarx.api_connections.CxCommon.get_result_state_id",
            return_value=0)
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_result_state(cx_conn,req_get,g_rsid):
    """Tests CxAPI.get_result_state"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'value':[{'StateName':'To Verify'}]}
    req_get.return_value = resp_mock
    response = CxAPI.get_result_state(5555555555555,987654321,'other state')
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_rsid.call_count == 1
    assert response == {'cxStateId':0,'cxStateName':'To Verify'}

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_cwe_id(cx_conn,req_get):
    """Tests CxAPI.get_cwe_id"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'value':[{'Cweid':102}]}
    req_get.return_value = resp_mock
    response = CxAPI.get_cwe_id(5555555555555,987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == 102

@mock.patch("checkmarx.api_connections.VulnDetails.get_cwe",
            return_value={'name':'cwe name','description':'cwe description','link':'cwe_link'})
@mock.patch("checkmarx.api_connections.CxCommon.get_result_state_id",
            return_value=2)
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_finding_details(cx_conn,req_get,g_rsid,g_cwe):
    """Tests CxAPI.get_finding_details"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'value':[{'Date':'2023-12-11T13:47:54.137198Zest',
                                             'SimilarityId':987654321,'StateName':'Confirmed',
                                             'Cweid':102,'ScanId':5555555555555,'Id':22}]}
    req_get.return_value = resp_mock
    response = CxAPI.get_finding_details(5555555555555,987654321,123456789)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_rsid.call_count == 1
    assert g_cwe.call_count == 1
    assert response == [{'cxLastScanDate':'2023-12-11 13:47:54','cxSimilarityID':987654321,
                         'cxResultState':'Confirmed','cxResultStateValue':2,'cxCWEID':102,
                         'cxCWETitle':'cwe name','cxCWEDescription':'cwe description',
                         'cxCWELink':'cwe_link','cxResultID':'5555555555555-22'}]

@mock.patch("checkmarx.api_connections.VulnDetails.get_cwe",
            return_value={'name':'cwe name','description':'cwe description','link':'cwe_link'})
@mock.patch("checkmarx.api_connections.CxCommon.get_result_state_id",
            return_value=2)
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_finding_details_by_path(cx_conn,req_get,g_rsid,g_cwe):
    """Tests CxAPI.get_finding_details_by_path"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'value':[{'Date':'2023-12-11T13:47:54.137198Zest',
                                             'SimilarityId':987654321,'StateName':'Confirmed',
                                             'Cweid':102,'ScanId':5555555555555,'Id':22}]}
    req_get.return_value = resp_mock
    response = CxAPI.get_finding_details_by_path(5555555555555,987654321,123456789)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_rsid.call_count == 1
    assert g_cwe.call_count == 1
    assert response == {'cxLastScanDate':'2023-12-11 13:47:54','cxLastScanID':5555555555555,
                        'cxSimilarityID':987654321,'cxResultState':'Confirmed',
                        'cxResultStateValue':2,'cxCWEID':102,'cxCWETitle':'cwe name',
                        'cxCWEDescription':'cwe description','cxCWELink':'cwe_link'}

@mock.patch("checkmarx.api_connections.cx_select",
            return_value=[('this is the description\'s text',),])
def test_g_query_desc(cxdb_sel):
    """Tests CxAPI.g_query_desc"""
    response = CxAPI.g_query_desc(987654321)
    assert cxdb_sel.call_count == 1
    assert response == 'this is the descriptions text'

@mock.patch("checkmarx.api_connections.CxAPI.g_query_desc",
            return_value='Query Description')
@mock.patch("checkmarx.api_connections.VulnDetails.get_cwe",
            return_value={'cwe_id':'CWE-547','name':'CWE Name','description':'CWE Description',
                          'link': 'https://cwe.mitre.org/data/definitions/547.html'})
@mock.patch("checkmarx.api_connections.CxAPI.get_cwe_id",
            return_value=547)
@mock.patch("checkmarx.api_connections.cx_select",
            return_value=[(1234567890,)])
@mock.patch("checkmarx.api_connections.CxAPI.get_result_description",
            return_value='result description')
@mock.patch("checkmarx.api_connections.CxCommon.get_result_state_id",
            return_value=2)
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_create_scan_results_json_high_severity(cx_conn,req_get,g_rsid,g_rd,sql_cx,
                                                         g_cweid,g_cwe,g_qd):
    """Tests CxAPI.create_scan_results_json"""
    resp_mock = mock.Mock(status_code=200,text='''"Query","QueryPath","Custom","PCI DSS v3.2.1","OWASP Top 10 2013","FISMA 2014","NIST SP 800-53","OWASP Top 10 2017","OWASP Mobile Top 10 2016","OWASP Top 10 API","ASD STIG 4.10","OWASP Top 10 2010","OWASP Top 10 2021","CWE top 25","MOIS(KISA) Secure Coding 2021","OWASP ASVS","SANS top 25","ASA Mobile Premium","ASA Premium","ASD STIG 5.2","Top Tier","SrcFileName","Line","Column","NodeId","Name","DestFileName","DestLine","DestColumn","DestNodeId","DestName","Result State","Result Severity","Assigned To","Comment","Link","Result Status","Detection Date"
"Hardcoded Password in Connection String","Python\Cx\Python Medium Threat\Hardcoded Password in Connection String Version:4","","PCI DSS (3.2.1) - 6.5.3 - Insecure cryptographic storage","A5-Security Misconfiguration","","","A6-Security Misconfiguration","","","","","A5-Security Misconfiguration","","","","","","ASA Premium","APSC-DV-003110 - CAT I The application must not contain embedded authentication data.","","scripts/maintenance_database_backups.py","75","85","1",""";PWD=""","scripts/maintenance_database_backups.py","72","46","2","connect","Confirmed","High","","John McCutchen appsec-ops (Baseline), [Friday, November 3, 2023 8:23:48 AM]: Changed status to Not Exploitable Stacy Castleton appsec-ops (Baseline), [Wednesday, August 16, 2023 7:59:33 AM]: Changed status to Not Exploitable John McCutchen appsec-ops (Baseline), [Thursday, July 20, 2023 8:03:30 AM]: Changed status to Not Exploitable John McCutchen appsec-ops (Baseline), [Wednesday, June 21, 2023 10:58:05 AM]: Changed status to Not Exploitable","https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1127803&projectid=10915&pathid=1","Recurrent","6/9/2023 12:04:37 AM"''')
    req_get.return_value = resp_mock
    response = CxAPI.create_scan_results_json(5555555555555,987654321,10915,None)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_rsid.call_count == 1
    assert g_rd.call_count == 1
    assert sql_cx.call_count == 1
    assert g_cweid.call_count == 1
    assert g_cwe.call_count == 1
    assert g_qd.call_count == 1

@mock.patch("checkmarx.api_connections.CxAPI.g_query_desc",
            return_value='Query Description')
@mock.patch("checkmarx.api_connections.VulnDetails.get_cwe",
            return_value={'cwe_id':'CWE-547','name':'CWE Name','description':'CWE Description',
                          'link': 'https://cwe.mitre.org/data/definitions/547.html'})
@mock.patch("checkmarx.api_connections.CxAPI.get_cwe_id",
            return_value=547)
@mock.patch("checkmarx.api_connections.cx_select",
            return_value=[(1234567890,)])
@mock.patch("checkmarx.api_connections.CxAPI.get_result_description",
            return_value='result description')
@mock.patch("checkmarx.api_connections.CxCommon.get_result_state_id",
            return_value=2)
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_create_scan_results_json_medium_severity(cx_conn,req_get,g_rsid,g_rd,sql_cx,
                                                        g_cweid,g_cwe,g_qd):
    """Tests CxAPI.create_scan_results_json"""
    resp_mock = mock.Mock(status_code=200,text='''"Query","QueryPath","Custom","PCI DSS v3.2.1","OWASP Top 10 2013","FISMA 2014","NIST SP 800-53","OWASP Top 10 2017","OWASP Mobile Top 10 2016","OWASP Top 10 API","ASD STIG 4.10","OWASP Top 10 2010","OWASP Top 10 2021","CWE top 25","MOIS(KISA) Secure Coding 2021","OWASP ASVS","SANS top 25","ASA Mobile Premium","ASA Premium","ASD STIG 5.2","Top Tier","SrcFileName","Line","Column","NodeId","Name","DestFileName","DestLine","DestColumn","DestNodeId","DestName","Result State","Result Severity","Assigned To","Comment","Link","Result Status","Detection Date"
"Hardcoded Password in Connection String","Python\Cx\Python Medium Threat\Hardcoded Password in Connection String Version:4","","PCI DSS (3.2.1) - 6.5.3 - Insecure cryptographic storage","A5-Security Misconfiguration","","","A6-Security Misconfiguration","","","","","A5-Security Misconfiguration","","","","","","ASA Premium","APSC-DV-003110 - CAT I The application must not contain embedded authentication data.","","scripts/maint/checkmarx_user_cleanup.py","56","24","1","""resource_owner_client&client_secret=""","scripts/maint/checkmarx_user_cleanup.py","61","29","4","post","Not Exploitable","Medium","","John McCutchen appsec-ops (Baseline), [Friday, November 3, 2023 8:23:48 AM]: Changed status to Not Exploitable Stacy Castleton appsec-ops (Baseline), [Monday, October 2, 2023 11:16:17 AM]: Changed status to Not Exploitable","https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1127803&projectid=10915&pathid=2","Recurrent","10/2/2023 11:15:27 AM"''')
    req_get.return_value = resp_mock
    response = CxAPI.create_scan_results_json(5555555555555,987654321,10915,None)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert g_rsid.call_count == 1
    assert g_rd.call_count == 1
    assert sql_cx.call_count == 1
    assert g_cweid.call_count == 1
    assert g_cwe.call_count == 1
    assert g_qd.call_count == 1

@mock.patch("scripts.checkmarx.api_connections.csv.reader")
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_scan_report(cx_conn,req_get,csv_read):
    """Tests CxAPI.get_scan_report"""
    response = CxAPI.get_scan_report(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert csv_read.call_count == 1

@mock.patch("checkmarx.api_connections.requests.post")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_create_scan_report(cx_conn,req_post):
    """Tests CxAPI.create_scan_report"""
    resp_mock = mock.Mock(status_code=202)
    resp_mock.json.return_value = {'reportId':1}
    req_post.return_value = resp_mock
    response = CxAPI.create_scan_report(987654321)
    assert cx_conn.call_count == 1
    assert req_post.call_count == 1
    assert response == 1

@mock.patch("checkmarx.api_connections.CxAPI.scan_report_status",
            return_value="Created")
def test_scan_report_complete(g_status):
    """Tests CxAPI.scan_report_complete"""
    response = CxAPI.scan_report_complete(1234567890)
    assert g_status.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_scan_report_status(cx_conn,req_get):
    """Tests CxAPI.scan_report_status"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'status':{'value':1}}
    req_get.return_value = resp_mock
    response = CxAPI.scan_report_status(987654321)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == 1

@mock.patch("checkmarx.api_connections.CxAPI.scan_report_complete",
            return_value=False)
@mock.patch("checkmarx.api_connections.CxAPI.create_scan_report",
            return_value=987654321)
@mock.patch("checkmarx.api_connections.CxAPI.create_scan_results_json",
            return_value='An array of dictionaries')
@mock.patch("checkmarx.api_connections.cx_select",
            return_value=[(456789123,),])
def test_cxapi_get_scan_results_report_exists(cxdb_sel,c_results,c_report,rep_comp):
    """Tests CxAPI.get_scan_results"""
    response = CxAPI.get_scan_results(123456789,10915,None)
    assert cxdb_sel.call_count == 1
    assert c_results.call_count == 1
    assert c_report.call_count == 0
    assert rep_comp.call_count == 0

@mock.patch("checkmarx.api_connections.CxAPI.scan_report_complete",
            return_value=True)
@mock.patch("checkmarx.api_connections.CxAPI.create_scan_report",
            return_value=987654321)
@mock.patch("checkmarx.api_connections.CxAPI.create_scan_results_json",
            return_value='An array of dictionaries')
@mock.patch("checkmarx.api_connections.cx_select",
            return_value=None)
def test_cxapi_get_scan_results_run_report_first(cxdb_sel,c_results,c_report,rep_comp):
    """Tests CxAPI.get_scan_results"""
    response = CxAPI.get_scan_results(123456789,10915,None)
    assert cxdb_sel.call_count == 1
    assert c_results.call_count == 1
    assert c_report.call_count == 1
    assert rep_comp.call_count == 1

@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_result_description(cx_conn,req_get):
    """Tests CxAPI.get_result_description"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'shortDescription':'description'}
    req_get.return_value = resp_mock
    response = CxAPI.get_result_description(123456,765)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert response == 'description'

@mock.patch("checkmarx.api_connections.requests.post")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_add_ticket_to_cx(cx_conn,req_post):
    """Tests CxAPI.add_ticket_to_cx"""
    resp_mock = mock.Mock(status_code=204)
    req_post.return_value = resp_mock
    response = CxAPI.add_ticket_to_cx(123456,'ABC-123')
    assert cx_conn.call_count == 1
    assert req_post.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.post")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_launch_cx_scan(cx_conn,req_post):
    """Tests CxAPI.launch_cx_scan"""
    resp_mock = mock.Mock(status_code=201)
    req_post.return_value = resp_mock
    response = CxAPI.launch_cx_scan(10915,'launched from unit test')
    assert cx_conn.call_count == 1
    assert req_post.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.post")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_branch_project(cx_conn,req_post):
    """Tests CxAPI.branch_project"""
    resp_mock = mock.Mock(status_code=201)
    resp_mock.json.return_value = {'id':1010101010}
    req_post.return_value = resp_mock
    response = CxAPI.branch_project('a_repo',987654321,52)
    assert cx_conn.call_count == 1
    assert req_post.call_count == 1
    assert response == 1010101010
    resp_mock = mock.Mock(status_code=201)
    resp_mock.json.return_value = {'id':1010101011}
    req_post.return_value = resp_mock
    response = CxAPI.branch_project('a_repo',1010101010,53)
    assert cx_conn.call_count == 2
    assert req_post.call_count == 2
    assert response == 1010101011

@mock.patch("checkmarx.api_connections.requests.put")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_set_project_team(cx_conn,req_put):
    """Tests CxAPI.set_project_team"""
    resp_mock = mock.Mock(status_code=204)
    req_put.return_value = resp_mock
    response = CxAPI.set_project_team('a_repo',987654321,52)
    assert cx_conn.call_count == 1
    assert req_put.call_count == 1
    assert response is True
    response = CxAPI.set_project_team('a_repo',1010101010,53)
    assert cx_conn.call_count == 2
    assert req_put.call_count == 2
    assert response is True

@mock.patch("checkmarx.api_connections.requests.put")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_set_policy(cx_conn,req_put):
    """Tests CxAPI.set_policy"""
    resp_mock = mock.Mock(status_code=200)
    req_put.return_value = resp_mock
    response = CxAPI.set_policy(987654321)
    assert cx_conn.call_count == 1
    assert req_put.call_count == 1
    assert response is True

@mock.patch("checkmarx.api_connections.requests.post")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_set_repo(cx_conn,req_post):
    """Tests CxAPI.set_repo"""
    resp_mock = mock.Mock(status_code=204)
    req_post.return_value = resp_mock
    response = CxAPI.set_repo('a_repo',987654321,None)
    assert cx_conn.call_count == 1
    assert req_post.call_count == 1
    assert response is True
    response = CxAPI.set_repo('a_repo',987654321,'main')
    assert cx_conn.call_count == 2
    assert req_post.call_count == 2
    assert response is True

@mock.patch("checkmarx.api_connections.CxAPI.get_last_scan_data",
            return_value={'ID':1010101,'Type':'Full','Finished':'2023-12-12 01:15:37',
                          'Duration':'00:07:43',
                          'Results':{'filesCount':10,'linesOfCode':1243,
                                     'languageStateCollection':[{'languageName':'apex'},
                                     {'languageName':'asp'},{'languageName':'cobol'},
                                     {'languageName':'common'},{'languageName':'cpp'},
                                     {'languageName':'csharp'},{'languageName':'dart'},
                                     {'languageName':'go'},{'languageName':'groovy'},
                                     {'languageName':'java'},{'languageName':'javascript'},
                                     {'languageName':'kotlin'},{'languageName':'objc'},
                                     {'languageName':'perl'},{'languageName':'php'},
                                     {'languageName':'plsql'},{'languageName':'python'},
                                     {'languageName':'rpg'},{'languageName':'ruby'},
                                     {'languageName':'scala'},{'languageName':'swift'},
                                     {'languageName':'vb6'},{'languageName':'vbnet'},
                                     {'languageName':'vbscript'},{'languageName':'unknown'}]}})
@mock.patch("checkmarx.api_connections.CxAPI.get_project_repo_set",
            return_value={'is_set':True,'branch':'master'})
@mock.patch("checkmarx.api_connections.requests.get")
@mock.patch("checkmarx.api_connections.CxAPI.checkmarx_connection",
            return_value='token')
def test_cxapi_get_project_details(cx_conn,req_get,repo_set,last_scan):
    """Tests CxAPI.get_project_details"""
    resp_mock = mock.Mock(status_code=200)
    resp_mock.json.return_value = {'name':'project_name (Baseline)','relatedProjects':[12345,67890],'id':10915}
    req_get.return_value = resp_mock
    response = CxAPI.get_project_details(10915)
    assert cx_conn.call_count == 1
    assert req_get.call_count == 1
    assert repo_set.call_count == 1
    assert last_scan.call_count == 1

if __name__ == '__main__':
    unittest.main()
