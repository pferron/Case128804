'''Unit tests for mend\ticket_handling.py'''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from mend.ticket_handling import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('mend.ticket_handling.select', side_effect=Exception())
@mock.patch('mend.ticket_handling.update', side_effect=Exception())
def test_MendTicketing_tickets_needed_exception(update_mock, select_mock):
    tickets = MendTicketing()
    tickets.tickets_needed('repo')
    update_mock.assert_called_once()
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
@mock.patch('mend.ticket_handling.update')
def test_MendTicketing_tickets_needed(update_mock, select_mock):
    select_mock.return_value = [[25,'License Violation']]
    tickets = MendTicketing()
    tickets.tickets_needed('repo')
    update_mock.assert_called_once()
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
def test_MendTicketing_fp_and_ne_to_close(select_mock):
    select_mock.return_value = [('AS-123','False Positive'),('AS-345','Not Exploitable')]
    tickets = MendTicketing()
    tickets.fp_and_ne_to_close('repo')
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select',side_effect=Exception())
def test_MendTicketing_fp_and_ne_to_close_exception(select_mock):
    tickets = MendTicketing()
    tickets.fp_and_ne_to_close('repo')
    select_mock.assert_called_once()

@mock.patch.object(GeneralTicketing, 'check_past_due')
@mock.patch.object(MendTicketing, 'get_vuln_license_violations',return_value = [{'Ticket': 'AS-123',
                                                                 'DueDate': '2023-07-17'}])
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'To Ticket',
                                        'FoundInLastScan': 1,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_license_violation_active(needed_mock, dedupe_mock, base_mock, severity_mock,
                                                                  ticket_mock, license_mock,pd_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    assert needed_mock.call_count == 1
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()
    pd_mock.assert_called_once()

@mock.patch.object(GeneralTicketing, 'check_past_due')
@mock.patch.object(MendTicketing, 'get_vuln_license_violations',return_value = {'Ticket': 'AS-123',
                                                                 'DueDate': '2023-07-17'})
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'To Ticket',
                                        'FoundInLastScan': 1,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'Other'}])
def test_MendTicketing_create_jira_descriptions_license_violation_other(needed_mock, dedupe_mock, base_mock, severity_mock,
                                                                  ticket_mock, license_mock, pd_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    assert needed_mock.call_count == 1
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()
    pd_mock.assert_called_once()

@mock.patch.object(GeneralTicketing, 'check_past_due')
@mock.patch.object(MendTicketing, 'get_vuln_license_violations',return_value = [{'Ticket': 'AS-123',
                                                                 'DueDate': '2023-07-17'}])
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'To Ticket',
                                        'FoundInLastScan': 0,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_license_violation_not_acitve(needed_mock, dedupe_mock, base_mock, severity_mock,
                                                                  ticket_mock, license_mock, pd_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    assert needed_mock.call_count == 1
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()
    pd_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'tickets_needed',side_effect=Exception())
def test_MendTicketing_create_jira_descriptions_tickets_exception(needed_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'dedupe_mend_tickets',side_effect=Exception())
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_dedupe_exception(needed_mock, dedupe_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_base_fields',side_effect=Exception())
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_basefields_exception(needed_mock, dedupe_mock, base_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_severity', side_effect=Exception())
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'status',
                                        'FoundInLastScan': 0,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_severity_exception(needed_mock, dedupe_mock, base_mock, severity_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_jira_ticket', side_effect=Exception())
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'status',
                                        'FoundInLastScan': 'active',
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_getticket_exception(needed_mock, dedupe_mock, base_mock, severity_mock, ticket_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_vuln_license_violations', side_effect=Exception())
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': 'violations',
                                        'Status': 'status',
                                        'FoundInLastScan': 0,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'License Violation'}])
def test_MendTicketing_create_jira_descriptions_license_exception(needed_mock, dedupe_mock, base_mock, severity_mock, ticket_mock, license_mock):
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_vuln_fields')
@mock.patch.object(GeneralTicketing, 'check_past_due', return_value = True)
@mock.patch.object(MendTicketing, 'get_vuln_license_violations', return_value = {})
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': '',
                                        'Status': 'To Ticket',
                                        'FoundInLastScan': 1,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'Vulnerability'}])
@pytest.mark.parametrize('sev, url',
                         [('Critical','url'),
                          ('High',None),
                          ('Medium','url')
                          ])
def test_MendTicketing_create_jira_descriptions_vulnerability_active(needed_mock, dedupe_mock, base_mock,
                                                              severity_mock, ticket_mock, license_mock,
                                                              pastdue_mock, vuln_mock, sev, url):
    vuln_mock.return_value = [{'Severity': sev,'VulnerabilityUrl': url,
                               'Vulnerability': 'XSS','Remediation':'fix it'}]
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()
    pastdue_mock.assert_called_once()
    vuln_mock.assert_called_once()

