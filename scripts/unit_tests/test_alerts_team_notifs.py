'''Unit tests for the team_notifs script '''

import unittest
from unittest import mock
import sys
import os
parent = os.path.abspath('.')
sys.path.insert(1,parent)
import pytest
import datetime
sys.modules['common.database_sql_server_connection'] = mock.MagicMock()
from scripts.alerts_team_notifs import *

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

@mock.patch.object(General,'cmd_processor',return_value=[{'function': 'class_setup',
                                                          'args': 'weekly'}])
@mock.patch("scripts.alerts_team_notifs.class_setup")
def test_main(cmd_mock,class_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_team_notifs.py', 'class_setup(weekly)']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()
        class_mock.assert_called_once()

@mock.patch.object(General,'cmd_processor',return_value=[{'function':
                                                          'no_slack_url_alert'}])
@mock.patch("scripts.alerts_team_notifs.no_slack_url_alert")
def test_main_no_script_args(cmd_mock,class_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_team_notifs.py', 'no_slack_url_alert()']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()
        class_mock.assert_called_once()

@mock.patch.object(General,'cmd_processor',return_value=[])
def test_main_no_sys_args(cmd_mock):
    '''tests main'''
    testargs = [r'c:\AppSec\scripts\\alerts_team_notifs.py']
    # arg_cnt = 2
    with mock.patch.object(sys, "argv", testargs):
        main()
        cmd_mock.assert_called_once()

@mock.patch.object(Misc, "end_timer")
@mock.patch.object(Misc, "start_timer")
@mock.patch.object(GetInfoSendNotif, "epic_check")
def test_class_setup(epic_check_mock,s_timer_mock,e_timer_mock):
    '''tests class setup function'''
    notif_manager_mock= GetInfoSendNotif()
    notif_manager_mock.time = 'time'
    class_setup('time')
    s_timer_mock.assert_called_once()
    epic_check_mock.assert_called_once()
    e_timer_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_epics_with_epics(conn_mock):
    '''test when there are epics to process'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = ['epic']
    res = send_notif_mock.get_epics()
    conn_mock.query_with_logs.assert_called_once()
    assert res is not None

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_epics_no_epics(conn_mock):
    '''test when there are no epics to process'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = []
    res = send_notif_mock.get_epics()
    conn_mock.query_with_logs.assert_called_once()
    assert not res

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch.object(GetInfoSendNotif, "get_epics")
def test_epic_check_no_epics(list_epics_mock, log_mock):
    '''tests when get_epics = []'''
    send_notif = GetInfoSendNotif()
    list_epics_mock.return_value = []
    send_notif.epic_check()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch.object(GetInfoSendNotif, "get_epics")
def test_epic_check_none_epics(epic_list_mock, log_mock):
    '''tests when get_epics = None'''
    send_notif = GetInfoSendNotif()
    epic_list_mock.return_value = None
    send_notif.epic_check()
    log_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "get_epics")
@mock.patch.object(GetInfoSendNotif, "process_ticket_epics")
def test_epic_check_with_epics(process_mock, epic_mock):
    '''tests when get_epics has results'''
    send_notif = GetInfoSendNotif()
    send_notif.time = 'daily'
    send_notif.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    epic_mock.return_value = [('AS-137', )]
    send_notif.epic_check()
    assert send_notif.epic_list == ['AS-137']
    process_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "slack_router")
@mock.patch.object(GetInfoSendNotif, "get_slack_jira_details")
@mock.patch.object(GetInfoSendNotif, "process_tickets")
def test_process_ticket_epics_regular_findings(process_ticket_mock, slack_deets_mock, router_mock):
    '''tests when no slack url is available in ProgTeams table'''
    send_notif = GetInfoSendNotif()
    send_notif.epic_list = ["AS-138"]
    slack_deets_mock.return_value = ["url","team","opentail","overduetail"]
    send_notif.process_ticket_epics()
    process_ticket_mock.assert_called_once()
    router_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "slack_send_totals")
@mock.patch.object(GetInfoSendNotif, "slack_router")
@mock.patch.object(GetInfoSendNotif, "slack_team_header_setup")
@mock.patch.object(GetInfoSendNotif, "get_pt_prog_team")
@mock.patch.object(GetInfoSendNotif, "process_pentest_tickets")
@mock.patch.object(GetInfoSendNotif, "get_slack_jira_details")
def test_process_ticket_epics_pentest_findings(slack_deets_mock, process_pentest_mock,
                                               pt_team_mock, slack_header_mock,
                                               slack_router_mock, slack_totals_mock):
    send_notif = GetInfoSendNotif()
    send_notif.epic_list = ['AS-139']
    slack_deets_mock.return_value = 'no_slack'
    process_pentest_mock.return_value = (['AS-145'], {'AS-345':['duedate','priority','summary']})
    send_notif.process_ticket_epics()
    process_pentest_mock.assert_called_once()
    pt_team_mock.assert_called_once()
    slack_header_mock.assert_called_once()
    slack_router_mock.assert_called_once()
    slack_totals_mock.assert_called_once()

