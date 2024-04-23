'''This module is used to send Slack notifications using Task Scheduler to Teams
regarding vulnerability Jira tickets creation and remediation'''

import sys
import os
import json
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from slack_sdk.webhook import WebhookClient
from common.logging import TheLogs
from common.constants import JIRA_SERVER, JIRA_TICKET_ROOT, SLACK_ROOT
from common.database_sql_server_connection import SQLServerConnection
from common.general import General
from common.miscellaneous import Misc
from dataclasses import dataclass, field

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
logs = TheLogs()
LOG = logs.setup_logging(LOG_FILE)
LOG_EXCEPTION = logs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

@dataclass
class ScrVars:
    """For use in any of the functions"""
    func : str = ''
    e_cnt : int = 0
    fe_cnt : int = 0
    e_array : list[str] = field(default_factory=list)
    fe_array : list[str] = field(default_factory=list)

def main():
    """Executes default stuff and allows for command line script run of class_setup"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # class_setup('monthly')
    # notif_manager= GetInfoSendNotif()
    # notif_manager.get_issue_details('CD-408')

def class_setup(timeframe):
    '''sets up notif_manager class and kicks off first function'''
    global notif_manager, log_variables
    running_function = 'class_setup'
    start_timer = Misc.start_timer()
    log_variables = ScrVars()
    notif_manager= GetInfoSendNotif()
    notif_manager.time = timeframe
    notif_manager.epic_check()
    Misc.end_timer(start_timer,rf'{ALERT_SOURCE}',running_function,ScrVars.e_cnt,ScrVars.fe_cnt)
    return notif_manager

@dataclass
class GetInfoSendNotif:
    '''
    get the Jira info associated with queries in the methods below
    using timeframe in sql_condition attribute
    '''
    sql_condition : dict[str,str] = field(default_factory=lambda:{'daily':'CreatedDateTime >= DATEADD(HOUR, -24, GETDATE())', 'weekly':'JiraDueDate <= GETDATE()','monthly':'JiraDueDate BETWEEN DATEADD(MONTH, -20, GETDATE()) AND DATEADD(MONTH, 1, GETDATE())', 'test':'CreatedDateTime >= DATEADD(MONTH, -20, GETDATE())' })
    epic_list : list[str] = field(default_factory=list)
    no_slack_tail : list[str] = field(default_factory=list)
    slack_tail : str = ''
    time : str = ''
    slack_team_header : str = ''
    slack_filter_message : str = ''
    log_condition : dict[str,str] = field(default_factory=lambda:{'daily':'NEW ', 'weekly':'OVERDUE ','monthly':'UPCOMING/OVERDUE ','test': 'TEST TEST'})
    notif_count : int = 0
    jira_open_tail : str = ''
    jira_overdue_tail : str = ''
    prog_team : str = ''
    time : str = ''
    slack_url : str = ''
    p_test : str = ''
    issue_count : int = 0
    conn = SQLServerConnection(source=ALERT_SOURCE,log_file=LOG_FILE, exception_log_file=EX_LOG_FILE)

    def epic_check(self):
        '''
        calls functions to see if need to process for notification(s)
        '''
        epic_list = self.get_epics()
        if epic_list == []:
            logs.log_headline("THERE ARE NO " + self.time + " NOTIFICATIONS TO BE PROCESSED", 2, "#", LOG)
        elif epic_list  is None:
            logs.log_headline("THERE WAS AN ISSUE WITH THE SQL QUERY, NONE WAS RETURNED, SEE EXCEPTION LOGS", 2, "#", LOG)
        else:
            for epics in epic_list:
                epic = epics[0]
                self.epic_list.append(epic)
            self.process_ticket_epics()
        return

    def get_epics(self):
        '''
        get the CurrentEpic associated with any issues that were created in last X time period
        '''
        self.conn.func = 'get_epics()'
        #'SYSDEV-5363' is a non-scan related epic
        sql = "SELECT DISTINCT CurrentEpic from JiraIssues WHERE "+ self.sql_condition[self.time] +" AND CurrentEpic IS NOT NULL AND CurrentEpic != 'SYSDEV-5363' AND JiraProjectKey != 'FOUR' AND JiraStatusCategory != 'Done' ORDER BY CurrentEpic"
        # tests for pen test tickets
        # sql = "SELECT DISTINCT CurrentEpic from JiraIssues WHERE CurrentEpic IS NOT NULL AND JiraProjectKey != 'FOUR' AND CurrentEpic = 'EATP-2896'"
         # tests for no pen test tickets
        # sql = "SELECT DISTINCT CurrentEpic from JiraIssues WHERE CurrentEpic IS NOT NULL AND JiraProjectKey != 'FOUR' AND CurrentEpic = 'SEC-2895'"
        # tests specific epic
        # sql = "SELECT DISTINCT CurrentEpic from JiraIssues WHERE "+ self.sql_condition[self.time] +" AND CurrentEpic IS NOT NULL AND JiraProjectKey != 'FOUR' AND CurrentEpic = 'CD-179'"
        # tests programming error
        # sql = "SELECT DISTINCT CurrentEpic from JiraIssuesWHERE "+ self.sql_condition[self.time] +" ANDCurrentEpic IS NOT NULL AND JiraProjectKey != 'FOUR' AND CurrentEpic = 'DDE-2894'"
        get_epics = self.conn.query_with_logs(sql)
        return get_epics

    def process_ticket_epics(self):
        '''gets all details needed per issue/epic for Slack notif'''
        for epic in self.epic_list:
            self.prog_team = ''
            get_slack_deets = self.get_slack_jira_details(epic)
            if get_slack_deets != "no_slack":
                issue_details = self.process_tickets(epic)
                self.slack_router(issue_details)
            else:
                #gets parent epic[0] from Jira issue key and issue details[1]
                all_issue_details = self.process_pentest_tickets(epic)
                if all_issue_details != 'no pen test issues':
                    epics = all_issue_details[0]
                    team_issue_details = all_issue_details[1]
                    for team_epic in epics:
                        team_issues = {}
                        self.get_pt_prog_team(team_epic)
                        for key, details in team_issue_details.items():
                            if key.startswith(team_epic.split('-')[0]):
                                team_issues.update({key: details})
                        self.issue_count = len(team_issues)
                        self.slack_team_header_setup()
                        self.slack_router(team_issues)
                    if epic in self.no_slack_tail:
                        self.no_slack_tail.remove(epic)
        if len(self.no_slack_tail) > 0:
            no_slack_url_alert(self.no_slack_tail)
        self.slack_send_totals()

    def get_license_issues(self, epic):
        '''gets upcoming/overdue license issues'''
        self.conn.func = 'get_license_issues()'
        sql = "SELECT DISTINCT JiraIssueKey from JiraIssues WHERE " + self.sql_condition[self.time] +\
            " AND CurrentEpic = '" + epic + "'AND JiraProjectKey != 'FOUR' AND JiraSummary LIKE '%Unapproved Open Source License%' AND RITMTicket IS NOT NULL ORDER BY JiraIssueKey"
        license_keys = self.conn.query_with_logs(sql)
        if license_keys == [] or license_keys is None:
            logs.log_headline("THERE ARE NO UPCOMING/OVERDUE LICENSE TICKETS FOR CurrentEpic " +\
                        epic + " in JiraIssues table", 2, "#", LOG)
        else:
            return license_keys

    def get_issues(self, epic):
        '''
        gets the Jira issues corresponding epic from JiraIssues table
        '''
        self.conn.func = 'get_issues()'
        sql = "SELECT DISTINCT JiraIssueKey from JiraIssues WHERE " + self.sql_condition[self.time] +\
            " AND CurrentEpic = '" + epic + "'AND JiraProjectKey != 'FOUR' AND JiraStatusCategory !=\
            'Done' ORDER BY JiraIssueKey"
        issue_keys = []
        issue_keys = self.conn.query_with_logs(sql)
        if self.time == 'monthly':
            license_keys = self.get_license_issues(epic)
            if license_keys:
                for license_key in license_keys:
                    issue_keys.append(license_key)
        if issue_keys == []:
            logs.log_headline("THERE ARE NO TICKETS FOR CurrentEpic '" + epic + "' IN JiraIssues TABLE", 2, '#', LOG)
        else:
            return issue_keys

    def get_pentest_issues(self, epic):
        '''
        gets the Jira issues corresponding epic from JiraIssues table for pen test findings
        '''
        self.conn.func = 'get_pentest_issues()'
        sql = "SELECT DISTINCT JiraIssueKey from JiraIssues WHERE CurrentEpic = '" + epic +\
            "' AND JiraStatusCategory != 'Done' AND " + self.sql_condition[self.time] +\
            " AND JiraProjectKey != 'FOUR' AND JiraSummary LIKE '%Pen Test%' ORDER BY JiraIssueKey"
        pt_issue_keys = self.conn.query_with_logs(sql)
        if pt_issue_keys == [] or pt_issue_keys is None:
            logs.log_headline("THERE ARE NO PENTEST TICKETS FOR CurrentEpic " +\
                        epic + " in JiraIssues table", 2, "#", LOG)
        else:
            return pt_issue_keys

    def get_pentest_issue_keys(self, issue_list):
        '''gets Jira issue keys from ticket numbers'''
        jira_keys = []
        for pt_ticket in issue_list:
            jira_key = pt_ticket.split('-')[0]
            if jira_key not in jira_keys:
                jira_keys.append(jira_key)
        return jira_keys

    def get_parent_epic(self, issue_keys):
        '''this gets progteam based on issue key root, this is dependent on having only one epic with issue key root in the ProgTeams table'''
        self.conn.func = 'get_parent_epic()'
        prog_team_epics = []
        for key in issue_keys:
            sql = "SELECT JiraParentKey FROM ProgTeams WHERE JiraKey = '" + key +"' AND Active = 1"
            teams = self.conn.query_with_logs(sql)
            if teams == []:
                logs.log_headline("THERE IS NO Active JiraParentKey FOR JiraKey" + key +\
                            " IN ProgTeams TABLE", 2, "#", LOG)
            else:
                parent_key = teams[0][0]
                if parent_key not in prog_team_epics:
                    prog_team_epics.append(parent_key)
        return prog_team_epics

    def get_slack_jira_details(self, epic):
        '''
        gets the Slack tail and ProgTeam for corresponding teams Slack channel from ProgTeams table
        '''
        self.conn.func = 'get_slack_jira_details()'
        sql = "SELECT SlackURL, ProgTeam, JiraOpenTail, JiraOverdueTail from ProgTeams WHERE JiraParentKey = '" + epic + "'"
        get_slack_deets = self.conn.query_with_logs(sql)
        if get_slack_deets == []:
            logs.log_headline("THERE IS NO SLACKTAIL FOR CurrentEpic " + epic +\
                    " IN ProgTeams TABLE WILL CHECK IF PEN TEST FINDINGS", 2, "*", LOG)
            self.no_slack_tail.append(epic)
            return "no_slack"
        else:
            # uncomment for prod
            self.slack_tail = get_slack_deets[0][0]
            # for testing, gets sent to appsec-test Slack channel
            # self.slack_tail = 'B04GS680KL6/xTYPaIdehhUTEoQy8UawkUZI'
            self.prog_team = get_slack_deets[0][1]
            self.jira_open_tail = get_slack_deets[0][2]
            self.jira_overdue_tail = get_slack_deets[0][3]
            self.slack_filter_message_setup()
            slack_url = SLACK_ROOT + self.slack_tail
            self.slack_url = slack_url
        return get_slack_deets

    def process_tickets(self, epic):
        '''process through tickets per epic and return details'''
        get_issues_list = self.get_issues(epic)
        issue_details = {}
        for issues in get_issues_list:
            issue = issues[0]
            ticket_details = self.get_issue_details(issue)
            issue_details.update({issue: ticket_details})
        self.issue_count = len(issue_details)
        self.slack_team_header_setup()
        return issue_details

    def process_pentest_tickets(self, epic):
        '''process through pen test tickets per epic and return details'''
        self.p_test = 'PEN TEST '
        get_issues_list = self.get_pentest_issues(epic)
        issue_details = {}
        issue_list = []
        if get_issues_list != None:
            for issues in get_issues_list:
                issue = issues[0]
                issue_list.append(issue)
                ticket_details = self.get_issue_details(issue)
                issue_details.update({issue: ticket_details})
            issue_keys = self.get_pentest_issue_keys(issue_list)
            get_parent_epic_from_key = self.get_parent_epic(issue_keys)
            return get_parent_epic_from_key, issue_details
        else:
            logs.log_headline("THERE ARE NO PENTEST TICKETS FOR CurrentEpic " + epic, 2, "*", LOG)
            return 'no pen test issues'

    def slack_filter_message_setup(self):
        '''adds slack filter message dependent upon timeframe'''
        if self.time == 'weekly':
            self.slack_filter_message = 'Jira Filter for overdue findings: <'+ JIRA_SERVER + self.jira_overdue_tail + '|*Click here*> '
        elif self.time == 'monthly':
            self.slack_filter_message = 'Jira Filter for open findings: <'+ JIRA_SERVER + self.jira_open_tail + '|*Click here*>'
        return

    def slack_team_header_setup(self):
        '''adds slack team message dependent upon timeframe'''
        if self.time == 'weekly':
            self.slack_team_header = ':alert: Weekly Alert: ' + self.prog_team +\
                ' Team     :alert: \\n\\nThere are '+ str(self.issue_count) +\
                ' overdue ' +self.p_test +'finding(s)!!!'
        elif self.time == 'monthly':
            self.slack_team_header  = ':alarm:  Monthly Alert: ' + self.prog_team +\
                ' Team    :alarm: \\n\\nThere are '+ str(self.issue_count) +\
                ' upcoming and/or overdue ' +self.p_test +'finding(s)'

    def slack_router(self, details):
        '''dependent upon the time routes to different Slack message'''
        if self.time == 'daily':
            self.daily_slack_message(details)
        elif self.time == 'test':
            self.daily_slack_message(details)
        else:
            self.weekly_monthly_message(details)

    def get_pt_prog_team(self, epic):
        '''get prog team from epic'''
        get_slack_deets = self.get_slack_jira_details(epic)
        self.prog_team = get_slack_deets[0][1]
        return self.prog_team

    def slack_send(self, header_block, message_block):
        '''sends slack message for daily, weekly, and monthly notifs'''
        webhook = WebhookClient(self.slack_url)
        message_block_send = message_block.rstrip(',')
        message = header_block + message_block_send + ']'
        message_array = json.loads(message)
        message_array = json.dumps(message_array, indent=5)
        response = webhook.send(
            blocks = message_array
        )
        self.slack_log(response)

    def slack_log(self, response):
        '''adds log message dependent upon response code'''
        if response.status_code == 200:
            logs.log_headline(self.log_condition[self.time] + self.p_test +
                     "TICKET ALERT SENT TO " + self.prog_team + "'S SLACK CHANNEL", 2, "#", LOG)
            self.notif_count += 1
            self.prog_team = ''
            self.prog_team = ''
            self.jira_open_tail = ''
            self.jira_overdue_tail = ''
            self.p_test = ''
            self.issue_count = 0
        elif response.status_code == 400:
            function='slack_log()'
            code = 'TNSlack-01'
            details = self.log_condition[self.time] + self.p_test + " TICKET ALERT NOT SENT TO " + self.prog_team + " DUE TO 400 STATUS CODE, HERE IS A CLUE? " + str(response.body)
            logs.function_exception(function, code, details, LOG_EXCEPTION, LOG, EX_LOG_FILE)

    def slack_send_totals(self):
        '''logs # Slack messages sent'''
        if self.notif_count == 0:
            logs.log_headline("NO NEW TICKET NOTIFS TODAY", 2, "#", LOG)
        else:
            logs.log_headline(str(self.notif_count) + "  ALERTS FOR "
                      + self.log_condition[self.time] + "TICKET NOTIFS HAVE BEEN PROCESSED", 2, "#", LOG)
            self.notif_count = 0

    def get_issue_details(self, issue):
        '''
        gets issue details for message
        '''
        self.conn.func = 'get_issue_details()'
        sql = "SELECT DISTINCT JiraDueDate, JiraPriority, JiraSummary from JiraIssues WHERE \
            JiraIssueKey = '" + issue + "' AND JiraProjectKey != 'FOUR'"
        results = self.conn.query_with_logs(sql)
        print('results', results)
        return results

    def daily_slack_message(self, issue_details):
        '''sends Slack message for new vuln tickets'''
        header_block = ''' [{
                                                "type": "header",
                                                "text": {
                                                    "type": "plain_text",
                                                    "text": ":looking:  New '''+self.p_test+'''ticket(s) created for '''+ self.prog_team + '''  :looking:"
                                                }
                                            }, '''
        message_block = ''''''
        for issue, details in issue_details.items():
            issue_url = JIRA_TICKET_ROOT + issue
            due_date = details[0][0]
            severity = details[0][1]
            summary = details[0][2]
            message_block += '''
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "*Summary:* '''+ summary + '''"
                                }
                            },
                            {
                                "type": "section",
                                "fields": [
                                    {
                                        "type": "mrkdwn",
                                        "text": "*Severity:* '''+ severity +'''"
                                    },
                                    {
                                        "type": "mrkdwn",
                                        "text": "*Due Date:* ''' + due_date.strftime("%b %d, %Y") +'''"
                                    }
                                ]
                            },
                            {
                                "type": "section",
                                "fields": [
                                    {
                                        "type": "mrkdwn",
                                        "text": "<'''+ str(issue_url) + "|" + str(issue) +  '''>"
                                    }
                                ]
                            },
                            {
                                "type": "divider"
                            },'''
        self.slack_send(header_block, message_block)
        self.slack_tail = ''
        return

    def weekly_monthly_message(self, issue_details):
        '''sets up weekly/monthly messages to be sent to teams, based on notif_manager.time'''
        header_block ='''[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "'''+ self.slack_team_header+'''"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Please include tickets in an upcoming sprint or request a <https://progfin.atlassian.net/wiki/spaces/IS/pages/1257275523/AppSec+Exceptions#Other-Exception-types|Due Date Exception>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "'''+ self.slack_filter_message+'''"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please let us know if you have any questions or if we can assist in any way!!"
                    }
                },
                {
                "type": "section",
                "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Jira Ticket(s):*"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Due Date:*"
                        }
                    ]
                },'''
        message_block = ''''''
        if self.issue_count < 50:
            for issue, details in issue_details.items():
                issue_url = JIRA_TICKET_ROOT + issue
                due_date = details[0][0]
                message_block += '''
                                {
                                "type": "section",
                                "fields": [
                                    {
                                            "type": "mrkdwn",
                                            "text": "<'''+ str(issue_url) + "|" + str(issue) +  '''>"
                                    },
                                    {
                                            "type": "mrkdwn",
                                            "text": "'''+ str(due_date) +  '''"
                                    }
                                    ]
                                },'''
        else:
            message_block += '''
                                {
                                "type": "section",
                                "fields": [
                                    {
                                            "type": "mrkdwn",
                                            "text": "See Jira Filter above, too many to list in Slack message"
                                    },
                                    {
                                            "type": "mrkdwn",
                                            "text": "*"
                                    }
                                    ]
                                },'''

        self.slack_send(header_block, message_block)
        self.slack_tail = ''

def no_slack_url_alert(teams):
    '''sends a slack alert if there is no slack tail in
    ProgTeams for epic and not pen test findings'''
    webhook = WebhookClient(SLACK_URL)
    header_block = '''[{
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Missing Slack URL(s)"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Generating Script:*\\n'''+ ALERT_SOURCE +'''"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Fix Location:*\\nProgTeams table"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "*Description:*\\nNotifications cannot be sent to Teams' Slack channels below due to SlackUrl missing from ProgTeams table"
                            }
                        ]
                    },'''
    message_block = ''''''
    for team in teams:
        message_block += '''
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "checkboxes",
                            "options":  [
                                {
                                    "text": {
                                            "type": "mrkdwn",
                                            "text": "''' +  str(team) +  '''"
                                        },
                                        "value": "''' +  str(team) +  '''"
                                }
                            ],
                            "action_id": "actionId-1"
                            }
                        ]
                },'''

    message_block_send = message_block.rstrip(',')
    message = header_block + message_block_send + ']'
    message_array = json.loads(message)
    response = webhook.send(
        blocks = message_array
    )
    if response.status_code == 200:
        logs.log_headline("ALERT SENT REGARDING NO SLACK URL FOR " + str(teams), 2, "#", LOG)
    elif response.status_code == 400:
        logs.log_headline("ALERT NOT SENT REGARDING NO SLACK URL DUE TO 400 STATUS CODE, HERE IS A CLUE? " + str(print(response.body)), 2, "#", LOG)

if __name__ == "__main__":
    main()
