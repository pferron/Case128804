'''Unit tests for the checkmarx.ticketing script '''

import unittest
from unittest import mock
from unittest.mock import Mock
import sys
import os
import pytest
from checkmarx.ticketing import *
parent=os.path.abspath('.')
sys.path.insert(1,parent)

def test_scrvar_reset_exception_counts():
    '''Tests ScrVar.reset_exception_counts'''
    ScrVar.reset_exception_counts()
    assert ScrVar.fe_cnt == 0
    assert ScrVar.ex_cnt == 0

def test_scrvar_update_exception_info():
    '''Tests ScrVar.update_exception_info'''
    ScrVar.update_exception_info({'FatalCount':3,'ExceptionCount':2})
    assert ScrVar.fe_cnt == 3
    assert ScrVar.ex_cnt == 2
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('1',),])
def test_cxticketing_cx_ticket_set(sql_sel,ex_sql):
    '''Tests CxTicketing.cx_ticket_set'''
    result = CxTicketing.cx_ticket_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_cx_ticket_set_ex_001(sql_sel,ex_sql):
    '''Tests CxTicketing.cx_ticket_set'''
    result = CxTicketing.cx_ticket_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('2024-12-12',0,None,None),])
def test_cxticketing_get_issue_status_to_set_open_reported(sql_sel,ex_sql):
    '''Tests CxTicketing.get_issue_status_to_set'''
    result = CxTicketing.get_issue_status_to_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == ('Open','Reported')

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('2024-12-12',0,'RITM1234',1),])
def test_cxticketing_get_issue_status_to_set_accepted_reported(sql_sel,ex_sql):
    '''Tests CxTicketing.get_issue_status_to_set'''
    result = CxTicketing.get_issue_status_to_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == ('Accepted','Reported')

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('2024-12-12',1,None,None),])
def test_cxticketing_get_issue_status_to_set_tech_debt_reported(sql_sel,ex_sql):
    '''Tests CxTicketing.get_issue_status_to_set'''
    result = CxTicketing.get_issue_status_to_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == ('Tech Debt','Reported')

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('2022-12-12',1,None,None),])
def test_cxticketing_get_issue_status_to_set_past_due_reported(sql_sel,ex_sql):
    '''Tests CxTicketing.get_issue_status_to_set'''
    result = CxTicketing.get_issue_status_to_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == ('Past Due','Reported')

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_issue_status_to_set_open_reported_ex_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_issue_status_to_set'''
    result = CxTicketing.get_issue_status_to_set('AS-1097')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == ('Open','Reported')
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',True,'To Update',
                '1120178-60'),('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',False,'To Close',
                '1120178-60')])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[12345])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest(can_link,ex_func,g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 0
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 1
    assert g_cwe.call_count == 1
    assert findings.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',True,'To Update',
                '1120178-60'),('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',False,'To Close',
                '1120178-60')])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[12345])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_tech_debt(can_link,ex_func,
                                                                              g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',0)
    assert can_link.call_count == 1
    assert ex_func.call_count == 0
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 1
    assert g_cwe.call_count == 1
    assert findings.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',True,'To Update',
                '1120178-60'),('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',False,'To Close',
                '1120178-60')])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_no_sims(can_link,ex_func,
                                                                            g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 0
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 0
    assert g_cwe.call_count == 0
    assert findings.call_count == 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[12345])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_no_findings(can_link,ex_func,
                                                                                g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 0
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 1
    assert g_cwe.call_count == 1
    assert findings.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',True,'To Update',
                '1120178-60'),('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',False,'To Close',
                '1120178-60')])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[12345])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_55_lines(can_link,ex_func,
                                                                             g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',55]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 0
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 1
    assert g_cwe.call_count == 1
    assert findings.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest')
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields')
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest')
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due')
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query')
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            side_effect=Exception)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_ex_001(can_link,ex_func,
                                                                           g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 1
    assert g_severity.call_count == 0
    assert rel_tkts.call_count == 0
    assert is_pd.call_count == 0
    assert g_sims.call_count == 0
    assert q_fields.call_count == 0
    assert g_cwe.call_count == 0
    assert findings.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_findings_for_query_src_and_dest',
            return_value=[('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',True,'To Update',
                '1120178-60'),('scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'scripts/secrets.py; Object: "conjur.get_secret"; Line: 71; Column: 20',
                'The application uses the hard-coded password "conjur.get_secret" for authentication purposes, either using it to verify users identities, or to access another remote system. This password at line 71 of \\scripts\\secrets.py appears in the code, implying it is accessible to anyone with source code access, and cannot be changed without rebuilding\xa0the application.',
                'https://securescanning.progleasing.com/CxWebClient/ViewerMain.aspx?scanid=1120178&projectid=10915&pathid=60',False,'To Close',
                '1120178-60')])
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs':'\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'Use Of Hardcoded Password','QueryDescription':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_sim_ids_by_query_src_and_dest',
            return_value=[12345])
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets_by_query',
            return_value={'ToAppend':['AS-123'],'Related':['AS-987']})
@mock.patch('checkmarx.ticketing.CxTicketing.get_most_severe',
            return_value='High')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_by_query_src_and_dest_ex_002(can_link,ex_func,
                                                                           g_severity,
                                                                    rel_tkts,is_pd,g_sims,q_fields,
                                                                    g_cwe,findings):
    '''Tests CxTicketing.create_jira_descriptions_by_query_src_and_dest'''
    query = [['Use Of Hardcoded Password','scripts/secrets.py','scripts/secrets.py',1]]
    result = CxTicketing.create_jira_descriptions_by_query_src_and_dest(query,10915,
                                                                        'appsec-ops',1)
    assert can_link.call_count == 1
    assert ex_func.call_count == 1
    assert g_severity.call_count == 1
    assert rel_tkts.call_count == 1
    assert is_pd.call_count == 1
    assert g_sims.call_count == 1
    assert q_fields.call_count == 1
    assert g_cwe.call_count == 1
    assert findings.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345',),('67890',)])
def test_cxticketing_get_sim_ids_by_query_src_and_dest(sql_sel,ex_sql):
    '''Tests CxTicketing.get_sim_ids_by_query_src_and_dest'''
    result = CxTicketing.get_sim_ids_by_query_src_and_dest('Query','Source','Destination',10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == ['12345','67890']

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_sim_ids_by_query_src_and_dest_ex_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_sim_ids_by_query_src_and_dest'''
    result = CxTicketing.get_sim_ids_by_query_src_and_dest('Query','Source','Destination',10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == []
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('Source','Destination','Description','Link',1,'Open','12345-6',),])
def test_cxticketing_get_findings_for_query_src_and_dest(sql_sel,ex_sql):
    '''Tests CxTicketing.get_findings_for_query_src_and_dest'''
    result = CxTicketing.get_findings_for_query_src_and_dest('Query',10915,'12345678')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_findings_for_query_src_and_dest_ex_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_findings_for_query_src_and_dest'''
    result = CxTicketing.get_findings_for_query_src_and_dest('Query',10915,'12345678')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value = True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_not_exploitable(ex_reset,log_hl,sql_select,ex_sql,j_close,
                                                     sql_upd,log_ln,u_statuses,ex_upd,ex_func):
    '''Tests CxTicketing.close_or_cancel_not_exploitable'''
    result = CxTicketing.close_or_cancel_not_exploitable('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_select.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 2
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert ex_func.call_count == 0

@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value = True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_not_exploitable_ex_cocne_001(ex_reset,log_hl,sql_select,
                                                                  ex_sql,j_close,sql_upd,log_ln,
                                                                  u_statuses,ex_upd,ex_func):
    '''Tests CxTicketing.close_or_cancel_not_exploitable'''
    result = CxTicketing.close_or_cancel_not_exploitable('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_select.call_count == 1
    assert ex_sql.call_count == 1
    assert j_close.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0
    assert u_statuses.call_count == 0
    assert ex_upd.call_count == 0
    assert ex_func.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_not_exploitable_ex_cocne_002(ex_reset,log_hl,sql_select,
                                                                  ex_sql,j_close,sql_upd,log_ln,
                                                                  u_statuses,ex_upd,ex_func):
    '''Tests CxTicketing.close_or_cancel_not_exploitable'''
    result = CxTicketing.close_or_cancel_not_exploitable('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_select.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 1
    assert u_statuses.call_count == 0
    assert ex_upd.call_count == 0
    assert ex_func.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value = True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_not_exploitable_ex_cocne_003(ex_reset,log_hl,sql_select,
                                                                  ex_sql,j_close,sql_upd,log_ln,
                                                                  u_statuses,ex_upd,ex_func):
    '''Tests CxTicketing.close_or_cancel_not_exploitable'''
    result = CxTicketing.close_or_cancel_not_exploitable('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_select.call_count == 1
    assert ex_sql.call_count == 1
    assert j_close.call_count == 1
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 2
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert ex_func.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.Alerts.manual_alert')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets(ex_reset,log_hl,sql_sel,ex_sql,j_close,ex_func,
                                             sql_upd,log_ln,u_statuses,ex_upd,alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 2
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert alert_man.call_count == 1

@mock.patch('checkmarx.ticketing.Alerts.manual_alert')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses')
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets_ex_coct_001(ex_reset,log_hl,sql_sel,ex_sql,j_close,
                                                         ex_func,sql_upd,log_ln,u_statuses,ex_upd,
                                                         alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert j_close.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0
    assert u_statuses.call_count == 0
    assert ex_upd.call_count == 0
    assert alert_man.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.Alerts.manual_alert')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets_ex_coct_002(ex_reset,log_hl,sql_sel,ex_sql,j_close,
                                                         ex_func,sql_upd,log_ln,u_statuses,ex_upd,
                                                         alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 1
    assert u_statuses.call_count == 0
    assert ex_upd.call_count == 0
    assert alert_man.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.Alerts.manual_alert')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets_ex_coct_003(ex_reset,log_hl,sql_sel,ex_sql,j_close,
                                                         ex_func,sql_upd,log_ln,u_statuses,ex_upd,
                                                         alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert j_close.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 2
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert alert_man.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.Alerts.manual_alert',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets_ex_coct_004(ex_reset,log_hl,sql_sel,ex_sql,j_close,
                                                         ex_func,sql_upd,log_ln,u_statuses,ex_upd,
                                                         alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 2
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert alert_man.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.Alerts.manual_alert')
@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.close_or_cancel_jira_ticket',
            return_value=False)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321',),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_close_or_cancel_tickets_close_failure(ex_reset,log_hl,sql_sel,ex_sql,j_close,
                                                         ex_func,sql_upd,log_ln,u_statuses,ex_upd,
                                                         alert_man):
    '''Tests CxTicketing.close_or_cancel_tickets'''
    result = CxTicketing.close_or_cancel_tickets('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_close.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 1
    assert u_statuses.call_count == 0
    assert ex_upd.call_count == 0
    assert alert_man.call_count == 1

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321','To Do','2024-12-31',None,),
                          ('AS-1234','Done','2024-01-31','2023-07-29'),
                          ('AS-1235','In Progress','2024-01-31',None)])
def test_cxticketing_get_related_tickets(sql_sel,ex_sql):
    '''Tests CxTicketing.get_related_tickets'''
    result = CxTicketing.get_related_tickets(10915,12345)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == {'ToAppend':['AS-4321'],'Related':['AS-1234','AS-1235']}

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_related_tickets_ex_grt_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_related_tickets'''
    result = CxTicketing.get_related_tickets(10915,12345)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == {'ToAppend':None,'Related':None}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-4321','To Do','2024-12-31',None,),
                          ('AS-1234','Done','2024-01-31','2023-07-29'),
                          ('AS-1235','In Progress','2024-01-31',None)])