@mock.patch("scripts.alerts_team_notifs.no_slack_url_alert")
def test_process_ticket_epics_no_slacktail(no_slack_mock):
    send_notif = GetInfoSendNotif()
    send_notif.no_slack_tail = ['AS-121']
    send_notif.process_ticket_epics()
    no_slack_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_issues_with_epics(conn_mock):
    '''test when there are epics to get Jira tickets from'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = ['AS-123', 'AS-456']
    res = send_notif_mock.get_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    assert res == ['AS-123', 'AS-456']

@mock.patch.object(GetInfoSendNotif, "get_license_issues")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_issues_with_epics_monthly(conn_mock, license_mock):
    '''test when there are epics to get Jira tickets from'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'monthly'
    send_notif_mock.sql_condition = {'monthly': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = ['AS-123', 'AS-456']
    license_mock.return_value = ['AS-111', 'AS-222']
    res = send_notif_mock.get_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    assert res == ['AS-123', 'AS-456','AS-111', 'AS-222']

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_license_issues_none(conn_mock, log_mock):
    '''tests getting license issues'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'monthly'
    send_notif_mock.sql_condition = {'monthly': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = []
    send_notif_mock.get_license_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_license_issues(conn_mock):
    '''tests getting license issues'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'monthly'
    send_notif_mock.sql_condition = {'monthly': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = ['AS-123']
    send_notif_mock.get_license_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()


@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_issues_no_epics(conn_mock, log_mock):
    '''test when there are NO epics to get Jira tickets from'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = []
    send_notif_mock.get_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_pentest_issues_with_epics(conn_mock):
    '''test when there are epics to get Jira tickets from for pentest findings'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = ['AS-124', 'AS-456']
    res = send_notif_mock.get_pentest_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    assert res == ['AS-124', 'AS-456']

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_pentest_issues_no_epics(conn_mock, log_mock):
    '''test when there are NO epics to get Jira tickets from for pentest findings'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.time = 'daily'
    send_notif_mock.sql_condition = {'daily': 'CreatedDateTime >= DATEADD(HOUR, -24, getdate())'}
    conn_mock.query_with_logs.return_value = []
    send_notif_mock.get_pentest_issues('AS-789')
    conn_mock.query_with_logs.assert_called_once()
    log_mock.assert_called_once()

def test_get_pentest_issue_keys():
    '''test to get issue list and extract Jira keys'''
    send_notif_mock = GetInfoSendNotif()
    res = send_notif_mock.get_pentest_issue_keys(['AS-125'])
    assert res == ['AS']

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_parent_epic_noparent(conn_mock, log_mock):
    '''tests when Jira issue key does not have a JiraParentKey'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    conn_mock.query_with_logs.return_value = []
    send_notif_mock.get_parent_epic(['ABC'])
    conn_mock.query_with_logs.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_parent_epic(conn_mock):
    '''tests when Jira issue key does have a JiraParentKey'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.conn.return_value = [('ABC-123', )]
    send_notif_mock.get_parent_epic(['ABC'])
    send_notif_mock.conn.query_with_logs.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_slack_jira_details_no_slack(conn_mock, log_mock):
    '''test when there are epics to get Jira tickets from'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    conn_mock.query_with_logs.return_value = []
    res = send_notif_mock.get_slack_jira_details('AS-126')
    conn_mock.query_with_logs.assert_called_once()
    log_mock.assert_called_once()
    assert res == 'no_slack'

@mock.patch.object(GetInfoSendNotif, "slack_filter_message_setup")
@mock.patch("alerts_team_notifs.SQLServerConnection.query_with_logs")
def test_get_slack_jira_details_with_details(conn_mock, notif_mock):
    '''test when there are epics to get Jira tickets from'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.conn.return_value = ['slacktail','team','opentail','overduetail']
    send_notif_mock.get_slack_jira_details('AS-127')
    notif_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif,"get_issue_details")
@mock.patch.object(GetInfoSendNotif, "slack_team_header_setup")
@mock.patch.object(GetInfoSendNotif, "get_issues")
def test_process_tickets(issue_mock, notif_mock, details_mock):
    '''test for getting issues and the details and combining into dictionary'''
    notif_manager = GetInfoSendNotif()
    issue = issue_mock.return_value = [('AS-345',)]
    details = details_mock.return_value = ['duedate','priority','summary']
    issue_details = {issue[0][0]: details}
    res = notif_manager.process_tickets('AS-128')
    notif_mock.assert_called_once()
    assert res == issue_details

@mock.patch.object(GetInfoSendNotif,"get_pentest_issue_keys")
@mock.patch.object(GetInfoSendNotif,"get_parent_epic")
@mock.patch.object(GetInfoSendNotif,"get_issue_details")
@mock.patch.object(GetInfoSendNotif, "get_pentest_issues")
def test_process_pentest_tickets(issues_mock, details_mock, parent_mock, keys_mock):
    '''test for getting pentest issues and the details and combining into dictionary'''
    notif_manager = GetInfoSendNotif()
    issue = issues_mock.return_value = [('AS-345',)]
    details = details_mock.return_value = ['duedate','priority','summary']
    issue_details = {issue[0][0]: details}
    issue_keys = keys_mock.return_value = ['AS']
    parent = parent_mock.return_value = 'AS-145'
    res = notif_manager.process_pentest_tickets('AS-129')
    assert res == (parent, issue_details)

@ mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch.object(GetInfoSendNotif, "get_pentest_issues")
def test_process_pentest_tickets_no_issues(issues_mock, log_mock):
    '''test for getting pentest issues and the details and combining into dictionary'''
    notif_manager = GetInfoSendNotif()
    issues_mock.return_value = None
    res = notif_manager.process_pentest_tickets('AS-130')
    assert res == 'no pen test issues'
    log_mock.assert_called_once()

def test_slack_filter_message_setup_weekly():
    '''tests message based weekly'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'weekly'
    send_notif_mock.jira_overdue_tail = ' overdue'
    send_notif_mock.slack_filter_message_setup()
    assert send_notif_mock.slack_filter_message == 'Jira Filter for overdue findings: <https://progfin.atlassian.net overdue|*Click here*> '

def test_slack_filter_message_setup_monthly():
    '''tests message based monthly'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'monthly'
    send_notif_mock.jira_open_tail = ' open'
    send_notif_mock.slack_filter_message_setup()
    assert send_notif_mock.slack_filter_message == 'Jira Filter for open findings: <https://progfin.atlassian.net open|*Click here*>'

def test_slack_team_header_setup_weekly():
    '''tests message based weekly'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'weekly'
    send_notif_mock.prog_team = 'getterdone'
    send_notif_mock.issue_count = 10
    send_notif_mock.p_test = ''
    send_notif_mock.slack_team_header_setup()
    assert send_notif_mock.slack_team_header == ':alert: Weekly Alert: getterdone Team     :alert: \\n\\nThere are 10 overdue finding(s)!!!'

def test_slack_team_header_setup_monthly():
    '''tests message based monthly'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'monthly'
    send_notif_mock.prog_team = 'getterdone'
    send_notif_mock.issue_count = 10
    send_notif_mock.p_test = ''
    send_notif_mock.slack_team_header_setup()
    assert send_notif_mock.slack_team_header == ':alarm:  Monthly Alert: getterdone Team    :alarm: \\n\\nThere are 10 upcoming and/or overdue finding(s)'

@mock.patch("alerts_team_notifs.GetInfoSendNotif.daily_slack_message")
def test_slack_router_daily(notif_mock):
    '''test slack router for daily timeframe'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.daily_slack_message = notif_mock
    send_notif_mock.time = 'daily'
    details = {'AS-140': ['duedate','priority','summary']}
    send_notif_mock.slack_router(details)
    notif_mock.assert_called_once()

@mock.patch("alerts_team_notifs.GetInfoSendNotif.daily_slack_message")
def test_slack_router_test(notif_mock):
    '''test slack router for test timeframe'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.daily_slack_message = notif_mock
    send_notif_mock.time = 'test'
    details = {'AS-130': ['duedate','priority','summary']}
    send_notif_mock.slack_router(details)
    notif_mock.assert_called_once()

@mock.patch("alerts_team_notifs.GetInfoSendNotif.weekly_monthly_message")
def test_slack_router_other(notif_mock):
    '''test slack router for other timeframe'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.weekly_monthly_message = notif_mock
    send_notif_mock.time = 'other'
    details = {'AS-141': ['duedate','priority','summary']}
    send_notif_mock.slack_router(details)
    notif_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "get_slack_jira_details")
def test_get_pt_prog_team(notif_mock):
    '''test getting prog_team for pen test findings from epic'''
    notif_mock.return_value = [('slack', 'team', 'open', 'overdue')]
    send_notif_mock = GetInfoSendNotif()
    res = send_notif_mock.get_pt_prog_team('AS-132')
    assert res == 'team'

@mock.patch("alerts_team_notifs.WebhookClient.send")
def test_slack_send(webhook_client_mock):
    '''tests slack message send'''
    header_block = '[{"type": "header"},'
    message_block = '{"type": "message"},'
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.slack_send(header_block, message_block)
    webhook_client_mock.assert_called_once()

@ mock.patch("alerts_team_notifs.TheLogs.log_headline")
def test_slack_log_200(log_mock, mock_response_200):
    '''test slack router for other timeframe'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'daily'
    send_notif_mock.p_test = ''
    send_notif_mock.prog_team = 'team'
    send_notif_mock.log_condition = {'daily': 'NEW '}
    send_notif_mock.slack_log(mock_response_200)
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.function_exception")
def test_slack_log_400(log_mock, mock_response_400):
    '''test slack router for other timeframe'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.time = 'daily'
    send_notif_mock.p_test = ''
    send_notif_mock.prog_team = 'team'
    send_notif_mock.log_condition = {'daily': 'NEW '}
    send_notif_mock.slack_log(mock_response_400)
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
def test_slack_send_totals_0(log_mock):
    '''tests slack_send_totals for count 0'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.notif_count = 0
    send_notif_mock.slack_send_totals()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
def test_slack_send_totals_else(log_mock):
    '''tests slack_send_totals for count >0'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.notif_count = 5
    send_notif_mock.time = 'daily'
    send_notif_mock.log_condition = {'daily': 'NEW '}
    send_notif_mock.slack_send_totals()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.SQLServerConnection")
def test_get_issue_details(conn_mock):
    '''tests getting issue details from ticket number'''
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.conn = conn_mock
    send_notif_mock.conn.query_with_logs.return_value = ['due date', 'priority', 'summary']
    res = send_notif_mock.get_issue_details('AS-133')
    assert res == ['due date', 'priority', 'summary']

@mock.patch.object(GetInfoSendNotif, "slack_send")
def test_daily_slack_message(send_mock):
    '''this tests building of the daily slack message'''
    issue_details = {"AS-134":[(datetime.date(2023, 11, 5), 'priority', 'summary')]}
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.p_test = ''
    send_notif_mock.prog_team = 'team'
    issue_url = 'url'
    send_notif_mock.daily_slack_message(issue_details)
    send_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "slack_send")
