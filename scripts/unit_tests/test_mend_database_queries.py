'''Unit tests for the database_queries script in mend'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from mend.database_queries import *

@mock.patch("mend.database_queries.select",
            return_value=[('repo',)])
def test_get_repos_with_product_token_on_file(sql_sel):
    '''Tests get_repos_with_product_token_on_file'''
    test = ReportQueries.get_repos_with_product_token_on_file()
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('token',)])
def test_get_product_token(sql_sel):
    '''Tests get_product_token'''
    test = ReportQueries.get_product_token('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value[0][0]

@mock.patch("mend.database_queries.select",
            return_value=[('Repo',)])
def test_alert_exists(sql_sel):
    '''Tests alert_exists'''
    test = ReportQueries.alert_exists('repo','project_name','key_uuid','alert_uuid')
    assert sql_sel.call_count == 1
    assert test is True

@mock.patch("mend.database_queries.select",
            return_value=[('ProjectName','KeyUuid','PolicyViolated','AlertUuid','AlertStatus')])
def test_get_alerts_to_sync(sql_sel):
    '''Tests get_alerts_to_sync'''
    test = ReportQueries.get_alerts_to_sync('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('JiraIssueKey')])
def test_get_ticket_by_finding_type(sql_sel):
    '''Tests get_ticket_by_finding_type'''
    test = ReportQueries.get_ticket_by_finding_type('repo','project_name','finding_type',
                                                    'key_uuid')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value[0][0]

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','Library','ProjectName','KeyUuid')])
def test_get_libraries_missing_data(sql_sel):
    '''Tests get_libraries_missing_data'''
    test = ReportQueries.get_libraries_missing_data('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectName','wsProjectToken')])
def test_get_project_info(sql_sel):
    '''Tests get_project_info'''
    test = ReportQueries.get_project_info('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey')])
def test_get_active_tech_debt(sql_sel):
    '''Tests get_active_tech_debt'''
    test = ReportQueries.get_active_tech_debt('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey','IngestionStatus')])
def test_get_no_fix_active(sql_sel):
    '''Tests get_no_fix_active'''
    test = ReportQueries.get_no_fix_active('repo','msg')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey')])
def test_get_false_positives_active(sql_sel):
    '''Tests get_false_positives_active'''
    test = ReportQueries.get_false_positives_active('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey')])
def test_get_not_exploitables_active(sql_sel):
    '''Tests get_not_exploitables_active'''
    test = ReportQueries.get_not_exploitables_active('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('JiraIssueKey','JiraDueDate')])
def test_get_past_due_tickets(sql_sel):
    '''Tests get_past_due_tickets'''
    test = ReportQueries.get_past_due_tickets('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','KeyUuid','AlertUuid','AlertStatus',
                           'JiraIssueKey')])
def test_get_alerts_to_reactivate(sql_sel):
    '''Tests get_alerts_to_reactivate'''
    test = ReportQueries.get_alerts_to_reactivate('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('JiraIssueKey','JiraDueDate','RITMTicket')])
def test_get_exceptions_to_process(sql_sel):
    '''Tests get_exceptions_to_process'''
    test = ReportQueries.get_exceptions_to_process('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('wsProjectToken','ProjectName','AlertUuid','AlertStatus','JiraIssueKey',
                           'KeyUuid','FindingType')])
def test_get_findings_to_close(sql_sel):
    '''Tests get_findings_to_close'''
    test = ReportQueries.get_findings_to_close('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('ProjectName','ProjectId','Severity','Library','KeyUuid','AlertUuid',
                           'AlertStatus')])
def test_get_license_violations(sql_sel):
    '''Tests get_license_violations'''
    test = ReportQueries.get_license_violations('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('Repo',)])
def test_check_if_finding_exists_vuln(sql_sel):
    '''Tests check_if_finding_exists_vuln'''
    test = ReportQueries.check_if_finding_exists_vuln('repo','project_name','key_uuid','vuln')
    assert sql_sel.call_count == 1
    assert test is True

@mock.patch("mend.database_queries.select",
            return_value=[('JiraProjectKey')])
def test_get_project_key(sql_sel):
    '''Tests get_project_key'''
    test = ReportQueries.get_project_key('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value[0][0]

@mock.patch("mend.database_queries.select",
            return_value=[('AlertUuid','wsProjectToken')])
def test_get_past_due_finding(sql_sel):
    '''Tests get_past_due_finding'''
    test = ReportQueries.get_past_due_finding('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.select",
            return_value=[('AlertUuid','wsProjectToken')])
def test_get_security_exceptions(sql_sel):
    '''Tests get_security_exceptions'''
    test = ReportQueries.get_security_exceptions('repo')
    assert sql_sel.call_count == 1
    assert test == sql_sel.return_value

@mock.patch("mend.database_queries.delete_row")
def test_clear_no_fix_available(sql_del):
    '''Tests clear_no_fix_available'''
    ReportQueries.clear_no_fix_available('repo')
    assert sql_del.call_count == 1

@mock.patch("mend.database_queries.update")
def test_reset_found_in_last_scan_lv(sql_upd):
    '''Tests reset_found_in_last_scan_lv'''
    ReportQueries.reset_found_in_last_scan_lv('repo')
    assert sql_upd.call_count == 1

@mock.patch("mend.database_queries.update")
def test_reset_found_in_last_scan_vuln(sql_upd):
    '''Tests reset_found_in_last_scan_vuln'''
    ReportQueries.reset_found_in_last_scan_vuln('repo','pj_name')
    assert sql_upd.call_count == 1

if __name__ == '__main__':
    unittest.main()