def test_cxticketing_get_related_tickets_by_query(sql_sel,ex_sql):
    '''Tests CxTicketing.get_related_tickets_by_query'''
    result = CxTicketing.get_related_tickets_by_query('SAST Finding: issue - repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == {'ToAppend':['AS-4321'],'Related':['AS-1234','AS-1235']}

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_related_tickets_by_query_ex_grtbq_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_related_tickets_by_query'''
    result = CxTicketing.get_related_tickets_by_query('SAST Finding: issue - repo')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == {'ToAppend':None,'Related':None}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[(12345,),])
def test_cxticketing_get_needed_sims(sql_sel,ex_sql):
    '''Tests CxTicketing.get_needed_sims'''
    result = CxTicketing.get_needed_sims(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == [12345]

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_needed_sims_ex_gns_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_needed_sims'''
    result = CxTicketing.get_needed_sims(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == []
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('query','s_file','s_file',3),])
def test_cxticketing_get_needed_queries(sql_sel,ex_sql):
    '''Tests CxTicketing.get_needed_queries'''
    result = CxTicketing.get_needed_queries(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == [('query','s_file','s_file',3),]

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_needed_queries_ex_gnq_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_needed_queries'''
    result = CxTicketing.get_needed_queries(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == []
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('Critical',0),])
def test_cxticketing_get_most_severe(sql_sel,ex_sql):
    '''Tests CxTicketing.get_most_severe'''
    result = CxTicketing.get_most_severe('query',10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == 'Critical'

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_most_severe_ex_gms_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_most_severe'''
    result = CxTicketing.get_most_severe('query',10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == 'High'
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.CxTicketing.check_finding_state',
            return_value=1)
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_sims',
            return_value=[12345])
