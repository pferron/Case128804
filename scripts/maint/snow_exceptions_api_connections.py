"""Queries SNow directly"""

import os
import traceback
import inspect
import re
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import requests
from common.logging import TheLogs
from common.database_appsec import select,insert_multiple_into_table,update_multiple_in_table
from common.jira_functions import GeneralTicketing
from maint.snow_exceptions_processing import SNowQueries

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SNOW_URL = os.environ.get('SNOW_URL')
SNOW_KEY = os.environ.get('SNOW_KEY')
SNOW_USER = os.environ.get('SNOW_USER')
SNOW_TABLE_APP = os.environ.get('SNOW_TABLE_APP')
SNOW_TABLE_APPROVAL = os.environ.get('SNOW_TABLE_APPROVAL')
SNOW_TABLE_CHANGE = os.environ.get('SNOW_TABLE_CHANGE')
SNOW_TABLE_EXCEPTION_FIELDS = os.environ.get('SNOW_TABLE_EXCEPTION_FIELDS')
SNOW_TABLE_REQ_ITEM = os.environ.get('SNOW_TABLE_REQ_ITEM')
SNOW_TABLE_CMDB = os.environ.get('SNOW_TABLE_CMDB')
SNOW_TABLE_JIRA = os.environ.get('SNOW_TABLE_JIRA')
SNOW_TABLE_TASK = os.environ.get('SNOW_TABLE_TASK')
DB_USER = os.environ.get('DB_USER')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    u_cnt = 0
    a_cnt = 0
    get_approvers = []
    table_connect = None
    table_approval = None
    table_change = None
    table_group = None
    table_jira = None
    table_task = None
    table_user = None
    snow_jira_project_key = None
    cur_dt = datetime.now(tz=ZoneInfo('US/Mountain'))
    subtract_hours = 2
    if (cur_dt.hour > 0 and cur_dt.hour < 7) or (cur_dt.hour > 18):
        subtract_hours = 24
    hrdt = cur_dt - timedelta(hours=subtract_hours)
    month = hrdt.month
    if month < 10:
        month = f'0{month}'
    day = hrdt.day
    if day < 10:
        day = f'0{day}'
    hour = hrdt.hour
    if hour < 10:
        hour = f'0{hour}'
    minute = hrdt.minute
    if minute < 10:
        minute = f'0{minute}'
    second = hrdt.second
    if second < 10:
        second = f'0{second}'
    hrdt = f"'{hrdt.year}-{month}-{day}'%2C'{hour}%3A{minute}%3A{second}'"
    daydt = cur_dt - timedelta(hours=24)
    month = daydt.month
    if month < 10:
        month = f'0{month}'
    day = daydt.day
    if day < 10:
        day = f'0{day}'
    hour = daydt.hour
    if hour < 10:
        hour = f'0{hour}'
    minute = daydt.minute
    if minute < 10:
        minute = f'0{minute}'
    second = daydt.second
    if second < 10:
        second = f'0{second}'
    daydt = f"'{daydt.year}-{month}-{day}'%2C'{hour}%3A{minute}%3A{second}'"
    wkdt = cur_dt - timedelta(weeks=1)
    month = wkdt.month
    if month < 10:
        month = f'0{month}'
    day = wkdt.day
    if day < 10:
        day = f'0{day}'
    hour = wkdt.hour
    if hour < 10:
        hour = f'0{hour}'
    minute = wkdt.minute
    if minute < 10:
        minute = f'0{minute}'
    second = wkdt.second
    if second < 10:
        second = f'0{second}'
    wkdt = f"'{wkdt.year}-{month}-{day}'%2C'{hour}%3A{minute}%3A{second}'"
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = 0
        exception_count = 0
        if 'FatalCount' in dictionary:
            fatal_count = dictionary['FatalCount']
        if 'ExceptionCount' in dictionary:
            exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

