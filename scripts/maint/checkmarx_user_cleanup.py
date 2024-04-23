"""Functions for maintenance_mend_user_cleanup"""

import inspect
import json
import os
import requests
import traceback
from common.constants import CX_BASE_URL, CX_USER, SNOW_USER
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime
from common.logging import TheLogs
from common.database_appsec import select, update_multiple_in_table, insert_multiple_into_table

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
WS_ORG = os.environ.get('WS_TOKEN')
CX_USER_KEY = os.environ.get('CX_USER_KEY')
CX_CLIENT_KEY = os.environ.get('CX_CLIENT_KEY')
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

class CxUsers():
    """"For assessing whether Mend users are still at the company"""

    @staticmethod
    def access_control_connection():
        """Creates the connection to Checkmarx"""
        access_token = None
        url = f'{CX_BASE_URL}/cxrestapi/auth/identity/connect/token'
        payload = f"""username={CX_USER}&password={CX_USER_KEY}&grant_type=password"""
        payload += """&scope=access_control_api&client_id="""
        payload += f"""resource_owner_client&client_secret={CX_CLIENT_KEY}"""
        headers = {
            'Host': CX_BASE_URL.replace("https://",""),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'access_token' in response:
                access_token = response['access_token']
        return access_token

    @staticmethod
    def is_user_active(user_email,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if the user is active"""
        results = None
        user_email = user_email.replace("@","%40")
        query_params = f'sysparm_query=email%3D{user_email}&sysparm_display_value=true'
        query_params += '&sysparm_exclude_reference_link=true&sysparm_fields=active&sysparm_limit=1'
        url = f'{SNOW_URL}{SNOW_TABLE_USER}?{query_params}'
        headers = {'Content-Type':'application/json','Accept':'application/json'}
        try:
            response = requests.get(url,auth=(SNOW_USER,SNOW_KEY),headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "CUC-IUA-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return results
        if response.status_code != 200:
            func = f"requests.get({url},auth=(SNOW_USER,SNOW_KEY),headers={headers},timeout=90)"
            e_code = "CUC-IUA-002"
            details = f'Status code returned: {response.status_code}\nExpected 200\n\n'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
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
    def remove_deactivated_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Builds a list of dictionaries for users to remove"""
        ScrVar.reset_exception_counts()
        failures = []
        access_token = CxUsers.access_control_connection()
        TheLogs.log_headline('RETRIEVING USERS FROM CHECKMARX',2,"#",main_log)
        url = f'{CX_BASE_URL}/cxrestapi/auth/Users'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        try:
            response = requests.get(url,headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get({url},headers={headers},timeout=90)"
            e_code = "CUC-RDU-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}
        if response.status_code != 200 or response.text == []:
            func = f"requests.get({url},headers={headers},timeout=90)"
            e_code = "CUC-RDU-002"
            notes = response.text
            details = f'Status code returned: {response.status_code}\nExpected 200\n\n'
            details += f'Response body: {notes}'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}
        users = response.json()
        if users != []:
            TheLogs.log_info('Users successfully retrieved',2,"*",main_log)
        else:
            TheLogs.log_info('Failed to retrieve users',2,"!",main_log)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}
        service_accounts = CxUsers.get_service_accounts(main_log,ex_log,ex_file)
        if service_accounts is not None and service_accounts != []:
            TheLogs.log_headline('PROCESSING SERVICE ACCOUNTS',2,"#",main_log)
            for user in users:
                user_id = user['id']
                user_name = user['userName']
                email = user['email']
                expiration_date = user['expirationDate']
                if expiration_date is not None:
                    if expiration_date != '2050-12-31T23:59:59.0598536Z':
                        remove_ex = CxUsers.remove_expiration_date(user_id,main_log,ex_log,ex_file)
                        if remove_ex is True:
                            expiration_date = '2050-12-31'
                            TheLogs.log_info(f'Expiration date for {email} ({id}) updated',2,"*",
                                            main_log)
                    else:
                        expiration_date = expiration_date.split("T",1)[0]
                if ('svc' in user_name or 'svc' in email) or str(user_id) in service_accounts:
                    CxUsers.process_service_account(user_id,user_name,email,expiration_date,main_log,
                                                    ex_log,ex_file)
        service_accounts = CxUsers.get_service_accounts(main_log,ex_log,ex_file)
        if service_accounts is not None and service_accounts != []:
            u_cnt = 0
            TheLogs.log_headline('PROCESSING NON-SERVICE ACCOUNT USERS',2,"#",main_log)
            for user in users:
                user_id = user['id']
                email = user['email']
                if str(user_id) not in service_accounts:
                    is_active = CxUsers.is_user_active(email,main_log,ex_log,ex_file)
                    if is_active is False:
                        deleted = CxUsers.delete_user_account(user_id,main_log,ex_log,ex_file)
                        if deleted is True:
                            TheLogs.log_info(f'Account for {email} deleted from Checkmarx',2,"*",
                                                main_log)
                            u_cnt = 1
                        else:
                            failures.append(email)
            if u_cnt == 0:
                TheLogs.log_info('No former employee accounts needed to be deleted',2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':failures}

    @staticmethod
    def get_service_accounts(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns a list of service accounts to exclude from auto deletion"""
        service_accounts = []
        sql = """SELECT ToolAccountID FROM ToolServiceAccounts WHERE Tool = 'Checkmarx'"""
        try:
            get_accounts = select(sql)
        except Exception as e_details:
            e_code = "CUC-GSA-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return None
        if get_accounts == []:
            details = 'Unable to retrieve Checkmarx service accounts from the database.'
            details += 'To avoid accidental deletion of these accounts, the script will '
            details += 'not delete any accounts for this run.'
            e_code = "CUC-GSA-002"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return None
        else:
            for account in get_accounts:
                service_accounts.append(account[0])
        return service_accounts

    @staticmethod
    def delete_user_account(user_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Deletes the user account from Checkmarx"""
        access_token = CxUsers.access_control_connection()
        url = f'{CX_BASE_URL}/cxrestapi/auth/Users/{user_id}'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        try:
            response = requests.delete(url,headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.delete({url},headers={headers},timeout=90)"
            e_code = "CUC-RDU-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return False
        if response.status_code != 204:
            func = f"requests.delete({url},headers={headers},timeout=90)"
            e_code = "CUC-DUA-002"
            notes = response.text
            details = f'Status code returned: {response.status_code}\nExpected 204\n\n'
            details += f'Response body: {notes}'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return False
        return True

    @staticmethod
    def remove_expiration_date(user_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Builds a list of dictionaries for users to remove"""
        data = CxUsers.get_user(user_id)
        # data = {'id': 1,'userName':'CxAdmin','lastLoginDate':'2023-09-27T18:58:51.8831987Z',
        # 'roleIds':[1,2,6,10,11],'teamIds':[1],'authenticationProviderId':1,'creationDate':
        # '2020-05-06T15:24:49.45Z','twoFAExemption':False,'accessToUi':True,'firstName':'admin',
        # 'lastName':'admin','email':'admin@cx.com','phoneNumber':'','cellPhoneNumber':'',
        # 'jobTitle':'', 'other':'','country':'','active':True,'expirationDate':
        # '2050-12-31T23:59:59.0598536Z','allowedIpList':[],'localeId':1}
        if data is not None:
            data['expirationDate'] = '2050-12-31T23:59:59.0598536Z'
            access_token = CxUsers.access_control_connection()
            url = f'{CX_BASE_URL}/cxrestapi/auth/Users/{user_id}'
            headers = {
                'Content-Type': 'application/json;v1.0',
                'Authorization': f'Bearer {access_token}',
            }
            try:
                response = requests.put(url,headers=headers,data=json.dumps(data),timeout=90)
            except Exception as e_details:
                func = f"requests.put({url},headers={headers},timeout=90)"
                e_code = "CUC-RED-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return False
            if response.status_code != 204:
                func = f"requests.put({url},headers={headers},timeout=90)"
                e_code = "CUC-RED-002"
                notes = response.text
                details = f'Status code returned: {response.status_code}\nExpected 204\n\n'
                details += f'Response body: {notes}'
                TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return False
            return True

    @staticmethod
    def get_user(user_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Builds a list of dictionaries for users to remove"""
        access_token = CxUsers.access_control_connection()
        url = f'{CX_BASE_URL}/cxrestapi/auth/Users/{user_id}'
        headers = {
            'Content-Type': 'application/json;v1.0',
            'Authorization': f'Bearer {access_token}',
        }
        try:
            response = requests.get(url,headers=headers,timeout=90)
        except Exception as e_details:
            func = f"requests.get({url},headers={headers},timeout=90)"
            e_code = "CUC-RDU-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        if response.status_code != 200:
            func = f"requests.get({url},headers={headers},timeout=90)"
            e_code = "CUC-GU-001"
            notes = response.text
            details = f'Status code returned: {response.status_code}\nExpected 204\n\n'
            details += f'Response body: {notes}'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        return response.json()

    @staticmethod
    def process_service_account(user_id,user_name,email,expiration_date,main_log=LOG,
                                ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Determines whether to update or insert the service account into
        ToolServiceAccounts"""
        service_account_exists = CxUsers.service_account_in_db(user_id,main_log,ex_log,ex_file)
        seen = datetime.now(tz=ZoneInfo('US/Mountain'))
        if service_account_exists is True:
            update_array = [{'SET':{'UserName':user_name,'Email':email,
                                    'ExpirationDate':expiration_date,'LastSeenInTool':seen},
                             'WHERE_EQUAL':{'ToolAccountID':user_id,'Tool':'Checkmarx'}}]
            try:
                updated = update_multiple_in_table('ToolServiceAccounts',update_array)
            except Exception as e_details:
                func = f"update_multiple_in_table('ToolServiceAccounts',{update_array})"
                e_code = "CUC-PSA-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return
            if updated > 0:
                message = f'Service account for {user_name} ({user_id}) updated in the database'
                TheLogs.log_info(message,2,"*",main_log)
        else:
            insert_array = [{'UserName':user_name,'Email':email,'ExpirationDate':expiration_date,
                             'LastSeenInTool':seen,'ToolAccountID':user_id,'Tool':'Checkmarx'}]
            try:
                added = insert_multiple_into_table('ToolServiceAccounts',insert_array)
            except Exception as e_details:
                func = f"insert_multiple_into_table('ToolServiceAccounts',{insert_array})"
                e_code = "CUC-PSA-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return
            if added > 0:
                message = f'Service account for {user_name} ({user_id}) added to the database'
                TheLogs.log_info(message,2,"*",main_log)
        return

    @staticmethod
    def service_account_in_db(user_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks if the service account is already in ToolServiceAccounts"""
        is_in_db = False
        sql = f"""SELECT TOP 1 ToolAccountID FROM ToolServiceAccounts
        WHERE ToolAccountID = '{user_id}' AND Tool = 'Checkmarx'"""
        try:
            in_db = select(sql)
        except Exception as e_details:
            e_code = "CUC-SAID-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        if in_db != []:
            is_in_db = True
        return is_in_db