def test_cxticketing_tickets_needed(g_sims,c_state,u_statuses,ex_upd):
    '''Tests CxTicketing.tickets_needed'''
    result = CxTicketing.tickets_needed(10915)
    assert g_sims.call_count == 2
    assert c_state.call_count == 1
    assert u_statuses.call_count == 1
    assert ex_upd.call_count == 1
    assert result == [12345]

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value='appsec_ops')
def test_cxticketing_can_ticket(sql_sel,ex_sql):
    '''Tests CxTicketing.can_ticket'''
    result = CxTicketing.can_ticket(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == {'FatalCount':0,'ExceptionCount':0,'Results':True}

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_can_ticket_ex_tn_001(sql_sel,ex_sql):
    '''Tests CxTicketing.can_ticket'''
    result = CxTicketing.can_ticket(10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result == {'FatalCount':0,'ExceptionCount':1,'Results':False}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update_multiple_in_table',
            return_value=1)
@mock.patch('checkmarx.ticketing.CxAPI.get_finding_details_by_path',
            return_value={'cxLastScanDate':'2023-10-06 06:03:49','cxLastScanID':9876,
                          'cxSimilarityID':74829854,'cxResultState':'Not Exploitable',
                          'cxResultStateValue':1,'cxCWEID':259,'cxCWETitle':'Title',
                          'cxCWEDescription':'Description',
                          'cxCWELink':'https://cwe.mitre.org/data/definitions/259.html'})
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345-6',9876,),])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_last_scan_data',
            return_value={'ID':9876})
def test_cxticketing_check_finding_state(g_scan,ex_func,sql_sel,ex_sql,g_details,mlti_upd):
    '''Tests CxTicketing.check_finding_state'''
    result = CxTicketing.check_finding_state(12345,10915)
    assert g_scan.call_count == 1
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_details.call_count == 1
    assert mlti_upd.call_count == 1
    assert result == 1

@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.CxAPI.get_finding_details_by_path')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_last_scan_data',
            side_effect=Exception)
