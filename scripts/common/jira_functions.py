"""Commonly used Jira functions"""

import inspect
import os
import sys
import json
import requests
import traceback
from common.constants import JIRA_SERVER, JIRA_USER, JIRA_FOUR_SERVER, JIRA_FOUR_USER
from datetime import datetime,timedelta
from dotenv import load_dotenv
from jira import JIRA
from requests.auth import HTTPBasicAuth
from common.logging import TheLogs
from common.database_jira import JiraDB
from common.database_appsec import select, update_multiple_in_table, update
from maint.jira_issues_database_queries import JIDatabase
parent = os.path.abspath('.')
sys.path.insert(1,parent)

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
JIRA_KEY = os.environ.get('JIRA_KEY')
JIRA_FOUR_KEY = os.environ.get('JIRA_FOUR_KEY')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    proj_list = ['FOUR']
    src = ALERT_SOURCE.replace("-","\\")

class GeneralTicketing():
    """Provides general functions for interacting with Jira"""

    @staticmethod
    def get_ticket_due_date(ticket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the due date of the ticket from JiraIssues"""
        t_due = None
        sql = f"""SELECT JiraDueDate FROM JiraIssues WHERE JiraIssueKey = '{ticket}'"""
        try:
            get_date = select(sql)
        except Exception as e_details:
            e_code = "CMN-GTDD-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                    'Results':t_due}
        if get_date != []:
            t_due = get_date[0][0].strftime("%b %d, %Y")
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':t_due}

    @staticmethod
    def remove_epic_link(jira_issue_key):
        """Removes the Epic link from a Jira ticket"""
        success = False
        jira_project_key = str(jira_issue_key).split("-",1)[0]
        if jira_project_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/2/issue/{jira_issue_key}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "fields":{
                "parent":{
                }
            }
        })
        response = requests.put(server,headers=headers,data=payload,auth=auth,timeout=60)
        if response.status_code == 204:
            success = True
        return success

    @staticmethod
    def has_related_link_type(repo):
        """Checks to see if we can link issues from the tickets"""
        can_link = False
        if repo == 'four':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        url = f"{server}/rest/api/3/issueLinkType"
        headers = {
        "Accept": "application/json"
        }
        response = requests.get(url,headers=headers,auth=auth,timeout=60)
        print(response.text)
        if response.status_code == 200:
            if any(d.get('name',None) == 'Relates' for d in response.json()['issueLinkTypes']):
                can_link = True
        return can_link

    @staticmethod
    def add_related_ticket(jira_issue_key,related_list):
        """Links related tickets to a ticket"""
        success = False
        s_cnt = 0
        jira_project_key = str(jira_issue_key).split("-",1)[0]
        if jira_project_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/2/issueLink"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        for item in related_list:
            payload = json.dumps({
                "inwardIssue":{
                    "key":item
                    },
                "outwardIssue":{
                    "key":jira_issue_key
                    },
                "type":{
                    "name":"Relates"
                }
            })
            response = requests.post(server,headers=headers,data=payload,auth=auth,timeout=60)
            if response.status_code == 204:
                s_cnt += 1
        if s_cnt == len(related_list):
            success = True
        return success

    @staticmethod
    def add_epic_link(jira_issue_key,epic):
        """Adds an Epic link to a Jira ticket"""
        success = False
        jira_project_key = str(jira_issue_key).split("-",1)[0]
        if jira_project_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
            epic_parent_field = 'customfield_10014'
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
            epic_parent_field = 'customfield_10008'
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/2/issue/{jira_issue_key}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "fields":{
                "parent":{
                    epic_parent_field: epic
                }
            }
        })
        response = requests.put(server,headers=headers,data=payload,auth=auth,timeout=60)
        if response.status_code == 204:
            success = True
        return success

    @staticmethod
    def verify_security_finding_type(proj_key):
        """Determines if Jira project has a Security Finding ticket type"""
        has_sf_type = False
        if proj_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        url =  f"{server}/rest/api/2/project/{proj_key}"
        auth = HTTPBasicAuth(user, apikey)
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(url,auth=auth,headers=headers,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issueTypes' in response:
                for i_type in response['issueTypes']:
                    if i_type['name'] == 'Security Finding':
                        has_sf_type = True
                        return has_sf_type
        return has_sf_type

    @staticmethod
    def get_project_name(proj_key):
        "Gets the name of the Jira project"
        proj_name = None
        if proj_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        url = f"{server}/rest/api/3/project/{proj_key}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.get(url, auth=auth, headers=headers, timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'name' in response:
                proj_name = response['name']
        return proj_name

    @staticmethod
    def get_all_project_keys():
        "Returns a list of all project keys"
        GeneralTicketing.cycle_through_project_keys()
        ScrVar.proj_list = sorted(set(ScrVar.proj_list))
        return ScrVar.proj_list

    @staticmethod
    def cycle_through_project_keys(start_at=0):
        "Returns a list of all project keys"
        GeneralTicketing.get_all_projects_paginated(start_at)

    @staticmethod
    def get_all_projects_paginated(start_at):
        "Returns a list of all project keys"
        auth = HTTPBasicAuth(str(JIRA_USER),str(JIRA_KEY))
        url = f"{JIRA_SERVER}/rest/api/3/project/search?maxResults=50&startAt={start_at}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.get(url, auth=auth, headers=headers, timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'values' in response:
                for proj in response['values']:
                    if 'key' in proj:
                        ScrVar.proj_list.append(proj['key'])
            if 'nextPage' in response:
                start_at += 50
                GeneralTicketing.cycle_through_project_keys(start_at)

    @staticmethod
    def get_jira_info(repo, tool):
        """Retrieves Jira information for a repo"""
        jira_info = None
        sql = f"""SELECT JiraProjectKey, JiraIssueParentKey FROM ApplicationAutomation
                WHERE Repo = '{repo}'"""
        if tool is not None:
            if tool.lower() in ('checkmarx', 'cx'):
                sql = f"""SELECT PCI, JiraProjectKey, JiraIssueParentKey, cxTechDebtBoarded
                        FROM ApplicationAutomation WHERE Repo = '{repo}' AND JiraIssueParentKey
                        IS NOT NULL"""
            elif tool.lower() in ('mend os'):
                sql = f"""SELECT PCI, JiraProjectKey, JiraIssueParentKey,  wsTechDebtBoarded
                FROM ApplicationAutomation WHERE Repo = '{repo}' AND JiraIssueParentKey IS NOT
                NULL"""
        try:
            jira_info = select(sql)
        except Exception:
            jira_info = None
        return jira_info

    @staticmethod
    def set_due_date(severity,td_boarded):
        """Calculates and returns the due date for a new ticket"""
        if td_boarded != 1 or td_boarded is None:
            remediation_days = 180
        else:
            if severity == 'Critical':
                remediation_days = 30
            elif severity == 'High':
                remediation_days = 90
            elif severity == 'Medium':
                remediation_days = 180
            else:
                remediation_days = 0
        due_date = str(datetime.now() + timedelta(remediation_days))[:10]
        return due_date

    @staticmethod
    def check_past_due(jira_issue_key):
        """Checks a ticket to see if it is past due"""
        past_due = False
        sql = f"""SELECT JiraIssueKey FROM JiraIssues WHERE JiraIssueKey = '{jira_issue_key}'
                AND JiraDueDate < GETDATE()"""
        is_past_due = select(sql)
        if is_past_due:
            past_due = True
        return past_due

    @staticmethod
    def check_exceptions(jira_issue_key):
        """Checks a ticket to see if has an active exception"""
        has_exception = False
        sql = f"""SELECT JiraIssueKey FROM JiraIssues WHERE JiraIssueKey = '{jira_issue_key}'
                AND JiraDueDate >= GETDATE() AND RITMTicket IS NOT NULL AND
                ExceptionApproved = 1"""
        get_exception = select(sql)
        if get_exception:
            has_exception = True
        return has_exception

    @staticmethod
    def check_tech_debt(jira_issue_key):
        """Checks a ticket to see if it is tech debt and not past due"""
        is_td = False
        sql = f"""SELECT JiraIssueKey FROM JiraIssues WHERE JiraIssueKey = '{jira_issue_key}'
                AND JiraDueDate >= GETDATE() AND RITMTicket IS NULL AND
                (ExceptionApproved = 0 OR ExceptionApproved IS NULL) AND TechDebt = 1"""
        get_td = select(sql)
        if get_td:
            is_td = True
        return is_td

    @staticmethod
    def cancel_jira_ticket(repo, jira_issue_key, comment):
        """Cancels and comments on a single Jira ticket"""
        success = False
        res_date = datetime.now()
        if repo == 'four':
            ticket_status = 'Abandoned'
            connection = jira_connection(repo)
            cancel_issue = connection.issue(jira_issue_key)
            connection.transition_issue(jira_issue_key, ticket_status)
            connection.add_comment(cancel_issue, comment)
            sql = f"""UPDATE JiraIssues SET JiraStatusCategory = 'Done',
            JiraResolutionDate = '{res_date}' WHERE JiraIssueKey =
            '{jira_issue_key}'"""
            update(sql)
            return True
        else:
            get_transitions = get_ticket_transitions(repo, jira_issue_key)
            transition_options = []
            for transition in get_transitions:
                ticket_status = None
                ticket_status_id = None
                if 'to' in transition:
                    if 'statusCategory' in transition['to']:
                        if 'key' in transition['to']['statusCategory']:
                            category_status = transition['to']['statusCategory']['key']
                            if str(category_status).lower() == 'done':
                                if 'id' in transition:
                                    ticket_status_id = transition['id']
                                if 'name' in transition:
                                    ticket_status = transition['name']
                if ticket_status is not None and ticket_status == 'Cancelled':
                    transition_options.append({'ticketStatusId': ticket_status_id,
                                            'ticketStatus': ticket_status})
            has_cancelled = list(filter(lambda option: option['ticketStatus'] == 'Cancelled',
                                        transition_options))
            if has_cancelled != []:
                ticket_status_id = has_cancelled[0]['ticketStatusId']
                ticket_status = has_cancelled[0]['ticketStatus']
            if ticket_status_id is not None and ticket_status is not None:
                try:
                    path = "/rest/api/3/issue/"
                    query_string = "?expand=transitions.fields"
                    url = f"""{JIRA_SERVER}{path}{jira_issue_key}/transitions{query_string}"""
                    auth = HTTPBasicAuth(JIRA_USER, JIRA_KEY)
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                    payload = json.dumps({
                        "update":{
                            "comment": [
                                {
                                    "add": {
                                        "body": comment
                                    }
                                }
                            ]
                        },
                        "transition": {
                            "id": str(ticket_status_id)
                        },
                        "fields": {
                            "resolution": {
                                "name": ticket_status
                            }
                        }
                    })
                    response = requests.post(url,data=payload,headers=headers,auth=auth,timeout=60)
                    if response.status_code == 201:
                        success = True
                    else:
                        connection = jira_connection(repo)
                        cancel_issue = connection.issue(jira_issue_key)
                        connection.transition_issue(jira_issue_key, ticket_status)
                        connection.add_comment(cancel_issue, comment)
                        success = True
                    if success is True:
                        GeneralTicketing.remove_epic_link(jira_issue_key)
                        sql = f"""UPDATE JiraIssues SET JiraStatusCategory = 'Done',
                        JiraResolutionDate = '{res_date}' WHERE JiraIssueKey =
                        '{jira_issue_key}'"""
                        update(sql)
                except Exception:
                    success = False
                    logged = datetime.now()
                    jira_project_key = str(jira_issue_key).split("-", 1)[0]
                    insert_info = [{'Repo':repo,'Date':logged,'JiraProjectKey':jira_project_key,
                                    'JiraIssueKey':jira_issue_key,'StatusAttempted':ticket_status}]
                    JiraDB.insert_multiple_into_table('JiraTicketClosureErrors',insert_info)
        return success

    @staticmethod
    def close_jira_ticket(repo, jira_issue_key, comment):
        """Closes out and comments on a single Jira ticket"""
        success = False
        if repo == 'four':
            transition_name = 'Completed - No Code Updates'
            connection = jira_connection(repo)
            close_issue = connection.issue(jira_issue_key)
            connection.transition_issue(jira_issue_key, transition_name)
            if comment is not None:
                connection.add_comment(close_issue, comment)
            success = True
        else:
            get_transition = GeneralTicketing.get_closed_transition(repo, jira_issue_key)
            if get_transition != {}:
                transition_id = get_transition['ID']
                transition_name = get_transition['Name']
                try:
                    if transition_id is not None and transition_name is not None:
                        url = f"""{JIRA_SERVER}/rest/api/3/issue/{jira_issue_key}/transitions?"""
                        url += """expand=transitions.fields"""
                        auth = HTTPBasicAuth(JIRA_USER, JIRA_KEY)
                        headers = {
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        }
                        payload = json.dumps({
                            "update":{
                                "comment": [
                                    {
                                        "add": {
                                            "body": comment
                                        }
                                    }
                                ]
                            },
                            "transition": {
                                "id": str(transition_id)
                            },
                            "fields": {
                                "resolution": {
                                    "name": transition_name
                                }
                            }
                        })
                        if comment is None:
                            payload = json.dumps({
                                "transition": {
                                    "id": str(transition_id)
                                },
                                "fields": {
                                    "resolution": {
                                        "name": transition_name
                                    }
                                }
                            })
                        response = requests.post(url,data=payload,headers=headers,auth=auth,
                        timeout=60)
                        if response.status_code != 204:
                            connection = jira_connection(repo)
                            close_issue = connection.issue(jira_issue_key)
                            connection.transition_issue(jira_issue_key, transition_name)
                            if comment is not None:
                                connection.add_comment(close_issue, comment)
                            success = True
                        else:
                            success = True
                except Exception:
                    success = False
                    logged = datetime.now()
                    jira_project_key = str(jira_issue_key).split("-", 1)[0]
                    insert_info = [{'Repo':repo,'Date':logged,'JiraProjectKey':jira_project_key,
                                    'JiraIssueKey':jira_issue_key,'StatusAttempted':transition_name}]
                    JiraDB.insert_multiple_into_table('JiraTicketClosureErrors',insert_info)
        return success

    @staticmethod
    def reopen_mend_license_violation_jira_ticket(repo,jira_issue_key,comment):
        """Reopens and comments on a single Jira ticket"""
        success = False
        if repo == 'four':
            transition_name = 'Backlog'
            connection = jira_connection(repo)
            reopen_issue = connection.issue(jira_issue_key)
            connection.transition_issue(jira_issue_key, transition_name)
            if comment is not None:
                connection.add_comment(reopen_issue, comment)
            success = True
        else:
            get_transition = GeneralTicketing.get_backlog_transition(repo,jira_issue_key)
            if get_transition != {}:
                transition_id = get_transition['ID']
                transition_name = get_transition['Name']
                try:
                    if transition_id is not None and transition_name is not None:
                        url = f"""{JIRA_SERVER}/rest/api/3/issue/{jira_issue_key}/transitions?"""
                        url += """expand=transitions.fields"""
                        auth = HTTPBasicAuth(JIRA_USER, JIRA_KEY)
                        headers = {
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        }
                        payload = json.dumps({
                            "update":{
                                "comment": [
                                    {
                                        "add": {
                                            "body": comment
                                        }
                                    }
                                ]
                            },
                            "transition": {
                                "id": str(transition_id)
                            },
                            "fields": {
                                "resolution": {
                                    "name": transition_name
                                }
                            }
                        })
                        if comment is None:
                            payload = json.dumps({
                                "transition": {
                                    "id": str(transition_id)
                                },
                                "fields": {
                                    "resolution": {
                                        "name": transition_name
                                    }
                                }
                            })
                        response = requests.post(url,data=payload,headers=headers,auth=auth,
                        timeout=60)
                        if response.status_code == 204:
                            return True
                        connection = jira_connection(repo)
                        reopen_issue = connection.issue(jira_issue_key)
                        connection.transition_issue(jira_issue_key, transition_name)
                        if comment is not None:
                            connection.add_comment(reopen_issue, comment)
                        success = True
                except Exception:
                    success = False
                    logged = datetime.now()
                    jira_project_key = str(jira_issue_key).split("-", 1)[0]
                    insert_info = [{'Repo':repo,'Date':logged,'JiraProjectKey':jira_project_key,
                                    'JiraIssueKey':jira_issue_key,'StatusAttempted':transition_name}]
                    JiraDB.insert_multiple_into_table('JiraTicketClosureErrors',insert_info)
        return success

    @staticmethod
    def create_jira_ticket(repo, proj_key, summary, desc, severity, labels, due_date, epic):
        """Creates a new Jira ticket"""
        issue = None
        if repo == 'four':
            issue_type = 'Story'
            due_date_field = 'customfield_10035'
            epic_parent_field = 'customfield_10014'
        else:
            issue_type = 'Security Finding'
            due_date_field = 'duedate'
            epic_parent_field = 'customfield_10008'
        if severity == 'Critical':
            severity = 'Highest'
        issue_details = {
            'project': {
                'key': proj_key
            },
            'summary': summary,
            'description': desc,
            'issuetype': {
                'name': issue_type
            },
            'priority': {
                'name': severity
            },
            'labels': labels,
            due_date_field: due_date,
            # Epic parent
            epic_parent_field: epic
        }
        issue = jira_connection(repo).create_issue(fields=issue_details)
        return issue.key

    @staticmethod
    def update_jira_ticket(jira_issue_key, repo, description, summary):
        """Updates the description field of a Jira ticket"""
        issue = jira_connection(repo).issue(jira_issue_key)
        issue.update(fields={'description': description, 'summary': summary})
        return True

    @staticmethod
    def update_jira_summary(jira_issue_key, repo, summary):
        """Updates the summary (title) field of a Jira ticket"""
        issue = jira_connection(repo).issue(jira_issue_key)
        issue.update(fields={'summary': summary})
        return True

    @staticmethod
    def update_ticket_due(jira_issue_key, repo, due_date, comment):
        """Updates the due date field of a Jira ticket"""
        success = False
        if repo.lower() == 'four':
            try:
                due_date_field = 'customfield_10035'
                connection = jira_connection(repo)
                issue = connection.issue(jira_issue_key)
                issue.update(fields={due_date_field: due_date})
                if comment is not None:
                    connection.add_comment(jira_issue_key, comment)
                success = True
            except Exception:
                return False
        else:
            try:
                user = JIRA_USER
                apikey = JIRA_KEY
                server =  JIRA_SERVER
                due_date_field = 'duedate'
                auth = HTTPBasicAuth(str(user),str(apikey))
                url = f"{server}/rest/api/2/issue/{jira_issue_key}"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                payload = json.dumps({
                    "fields":{
                        due_date_field: due_date
                    }
                })
                response = requests.put(url,headers=headers,data=payload,auth=auth,timeout=60)
                if response.status_code == 204:
                    success = True
                    if comment is not None:
                        url = f"{server}/rest/api/2/issue/{jira_issue_key}/comment"
                        headers = {
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        }
                        payload = json.dumps({
                            "body": comment
                        })
                        response = requests.post(url,headers=headers,data=payload,auth=auth,
                                                 timeout=60)
            except Exception:
                return False
        return success

    @staticmethod
    def get_closed_states():
        """Gets the approved closed states for Jira tickets in priority order"""
        closed_states = []
        sql = """SELECT Priority, Status FROM JiraIssuesClosedStates ORDER BY Priority"""
        try:
            states = select(sql)
        except Exception as e_details:
            e_code = "PS-GTFF-001"
            TheLogs.sql_exception(sql,e_code,e_details,LOG_EXCEPTION,LOG,EX_LOG_FILE,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return closed_states
        if states != []:
            for state in states:
                closed_states.append(state[1])
        return closed_states

    @staticmethod
    def get_closed_transition(repo, jira_issue_key):
        """Gets the possible closed transitions for a Jira ticket"""
        if repo == 'four':
            return {'ID':'271','Name':'Completed - No Code Updates'}
        email = JIRA_USER
        api_token = JIRA_KEY
        url =  f"{JIRA_SERVER}/rest/api/2/issue/{jira_issue_key}/transitions"
        auth = HTTPBasicAuth(email, api_token)
        headers = {
            "Accept": "application/json"
        }
        transition_response = requests.get(url, auth=auth, headers=headers, timeout=60)
        # transition_response.text = {"expand":"transitions","transitions":[{"id":"41","name":
        # "Done","to":{"self":"https://progfin.atlassian.net/rest/api/2/status/10005",
        # "description":"This issue needs no more work.","iconUrl":
        # "https://progfin.atlassian.net/images/icons/subtask.gif","name":"Done","id":"10005",
        # "statusCategory":{"self":"https://progfin.atlassian.net/rest/api/2/statuscategory/3",
        # "id":3,"key":"done","colorName":"green","name":"Done"}},"hasScreen":False,
        # "isGlobal":True,"isInitial":False,"isAvailable":True,"isConditional":False,"isLooped":
        # False},{"id":"81","name":"Cancelled","to":{"self":
        # "https://progfin.atlassian.net/rest/api/2/status/15001","description":"This issue has
        # been aborted or cancelled to move into next phase.","iconUrl":
        # "https://progfin.atlassian.net/images/icons/statuses/trash.png","name":"Cancelled","id":
        # "15001","statusCategory":{"self":
        # "https://progfin.atlassian.net/rest/api/2/statuscategory/3","id":3,"key":"done",
        # "colorName":"green","name":"Done"}},"hasScreen":False,"isGlobal":True,"isInitial":False,
        # "isAvailable":True,"isConditional":False,"isLooped":False}]}
        transitions = {}
        if transition_response.status_code == 200:
            closed_states = GeneralTicketing.get_closed_states()
            # closed_states = ['Completed', 'Closed', 'Done', 'Resolved', 'To Close']
            transition_response = transition_response.json()
            if 'transitions' in transition_response and closed_states != []:
                all_transitions = transition_response['transitions']
                for c_state in closed_states:
                    if 'ID' in transitions and 'Name' in transitions:
                        if transitions['ID'] is not None and transitions['Name'] is not None:
                            break
                    for transition in all_transitions:
                        if 'to' in transition:
                            if 'statusCategory' in transition['to']:
                                if 'name' in transition['to']['statusCategory']:
                                    transition_id = None
                                    transition_name = None
                                    category = transition['to']['statusCategory']['name'].lower()
                                    if category == 'done':
                                        if 'name' in transition:
                                            transition_name = transition['name']
                                            if transition_name == c_state:
                                                if 'id' in transition:
                                                    transition_id = transition['id']
                                            if (transition_id is not None and
                                                transition_name is not None):
                                                transitions['ID'] = transition_id
                                                transitions['Name'] = transition_name
        return transitions

    @staticmethod
    def get_backlog_transition(repo, jira_issue_key):
        """Gets the backlog transition for a Jira ticket"""
        if repo == 'four':
            return {'ID':'11','Name':'Backlog'}
        else:
            email = JIRA_USER
            api_token = JIRA_KEY
            url =  f"{JIRA_SERVER}/rest/api/2/issue/{jira_issue_key}/transitions"
        auth = HTTPBasicAuth(email, api_token)
        headers = {
            "Accept": "application/json"
        }
        transition_response = requests.get(url, auth=auth, headers=headers, timeout=60)
        # transition_response.text = {"expand":"transitions","transitions":[{"id":"41","name":
        # "Done","to":{"self":"https://progfin.atlassian.net/rest/api/2/status/10005",
        # "description":"This issue needs no more work.","iconUrl":
        # "https://progfin.atlassian.net/images/icons/subtask.gif","name":"Done","id":"10005",
        # "statusCategory":{"self":"https://progfin.atlassian.net/rest/api/2/statuscategory/3",
        # "id":3,"key":"done","colorName":"green","name":"Done"}},"hasScreen":False,
        # "isGlobal":True,"isInitial":False,"isAvailable":True,"isConditional":False,"isLooped":
        # False},{"id":"81","name":"Cancelled","to":{"self":
        # "https://progfin.atlassian.net/rest/api/2/status/15001","description":"This issue has
        # been aborted or cancelled to move into next phase.","iconUrl":
        # "https://progfin.atlassian.net/images/icons/statuses/trash.png","name":"Cancelled","id":
        # "15001","statusCategory":{"self":
        # "https://progfin.atlassian.net/rest/api/2/statuscategory/3","id":3,"key":"done",
        # "colorName":"green","name":"Done"}},"hasScreen":False,"isGlobal":True,"isInitial":False,
        # "isAvailable":True,"isConditional":False,"isLooped":False}]}
        transitions = {}
        if transition_response.status_code == 200:
            transition_response = transition_response.json()
            if 'transitions' in transition_response:
                all_transitions = transition_response['transitions']
                for transition in all_transitions:
                    if 'to' in transition:
                        if 'statusCategory' in transition['to']:
                            if 'name' in transition['to']['statusCategory']:
                                transition_id = None
                                transition_name = None
                                category = transition['to']['statusCategory']['name'].lower()
                                if category != 'done':
                                    if 'name' in transition:
                                        transition_name = transition['name']
                                        if transition_name == 'Backlog':
                                            if 'id' in transition:
                                                transition_id = transition['id']
                                        if (transition_id is not None and
                                            transition_name is not None):
                                            transitions['ID'] = transition_id
                                            transitions['Name'] = transition_name
        return transitions

    @staticmethod
    def get_ticket_status(jira_issue_key):
        """Gets the status category from JiraIssues for a ticket"""
        category = None
        sql = f"""SELECT JiraStatusCategory FROM JiraIssues WHERE JiraIssueKey =
        '{jira_issue_key}'"""
        result = select(sql)
        if result:
            category = result[0][0]
        return category

    @staticmethod
    def leave_ticket_open(tool,jira_issue_key):
        """If a ticket should be left open - returns True if it has open items, False if it is
        ready to close"""
        if tool.lower() == 'checkmarx':
            statuses = "('Accepted','Open','Needs Update','Past Due','Tech Debt')"
            table = 'SASTFindings'
        elif tool.lower() == 'mend os':
            statuses = "('Accepted','Open','Needs Update','Past Due','Tech Debt')"
            table = 'OSFindings'
        else:
            return True
        sql = f"""SELECT TOP 1 JiraIssueKey FROM {table} WHERE Status IN {statuses} AND
        JiraIssueKey = '{jira_issue_key}'"""
        has_open_items = select(sql)
        if not has_open_items:
            return False
        return True

    @staticmethod
    def add_comment_to_ticket(repo,jira_issue_key,comment):
        """Adds a comment to a ticket"""
        connection = jira_connection(repo)
        connection.add_comment(jira_issue_key,comment)

    @staticmethod
    def has_repo_exceptions(repo,due_date,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''If an active repo-wide exception exists, return the RITMTicket, due date, and standard'''
        ex_details = {'RITMTicket':None,'Standard':None,'ApprovedDate':None,'Duration':None,'Due':None}
        sql = f"""SELECT RITMTicket, ExceptionStandard, ApprovedDate, ExceptionDuration,
        ExceptionExpirationDate FROM SNowSecurityExceptions WHERE AppliesToFullRepo LIKE '%{repo}%' AND
        ApprovalStatus = 'Approved' AND ApprovedByName IS NOT NULL AND ApprovedDate IS NOT NULL AND
        ExceptionExpirationDate >= '{due_date}' ORDER BY ExceptionExpirationDate DESC"""
        try:
            has_ex = select(sql)
        except Exception as e_details:
            e_code = "CJF-HRE-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return ex_details
        if has_ex != []:
            ex_details['RITMTicket'] = has_ex[0][0]
            ex_details['Standard'] = has_ex[0][1]
            ex_details['ApprovedDate'] = has_ex[0][2]
            ex_details['Duration'] = has_ex[0][3]
            ex_details['Due'] = has_ex[0][4]
        return ex_details

    @staticmethod
    def close_or_cancel_jira_ticket(repo,jira_issue_key,comment='',tool=''):
        """Determines whether to close or cancel a Jira ticket and then carries out that action"""
        success = False
        issue_closed = GeneralTicketing.get_ticket_status(jira_issue_key)
        if issue_closed is not None and issue_closed == 'Done':
            return True
        elif issue_closed is None:
            return False
        leave_open = GeneralTicketing.leave_ticket_open(tool,jira_issue_key)
        if leave_open is True:
            return False
        if repo == 'four':
            transition_name = 'Completed - No Code Updates'
            connection = jira_connection(repo)
            close_issue = connection.issue(jira_issue_key)
            connection.transition_issue(jira_issue_key, transition_name)
            if comment is not None and len(comment) > 1:
                connection.add_comment(close_issue, comment)
            return True
        else:
            required_fields = GeneralTicketing.get_accounting_and_compliance(repo, jira_issue_key)
            if required_fields != {}:
                act_st = required_fields['AccountingDemo']
                com_st = required_fields['ComplianceDemo']
                status_category = required_fields['StatusCategory']
                p_demo = {'Passed','Not Needed','Conditionally Passed'}
                s_comment = ''
                f_comment = "manual review of this ticket by ProdSec is necessary. "
                f_comment += "*Please leave this ticket open and reach out to ProdSec to "
                f_comment += "get this issue resolved.*"
                close = 0
                if status_category == 'To Do':
                    comment += f" The Jira status category of {status_category} indicates that no"
                    comment += " work has been completed on this ticket. As such, no analysis of "
                    comment += "the Accounting Demo and Compliance Demo fields is necessary. *The "
                    comment += "ticket is being cancelled.*"
                    success = GeneralTicketing.cancel_jira_ticket(repo, jira_issue_key, comment)
                    return success
                elif status_category == 'In Progress':
                    s_comment += f" The Jira status category of {status_category} indicates that "
                    s_comment += "there has been some effort expended to remediate this finding. "
                    s_comment += "An automated analysis reveals that "
                    if act_st in p_demo and com_st in p_demo:
                        close = 1
                        f_comment = f"Accounting Demo is set to {act_st} and Compliance Demo is "
                        f_comment += f"set to {com_st}. Both fields are in desirable states. *As "
                        f_comment += "such, this ticket is being closed.*"
                    elif act_st is None and com_st is None:
                        close = 1
                        f_comment = "the Accounting Demo (customfield_14906) and Compliance "
                        f_comment += "Demo (customfield_14908) fields are not present on this "
                        f_comment += "ticket. This indicates that demos are not required for this "
                        f_comment += "ticket. *As such, this ticket is being closed.*"
                    elif act_st == 'Not Set' and com_st == 'Not Set':
                        f_comment = "neither the Accounting Demo nor the Compliance Demo "
                        f_comment += "field has been set. Both fields are required to be set to "
                        f_comment += "either Passed or Not Needed before this ticket can be "
                        f_comment += "closed. *Please work with the appropriate parties to review "
                        f_comment += "this ticket and then manually close it once both fields "
                        f_comment += "have been properly set.*"
                    elif (act_st not in p_demo and act_st is not None and com_st not in p_demo and
                          com_st is not None):
                        f_comment = f"Accounting Demo is set to {act_st} and Compliance Demo is "
                        f_comment += f"set to {com_st}. Neither field is in a desirable state. "
                        f_comment += "Both must be set to Passed or Not Needed before this "
                        f_comment += "ticket can be closed. *Please work with the appropriate "
                        f_comment += "parties to review this ticket and then manually close it "
                        f_comment += "once both fields have been properly set.*"
                    elif (act_st in p_demo and com_st == 'Not Set') or (act_st == 'Not Set' and
                                                                         com_st in p_demo):
                        if act_st in p_demo:
                            good_f = 'Accounting Demo'
                            good_v = act_st
                            bad_f = 'Compliance Demo'
                            bad_v = com_st
                        else:
                            good_f = 'Compliance Demo'
                            good_v = com_st
                            bad_f = 'Accounting Demo'
                            bad_v = act_st
                        f_comment = f"{good_f} is set to {good_v}, which is a desirable state. "
                        f_comment += f"However, {bad_f} is not set. {bad_f} must be set to Passed "
                        f_comment += "or Not Needed before this ticket can be closed. *Please work "
                        f_comment += "with the appropriate parties to review this ticket and then "
                        f_comment += f"manually close it once {bad_f} has been properly set.*"
                    elif (act_st in p_demo and com_st is not None and com_st not in p_demo and
                          com_st != 'Not Set') or (act_st is not None and act_st not in p_demo and
                                                   act_st != 'Not Set' and com_st in p_demo):
                        if act_st in p_demo:
                            good_f = 'Accounting Demo'
                            good_v = act_st
                            bad_f = 'Compliance Demo'
                            bad_v = com_st
                        else:
                            good_f = 'Compliance Demo'
                            good_v = com_st
                            bad_f = 'Accounting Demo'
                            bad_v = act_st
                        f_comment = f"{good_f} is set to {good_v}, which is a desirable state. "
                        f_comment += f"However, {bad_f} is set to {bad_v}, which is not a "
                        f_comment += f"desirable state. {bad_f} must be set to Passed or Not "
                        f_comment += "Needed before this ticket can be closed. *Please work with "
                        f_comment += "the appropriate parties to review this ticket and then "
                        f_comment += f"manually close it once {bad_f} has been properly set.*"
                    elif (act_st is None and com_st not in p_demo and com_st is not None and
                          com_st != 'Not Set') or (act_st not in p_demo and act_st is not None and
                                                   act_st != 'Not Set' and com_st is None):
                        if act_st is None:
                            missing_f = 'Accounting Demo (customfield_14906)'
                            bad_f = 'Compliance Demo'
                            bad_v = com_st
                        else:
                            missing_f = 'Compliance Demo (customfield_14908)'
                            bad_f = 'Accounting Demo'
                            bad_v = act_st
                        f_comment = f"{bad_f} is set to {bad_v}, which is not a "
                        f_comment += f"desirable state. {bad_f} must be set to Passed or Not "
                        f_comment += "Needed before this ticket can be closed. Please work with "
                        f_comment += "the appropriate parties to review this ticket and ensure "
                        f_comment += "the value has been properly set. Additionally, the "
                        f_comment += f"{missing_f} field is not present on this ticket or the "
                        f_comment += "script was unable to obtain its value. *Please ensure "
                        f_comment += f"{missing_f} is present on the ticket template and that it "
                        f_comment += "is properly set to either Passed or Not Needed by the "
                        f_comment += "appropriate parties and then manually close this ticket.*"
                    elif (act_st is None and com_st in p_demo) or (act_st in p_demo and
                                                                   com_st is None):
                        if act_st is None:
                            missing_f = 'Accounting Demo (customfield_14906)'
                            good_f = 'Compliance Demo'
                            good_v = com_st
                        else:
                            missing_f = 'Compliance Demo (customfield_14908)'
                            good_f = 'Accounting Demo'
                            good_v = act_st
                        f_comment = f"{good_f} is set to {good_v}, which is a desirable "
                        f_comment += f"state. However, the {missing_f} field is not present on "
                        f_comment += "this ticket or the script was unable to obtain its value. "
                        f_comment += f"*Please ensure {missing_f} is present on the ticket "
                        f_comment += "template and that it is properly set to either Passed or "
                        f_comment += "Not Needed by the appropriate parties and then manually "
                        f_comment += "close this ticket.*"
                    elif (act_st is None and com_st == 'Not Set') or (act_st == 'Not Set' and
                                                                      com_st is None):
                        if act_st is None:
                            missing_f = 'Accounting Demo (customfield_14906)'
                            ns_f = 'Compliance Demo'
                        else:
                            missing_f = 'Compliance Demo (customfield_14908)'
                            ns_f = 'Accounting Demo'
                        f_comment = f"{ns_f} is not set. {ns_f} must be set to Passed "
                        f_comment += "or Not Needed before this ticket can be closed. Please work "
                        f_comment += "with the appropriate parties to review this ticket and to "
                        f_comment += f"ensure {ns_f} has been properly set. Additionally, the "
                        f_comment += f"{missing_f} field is not present on this ticket or the "
                        f_comment += "script was unable to obtain its value. Please ensure "
                        f_comment += f"{missing_f} is present on the ticket template and "
                        f_comment += "that it is properly set to either Passed or Not Needed by "
                        f_comment += "the appropriate parties. *Once both fields are present on "
                        f_comment += "this ticket and properly set to Passed or Not Needs, "
                        f_comment += "this ticket should be manually closed.*"
                    comment += f"{s_comment}{f_comment} "
                    if close == 1:
                        success = GeneralTicketing.close_jira_ticket(repo,jira_issue_key,comment)
                    else:
                        comment += "\n_If you feel there is an issue with this automated analysis, "
                        comment += "please reach out to ProdSec as soon as possible._"
                        connection = jira_connection(repo)
                        connection.add_comment(jira_issue_key,comment)
                        success = True
        return success

    @staticmethod
    def get_accounting_and_compliance(repo,jira_issue_key):
        """Retrieves the Accounting Demo and Compliance Demo fields"""
        response_array = {}
        if repo.lower() == 'four':
            user = JIRA_FOUR_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = str(server) + "/rest/api/3/search"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        query = {
            'jql': 'key = "' + str(jira_issue_key) + '"'
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        response_status = response.status_code
        if response_status == 200:
            response = response.json()
            if 'issues' in response:
                issue_array = {}
                for isu in response['issues']:
                    accounting = None
                    compliance = None
                    if 'fields' in isu:
                        if 'customfield_14906' in isu['fields']:
                            accounting = 'Not Set'
                            check_value = isu['fields']['customfield_14906']
                            if isinstance(check_value, dict):
                                if 'value' in check_value:
                                    accounting = check_value['value']
                        if 'customfield_14908' in isu['fields']:
                            compliance = 'Not Set'
                            check_value = isu['fields']['customfield_14908']
                            if isinstance(check_value, dict):
                                if 'value' in check_value:
                                    compliance = check_value['value']
                        if 'statusCategory' in isu['fields']['status']:
                            if 'name' in isu['fields']['status']['statusCategory']:
                                status_category = isu['fields']['status']['statusCategory']['name']
                    issue_array['AccountingDemo'] = accounting
                    issue_array['ComplianceDemo'] = compliance
                    issue_array['StatusCategory'] = status_category
                response_array = issue_array
        return response_array

    @staticmethod
    def get_child_programs(proj_key):
        """Used by infosecdashboard.py for updating child programs"""
        prog_issues = []
        if proj_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/3/search?maxResults=50"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        find = f"project = {proj_key} and issuetype = Program AND (updatedDate >= -14d OR "
        find += "created >= -14d) order by created DESC"
        query = {
            'jql': find
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issues' in response:
                for issue in response['issues']:
                    issue_key = None
                    issue_type = None
                    subtask_cnt = 0
                    subtasks = []
                    summary = None
                    labels = ''
                    priority = None
                    state = None
                    stat_cat = None
                    reporter = None
                    assignee = None
                    d_created = None
                    d_due = None
                    d_start = None
                    d_updated = None
                    d_resolution = None
                    if 'key' in issue:
                        issue_key = issue['key']
                        if 'fields' in issue:
                            if 'issuetype' in issue['fields']:
                                if (issue['fields']['issuetype'] != [] and
                                    issue['fields']['issuetype'] is not None):
                                    if 'name' in issue['fields']['issuetype']:
                                        issue_type = issue['fields']['issuetype']['name']
                            if 'subtasks' in issue['fields']:
                                if (issue['fields']['subtasks'] != [] and
                                    issue['fields']['subtasks'] is not None):
                                    for task in issue['fields']['subtasks']:
                                        subtask_cnt += 1
                                        subtasks.append(task['key'])
                            if 'summary' in issue['fields']:
                                summary = issue['fields']['summary']
                            if 'labels' in issue['fields']:
                                if (issue['fields']['labels'] != [] and
                                    issue['fields']['labels'] is not None):
                                    for label in issue['fields']['labels']:
                                        labels += str(label) + "; "
                                    labels += "None"
                                    labels = labels.replace("; None", "")
                            if 'priority' in issue['fields']:
                                if (issue['fields']['priority'] != [] and
                                    issue['fields']['priority'] is not None):
                                    if 'name' in issue['fields']['priority']:
                                        priority = issue['fields']['priority']['name']
                            if 'status' in issue['fields']:
                                if (issue['fields']['status'] != [] and
                                    issue['fields']['status'] is not None):
                                    if 'name' in issue['fields']['status']:
                                        state = issue['fields']['status']['name']
                                    if 'statusCategory' in issue['fields']['status']:
                                        if (issue['fields']['status']['statusCategory'] != [] and
                                            issue['fields']['status']['statusCategory'] is not
                                            None):
                                            if 'name' in issue['fields']['status']['statusCategory']:
                                                stat_cat = issue['fields']['status']['statusCategory']['name']
                            if 'reporter' in issue['fields']:
                                if (issue['fields']['reporter'] != [] and
                                    issue['fields']['reporter'] is not None):
                                    if 'displayName' in issue['fields']['reporter']:
                                        reporter = issue['fields']['reporter']['displayName']
                            if 'assignee' in issue['fields']:
                                if (issue['fields']['assignee'] != [] and
                                    issue['fields']['assignee'] is not None):
                                    if 'displayName' in issue['fields']['assignee']:
                                        assignee = issue['fields']['assignee']['displayName']
                            if 'created' in issue['fields']:
                                d_created = str(issue['fields']['created']).split("T",1)[0]
                            if 'duedate' in issue['fields']:
                                d_due = issue['fields']['duedate']
                            if 'updated' in issue['fields']:
                                d_updated = str(issue['fields']['updated']).split("T",1)[0]
                            if 'resolutiondate' in issue['fields']:
                                if (stat_cat == 'Done' and issue['fields']['resolutiondate'] is
                                    not None):
                                    r_date = issue['fields']['resolutiondate']
                                    d_resolution = str(r_date).split("T",1)[0]
                            if 'customfield_14841' in issue['fields']:
                                if issue['fields']['customfield_14841'] is not None:
                                    d_start = issue['fields']['customfield_14841'].split("T",1)[0]
                        if labels == '':
                            labels = None
                        if issue_type == 'Program':
                            prog_issues.append({'IssueKey': issue_key,'IssueType': issue_type,
                                                'ProgramName': summary,'SubtaskCount': subtask_cnt,
                                                'Subtasks': subtasks,'Labels': labels,
                                                'Priority': priority,'State': state,
                                                'JiraStatusCategory': stat_cat,
                                                'Reporter': reporter,'Assignee': assignee,
                                                'CreatedDate': d_created,'DueDate': d_due,
                                                'UpdatedDate': d_updated,
                                                'ResolutionDate': d_resolution,
                                                'StartDate': d_start})
        return prog_issues

    @staticmethod
    def get_child_projects(jira_key):
        """Used by infosecdashboard.py for updating child projects"""
        children = []
        jira_project_key = str(jira_key).split("-",1)[0]
        if jira_project_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/3/search?maxResults=50"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        find = f'issuetype = Project AND issuekey in portfolioChildIssuesOf("{jira_key}") AND '
        find += '(updatedDate >= -14d OR created >= -14d) order by created DESC'
        query = {
            'jql': find
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issues' in response:
                for issue in response['issues']:
                    i_key = None
                    i_type = None
                    subtask_cnt = 0
                    subtasks = []
                    summary = None
                    labels = ''
                    priority = None
                    state = None
                    stat_cat = None
                    reporter = None
                    assignee = None
                    d_created = None
                    d_due = None
                    d_start = None
                    d_updated = None
                    d_resolution = None
                    if 'key' in issue:
                        i_key = issue['key']
                        if 'fields' in issue:
                            if 'issuetype' in issue['fields']:
                                if (issue['fields']['issuetype'] != [] and
                                    issue['fields']['issuetype'] is not None):
                                    if 'name' in issue['fields']['issuetype']:
                                        i_type = issue['fields']['issuetype']['name']
                            if 'subtasks' in issue['fields']:
                                if (issue['fields']['subtasks'] != [] and
                                    issue['fields']['subtasks'] is not None):
                                    for task in issue['fields']['subtasks']:
                                        subtask_cnt += 1
                                        subtasks.append(task['key'])
                            if 'summary' in issue['fields']:
                                summary = issue['fields']['summary']
                            if 'labels' in issue['fields']:
                                if (issue['fields']['labels'] != [] and
                                    issue['fields']['labels'] is not None):
                                    for label in issue['fields']['labels']:
                                        labels += str(label) + "; "
                                    labels += "None"
                                    labels = labels.replace("; None", "")
                            if 'priority' in issue['fields']:
                                if (issue['fields']['priority'] != [] and
                                    issue['fields']['priority'] is not None):
                                    if 'name' in issue['fields']['priority']:
                                        priority = issue['fields']['priority']['name']
                            if 'status' in issue['fields']:
                                if (issue['fields']['status'] != [] and
                                    issue['fields']['status'] is not None):
                                    if 'name' in issue['fields']['status']:
                                        state = issue['fields']['status']['name']
                                    if 'statusCategory' in issue['fields']['status']:
                                        if (issue['fields']['status']['statusCategory'] != [] and
                                            issue['fields']['status']['statusCategory'] is not None):
                                            if 'name' in issue['fields']['status']['statusCategory']:
                                                stat_cat = issue['fields']['status']['statusCategory']['name']
                            if 'reporter' in issue['fields']:
                                if (issue['fields']['reporter'] != [] and
                                    issue['fields']['reporter'] is not None):
                                    if 'displayName' in issue['fields']['reporter']:
                                        reporter = issue['fields']['reporter']['displayName']
                            if 'assignee' in issue['fields']:
                                if (issue['fields']['assignee'] != [] and
                                    issue['fields']['assignee'] is not None):
                                    if 'displayName' in issue['fields']['assignee']:
                                        assignee = issue['fields']['assignee']['displayName']
                            if 'created' in issue['fields']:
                                d_created = str(issue['fields']['created']).split("T",1)[0]
                            if 'duedate' in issue['fields']:
                                d_due = issue['fields']['duedate']
                            if 'updated' in issue['fields']:
                                d_updated = str(issue['fields']['updated']).split("T",1)[0]
                            if 'resolutiondate' in issue['fields']:
                                if (state == 'Done' and
                                    issue['fields']['resolutiondate'] is not None):
                                    d_resolution = str(issue['fields']['resolutiondate']).split("T",1)[0]
                            if 'customfield_14841' in issue['fields']:
                                if issue['fields']['customfield_14841'] is not None:
                                    d_start = issue['fields']['customfield_14841'].split("T",1)[0]
                        if labels == '':
                            labels = None
                        if i_type == 'Project':
                            children.append({'IssueKey': i_key, 'IssueType': i_type,
                                             'Summary': summary, 'SubtaskCount': subtask_cnt,
                                             'Subtasks': subtasks, 'Labels': labels,
                                             'Priority': priority, 'State': state,
                                             'JiraStatusCategory': stat_cat, 'Reporter': reporter,
                                             'Assignee': assignee, 'CreatedDate': d_created,
                                             'DueDate': d_due, 'UpdatedDate': d_updated,
                                             'ResolutionDate': d_resolution, 'StartDate': d_start})
        return children

    @staticmethod
    def get_child_epics(jira_key):
        """Used by infosecdashboard.py for updating child epics"""
        children = []
        jira_project_key = str(jira_key).split("-",1)[0]
        if jira_project_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/3/search?maxResults=50"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        # find = f'issuetype = Epic AND issuekey in portfolioChildIssuesOf("{jira_key}") AND '
        # find += '(updatedDate >= -7d OR created >= -7d) order by created DESC'
        find = f'issuetype = Epic AND issuekey in portfolioChildIssuesOf("{jira_key}")'
        query = {
            'jql': find
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issues' in response:
                for issue in response['issues']:
                    i_key = None
                    i_type = None
                    subtask_cnt = 0
                    subtasks = []
                    summary = None
                    labels = ''
                    priority = None
                    state = None
                    stat_cat = None
                    reporter = None
                    assignee = None
                    d_created = None
                    d_due = None
                    d_start = None
                    d_updated = None
                    d_resolution = None
                    if 'key' in issue:
                        i_key = issue['key']
                        if 'fields' in issue:
                            if 'issuetype' in issue['fields']:
                                if (issue['fields']['issuetype'] != [] and
                                    issue['fields']['issuetype'] != None):
                                    if 'name' in issue['fields']['issuetype']:
                                        i_type = issue['fields']['issuetype']['name']
                                        i_type = str(i_type).replace("'","")
                            if 'subtasks' in issue['fields']:
                                if (issue['fields']['subtasks'] != [] and
                                    issue['fields']['subtasks'] != None):
                                    for task in issue['fields']['subtasks']:
                                        subtask_cnt += 1
                                        subtasks.append(task['key'])
                            if 'summary' in issue['fields']:
                                summary = issue['fields']['summary']
                                summary = str(summary).replace("'","")
                            if 'labels' in issue['fields']:
                                if (issue['fields']['labels'] != [] and
                                    issue['fields']['labels'] != None):
                                    for label in issue['fields']['labels']:
                                        labels += str(label) + "; "
                                    labels += "None"
                                    labels = labels.replace("; None", "").replace("'","")
                            if 'priority' in issue['fields']:
                                if (issue['fields']['priority'] != [] and
                                    issue['fields']['priority'] != None):
                                    if 'name' in issue['fields']['priority']:
                                        priority = issue['fields']['priority']['name']
                            if 'status' in issue['fields']:
                                if (issue['fields']['status'] != [] and
                                    issue['fields']['status'] != None):
                                    if 'name' in issue['fields']['status']:
                                        state = issue['fields']['status']['name']
                                    if 'statusCategory' in issue['fields']['status']:
                                        if (issue['fields']['status']['statusCategory'] != [] and
                                            issue['fields']['status']['statusCategory'] != None):
                                            if 'name' in issue['fields']['status']['statusCategory']:
                                                stat_cat = issue['fields']['status']['statusCategory']['name']
                            if 'reporter' in issue['fields']:
                                if (issue['fields']['reporter'] != [] and
                                    issue['fields']['reporter'] != None):
                                    if 'displayName' in issue['fields']['reporter']:
                                        reporter = issue['fields']['reporter']['displayName']
                            if 'assignee' in issue['fields']:
                                if (issue['fields']['assignee'] != [] and
                                    issue['fields']['assignee'] != None):
                                    if 'displayName' in issue['fields']['assignee']:
                                        assignee = issue['fields']['assignee']['displayName']
                            if 'created' in issue['fields']:
                                d_created = str(issue['fields']['created'])
                                if d_created is not None:
                                    d_created = d_created.split("T",1)[0]
                            if 'duedate' in issue['fields']:
                                d_due = issue['fields']['duedate']
                                if d_due is not None:
                                    d_due = d_due.split("T",1)[0]
                            if 'updated' in issue['fields']:
                                d_updated = str(issue['fields']['updated'])
                                if d_updated is not None:
                                    d_updated = d_updated.split("T",1)[0]
                            if 'resolutiondate' in issue['fields']:
                                if state == 'Done' and issue['fields']['resolutiondate'] != None:
                                    date = issue['fields']['resolutiondate']
                                    d_resolution = str(date)
                                    if d_resolution is not None:
                                        d_resolution = d_resolution.split("T",1)[0]
                            if 'customfield_14841' in issue['fields']:
                                if issue['fields']['customfield_14841'] != None:
                                    d_start = issue['fields']['customfield_14841']
                                    if d_start is not None:
                                        d_start = d_start.split("T",1)[0]
                        if labels == '':
                            labels = None
                        if i_type == 'Epic':
                            children.append({'IssueKey': i_key, 'IssueType': i_type,
                                             'Summary': summary, 'SubtaskCount': subtask_cnt,
                                             'Subtasks': subtasks, 'Labels': labels,
                                             'Priority': priority, 'State': state,
                                             'JiraStatusCategory': stat_cat, 'Reporter': reporter,
                                             'Assignee': assignee, 'CreatedDate': d_created,
                                             'DueDate': d_due, 'UpdatedDate': d_updated,
                                             'ResolutionDate': d_resolution, 'StartDate': d_start})
        return children

    @staticmethod
    def get_child_issues(proj_key, start_at):
        """Allows looping through child issues for a given proj key for updates to the
        InfoSecDashboard database"""
        issues = []
        if proj_key == 'FOUR':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        if start_at == 0:
            server = f"{server}/rest/api/3/search"
        else:
            server = f"{server}/rest/api/3/search?maxResults=50&startAt={start_at}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        find = f'"Epic Link"="{proj_key}" AND (updatedDate >= -14d OR created >= -14d) order by '
        find += 'created DESC'
        query = {
            'jql': find
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issues' in response:
                for issue in response['issues']:
                    i_key = None
                    i_type = None
                    subtask_cnt = 0
                    subtasks = []
                    summary = None
                    labels = ''
                    priority = None
                    state = None
                    stat_cat = None
                    reported = None
                    assignee = None
                    d_created = None
                    d_due = None
                    d_start = None
                    d_update = None
                    d_resolution = None
                    if 'key' in issue:
                        i_key = issue['key']
                        if 'fields' in issue:
                            if 'issuetype' in issue['fields']:
                                if (issue['fields']['issuetype'] != [] and
                                    issue['fields']['issuetype'] != None):
                                    if 'name' in issue['fields']['issuetype']:
                                        i_type = issue['fields']['issuetype']['name']
                            if 'subtasks' in issue['fields']:
                                if (issue['fields']['subtasks'] != [] and
                                    issue['fields']['subtasks'] != None):
                                    for task in issue['fields']['subtasks']:
                                        subtask_cnt += 1
                                        subtasks.append(task['key'])
                            if 'summary' in issue['fields']:
                                summary = issue['fields']['summary']
                            if 'labels' in issue['fields']:
                                if (issue['fields']['labels'] != [] and
                                    issue['fields']['labels'] != None):
                                    for label in issue['fields']['labels']:
                                        labels += str(label) + "; "
                                    labels += "None"
                                    labels = labels.replace("; None", "")
                            if 'priority' in issue['fields']:
                                if (issue['fields']['priority'] != [] and
                                    issue['fields']['priority'] != None):
                                    if 'name' in issue['fields']['priority']:
                                        priority = issue['fields']['priority']['name']
                            if 'status' in issue['fields']:
                                if (issue['fields']['status'] != [] and
                                    issue['fields']['status'] != None):
                                    if 'name' in issue['fields']['status']:
                                        state = issue['fields']['status']['name']
                                    if 'statusCategory' in issue['fields']['status']:
                                        if (issue['fields']['status']['statusCategory'] != [] and
                                            issue['fields']['status']['statusCategory'] != None):
                                            if 'name' in issue['fields']['status']['statusCategory']:
                                                stat_cat = issue['fields']['status']['statusCategory']['name']
                            if 'reporter' in issue['fields']:
                                if (issue['fields']['reporter'] != [] and
                                    issue['fields']['reporter'] != None):
                                    if 'displayName' in issue['fields']['reporter']:
                                        reported = issue['fields']['reporter']['displayName']
                            if 'assignee' in issue['fields']:
                                if (issue['fields']['assignee'] != [] and
                                    issue['fields']['assignee'] != None):
                                    if 'displayName' in issue['fields']['assignee']:
                                        assignee = issue['fields']['assignee']['displayName']
                            if 'created' in issue['fields']:
                                d_created = str(issue['fields']['created'])
                                if d_created is not None:
                                    d_created = d_created.split("T",1)[0]
                            if 'duedate' in issue['fields']:
                                d_due = issue['fields']['duedate']
                                if d_due is not None:
                                    d_due = d_due.split("T",1)[0]
                            if 'updated' in issue['fields']:
                                d_update = str(issue['fields']['updated'])
                                if d_update is not None:
                                    d_update = d_update.split("T",1)[0]
                            if 'resolutiondate' in issue['fields']:
                                if state == 'Done' and issue['fields']['resolutiondate'] != None:
                                    date = issue['fields']['resolutiondate']
                                    d_resolution = str(date).split("T",1)[0]
                            if 'customfield_14841' in issue['fields']:
                                if issue['fields']['customfield_14841'] != None:
                                    d_start = issue['fields']['customfield_14841']
                                    if d_start is not None:
                                        d_start = d_start.split("T",1)[0]
                        if labels == '':
                            labels = None
                    issues.append({'IssueKey': i_key, 'IssueType': i_type, 'Summary': summary,
                                    'SubtaskCount': subtask_cnt, 'Subtasks': subtasks,
                                    'Labels': labels, 'Priority': priority, 'State': state,
                                    'JiraStatusCategory': stat_cat, 'Reporter': reported,
                                    'Assignee': assignee, 'CreatedDate': d_created,
                                    'DueDate': d_due, 'UpdatedDate': d_update,
                                    'ResolutionDate': d_resolution,
                                    'StartDate': d_start})
        return issues

    @staticmethod
    def get_task_json(issue_key):
        """Used for updating tasks in the InfoSecDashboard database"""
        tasks = {}
        jira_project_key = str(issue_key).split("-",1)[0]
        if jira_project_key.lower() == 'four':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/3/search"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        find = f'key = "{issue_key}"'
        query = {
            'jql': find
        }
        response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
        if response.status_code == 200 and 'issues' in response.json():
            dict = response.json()
            dict = dict['issues'][0]
            tasks = {}
            task_key = None
            i_type = None
            subtask_cnt = 0
            subtasks = []
            labels = None
            priority = None
            state = None
            stat_cat = None
            summary = None
            reporter = None
            assignee = None
            d_created = None
            d_due = None
            d_start = None
            d_updated = None
            d_resolution = None
            if 'key' in dict:
                task_key = str(dict['key']).replace("'","")
            if 'fields' in dict:
                if 'issuetype' in dict['fields']:
                    if dict['fields']['issuetype'] != None and dict['fields']['issuetype'] != {}:
                        if 'name' in dict['fields']['issuetype']:
                            i_type = str(dict['fields']['issuetype']['name']).replace("'","")
                if 'subtasks' in dict['fields']:
                    if dict['fields']['subtasks'] != None and dict['fields']['subtasks'] != []:
                        for task in dict['fields']['subtasks']:
                            subtask_cnt += 1
                            subtasks.append(str(task['key']).replace("'",""))
                if 'summary' in dict['fields']:
                    summary = str(dict['fields']['summary']).replace("'","")
                if 'labels' in dict['fields']:
                    if dict['fields']['labels'] != None and dict['fields']['labels'] != []:
                        labels = ''
                        for label in dict['fields']['labels']:
                            labels += str(label).replace("'","") + "; "
                        labels += "None"
                        labels = str(labels).replace("; None","")
                if labels == None or labels == 'None' or labels == '':
                    labels = None
                if 'priority' in dict['fields']:
                    if dict['fields']['priority'] != None and dict['fields']['priority'] != {}:
                        if 'name' in dict['fields']['priority']:
                            priority = str(dict['fields']['priority']['name']).replace("'","")
                if 'status' in dict['fields']:
                    if dict['fields']['status'] != None and dict['fields']['status'] != {}:
                        if 'name' in dict['fields']['status']:
                            state = str(dict['fields']['status']['name']).replace("'","")
                        if 'statusCategory' in dict['fields']['status']:
                            if (dict['fields']['status']['statusCategory'] != None and
                                dict['fields']['status']['statusCategory'] != []):
                                if 'name' in dict['fields']['status']['statusCategory']:
                                    cat = dict['fields']['status']['statusCategory']['name']
                                    stat_cat = str(cat).replace("'","")
                if 'reporter' in dict['fields']:
                    if dict['fields']['reporter'] != None and dict['fields']['reporter'] != {}:
                        if 'displayName' in dict['fields']['reporter']:
                            rep = dict['fields']['reporter']['displayName']
                            reporter = str(rep).replace("'","")
                if 'assignee' in dict['fields']:
                    if dict['fields']['assignee'] != None and dict['fields']['assignee'] != {}:
                        if 'displayName' in dict['fields']['assignee']:
                            agn = dict['fields']['assignee']['displayName']
                            assignee = str(agn).replace("'","")
                if 'created' in dict['fields']:
                    d_created = str(dict['fields']['created']).split("T",1)[0]
                if 'updated' in dict['fields']:
                    d_updated = str(dict['fields']['updated']).split("T",1)[0]
                if 'duedate' in dict['fields']:
                    d_due = str(dict['fields']['duedate']).split("T",1)[0]
                if 'resolutiondate' in dict['fields']:
                    if state == 'Done' and dict['fields']['resolutiondate'] != None:
                        d_resolution = str(dict['fields']['resolutiondate']).split("T",1)[0]
                if 'customfield_14841' in dict['fields']:
                    if dict['fields']['customfield_14841'] != None:
                        d_start = str(dict['fields']['customfield_14841']).split("T",1)[0]
            tasks['IssueKey'] =  task_key
            tasks['IssueType'] = i_type
            tasks['Summary'] = summary
            tasks['SubtaskCount'] = subtask_cnt
            tasks['Subtasks'] = subtasks
            tasks['Labels'] = labels
            tasks['Priority'] = priority
            tasks['State'] = state
            tasks['JiraStatusCategory'] = stat_cat
            tasks['Reporter'] = reporter
            tasks['Assignee'] = assignee
            tasks['CreatedDate'] = d_created
            tasks['UpdatedDate'] = d_updated
            tasks['DueDate'] = d_due
            tasks['ResolutionDate'] = d_resolution
            tasks['StartDate'] = d_start
        return tasks

    @staticmethod
    def has_sf_ticket_type(proj_key):
        """Used for getting available ticket types"""
        has_sf = 0
        if proj_key.lower() == 'four':
            user = JIRA_USER
            apikey = JIRA_FOUR_KEY
            server =  JIRA_FOUR_SERVER
        else:
            user = JIRA_USER
            apikey = JIRA_KEY
            server =  JIRA_SERVER
        auth = HTTPBasicAuth(str(user),str(apikey))
        server = f"{server}/rest/api/2/project/{proj_key}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.get(server,headers=headers,auth=auth,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'issueTypes' in response:
                for type in response['issueTypes']:
                    if 'name' in type:
                        if type['name'] == 'Security Finding':
                            has_sf = 1
        return has_sf

def jira_connection(the_repo):
    """Creates the connection to Jira"""
    #Resets the jira_connection to ensure correct assignment of the connection details
    connection_to_jira = None
    if the_repo.lower() == 'four':
        user = JIRA_FOUR_USER
        apikey = JIRA_FOUR_KEY
        server =  JIRA_FOUR_SERVER
    else:
        user = JIRA_USER
        apikey = JIRA_KEY
        server =  JIRA_SERVER
    options = {"server": server}
    connection_to_jira = JIRA(options, basic_auth=(user, apikey))
    return connection_to_jira

def get_open_jira_issues(repo, max_results, start_at, jira_project_key):
    """Retrieves paginated results for Jira issues added/changed in the past 7 days"""
    response_array = {}
    insert_issues = []
    update_issues = []
    if repo == 'four':
        user = JIRA_FOUR_USER
        apikey = JIRA_FOUR_KEY
        server =  JIRA_FOUR_SERVER
    else:
        user = JIRA_USER
        apikey = JIRA_KEY
        server =  JIRA_SERVER
    auth = HTTPBasicAuth(str(user),str(apikey))
    if start_at == 0:
        server = str(server) + "/rest/api/3/search"
    else:
        start_at = "&startAt=" + str(start_at)
        max_results = 100
        server = str(server) + "/rest/api/3/search?maxResults=" + str(max_results) + str(start_at)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if repo is not None and repo == 'four':
        query = {
            'jql': '(labels = security_finding OR labels = AppSec) AND (updatedDate >= -7d OR created >= -7d) AND issuetype != Epic ORDER BY key ASC'
        }
    else:
        if jira_project_key == 'All':
            query = {
                'jql': 'issuetype = "Security Finding" AND (updatedDate >= -7d OR created >= -7d) ORDER BY key ASC'
            }
        else:
            query = {
                'jql': 'labels = "' + str(repo) + '" AND issuetype = "Security Finding" AND (updatedDate >= -7d OR created >= -7d) ORDER BY key ASC'
            }
    response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
    response_status = response.status_code
    if response_status == 200:
        response = response.json()
        issue_count = 0
        start_at = None
        total = None
        if 'startAt' in response:
            start_at =  response['startAt']
        if 'total' in response:
            total =  response['total']
        if 'issues' in response:
            issue_count += len(response['issues'])
            for issue in response['issues']:
                jira_issue_key = issue['key']
                jira_project_key = str(jira_issue_key).split("-", maxsplit=1)[0]
                current_epic = None
                current_epic_project_key = None
                jira_summary = None
                jira_status = None
                jira_status_category = None
                jira_created = None
                jira_due_date = None
                tech_debt = 0
                source = None
                jira_resolution_date = None
                jira_priority = None
                if 'fields' in issue and issue['fields'] is not None and issue['fields'] != {}:
                    if 'priority' in issue['fields']:
                        if 'name' in issue['fields']['priority']:
                            jira_priority = issue['fields']['priority']['name']
                    if repo == 'four':
                        if 'customfield_10035' in issue['fields']:
                            jira_due_date = issue['fields']['customfield_10035']
                    else:
                        if 'duedate' in issue['fields']:
                            jira_due_date = issue['fields']['duedate']
                    if 'parent' in issue['fields']:
                        if (issue['fields']['parent'] is not None and
                            'key' in issue['fields']['parent']):
                            current_epic = issue['fields']['parent']['key']
                            current_epic_project_key = str(current_epic).split("-", maxsplit=1)[0]
                    if 'summary' in issue['fields']:
                        jira_summary = issue['fields']['summary']
                        source = 'Other'
                        if jira_summary.__contains__("Pen Test"):
                            source = 'Pen Test'
                        elif jira_summary.__contains__("Open Source"):
                            source = 'Mend OS'
                        elif jira_summary.__contains__("SAST Finding"):
                            source = 'Checkmarx'
                    if 'status' in issue['fields']:
                        if 'name' in issue['fields']['status']:
                            jira_status = issue['fields']['status']['name']
                        if 'statusCategory' in issue['fields']['status']:
                            if 'name' in issue['fields']['status']['statusCategory']:
                                jira_status_category = issue['fields']['status']['statusCategory']['name']
                                if jira_status_category == 'Done':
                                    if repo == 'four':
                                        if 'statuscategorychangedate' in issue['fields']:
                                            jira_resolution_date = str(issue['fields']['statuscategorychangedate']).split("T", maxsplit=1)[0]
                                            if jira_resolution_date is not None and jira_resolution_date != 'None':
                                                jira_resolution_date = str(issue['fields']['statuscategorychangedate']).split(".", maxsplit=1)[0].replace("T"," ")
                                    else:
                                        if 'resolutiondate' in issue['fields']:
                                            jira_resolution_date = str(issue['fields']['resolutiondate']).split("T", maxsplit=1)[0]
                                            if jira_resolution_date is not None and jira_resolution_date != 'None':
                                                jira_resolution_date = str(issue['fields']['resolutiondate']).split(".", maxsplit=1)[0].replace("T"," ")
                    if 'created' in issue['fields']:
                        jira_created_date = str(issue['fields']['created']).split("T", maxsplit=1)[0]
                        if jira_created_date is not None and jira_created_date != 'None':
                            jira_created = str(issue['fields']['created']).split(".", maxsplit=1)[0].replace("T"," ")
                    if 'labels' in issue['fields']:
                        if issue['fields']['labels'] != [] and issue['fields']['labels'] != 'None':
                            if 'tech_debt' in issue['fields']['labels']:
                                tech_debt = 1
                exists = JIDatabase.check_for_jira_issue(jira_issue_key)
                if exists['Results'] is False:
                    insert_issues.append({'Repo': repo, 'OriginalEpic': current_epic, 'OriginalEpicProjectKey': current_epic_project_key, 'CurrentEpic': current_epic, 'CurrentEpicProjectKey': current_epic_project_key, 'JiraIssueKey': jira_issue_key, 'JiraProjectKey': jira_project_key, 'JiraSummary': jira_summary, 'JiraPriority': jira_priority, 'JiraDueDate': jira_due_date, 'JiraStatus': jira_status, 'JiraStatusCategory': jira_status_category, 'TechDebt': tech_debt, 'JiraCreated': jira_created, 'JiraResolutionDate': jira_resolution_date, 'Source': source})
                else:
                    update_issues.append({'SET': {'CurrentEpic': current_epic,
                                                  'CurrentEpicProjectKey': current_epic_project_key,
                                                  'JiraProjectKey': jira_project_key,
                                                  'JiraSummary': jira_summary,
                                                  'JiraPriority': jira_priority,
                                                  'JiraDueDate': jira_due_date,
                                                  'JiraStatus': jira_status,
                                                  'JiraStatusCategory': jira_status_category,
                                                  'TechDebt': tech_debt,
                                                  'JiraCreated': jira_created,
                                                  'JiraResolutionDate': jira_resolution_date,
                                                  'Source': source},
                                          'WHERE_EQUAL': {'JiraIssueKey': jira_issue_key}})
        response_array['startAt'] = start_at
        response_array['total'] = total
        response_array['issueCount'] = issue_count
        response_array['issues'] = insert_issues
        response_array['updates'] = update_issues
    return {'FatalCount': 0, 'ExceptionCount': 0, 'Results': response_array}

def check_moved_issue(repo, current_epic, current_epic_project_key, jira_issue_key,
                      jira_project_key,main_log=LOG):
    """Retrieves the current Epic and Jira issue key for a Jira ticket"""
    u_cnt = 0
    u_array = []
    if repo is not None and repo == 'four':
        return 0
    else:
        user = JIRA_USER
        apikey = JIRA_KEY
        server =  JIRA_SERVER
    auth = HTTPBasicAuth(str(user),str(apikey))
    server = str(server) + "/rest/api/3/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    query = {
        'jql': 'key = "' + str(jira_issue_key) + '"'
    }
    response = requests.get(server, headers=headers, params=query, auth=auth, timeout=60)
    response_status = response.status_code
    if response_status == 200:
        response = response.json()
        if 'issues' in response:
            new_jira_issue_key = response['issues'][0]['key']
            new_jira_project_key = str(new_jira_issue_key).split("-", maxsplit=1)[0]
            new_current_epic = None
            new_current_epic_proj_key = None
            if ('fields' in response['issues'][0] and response['issues'][0]['fields'] is not None
                and response['issues'][0]['fields'] != {}):
                if 'parent' in response['issues'][0]['fields']:
                    if response['issues'][0]['fields']['parent'] is not None:
                        if 'key' in response['issues'][0]['fields']['parent']:
                            new_current_epic = response['issues'][0]['fields']['parent']['key']
                            new_current_epic_proj_key = new_current_epic.split("-",maxsplit=1)[0]
            updates = {}
            if current_epic is None and new_current_epic is not None:
                updates['OriginalEpic'] = new_current_epic
                updates['OriginalEpicProjectKey'] = current_epic
            elif current_epic is not None and new_current_epic != current_epic:
                updates['OriginalEpic'] = current_epic
                updates['CurrentEpic'] = new_current_epic
                updates['OriginalEpicProjectKey'] = current_epic_project_key
                updates['CurrentEpicProjectKey'] = new_current_epic_proj_key
            if new_jira_issue_key is not None and (jira_issue_key != new_jira_issue_key or
                                                   jira_project_key != new_jira_project_key):
                updates['OldJiraIssueKey'] = jira_issue_key
                updates['JiraIssueKey'] = new_jira_issue_key
                updates['OldJiraProjectKey'] = jira_project_key
                updates['JiraProjectKey'] = new_jira_project_key
            if updates != {}:
                u_array.append({'SET': updates,
                                'WHERE_EQUAL': {'JiraIssueKey': jira_issue_key},
                                'WHERE_NOT': None})
        try:
            u_cnt += update_multiple_in_table('JiraIssues',u_array)
        except Exception as e_details:
            func = f"update_multiple_in_table('JiraIssues','{u_array}')"
            e_code = 'CJF-CMI-001'
            TheLogs.function_exception(func,e_code,e_details,LOG_EXCEPTION,main_log,EX_LOG_FILE,
                                    ScrVar.src,inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
    return u_cnt

def get_open_tool_issues(repo,max_results,start_at,tool=None):
    """Retrieves paginated results for Checkmarx Jira issues added/changed in the past 7 days"""
    response_array = {}
    insert_issues = []
    update_issues = []
    add_summary = ''
    if tool is not None:
        if tool.lower() == 'checkmarx':
            add_summary = ' AND summary ~ "SAST Findings"'
        elif 'mend os' in tool.lower():
            add_summary = ' AND (summary ~ "OS Findings" OR summary ~ "Unapproved Open Source License Use")'
    if repo == 'four':
        user = JIRA_FOUR_USER
        apikey = JIRA_FOUR_KEY
        server =  JIRA_FOUR_SERVER
    else:
        user = JIRA_USER
        apikey = JIRA_KEY
        server =  JIRA_SERVER
    auth = HTTPBasicAuth(str(user),str(apikey))
    start = "startAt=" + str(start_at)
    if max_results == 0 or start_at == 0:
        server = str(server) + "/rest/api/3/search"
    else:
        server = str(server) + "/rest/api/3/search?" + str(start)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if repo is not None and repo == 'four':
        query = {
            'jql': f'(labels = security_finding OR labels = AppSec) AND (updatedDate >= -7d OR created >= -7d) AND issuetype != Epic{add_summary} ORDER BY key ASC'
        }
    elif repo == 'All':
        query = {
            'jql': f'issuetype = "Security Finding" AND (updatedDate >= -7d OR created >= -7d){add_summary} ORDER BY key ASC'
        }
    else:
        query = {
            'jql': f'labels = "{repo}" AND issuetype = "Security Finding"{add_summary} AND (updatedDate >= -7d OR created >= -7d) ORDER BY key ASC'
        }
    response = requests.get(server,headers=headers,params=query,auth=auth,timeout=60)
    response_status = response.status_code
    if response_status == 200:
        response = response.json()
        issue_count = 0
        start_at = None
        total = None
        if 'startAt' in response:
            start_at =  response['startAt']
        if 'total' in response:
            total =  response['total']
        if 'issues' in response:
            issue_count += len(response['issues'])
            for issue in response['issues']:
                jira_issue_key = issue['key']
                jira_project_key = str(jira_issue_key).split("-", maxsplit=1)[0]
                current_epic = None
                current_epic_project_key = None
                jira_summary = None
                jira_status = None
                jira_status_category = None
                jira_created = None
                jira_due_date = None
                tech_debt = 0
                source = None
                jira_resolution_date = None
                jira_priority = None
                if 'fields' in issue and issue['fields'] is not None and issue['fields'] != {}:
                    if 'priority' in issue['fields']:
                        if 'name' in issue['fields']['priority']:
                            jira_priority = issue['fields']['priority']['name']
                    if repo == 'four':
                        if 'customfield_10035' in issue['fields']:
                            jira_due_date = issue['fields']['customfield_10035']
                    else:
                        if 'duedate' in issue['fields']:
                            jira_due_date = issue['fields']['duedate']
                    if 'parent' in issue['fields']:
                        if (issue['fields']['parent'] is not None and
                            'key' in issue['fields']['parent']):
                            current_epic = issue['fields']['parent']['key']
                            current_epic_project_key = str(current_epic).split("-", maxsplit=1)[0]
                    if 'summary' in issue['fields']:
                        jira_summary = issue['fields']['summary']
                        source = 'Other'
                        if jira_summary.__contains__("Pen Test"):
                            source = 'Pen Test'
                        elif jira_summary.__contains__("Open Source"):
                            source = 'Mend OS'
                        elif jira_summary.__contains__("SAST Finding"):
                            source = 'Checkmarx'
                    if 'status' in issue['fields']:
                        if 'name' in issue['fields']['status']:
                            jira_status = issue['fields']['status']['name']
                        if 'statusCategory' in issue['fields']['status']:
                            if 'name' in issue['fields']['status']['statusCategory']:
                                jira_status_category = issue['fields']['status']['statusCategory']['name']
                                if jira_status_category == 'Done':
                                    if repo == 'four':
                                        if 'statuscategorychangedate' in issue['fields']:
                                            jira_resolution_date = str(issue['fields']['statuscategorychangedate']).split("T", maxsplit=1)[0]
                                            if jira_resolution_date is not None and jira_resolution_date != 'None':
                                                jira_resolution_date = str(issue['fields']['statuscategorychangedate']).split(".", maxsplit=1)[0].replace("T"," ")
                                    else:
                                        if 'resolutiondate' in issue['fields']:
                                            jira_resolution_date = str(issue['fields']['resolutiondate']).split("T", maxsplit=1)[0]
                                            if jira_resolution_date is not None and jira_resolution_date != 'None':
                                                jira_resolution_date = str(issue['fields']['resolutiondate']).split(".", maxsplit=1)[0].replace("T"," ")
                    if 'created' in issue['fields']:
                        jira_created_date = str(issue['fields']['created']).split("T", maxsplit=1)[0]
                        if jira_created_date is not None and jira_created_date != 'None':
                            jira_created = str(issue['fields']['created']).split(".", maxsplit=1)[0].replace("T"," ")
                            dt_created = str(issue['fields']['created']).replace("T"," ").split(".",1)[0]
                    if 'labels' in issue['fields']:
                        if issue['fields']['labels'] != [] and issue['fields']['labels'] != 'None':
                            if 'tech_debt' in issue['fields']['labels']:
                                tech_debt = 1
                exists = JIDatabase.check_for_jira_issue(jira_issue_key)
                if exists['Results'] is False:
                    insert_issues.append({'Repo':repo,'OriginalEpic':current_epic,
                                          'OriginalEpicProjectKey':current_epic_project_key,
                                          'CurrentEpic':current_epic,'CurrentEpicProjectKey':
                                          current_epic_project_key,'JiraIssueKey':jira_issue_key,
                                          'JiraProjectKey':jira_project_key,'JiraSummary':
                                          jira_summary,'JiraPriority':jira_priority,'JiraDueDate':
                                          jira_due_date,'JiraStatus':jira_status,
                                          'JiraStatusCategory':jira_status_category,'TechDebt':
                                          tech_debt,'JiraCreated':jira_created,
                                          'JiraResolutionDate':jira_resolution_date,
                                          'CreatedDateTime':str(dt_created),'Source':source})
                else:
                    update_issues.append({'SET': {'CurrentEpic': current_epic,
                                                  'CurrentEpicProjectKey': current_epic_project_key,
                                                  'JiraProjectKey': jira_project_key,
                                                  'JiraSummary': jira_summary,
                                                  'JiraPriority': jira_priority,
                                                  'JiraDueDate': jira_due_date,
                                                  'JiraStatus': jira_status,
                                                  'JiraStatusCategory': jira_status_category,
                                                  'TechDebt': tech_debt,
                                                  'JiraCreated': jira_created,
                                                  'CreatedDateTime': str(dt_created),
                                                  'JiraResolutionDate': jira_resolution_date,
                                                  'Source': source},
                                          'WHERE_EQUAL': {'JiraIssueKey': jira_issue_key},
                                          'WHERE_NOT': None})
        response_array['startAt'] = start_at
        response_array['total'] = total
        response_array['issueCount'] = issue_count
        response_array['issues'] = insert_issues
        response_array['updates'] = update_issues
    return {'FatalCount': 0, 'ExceptionCount': 0, 'Results': response_array}

def get_ticket_transitions(repo, jira_issue_key):
    """Gets the possible transitions for a Jira ticket"""
    if repo == 'four':
        email = JIRA_FOUR_USER
        api_token = JIRA_FOUR_KEY
        url =  f"{JIRA_FOUR_SERVER}/rest/api/2/issue/{jira_issue_key}/transitions"
    else:
        email = JIRA_USER
        api_token = JIRA_KEY
        url =  f"{JIRA_SERVER}/rest/api/2/issue/{jira_issue_key}/transitions"
    auth = HTTPBasicAuth(email, api_token)
    headers = {
        "Accept": "application/json"
    }
    transition_response = requests.get(url, auth=auth, headers=headers, timeout=60)
    response = None
    if transition_response.status_code == 200:
        transition_response = transition_response.json()
        if 'transitions' in transition_response:
            response = transition_response['transitions']
    return response

def update_jira_description(jira_issue_key, repo, new_description):
    """Updates the description for a Jira ticket to only what is provided"""
    issue = jira_connection(repo).issue(jira_issue_key)
    issue.update(fields={'description': new_description})