@mock.patch.object(MendTicketing, 'get_vuln_fields')
@mock.patch.object(GeneralTicketing, 'check_past_due', return_value = True)
@mock.patch.object(MendTicketing, 'get_vuln_license_violations', return_value = {})
@mock.patch.object(MendTicketing, 'get_jira_ticket', return_value = 'AS-123')
@mock.patch.object(MendTicketing, 'get_severity', return_value = 'Medium')
@mock.patch.object(MendTicketing, 'get_base_fields', return_value = [{'ProjectName': 'pj_name',
                                        'ProjectId': 'pj_id',
                                        'Library': 'lib',
                                        'KeyUuid': 'key',
                                        'LibraryLocations': 'lib_loc',
                                        'LicenseViolations': '',
                                        'Status': 'To Ticket',
                                        'FoundInLastScan': 0,
                                        'Version': 'version'}])
@mock.patch.object(MendTicketing, 'dedupe_mend_tickets', return_value = True)
@mock.patch.object(MendTicketing, 'tickets_needed', return_value =[{'GroupId': 25,
                                                                    'FindingType': 'Vulnerability'}])
@pytest.mark.parametrize('sev, url',
                         [('Critical','url'),
                          ('High',None),
                          ('Medium','url')
                          ])
def test_MendTicketing_create_jira_descriptions_vulnerability__not_active(needed_mock, dedupe_mock, base_mock,
                                                              severity_mock, ticket_mock, license_mock,
                                                              pastdue_mock, vuln_mock, sev, url):
    vuln_mock.return_value = [{'Severity': sev,'VulnerabilityUrl': url,
                               'Vulnerability': 'XSS','Remediation':'fix it'}]
    tickets = MendTicketing()
    tickets.create_jira_descriptions('repo')
    needed_mock.assert_called_once()
    dedupe_mock.assert_called_once()
    base_mock.assert_called_once()
    severity_mock.assert_called_once()
    ticket_mock.assert_called_once()
    license_mock.assert_called_once()
    pastdue_mock.assert_called_once()
    vuln_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
def test_MendTicketing_get_base_fields(select_mock):
    select_mock.return_value = [('ProjectName','ProjectId','Library','KeyUuid','LibraryLocs',
                                 'LicenseViolations','Status','FoundInLastScan','Version'),
                                 ('ProjectName2','ProjectId2','Library2','KeyUuid2','LibraryLocs2',
                                 'LicenseViolations2','Status2','FoundInLastScan2','Version2'),
                                 ('ProjectName','ProjectId2','Library2','KeyUuid2','LibraryLocs2',
                                 'LicenseViolations2','Status2','FoundInLastScan2','Version2')]
    tickets = MendTicketing()
    tickets.get_base_fields(25,'finding_type','repo')
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
def test_get_severity(select_mock):
    select_mock.return_value = [['Medium', 'value']]
    tickets = MendTicketing()
    tickets.get_severity(25, 'repo')
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
def test_get_vuln_fields(select_mock):
    select_mock.return_value = [['fix it']]
    select_mock.return_value = [['XSS','Medium','sevValue']]
    tickets = MendTicketing()
    tickets.get_vuln_fields(25, 'repo')
    assert select_mock.call_count == 2

@mock.patch('mend.ticket_handling.select')
def test_get_vuln_license_violations(select_mock):
    select_mock.return_value = [['AS-123', '2023-07-17']]
    tickets = MendTicketing()
    tickets.get_vuln_license_violations(25, 'repo')
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.select')
@pytest.mark.parametrize('vuln_type',
                         [('Vulnerability'),
                          ('License Violation')
                          ])
def test_get_jira_ticket(select_mock, vuln_type):
    select_mock.return_value = [['AS-123', '2023-07-17']]
    tickets = MendTicketing()
    tickets.get_jira_ticket(25, vuln_type, 'repo')
    select_mock.assert_called_once()

@mock.patch('mend.ticket_handling.update')
@mock.patch('mend.ticket_handling.GeneralTicketing.cancel_jira_ticket')
@mock.patch('mend.ticket_handling.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,cjt_se,cjt_rv,cjt_cnt,sql_upd_se,sql_upd_cnt,response_rv",
                         [("All expected values",None,[('KEY-123','2023-12-01 00:00:05','In Progress'),('KEY-125','2023-12-01 00:00:05','To Do'),],None,True,1,None,1,True),
                          ("Exception: sql_sel",Exception,None,None,None,0,None,0,False),
                          ("Exception: cjt",None,[('KEY-123','2023-12-01 00:00:05','In Progress'),('KEY-125','2023-12-01 00:00:05','To Do'),],Exception,None,1,None,0,False),
                          ("Exception: sql_upd",None,[('KEY-123','2023-12-01 00:00:05','In Progress'),('KEY-125','2023-12-01 00:00:05','To Do'),],None,True,1,Exception,1,True)])
def test_mendticketing_dedupe_mend_tickets(sql_sel,cjt,sql_upd,
                                           description,sql_sel_se,sql_sel_rv,cjt_se,cjt_rv,cjt_cnt,
                                           sql_upd_se,sql_upd_cnt,response_rv):
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    cjt.side_effect = cjt_se
    cjt.return_value = cjt_rv
    sql_upd.side_effect = sql_upd_se
    response = MendTicketing.dedupe_mend_tickets('group_id','repo')
    assert sql_sel.call_count == 1
    assert cjt.call_count == cjt_cnt
    assert sql_upd.call_count == sql_upd_cnt
    assert response == response_rv

if __name__ == '__main__':
    unittest.main()