def test_cxticketing_check_finding_state_ex_cfs_001(g_scan,ex_func,sql_sel,ex_sql,g_details,
                                                    mlti_upd):
    '''Tests CxTicketing.check_finding_state'''
    result = CxTicketing.check_finding_state(12345,10915)
    assert g_scan.call_count == 1
    assert ex_func.call_count == 1
    assert sql_sel.call_count == 0
    assert ex_sql.call_count == 0
    assert g_details.call_count == 0
    assert mlti_upd.call_count == 0
    assert result == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.CxAPI.get_finding_details_by_path')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_last_scan_data',
            return_value={'ID':9876})
def test_cxticketing_check_finding_state_ex_cfs_002(g_scan,ex_func,sql_sel,ex_sql,g_details,
                                                    mlti_upd):
    '''Tests CxTicketing.check_finding_state'''
    result = CxTicketing.check_finding_state(12345,10915)
    assert g_scan.call_count == 1
    assert ex_func.call_count == 0
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_details.call_count == 0
    assert mlti_upd.call_count == 0
    assert result == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxAPI.get_finding_details_by_path',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345-6',9876,),])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_last_scan_data',
            return_value={'ID':9876})
def test_cxticketing_check_finding_state_ex_cfs_003_004(g_scan,ex_func,sql_sel,ex_sql,g_details,
                                                        mlti_upd):
    '''Tests CxTicketing.check_finding_state'''
    result = CxTicketing.check_finding_state(12345,10915)
    assert g_scan.call_count == 1
    assert ex_func.call_count == 2
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_details.call_count == 1
    assert mlti_upd.call_count == 1
    assert result == 0
    assert ScrVar.ex_cnt == 2
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,g_cwe,
                                              g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 0
    assert c_tkts.call_count == 1
    assert c_pd.call_count == 1
    assert g_query.call_count == 1
    assert g_sev.call_count == 1
    assert g_cwe.call_count == 1
    assert g_vulns.call_count == 1
    assert vulns_compact.call_count == 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=False)
def test_cxticketing_create_jira_descriptions_no_linking(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,
                                                         g_cwe,g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 0
    assert c_tkts.call_count == 1
    assert c_pd.call_count == 1
    assert g_query.call_count == 1
    assert g_sev.call_count == 1
    assert g_cwe.call_count == 1
    assert g_vulns.call_count == 1
    assert vulns_compact.call_count == 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':' '*30000 + 'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_long(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,g_cwe,
                                                   g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 0
    assert c_tkts.call_count == 1
    assert c_pd.call_count == 1
    assert g_query.call_count == 1
    assert g_sev.call_count == 1
    assert g_cwe.call_count == 1
    assert g_vulns.call_count == 1
    assert vulns_compact.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':'x'*67000 + 'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_longer(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,
                                                     g_cwe,g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 0
    assert c_tkts.call_count == 1
    assert c_pd.call_count == 1
    assert g_query.call_count == 1
    assert g_sev.call_count == 1
    assert g_cwe.call_count == 1
    assert g_vulns.call_count == 1
    assert vulns_compact.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            side_effect=Exception)
def test_cxticketing_create_jira_descriptions_ex_cjd_001(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,
                                                         g_cwe,g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 1
    assert c_tkts.call_count == 0
    assert c_pd.call_count == 0
    assert g_query.call_count == 0
    assert g_sev.call_count == 0
    assert g_cwe.call_count == 0
    assert g_vulns.call_count == 0
    assert vulns_compact.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns_compact')
@mock.patch('checkmarx.ticketing.CxTicketing.get_vulns',
            return_value={'Vulnerabilities':'Description'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_cwe_details',
            return_value={'CWEs': '\nh2. *CWE Reference:*\n* Links and descriptions.\n'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_severity',
            return_value='Medium')
@mock.patch('checkmarx.ticketing.CxTicketing.get_query_fields',
            return_value={'QueryName':'query','QueryDescription':'query_description'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.check_past_due',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxTicketing.check_for_other_tickets',
            return_value={'ToAppend':['AS-123'],'Related':['AS-321']})
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_related_link_type',
            return_value=True)
def test_cxticketing_create_jira_descriptions_ex_cjd_002(j_links,ex_func,c_tkts,c_pd,g_query,g_sev,
                                                         g_cwe,g_vulns,vulns_compact):
    '''Tests CxTicketing.create_jira_descriptions'''
    result = CxTicketing.create_jira_descriptions([123456],10915,'appsec-ops')
    assert j_links.call_count == 1
    assert ex_func.call_count == 1
    assert c_tkts.call_count == 1
    assert c_pd.call_count == 1
    assert g_query.call_count == 1
    assert g_sev.call_count == 1
    assert g_cwe.call_count == 1
    assert g_vulns.call_count == 1
    assert vulns_compact.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.g_query_desc',
            return_value='Description')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('query','description',),])
def test_cxticketing_get_query_fields(sql_sel,ex_sql,g_qd,ex_func,sql_upd):
    '''Tests CxTicketing.get_query_fields'''
    result = CxTicketing.get_query_fields(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_qd.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert result == {'QueryName':'query','QueryDescription':'description'}

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.g_query_desc',
            return_value='description')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('query',None,),])
