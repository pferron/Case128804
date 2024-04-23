"""Functions for maintenance_mend_user_cleanup"""

import inspect
import os
import requests
import traceback
from common.constants import SNOW_USER, WS_URL
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime
from common.logging import TheLogs
from common.database_appsec import select, update_multiple_in_table, insert_multiple_into_table
from mend.api_connections import MendAPI

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
WS_ORG = os.environ.get('WS_TOKEN')
SNOW_URL = os.environ.get('SNOW_URL')
SNOW_KEY = os.environ.get('SNOW_KEY')
SNOW_TABLE_USER = os.environ.get('SNOW_TABLE_USER')
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class MendUsers():
    """"For assessing whether Mend users are still at the company"""

    @staticmethod
    def is_user_active(user_email,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if the user is active"""
        results = None
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        user_email = user_email.replace("@","%40")
        query_params = f'sysparm_query=email%3D{user_email}&sysparm_display_value=true'
        query_params += '&sysparm_exclude_reference_link=true&sysparm_fields=active&sysparm_limit=1'
        url = f'{SNOW_URL}{SNOW_TABLE_USER}?{query_params}'
        headers = {'Content-Type':'application/json','Accept':'application/json'}
        try:
            response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "MUC-IUA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return results
        if response.status_code != 200:
            func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "MUC-IUA-002"
            details = f'Status code returned: {response.status_code}\nExpected 200\n\n'
            TheLogs.function_exception(func,e_code,details,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return results
        user_info = response.json()
        if 'result' in user_info:
            results = False
            if user_info['result'] != []:
                if 'active' in user_info['result'][0]:
                    if user_info['result'][0]['active'] == 'true':
                        results = True
        return results

    @staticmethod
    def update_service_accounts(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Builds a list of dictionaries for users to remove"""
        failures = []
        TheLogs.log_headline("RETRIEVING MEND SERVICE ACCOUNTS FROM THE API",2,"#",main_log)
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = "search=userType:equals:Service&sort=roles&pageSize=9999"
        url = f"{WS_URL}/orgs/{WS_ORG}/users?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        try:
            response = requests.get(url,headers=headers,data=payload,timeout=60)
        except Exception as e_details:
            func = f"requests.get({url},headers={headers},data={payload},timeout=60)"
            e_code = "MUC-GSA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}
        # response.status_code == 200
        # response.text = {'additionalData':{'totalItems':40,'isLastPage':true},
        # 'retVal':[{"uuid":"aee2f5a0-ff9c-4b5a-a962-1dd062a29378","name":"CircleCI_WS","email":
        # "circleci_ws@progleasing.com","userType":"SERVICE","accountStatus":"ACTIVE"}],
        # 'supportToken':'2eac3073a25d04fe4ab4003993ac945af1695847861538'}
        if response.status_code != 200:
            func = f"requests.get({url},headers={headers},data={payload},timeout=60)"
            details = f'A fatal exception occurred making an API call to:\n{url}\n\nExpected '
            details += f'status code 200, but {response.status_code} was returned. As a result, '
            details += 'service accounts could not be retrieved from Mend.\n\n'
            e_code = "MUC-GSA-002"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
        if response.status_code == 200:
            TheLogs.log_info('API response was successful',2,"*",main_log)
            results = response.json()
            if 'retVal' in results:
                users = results['retVal']
                tool = 'Mend OS'
                for user in users:
                    user_id = None
                    user_name = None
                    email = None
                    if 'email' in user:
                        email = user['email']
                    if 'name' in user:
                        user_name = user['name']
                    if 'uuid' in user:
                        user_id = user['uuid']
                    service_account_exists = MendUsers.service_account_in_db(user_id,main_log,
                                                                             ex_log,ex_file)
                    seen = datetime.now(tz=ZoneInfo('US/Mountain'))
                    if service_account_exists is True:
                        update_array = [{'SET':{'UserName':user_name,'Email':email,
                                                'LastSeenInTool':seen},
                                        'WHERE_EQUAL':{'ToolAccountID':user_id,'Tool':'Mend OS'}}]
                        try:
                            updated = update_multiple_in_table('ToolServiceAccounts',update_array)
                        except Exception as e_details:
                            func = f"update_multiple_in_table('ToolServiceAccounts',{update_array})"
                            e_code = "MUC-GSA-003"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.fe_cnt += 1
                            return
                        if updated > 0:
                            message = f'Service account for {user_name} ({user_id}) updated in '
                            message += 'the database'
                            TheLogs.log_info(message,2,"*",main_log)
                    else:
                        insert_array = [{'UserName':user_name,'Email':email,'LastSeenInTool':seen,
                                         'ToolAccountID':user_id,'Tool':'Mend OS'}]
                        try:
                            added = insert_multiple_into_table('ToolServiceAccounts',insert_array)
                        except Exception as e_details:
                            func = "insert_multiple_into_table('ToolServiceAccounts',"
                            func += f"{insert_array})"
                            e_code = "CUC-GSA-004"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.fe_cnt += 1
                            return
                        if added > 0:
                            message = f'Service account for {user_name} ({user_id}) added to the '
                            message += 'database'
                            TheLogs.log_info(message,2,"*",main_log)
        return

    @staticmethod
    def service_account_in_db(user_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if the service account is already in ToolServiceAccounts"""
        is_in_db = False
        sql = f"""SELECT TOP 1 ToolAccountID FROM ToolServiceAccounts
        WHERE ToolAccountID = '{user_id}' AND Tool = 'Mend OS'"""
        try:
            in_db = select(sql)
        except Exception as e_details:
            e_code = "MUC-SAID-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        if in_db != []:
            is_in_db = True
        return is_in_db

    @staticmethod
    def remove_deactivated_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Builds a list of dictionaries for users to remove"""
        ScrVar.reset_exception_counts()
        u_cnt = 0
        failures = []
        MendUsers.update_service_accounts(main_log,ex_log,ex_file)
        TheLogs.log_headline("RETRIEVING NON-SERVICE ACCOUNT USERS FROM THE MEND API",2,"#",
                             main_log)
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = "search=userType:equals:Regular&sort=roles&pageSize=9999"
        url = f"{WS_URL}/orgs/{WS_ORG}/users?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        try:
            response = requests.get(url,headers=headers,data=payload,timeout=60)
        except Exception as e_details:
            func = f"requests.get({url},headers={headers},data={payload},timeout=60)"
            e_code = "MUC-RDA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}
        # response.status_code == 200
        # response.text = {'additionalData':{'totalItems':40,'isLastPage':true},
        # 'retVal':[{'uuid':'0ec3794f-7d6f-452d-8342-3359ccb9b199','name':'John McCutchen',
        # 'email':'john.mccutchen@progleasing.com','userType':'REGULAR',
        # 'accountStatus':'ACTIVE'}],
        # 'supportToken':'2eac3073a25d04fe4ab4003993ac945af1695847861538'}
        if response.status_code != 200:
            func = f"requests.get({url},headers={headers},data={payload},timeout=60)"
            details = f'A fatal exception occurred making an API call to:\n{url}\n\nExpected '
            details += f'status code 200, but {response.status_code} was returned. As a result, '
            details += 'user accounts could not be retrieved from Mend.'
            e_code = "MUC-RDA-002"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
            ScrVar.fe_cnt += 1
        if response.status_code == 200:
            TheLogs.log_info('API response was successful',2,"*",main_log)
            results = response.json()
            if 'retVal' in results:
                users = results['retVal']
                TheLogs.log_headline('CHECKING ACTIVE STATUS OF MEND USERS',2,"#",main_log)
                for user in users:
                    email = None
                    uuid = None
                    is_active = True
                    if 'email' in user:
                        email = user['email']
                        is_active = MendUsers.is_user_active(email,main_log,ex_log,ex_file)
                    if is_active is False:
                        if 'uuid' in user:
                            uuid = user['uuid']
                            remove_user = MendUsers.delete_mend_account(uuid,main_log,ex_log,
                                                                        ex_file)
                            if remove_user is True:
                                TheLogs.log_info(f'Account for {email} removed',2,'*',main_log)
                                u_cnt = 1
                            else:
                                TheLogs.log_info(f'Removal of account for {email} failed',2,'!',
                                                 main_log)
                                failures.append(email)
        if u_cnt == 0:
            TheLogs.log_info('No former employee accounts were deleted',2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}

    @staticmethod
    def delete_mend_account(user_uuid,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Deletes a user account from Mend"""
        success = False
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        url = f"{WS_URL}/orgs/{WS_ORG}/users/{user_uuid}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        try:
            response = requests.delete(url,headers=headers,data=payload,timeout=60)
        except Exception as e_details:
            func = f"requests.delete({url},headers={headers},data={payload},timeout=90)"
            e_code = "MUC-DMA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return success
        if response.status_code != 200:
            details = f'A fatal exception occurred making an API call to:\n{url}\n\nExpected '
            details += f'status code 200, but {response.status_code} was returned. As a result, '
            details += f'the user account for {user_uuid} could not be deleted.'
            func = f"requests.delete({url},headers={headers},data={payload},timeout=90)"
            e_code = "MUC-DMA-002"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        if response.status_code == 200:
            response = response.json()
            success = True
        return success