def test_weekly_monthly_message_lessthan_50(send_mock):
    '''this tests building of the weekly/monthly slack message less than 50 issues'''
    issue_details = {"AS-135":[(datetime.date(2023, 11, 5), 'priority', 'summary')]}
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.p_test = ''
    send_notif_mock.prog_team = 'team'
    send_notif_mock.issue_count = 2
    issue_url = 'url'
    send_notif_mock.weekly_monthly_message(issue_details)
    send_mock.assert_called_once()

@mock.patch.object(GetInfoSendNotif, "slack_send")
def test_weekly_monthly_message_morethan_50(send_mock):
    '''this tests building of the weekly/monthly slack message more than 50 issues'''
    issue_details = {"AS-136":[(datetime.date(2023, 11, 5), 'priority', 'summary')]}
    send_notif_mock = GetInfoSendNotif()
    send_notif_mock.p_test = ''
    send_notif_mock.prog_team = 'team'
    send_notif_mock.issue_count = 60
    issue_url = 'url'
    send_notif_mock.weekly_monthly_message(issue_details)
    send_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.WebhookClient.send")
def test_no_slack_url_alert_200(webhook_client_mock, log_mock, mock_response_200):
    '''test successful slack message when there is no slack url for team'''
    teams = ['teams']
    webhook_client_mock.return_value = mock_response_200
    no_slack_url_alert(teams)
    webhook_client_mock.assert_called_once()
    log_mock.assert_called_once()

@mock.patch("alerts_team_notifs.TheLogs.log_headline")
@mock.patch("alerts_team_notifs.WebhookClient.send")
def test_no_slack_url_alert_400(webhook_client_mock, log_mock, mock_response_400):
    '''test unsuccessful slack message when there is no slack url for team'''
    teams = ['teams']
    webhook_client_mock.return_value = mock_response_400
    no_slack_url_alert(teams)
    webhook_client_mock.assert_called_once()
    log_mock.assert_called_once()

if __name__ == '__main__':
    unittest.main()