def test_cxticketing_get_query_fields_get_description(sql_sel,ex_sql,g_qd,ex_func,sql_upd):
    '''Tests CxTicketing.get_query_fields'''
    result = CxTicketing.get_query_fields(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_qd.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert result == {'QueryName':'query','QueryDescription':'description'}

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.g_query_desc',
            return_value='description')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_query_fields_ex_gqf_001(sql_sel,ex_sql,g_qd,ex_func,sql_upd):
    '''Tests CxTicketing.get_query_fields'''
    result = CxTicketing.get_query_fields(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_qd.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert result == {}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.g_query_desc',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('query',None,),])
def test_cxticketing_get_query_fields_ex_gqf_002(sql_sel,ex_sql,g_qd,ex_func,sql_upd):
    '''Tests CxTicketing.get_query_fields'''
    result = CxTicketing.get_query_fields(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_qd.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert result == {}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.g_query_desc',
            return_value='description')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('query',None,),])
def test_cxticketing_get_query_fields_ex_gqf_003(sql_sel,ex_sql,g_qd,ex_func,sql_upd):
    '''Tests CxTicketing.get_query_fields'''
    result = CxTicketing.get_query_fields(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_qd.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert result == {}
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.VulnDetails.get_cwe',
            return_value={'cwe_id':'CWE-259','name':'Use of Hard-coded Password',
                          'description':'A verbose description',
                          'link':'https://cwe.mitre.org/data/definitions/259.html'})
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('259',None,None,None,'High',1,),])
def test_cxticketing_get_cwe_details(sql_sel,ex_sql,g_cwe,ex_func,sql_upd):
    '''Tests CxTicketing.get_cwe_details'''
    result = CxTicketing.get_cwe_details(74829854,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_cwe.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.VulnDetails.get_cwe',
            return_value={'cwe_id':'CWE-259','name':'Use of Hard-coded Password',
                          'description':'A verbose description',
                          'link':None})
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('259',None,None,None,'Medium',2,),])
def test_cxticketing_get_cwe_details_low_sev_no_link(sql_sel,ex_sql,g_cwe,ex_func,sql_upd):
    '''Tests CxTicketing.get_cwe_details'''
    result = CxTicketing.get_cwe_details(74829854,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_cwe.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.VulnDetails.get_cwe')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_cwe_details_ex_gqf_001(sql_sel,ex_sql,g_cwe,ex_func,sql_upd):
    '''Tests CxTicketing.get_cwe_details'''
    result = CxTicketing.get_cwe_details(74829854,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_cwe.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.VulnDetails.get_cwe',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('259',None,None,None,'High',1,),])
def test_cxticketing_get_cwe_details_ex_gqf_002(sql_sel,ex_sql,g_cwe,ex_func,sql_upd):
    '''Tests CxTicketing.get_cwe_details'''
    result = CxTicketing.get_cwe_details(74829854,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_cwe.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.VulnDetails.get_cwe',
            return_value={'cwe_id':'CWE-259','name':'Use of Hard-coded Password',
                          'description':'A verbose description',
                          'link':'https://cwe.mitre.org/data/definitions/259.html'})
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('259',None,None,None,'High',1,),])
def test_cxticketing_get_cwe_details_ex_gqf_003(sql_sel,ex_sql,g_cwe,ex_func,sql_upd):
    '''Tests CxTicketing.get_cwe_details'''
    result = CxTicketing.get_cwe_details(74829854,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_cwe.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('High',),])