class SNowAPI():
    """Returns data from the SNow API"""

    @staticmethod
    def update_snow_approvers(main_log=LOG,ex_log=LOG,ex_file=EX_LOG_FILE):
        """Pulls the list of current approvers for the Ciso Temp Exception Approval Group
        and updates the SNowSecurityApprovers table"""
        ScrVar.reset_exception_counts()
        message = 'Updates to SNowSecurityApprovers failed'
        i_users = []
        u_users = []
        call = '/table/sys_user_grmember'
        query_params = 'sysparm_display_value=true&sysparm_fields=user'
        query_params += '&group=Ciso%20Temp%20Exception%20Approval%20Group'
        url = f'{SNOW_URL}{call}?{query_params}'
        headers = {'Content-Type':'application/json','Accept':'application/json'}
        try:
            response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get('{url}',auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "SEAC-USA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if response.status_code == 200:
            response = response.json()
            if 'result' in response:
                if response['result'] != []:
                    mark_users = SNowQueries.mark_approvers_inactive(main_log,ex_log,ex_file)
                    ScrVar.update_exception_info(mark_users)
                for user in response['result']:
                    u_users.append({'SET':{'CurrentApprover':1},
                                    'WHERE_EQUAL':{'ApproverName':user['user']['display_value']}})
                    i_users.append({'ApproverName':user['user']['display_value'],'CurrentApprover':1,
                                    'AddedDate':datetime.now(),'AddedBy':DB_USER})
                try:
                    update_multiple_in_table('SNowSecurityApprovers',u_users,show_progress=False)
                except Exception as e_details:
                    func = f"update_multiple_in_table('SNowSecurityApprovers',{u_users},"
                    func += "show_progress=False)"
                    e_code = "SEAC-USA-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                            inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.ex_cnt += 1
                try:
                    insert_multiple_into_table('SNowSecurityApprovers',i_users,verify_on=['ApproverName'],
                                           show_progress=False)
                except Exception as e_details:
                    func = f"insert_multiple_into_table('SNowSecurityApprovers',{i_users},"
                    func += "verify_on=['ApproverName'],show_progress=False)"
                    e_code = "SEAC-USA-003"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                            inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.ex_cnt += 1
                if ScrVar.ex_cnt == 0:
                    message = 'SNowSecurityApprovers successfully updated'
                ScrVar.get_approvers = security_approvers(main_log,ex_log,ex_file)
        TheLogs.log_info(message,2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def process_exception_requests(period,main_log=LOG,
                                      ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE,ritm_ticket=None):
        """Returns a list of exception requests created and/or updated within the given period"""
        added = 0
        updated = 0
        ScrVar.reset_exception_counts()
        if ScrVar.get_approvers == []:
            ScrVar.get_approvers = security_approvers(main_log,ex_log,ex_file)
        existing_tickets = SNowQueries.get_all_ritms(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(existing_tickets)
        ex_tkts_w_jira = existing_tickets['Results']['JiraSet']
        ex_tkts_no_jira = existing_tickets['Results']['JiraNotSet']
        query_params = "sysparm_query="
        query_params += "short_description%3DInformation%20Security%20Standard%20Exception"
        query_params += "%5Eassignment_group%3D2653af3edb987010fe01e8ca48961917"
        if period == 'hourly':
            query_params += f'%5Esys_created_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.hrdt})'
            query_params += f'%5EORsys_updated_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.hrdt})'
            query_params += f'%5EORclosed_at%3E%3Djavascript%3Ags.dateGenerate({ScrVar.hrdt})'
        elif period == 'past_24_hours':
            query_params += f'%5Esys_created_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.daydt})'
            query_params += f'%5EORsys_updated_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.daydt})'
            query_params += f'%5EORclosed_at%3E%3Djavascript%3Ags.dateGenerate({ScrVar.daydt})'
        elif period == 'past_week':
            query_params += f'%5Esys_created_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.wkdt})'
            query_params += f'%5EORsys_updated_on%3E%3Djavascript%3Ags.dateGenerate({ScrVar.wkdt})'
            query_params += f'%5EORclosed_at%3E%3Djavascript%3Ags.dateGenerate({ScrVar.wkdt})'
        elif period == 'past_month':
            query_params += '%5Esys_created_on%3E%3Djavascript%3Ags.beginningOfLast30Days()'
            query_params += '%5EORsys_updated_on%3E%3Djavascript%3Ags.beginningOfLast30Days()'
            query_params += '%5EORclosed_at%3E%3Djavascript%3Ags.beginningOfLast30Days()'
        elif period == 'past_quarter':
            query_params += '%5Esys_created_on%3E%3Djavascript%3Ags.beginningOfLast3Months()'
            query_params += '%5EORsys_updated_on%3E%3Djavascript%3Ags.beginningOfLast3Months()'
            query_params += '%5EORclosed_at%3E%3Djavascript%3Ags.beginningOfLast3Months()'
        elif period == 'past_6_months':
            query_params += '%5Esys_created_on%3E%3Djavascript%3Ags.beginningOfLast6Months()'
            query_params += '%5EORsys_updated_on%3E%3Djavascript%3Ags.beginningOfLast6Months()'
            query_params += '%5EORclosed_at%3E%3Djavascript%3Ags.beginningOfLast6Months()'
        elif period == 'past_12_months':
            query_params += '%5Esys_created_on%3E%3Djavascript%3Ags.beginningOfLast12Months()'
            query_params += '%5EORsys_updated_on%3E%3Djavascript%3Ags.beginningOfLast12Months()'
            query_params += '%5EORclosed_at%3E%3Djavascript%3Ags.beginningOfLast12Months()'
        elif period == 'past_15_minutes':
            query_params += '%5Esys_created_on%3E%3Djavascript%3Ags.beginningOfLast15Minutes()'
            query_params += '%5EORsys_updated_on%3E%3Djavascript%3Ags.beginningOfLast15Minutes()'
            query_params += '%5EORclosed_at%3E%3Djavascript%3Ags.beginningOfLast15Minutes()'
        if ritm_ticket is not None:
            query_params = f"sysparm_query=task_effective_number={ritm_ticket}"
        query_params += "&sysparm_display_value=true&sysparm_exclude_reference_link=true"
        query_params += "&sysparm_fields=task_effective_number%2Copened_at%2Cdue_date"
        query_params += "%2Csys_updated_on%2Cclosed_at%2Copened_by%2Cu_requested_for%2Copened_by"
        query_params += "%2Cstate%2Cactive%2Cassignment_group%2Csys_id%2Capproval%2Cstage%2C"
        query_params += "escalation%2Cconfiguration_item"
        url = f'{SNOW_URL}{SNOW_TABLE_REQ_ITEM}?{query_params}'
        headers = {'Content-Type':'application/json','Accept':'application/json'}
        try:
            response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get('{url}',auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "SEAC-GATUOA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                    'Results':{'added':added,'updated':updated}}
        if response.status_code != 200:
            func = f"requests.get('{url}',auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "SEAC-GATUOA-002"
            details = f'Status code returned: {response.status_code}\nExpected 200'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                    'Results':{'added':added,'updated':updated}}
        response = response.json()
        total = len(response['result'])
        processed = 0
        for ticket in response['result']:
            processed += 1
            print(f'          Processing {processed} of {total}',end='\r')
            fields = get_fields_for_exception_ticket(ticket['sys_id'],main_log,ex_log,ex_file)
            standard = None
            if 'Standard or procedure document number & version for which the exception is requested' in fields:
                standard = fields['Standard or procedure document number & version for which the exception is requested']
                standard = standard.split(' ',1)[0]
            # if standard is not None and str(standard).startswith('IS18.'):
            if standard is not None:
                a_item = {}
                u_item = {'SET':{},'WHERE_EQUAL':{}}
                ritmticket = None
                if ticket['task_effective_number'] != '':
                    ritmticket = ticket['task_effective_number']
                a_item['RITMTicket'] = ritmticket
                u_item['WHERE_EQUAL']['RITMTicket'] = ritmticket
                a_item['JiraTickets'] = fields['JiraTickets']
                if ritmticket in ex_tkts_no_jira:
                    u_item['SET']['JiraTickets'] = fields['JiraTickets']
                ritm_sysid = None
                if ticket['sys_id'] != '':
                    ritm_sysid = ticket['sys_id']
                a_item['RITMSysId'] = ritm_sysid
                u_item['SET']['RITMSysId'] = ritm_sysid
                assignment_group = None
                if ticket['assignment_group'] != '':
                    assignment_group = ticket['assignment_group'].replace("'","")
                a_item['AssignedToGroup'] = assignment_group
                u_item['SET']['AssignedToGroup'] = assignment_group
                opened_at = None
                if ticket['opened_at'] != '':
                    opened_at = ticket['opened_at']
                a_item['CreatedDate'] = opened_at
                u_item['SET']['CreatedDate'] = opened_at
                sys_updated_on = None
                if ticket['sys_updated_on'] != '':
                    sys_updated_on = ticket['sys_updated_on']
                a_item['UpdatedDate'] = sys_updated_on
                u_item['SET']['UpdatedDate'] = sys_updated_on
                due_date = None
                if ticket['due_date'] != '':
                    due_date = ticket['due_date']
                a_item['DueDate'] = due_date
                u_item['SET']['DueDate'] = due_date
                closed_at = None
                if ticket['closed_at'] != '':
                    closed_at = ticket['closed_at']
                a_item['ClosedDate'] = closed_at
                u_item['SET']['ClosedDate'] = closed_at
                active = 0
                if ticket['active'] == 'true':
                    active = 1
                a_item['IsActive'] = active
                u_item['SET']['IsActive'] = active
                opened_by = None
                if ticket['opened_by'] != '':
                    opened_by = ticket['opened_by'].replace("'","")
                a_item['CreatedBy'] = opened_by
                u_item['SET']['CreatedBy'] = opened_by
                u_requested_for = None
                if ticket['u_requested_for'] != '':
                    u_requested_for = ticket['u_requested_for'].replace("'","")
                a_item['RequestedFor'] = u_requested_for
                u_item['SET']['RequestedFor'] = u_requested_for
                status = None
                if ticket['state'] != '':
                    status = ticket['state'].replace("'","")
                a_item['Status'] = status
                u_item['SET']['Status'] = status
                stage = None
                if ticket['stage'] != '':
                    stage = ticket['stage'].replace("'","")
                a_item['Stage'] = stage
                u_item['SET']['Stage'] = stage
                escalation = None
                if ticket['escalation'] != '':
                    escalation = ticket['escalation'].replace("'","")
                a_item['Escalation'] = escalation
                u_item['SET']['Escalation'] = escalation
                configuration_item = None
                if ticket['configuration_item'] != '':
                    configuration_item = ticket['configuration_item'].replace("'","")
                a_item['ConfigurationItem'] = configuration_item
                u_item['SET']['ConfigurationItem'] = configuration_item
                approval = None
                if ticket['approval'] != '':
                    approval = ticket['approval']
                a_item['ApprovalStatus'] = approval
                u_item['SET']['ApprovalStatus'] = approval
                duration = None
                expires = None
                a_records = get_exception_approval_records(ticket['task_effective_number'],main_log,
                                                        ex_log,ex_file)
                if a_records != {}:
                    if a_records['ApprovedByName'] in ScrVar.get_approvers:
                        a_item['ApprovedByName'] = a_records['ApprovedByName']
                        a_item['ApprovedDate'] = a_records['ApprovedDate']
                        u_item['SET']['ApprovedByName'] = a_records['ApprovedByName']
                        u_item['SET']['ApprovedDate'] = a_records['ApprovedDate']
                if 'Length of time for which exception is required' in fields:
                    duration = fields['Length of time for which exception is required']
                if 'Date exception expires' in fields:
                    expires = fields['Date exception expires']
                a_item['ExceptionStandard'] = standard
                a_item['ExceptionDuration'] = duration
                a_item['ExceptionExpirationDate'] = expires
                u_item['SET']['ExceptionStandard'] = standard
                u_item['SET']['ExceptionDuration'] = duration
                u_item['SET']['ExceptionExpirationDate'] = expires
                if (a_item['RITMTicket'] not in ex_tkts_w_jira and a_item['RITMTicket'] not in
                    ex_tkts_no_jira):
                    try:
                        added += insert_multiple_into_table('SNowSecurityExceptions',a_item,
                                                   verify_on=['RITMTicket'],show_progress=False)
                    except Exception as e_details:
                        func = f"insert_multiple_into_table('SNowSecurityExceptions',{a_item},"
                        func += "verify_on=['RITMTicket'],show_progress=False)"
                        e_code = "SEAC-GATUOA-003"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                                inspect.stack()[0][3],traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                else:
                    try:
                        updated += update_multiple_in_table('SNowSecurityExceptions',u_item,
                                                            show_progress=False)
                    except Exception as e_details:
                        func = f"update_multiple_in_table('SNowSecurityExceptions',{u_item},"
                        func += ",show_progress=False)"
                        e_code = "SEAC-GATUOA-004"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                                inspect.stack()[0][3],traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                'Results':{'added':added,'updated':updated}}

def get_fields_for_exception_ticket(sys_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                                    ex_file=EX_LOG_FILE):
    '''Gets the variables for a request'''
    fields = {}
    jira_keys = GeneralTicketing.get_all_project_keys()
    all_jiraissues = SNowQueries.get_all_jiraissues(main_log,ex_log,ex_file)['Results']
    jira_tickets = []
    query_params = f"sysparm_query=request_item%3D{sys_id}"
    url = f"{SNOW_URL}{SNOW_TABLE_EXCEPTION_FIELDS}?{query_params}"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    try:
        response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
    except Exception as e_details:
        func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
        e_code = "SEAC-GFFET-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return fields
    if response.status_code != 200:
        e_details = f"Response returned status code {response.status_code}. Expected 200."
        func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
        e_code = "SEAC-GFFET-002"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return fields
    data = response.json()
    for item in data['result']:
        d_url = f"{item['sc_item_option']['link']}?sysparm_display_value=true"
        d_url += "&sysparm_exclude_reference_link=true"
        data = get_exception_field_value(d_url,main_log,ex_log,ex_file)
        key = data['item_option_new']
        if key in ('Length of time for which exception is required',
                   'Standard or procedure document number & version for which the exception is requested',
                   'Date exception expires'):
            fields[key] = data['value']
        else:
            get_tickets_from_text = re.findall(r"[A-Z]+-[0-9]+",data['value'].replace(" -","-").replace("- ","-"))
            for item in get_tickets_from_text:
                if item in all_jiraissues:
                    check_key = item.split("-",1)[0]
                    if check_key in jira_keys:
                        jira_tickets.append(f"{item}")
    if jira_tickets == []:
        jira_tickets = None
    else:
        jira_tickets = sorted(set(jira_tickets))
        jira_tickets = ','.join(jira_tickets)
    fields['JiraTickets'] = jira_tickets
    return fields

def get_exception_field_value(d_url,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Returns the value of a specific exception field'''
    fields = None
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    try:
        response = requests.get(d_url,auth=(SNOW_USER,SNOW_KEY),headers=headers,
                                timeout=90)
    except Exception as e_details:
        func = f"requests.get({d_url},auth=(SNOW_USER,SNOW_KEY),headers={headers},"
        func += "timeout=90)"
        e_code = "SEAC-GEFV-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.ex_cnt += 1
        return fields
    if response.status_code != 200:
        e_details = f"Response status code was {response.status_code}. Expected 200."
        func = f"requests.get({d_url},auth=(SNOW_USER,SNOW_KEY),headers={headers},"
        func += "timeout=90)"
        e_code = "SEAC-GEFV-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    ScrVar.src,inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.ex_cnt += 1
        return fields
    fields = response.json()['result']
    return fields

def get_exception_approval_records(ritm_number,main_log=LOG,ex_log=LOG_EXCEPTION,
                                    ex_file=EX_LOG_FILE):
    '''Gets the approval records for the ticket'''
    if ScrVar.get_approvers == []:
        ScrVar.get_approvers = security_approvers(main_log,ex_log,ex_file)
    fields = {}
    query_params = f"sysparm_query=u_approval_for_string%3D{ritm_number}%5Estate%3Dapproved"
    query_params += "&sysparm_display_value=true"
    query_params += "&sysparm_exclude_reference_link=true&sysparm_fields=u_number%2Csys_id%2C"
    query_params += "sys_created_on%2Csys_updated_on%2Cdue_date%2Cexpected_start%2Cstate%2C"
    query_params += "approver"
    url = f'{SNOW_URL}{SNOW_TABLE_APPROVAL}?{query_params}'
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    try:
        response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
    except Exception as e_details:
        func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
        e_code = "SEAC-GEAR-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return fields
    if response.status_code != 200:
        e_details = f"Response returned status code {response.status_code}. Expected 200."
        func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
        e_code = "SEAC-GEAR-002"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                    inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return fields
    data = response.json()
    if data != []:
        for record in data['result']:
            if record['approver'] in ScrVar.get_approvers:
                if record['state'] == 'Approved':
                    fields['ApprovedByName'] = record['approver']
                    fields['ApprovedDate'] = record['sys_updated_on']
                return fields
    return fields

def security_approvers(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Returns a list of names from the SNowSecurityApprovers table"""
    approvers = []
    sql = """SELECT DISTINCT ApproverName FROM SNowSecurityApprovers ORDER BY ApproverName"""
    try:
        names = select(sql)
    except Exception as e_details:
        e_code = "SEAC-SA-001"
        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                              inspect.stack()[0][3],traceback.format_exc())
        ScrVar.ex_cnt += 1
        return approvers
    if names != []:
        for name in names:
            approvers.append(name[0])
    return approvers