def test_cxticketing_get_severity(sql_sel,ex_sql):
    '''Tests CxTicketing.get_severity'''
    result = CxTicketing.get_severity(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert result == 'High'

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_severity_ex_gs_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_severity'''
    result = CxTicketing.get_severity(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert result is None
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_result_description',
            return_value='A str is returned')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',None,1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),])
def test_cxticketing_get_vulns_one(sql_sel,ex_sql,g_desc,ex_func,sql_upd):
    '''Tests CxTicketing.get_vulns'''
    result = CxTicketing.get_vulns(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_desc.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_result_description',
            return_value='A str is returned')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',None,1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Close','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link','desc',1,'To Ticket','123457-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           None,'2023-10-27'),
                           ('link','desc',1,'To Ticket','12345-6',
                           None,
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),])
def test_cxticketing_get_vulns_many(sql_sel,ex_sql,g_desc,ex_func,sql_upd):
    '''Tests CxTicketing.get_vulns'''
    result = CxTicketing.get_vulns(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_desc.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_result_description',
            return_value='A str is returned')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_vulns_ex_gv_001(sql_sel,ex_sql,g_desc,ex_func,sql_upd):
    '''Tests CxTicketing.get_vulns'''
    result = CxTicketing.get_vulns(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_desc.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_result_description',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',None,1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),])
def test_cxticketing_get_vulns_ex_gv_002(sql_sel,ex_sql,g_desc,ex_func,sql_upd):
    '''Tests CxTicketing.get_vulns'''
    result = CxTicketing.get_vulns(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert g_desc.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.get_result_description',
            return_value='A str is returned')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',None,1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),])
def test_cxticketing_get_vulns_ex_gv_003(sql_sel,ex_sql,g_desc,ex_func,sql_upd):
    '''Tests CxTicketing.get_vulns'''
    result = CxTicketing.get_vulns(12345,10915)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert g_desc.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),])
def test_cxticketing_get_vulns_compact_one(sql_sel,ex_sql):
    '''Tests CxTicketing.get_vulns_compact'''
    result = CxTicketing.get_vulns_compact(12345,10915,'regular')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('link',1,'To Ticket','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27'),
                           ('link',1,'To Close','12345-6',
                           'src; Object: obj; Line: 1; Column: 5',
                           'dest; Object: obj; Line: 1; Column: 5','2023-10-27')])
def test_cxticketing_get_vulns_compact_to_close(sql_sel,ex_sql):
    '''Tests CxTicketing.get_vulns_compact'''
    result = CxTicketing.get_vulns_compact(12345,10915,'super')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0

@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_get_vulns_compact_ex_gvc_001(sql_sel,ex_sql):
    '''Tests CxTicketing.get_vulns_compact'''
    result = CxTicketing.get_vulns_compact(12345,10915,'super')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-1234','2023-10-01 03:45:57',),('AS-1235','2023-10-21 07:26:14',)])
def test_cxticketing_check_for_other_tickets(sql_sel,ex_sql,j_cancel,ex_func,sql_upd,g_related):
    '''Tests CxTicketing.check_for_other_tickets'''
    result = CxTicketing.check_for_other_tickets(12345,10915,'appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_cancel.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert g_related.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-1234','2023-10-01 03:45:57',),])
def test_cxticketing_check_for_other_tickets_only_one(sql_sel,ex_sql,j_cancel,ex_func,sql_upd,
                                                      g_related):
    '''Tests CxTicketing.check_for_other_tickets'''
    result = CxTicketing.check_for_other_tickets(12345,10915,'appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_cancel.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert g_related.call_count == 1

@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
def test_cxticketing_check_for_other_tickets_ex_cfot_001(sql_sel,ex_sql,j_cancel,ex_func,sql_upd,
                                                         g_related):
    '''Tests CxTicketing.check_for_other_tickets'''
    result = CxTicketing.check_for_other_tickets(12345,10915,'appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert j_cancel.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert g_related.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.cancel_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-1234','2023-10-01 03:45:57',),('AS-1235','2023-10-21 07:26:14',)])
def test_cxticketing_check_for_other_tickets_ex_cfot_002(sql_sel,ex_sql,j_cancel,ex_func,sql_upd,
                                                         g_related):
    '''Tests CxTicketing.check_for_other_tickets'''
    result = CxTicketing.check_for_other_tickets(12345,10915,'appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert j_cancel.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert g_related.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.CxTicketing.get_related_tickets')
@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.cancel_jira_ticket',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('AS-1234','2023-10-01 03:45:57',),('AS-1235','2023-10-21 07:26:14',)])
def test_cxticketing_check_for_other_tickets_ex_cfot_003(sql_sel,ex_sql,j_cancel,ex_func,sql_upd,
                                                         g_related):
    '''Tests CxTicketing.check_for_other_tickets'''
    result = CxTicketing.check_for_other_tickets(12345,10915,'appsec-ops')
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert j_cancel.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert g_related.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update',
            return_value=1)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345-6','AS-1234'),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_add_tickets_to_cx(ex_reset,log_hl,sql_sel,ex_sql,cx_tkt,ex_func,
                                       sql_upd,log_ln):
    '''Tests CxTicketing.add_tickets_to_cx'''
    result = CxTicketing.add_tickets_to_cx('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert cx_tkt.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 1

@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_add_tickets_to_cx_ex_attc_001(ex_reset,log_hl,sql_sel,ex_sql,cx_tkt,ex_func,
                                       sql_upd,log_ln):
    '''Tests CxTicketing.add_tickets_to_cx'''
    result = CxTicketing.add_tickets_to_cx('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert cx_tkt.call_count == 0
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 0
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345-6','AS-1234'),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_add_tickets_to_cx_ex_attc_002(ex_reset,log_hl,sql_sel,ex_sql,cx_tkt,ex_func,
                                                   sql_upd,log_ln):
    '''Tests CxTicketing.add_tickets_to_cx'''
    result = CxTicketing.add_tickets_to_cx('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 0
    assert cx_tkt.call_count == 1
    assert ex_func.call_count == 1
    assert sql_upd.call_count == 0
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.select',
            return_value=[('12345-6','AS-1234'),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_add_tickets_to_cx_ex_attc_003(ex_reset,log_hl,sql_sel,ex_sql,cx_tkt,ex_func,
                                                   sql_upd,log_ln):
    '''Tests CxTicketing.add_tickets_to_cx'''
    result = CxTicketing.add_tickets_to_cx('appsec-ops',10915)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == 1
    assert cx_tkt.call_count == 1
    assert ex_func.call_count == 0
    assert sql_upd.call_count == 1
    assert log_ln.call_count == 1
    assert ScrVar.ex_cnt == 1
    ScrVar.ex_cnt = 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set')
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
@pytest.mark.parametrize("g_status_rv",
                         [('Open', 'Reported'),
                          ('Accepted', 'Reported')])
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest(ex_reset,log_hl,g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins,g_status_rv):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    g_status.return_value = g_status_rv
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 4
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 2
    assert add_tkt.call_count == 2
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date')
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set')
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest')
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries')
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=None)
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_no_g_jira_info(ex_reset,log_hl,
                                                                    g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1
    assert g_queries.call_count == 0
    assert c_desc.call_count == 0
    assert g_status.call_count == 0
    assert g_due.call_count == 0
    assert u_tkt.call_count == 0
    assert s_due.call_count == 0
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 0
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date')
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set')
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest')
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries')
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_g_jira_info(ex_reset,log_hl,
                                                                    g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 0
    assert g_queries.call_count == 0
    assert c_desc.call_count == 0
    assert g_status.call_count == 0
    assert g_due.call_count == 0
    assert u_tkt.call_count == 0
    assert s_due.call_count == 0
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 0
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date')
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set')
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest')
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_no_g_queries(ex_reset,log_hl,
                                                                                  g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 1
    assert g_queries.call_count == 1
    assert c_desc.call_count == 0
    assert g_status.call_count == 0
    assert g_due.call_count == 0
    assert u_tkt.call_count == 0
    assert s_due.call_count == 0
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 0
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_no_c_desc(ex_reset,log_hl,
                                                                               g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 0
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 0
    assert g_due.call_count == 0
    assert u_tkt.call_count == 0
    assert s_due.call_count == 0
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 0
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_no_updates(ex_reset,log_hl,
                                                                                g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert log_ln.call_count == 0
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 0
    assert g_due.call_count == 0
    assert u_tkt.call_count == 0
    assert s_due.call_count == 0
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 0
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx')
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_u_tkt(ex_reset,log_hl,
                                                                              g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 3
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 1
    assert add_tkt.call_count == 0
    assert rel_tkts.call_count == 0
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_s_due(ex_reset,log_hl,
                                                                              g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 3
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 0
    assert tkt_set.call_count == 1
    assert add_tkt.call_count == 1
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_c_ticket(ex_reset,log_hl,
                                                                                 g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 3
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 1
    assert add_tkt.call_count == 1
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_add_tkt(ex_reset,log_hl,g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 2
    assert log_ln.call_count == 4
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 2
    assert add_tkt.call_count == 2
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_rel_tkts(ex_reset,log_hl,
                                                                                 g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 4
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 2
    assert add_tkt.call_count == 2
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_mlti_upd(ex_reset,log_hl,g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 3
    assert log_ln.call_count == 4
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 2
    assert add_tkt.call_count == 2
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.CxAPI.add_ticket_to_cx',
            return_value=True)
@mock.patch('checkmarx.ticketing.CxTicketing.cx_ticket_set',
            return_value=0)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.get_issue_status_to_set',
            return_value=('Open', 'Reported'))
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions_by_query_src_and_dest',
            return_value={'Descriptions':[{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'High',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':['AS-123'],
            'Related':['AS-987']},'SimilarityIDs':'7482985','Description':
            'The description for Jira','Findings':['1120178-60']},{'Summary':
            'SAST Finding: cxQuery (SourceFile to DestFile) - appsec-ops','Severity':'Medium',
            'Labels':['security_finding','appsec-ops'],'RelatedTickets':{'ToAppend':[],
            'Related':[]},'SimilarityIDs':'73482985','Description':
            'The description for Jira','Findings':['1120178-64']}],'LinkTickets': True})
@mock.patch('checkmarx.ticketing.CxTicketing.get_needed_queries',
            return_value=[('cxQuery','SourceFile','DestinationFile',1),])
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_by_query_src_and_dest_ex_mlti_ins(ex_reset,log_hl,
                                                                                 g_jira_info,
                                                                     ex_func,log_ln,g_queries,
                                                                     c_desc,g_status,g_due,u_tkt,
                                                                     s_due,c_ticket,tkt_set,
                                                                     add_tkt,rel_tkts,mlti_upd,
                                                                     mlti_ins):
    """Tests CxTicketing.create_and_update_tickets_by_query_src_and_dest"""
    CxTicketing.create_and_update_tickets_by_query_src_and_dest('repo',1234567890)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert log_ln.call_count == 4
    assert g_queries.call_count == 1
    assert c_desc.call_count == 1
    assert g_status.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert c_ticket.call_count == 1
    assert tkt_set.call_count == 2
    assert add_tkt.call_count == 2
    assert rel_tkts.call_count == 1
    assert mlti_upd.call_count == 3
    assert mlti_ins.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert s_due.call_count == 1
    assert u_tkt.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses')
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions')
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date')
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions')
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_g_jira_info(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 0
    assert g_due.call_count == 0
    assert s_due.call_count == 0
    assert u_tkt.call_count == 0
    assert has_repo_ex.call_count == 0
    assert c_tkt.call_count == 0
    assert add_cmt.call_count == 0
    assert rel_tkt.call_count == 0
    assert mlti_upd.call_count == 0
    assert mlti_ins.call_count == 0
    assert sql_upd.call_count == 0
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 0
    assert u_statuses.call_count == 0
    assert ex_info.call_count == 0

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',0,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_u_ticket(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert s_due.call_count == 1
    assert u_tkt.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 3
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_s_due(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert has_repo_ex.call_count == 0
    assert c_tkt.call_count == 0
    assert add_cmt.call_count == 0
    assert rel_tkt.call_count == 0
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 3
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_has_repo(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 0
    assert add_cmt.call_count == 0
    assert rel_tkt.call_count == 0
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 3
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_c_tkt(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 0
    assert rel_tkt.call_count == 0
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 3
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_add_cmt(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_rel_tkt(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert u_tkt.call_count == 1
    assert s_due.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_mlti_upd(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert s_due.call_count == 1
    assert u_tkt.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update')
@mock.patch('checkmarx.ticketing.insert_multiple_into_table',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_mlti_ins(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 1
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert s_due.call_count == 1
    assert u_tkt.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 0
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

@mock.patch('checkmarx.ticketing.ScrVar.update_exception_info')
@mock.patch('checkmarx.ticketing.CxReports.update_finding_statuses',
            return_value={'FatalCount':0,'ExceptionCount':0})
@mock.patch('checkmarx.ticketing.TheLogs.log_info')
@mock.patch('checkmarx.ticketing.TheLogs.sql_exception')
@mock.patch('checkmarx.ticketing.update',
            side_effect=Exception)
@mock.patch('checkmarx.ticketing.insert_multiple_into_table')
@mock.patch('checkmarx.ticketing.update_multiple_in_table')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_related_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.add_comment_to_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.create_jira_ticket',
            return_value='ABC-123')
@mock.patch('checkmarx.ticketing.GeneralTicketing.has_repo_exceptions',
            return_value={'Due':'2024-10-10','RITMTicket':'ExTicket','Standard':'IS1010.120',
                          'Duration':2,'Approved':'2023-11-24 12:12:12'})
@mock.patch('checkmarx.ticketing.GeneralTicketing.set_due_date',
            return_value='2024-01-24')
@mock.patch('checkmarx.ticketing.GeneralTicketing.update_jira_ticket')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_ticket_due_date',
            return_value={'FatalCount':0,'ExceptionCount':0,'Results':'2024-01-24'})
@mock.patch('checkmarx.ticketing.CxTicketing.create_jira_descriptions',
            return_value=[{'cxSimilarityId':74829854,'ExistingTicket':'AS-4321','Severity':'Medium',
                'Summary':'SAST Finding: Use Of Hardcoded Password - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-259: Use of Hard-coded Password|https://cwe.mitre.org/data/definitions/259.html]* - {color:#ff991f}*Medium*{color}\nThe software contains a hard-coded password, which it uses for its own inbound authentication or for outbound communication to external components.\n',
                'RelatedTickets':[]},
                {'cxSimilarityId':-952405625,'ExistingTicket':None,'Severity':'Medium',
                'Summary':'SAST Finding: Hardcoded Password in Connection String - appsec-ops',
                'Description':'h6. Ticket updated by automation on October 30, 2023.\nh2. *CWE Reference:*\n* *[CWE-547: Use of Hard-coded, Security-relevant Constants|https://cwe.mitre.org/data/definitions/547.html]* - {color:#ff991f}*Medium*{color}\nThe program uses hard-coded constants instead of symbolic names for security-critical values, which increases the likelihood of mistakes during code maintenance or security policy change.\n',
                'RelatedTickets':['AS-1189']}])
@mock.patch('checkmarx.ticketing.TheLogs.function_exception')
@mock.patch('checkmarx.ticketing.GeneralTicketing.get_jira_info',
            return_value=[(0,'PROG','PROG-123456789',1,),])
@mock.patch('checkmarx.ticketing.CxTicketing.tickets_needed',
            return_value=[123456,-654321])
@mock.patch('checkmarx.ticketing.TheLogs.log_headline')
@mock.patch('checkmarx.ticketing.ScrVar.reset_exception_counts')
def test_cxticketing_create_and_update_tickets_ex_sql_upd(ex_reset,log_hl,need_tkts,g_jira_info,ex_func,
                                               c_desc,g_due,u_tkt,s_due,has_repo_ex,c_tkt,add_cmt,
                                               rel_tkt,mlti_upd,mlti_ins,sql_upd,ex_sql,log_ln,
                                               u_statuses,ex_info):
    """Tests CxTicketing.create_and_update_tickets"""
    CxTicketing.create_and_update_tickets('repo',9876543210)
    assert ex_reset.call_count == 1
    assert log_hl.call_count == 1
    assert need_tkts.call_count == 1
    assert g_jira_info.call_count == 1
    assert ex_func.call_count == 0
    assert c_desc.call_count == 1
    assert g_due.call_count == 1
    assert s_due.call_count == 1
    assert u_tkt.call_count == 1
    assert has_repo_ex.call_count == 1
    assert c_tkt.call_count == 1
    assert add_cmt.call_count == 1
    assert rel_tkt.call_count == 1
    assert mlti_upd.call_count == 1
    assert mlti_ins.call_count == 1
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == 1
    assert log_ln.call_count == 4
    assert u_statuses.call_count == 1
    assert ex_info.call_count == 1

if __name__ == '__main__':
    unittest.main()
