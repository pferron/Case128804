"""Common functions for Checkmarx"""

import os
import requests
import sys
import time
from common.constants import KB4_SERVER
from common.logging import TheLogs
from dotenv import load_dotenv


parent = os.path.abspath('.')
sys.path.insert(1,parent)

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
KB4_KEY = os.environ.get('KB4_KEY')
HEADERS = {'Authorization': f'Bearer {KB4_KEY}'}


class ScrVar():
    """Stuff for this script"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []

class KB4API():
    """Connects to KnowBe4 API and database to perform various tasks"""

    @staticmethod
    def get_users(page,status,main_log=LOG):
        """Gets a list of users from KnowBe4"""
        user_list = None
        user_cnt = 0
        url = f'{KB4_SERVER}/users?status={status}&per_page=500&page={page}'
        try:
            response = requests.get(url, headers = HEADERS, timeout=120)
        except Exception as details:
            func = f"requests.get('{url}', headers = {HEADERS}, timeout=120)"
            e_code = "KAC-GU-001"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': 'fail'}
        if response.status_code != 200:
            return 'fail'
        user_list = []
        response = response.json()
        user_cnt = len(response)
        for user in response:
            employee_number = None
            if 'employee_number' in user:
                employee_number = user['employee_number']
            user_id = None
            if 'id' in user:
                user_id = user['id']
            first_name = None
            if 'first_name' in user:
                first_name = user['first_name']
            last_name = None
            if 'last_name' in user:
                last_name = user['last_name']
            job_title = None
            if 'job_title' in user:
                job_title = user['job_title']
            email = None
            if 'email' in user:
                email = user['email']
            location = None
            if 'location' in user:
                location = user['location']
            division = None
            if 'division' in user:
                division = user['division']
            organization = None
            if 'organization' in user:
                organization = user['organization']
            department = None
            if 'department' in user:
                department = user['department']
            manager_name = None
            if 'manager_name' in user:
                manager_name = user['manager_name']
            manager_email = None
            if 'manager_email' in user:
                manager_email = user['manager_email']
            phish_prone_percentage = None
            if 'phish_prone_percentage' in user:
                phish_prone_percentage = user['phish_prone_percentage']
            current_risk_score = None
            if 'current_risk_score' in user:
                current_risk_score = user['current_risk_score']
            user_list.append({'employee_number': employee_number, 'id': user_id,
                            'first_name': first_name, 'last_name': last_name,
                            'job_title': job_title, 'email': email,
                            'location': location, 'division': division,
                            'organization': organization, 'department': department,
                            'manager_name': manager_name, 'manager_email': manager_email,
                            'phish_prone_percentage': phish_prone_percentage,
                            'current_risk_score': current_risk_score})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results':user_list,
                'UserCount':user_cnt}

    @staticmethod
    def get_user_groups(main_log=LOG):
        """Gets a list of user groups from KnowBe4"""
        groups = None
        url = f'{KB4_SERVER}/groups?status=active'
        try:
            response = requests.get(url, headers = HEADERS, timeout=120)
        except Exception as details:
            func = f"requests.get('{url}', headers = {HEADERS}, timeout=120)"
            e_code = "KAC-GUG-001"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': 'fail'}
        if response.status_code != 200:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':'fail'}
        groups = []
        response = response.json()
        for group in response:
            group_id = None
            if 'id' in group:
                group_id = group['id']
            name = None
            if 'name' in group:
                name = group['name']
            member_count = None
            if 'member_count' in group:
                member_count = group['member_count']
            current_risk_score = None
            if 'current_risk_score' in group:
                current_risk_score = group['current_risk_score']
            groups.append({'id': group_id, 'name': name, 'member_count': member_count,
                            'current_risk_score': current_risk_score})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':groups}

    @staticmethod
    def get_training_campaigns(main_log=LOG):
        """Gets a list of training campaigns from KnowBe4"""
        campaigns = None
        url = f'{KB4_SERVER}/training/campaigns'
        try:
            response = requests.get(url, headers = HEADERS, timeout=120)
        except Exception as details:
            func = f"requests.get('{url}', headers = {HEADERS}, timeout=120)"
            e_code = "KAC-GTC-001"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':'fail'}
        if response.status_code != 200:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':'fail'}
        campaigns = []
        response = response.json()
        for camp in response:
            campaign_id = None
            if 'campaign_id' in camp:
                campaign_id = camp['campaign_id']
            name = None
            if 'name' in camp:
                name = camp['name']
            if name is not None:
                name = name.replace("'","")
            status = None
            if 'status' in camp:
                status = camp['status']
            if status is not None:
                status = status.replace("'","")
            duration_type = None
            if 'duration_type' in camp:
                duration_type = camp['duration_type']
            start_date = None
            if 'start_date' in camp:
                start_date = camp['start_date']
            if start_date is not None:
                start_date = start_date.split(".",1)[0].replace("T"," ")
            end_date = None
            if 'end_date' in camp:
                end_date = camp['end_date']
            if end_date is not None:
                end_date = end_date.split(".",1)[0].replace("T"," ")
            relative_duration = None
            if 'relative_duration' in camp:
                relative_duration = camp['relative_duration']
            relative_duration = None
            if 'auto_enroll' in camp:
                auto_enroll = camp['auto_enroll']
            allow_multiple_enrollments = None
            if 'allow_multiple_enrollments' in camp:
                allow_multiple_enrollments = camp['allow_multiple_enrollments']
            completion_percentage = None
            if 'completion_percentage' in camp:
                completion_percentage = camp['completion_percentage']
            campaigns.append({'campaign_id': campaign_id, 'name': name, 'status': status,
                            'duration_type': duration_type, 'start_date': start_date,
                            'end_date': end_date, 'relative_duration': relative_duration,
                            'auto_enroll': auto_enroll, 'allow_multiple_enrollments':
                            allow_multiple_enrollments, 'completion_percentage':
                            completion_percentage})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':campaigns}

    @staticmethod
    def get_phishing_campaigns(main_log=LOG):
        """Gets a list of phishing campaigns from KnowBe4"""
        campaigns = None
        url = f'{KB4_SERVER}/phishing/campaigns'
        try:
            response = requests.get(url, headers = HEADERS, timeout=120)
        except Exception as details:
            func = f"requests.get('{url}', headers = {HEADERS}, timeout=120)"
            e_code = "KAC-GPC-001"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': 'fail'}
        if response.status_code != 200:
            return 'fail'
        campaigns = []
        response = response.json()
        for camp in response:
            scheduled_count = 0
            delivered_count = 0
            opened_count = 0
            clicked_count = 0
            replied_count = 0
            attachment_open_count = 0
            macro_enabled_count = 0
            data_entered_count = 0
            reported_count = 0
            bounced_count = 0
            campaign_id = None
            if 'campaign_id' in camp:
                campaign_id = camp['campaign_id']
            name = None
            if 'name' in camp:
                name = camp['name']
            if name is not None:
                name = name.replace("'","")
            groups = None
            if ('groups' in camp and camp['groups'] is not None and camp['groups'] != 'None'
                and camp['groups'] != []):
                groups = []
                for group in camp['groups']:
                    if 'name' in group and group['name'] != '' and group['name'] is not None:
                        groups.append(group['name'])
                if len(groups) > 0:
                    groups = str(groups).replace("[","").replace("]","").replace(",","; ")
                    groups = groups.replace("'","")
            last_run = None
            if 'last_run' in camp:
                last_run = camp['last_run']
            if last_run is not None:
                last_run = last_run.split(".",1)[0].replace("T"," ")
            last_phish_prone_percentage = None
            if 'last_phish_prone_percentage' in camp:
                last_phish_prone_percentage = camp['last_phish_prone_percentage']
            status = None
            if 'status' in camp:
                status = camp['status']
            hidden = None
            if 'hidden' in camp:
                hidden = camp['hidden']
            psts_count = None
            if 'psts_count' in camp:
                psts_count = camp['psts_count']
            send_duration = None
            if 'send_duration' in camp:
                send_duration = camp['send_duration']
            if send_duration is not None:
                send_duration = send_duration.replace("'","")
            track_duration = None
            if 'track_duration' in camp:
                track_duration = camp['track_duration']
            if track_duration is not None:
                track_duration = track_duration.replace("'","")
            frequency = None
            if 'frequency' in camp:
                frequency = camp['frequency']
            frequency = frequency.replace("'","")
            create_date = None
            if 'create_date' in camp:
                create_date = camp['create_date']
            if create_date is not None:
                create_date = create_date.split(".",1)[0].replace("T"," ")
            difficulty_filter = None
            if ('difficulty_filter' in camp and camp['difficulty_filter'] is not None and
                camp['difficulty_filter'] != 'None' and camp['difficulty_filter'] != []):
                if len(camp['difficulty_filter']) != 0:
                    difficulty_filter = str(camp['difficulty_filter']).replace("[","")
                    difficulty_filter = difficulty_filter.replace("]","").replace("',",";")
                    difficulty_filter = difficulty_filter.replace("'","")
            if ('psts' in camp and camp['psts'] is not None and camp['psts'] != 'None' and
                camp['psts'] != []):
                for item in camp['psts']:
                    time.sleep(2)
                    stats = KB4API.get_campaign_stats(item['pst_id'],main_log)
                    stats = stats['Results']
                    scheduled_count += stats['scheduled_count']
                    delivered_count += stats['delivered_count']
                    opened_count += stats['opened_count']
                    replied_count += stats['replied_count']
                    attachment_open_count += stats['attachment_open_count']
                    macro_enabled_count += stats['macro_enabled_count']
                    data_entered_count += stats['data_entered_count']
                    reported_count += stats['reported_count']
                    bounced_count += stats['bounced_count']
                    clicked_count += stats['clicked_count']
            campaigns.append({'campaign_id': campaign_id, 'name': name, 'groups': groups,
                              'last_run': last_run,
                              'last_phish_prone_percentage': last_phish_prone_percentage,
                              'status': status, 'hidden': hidden, 'psts_count': psts_count,
                              'send_duration': send_duration, 'track_duration': track_duration,
                              'frequency': frequency, 'create_date': create_date,
                              'difficulty_filter': difficulty_filter,
                              'scheduled_count': scheduled_count,
                              'delivered_count': delivered_count, 'opened_count': opened_count,
                              'clicked_count': clicked_count, 'replied_count': replied_count,
                              'attachment_open_count': attachment_open_count,
                              'macro_enabled_count': macro_enabled_count,
                              'data_entered_count': data_entered_count,
                              'reported_count': reported_count, 'bounced_count': bounced_count})
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': campaigns}

    @staticmethod
    def get_campaign_stats(pst_id,main_log=LOG):
        """Gets the stats for a specific campaign from KnowBe4"""
        camp_stats = 'fail'
        url = f'{KB4_SERVER}/phishing/security_tests/{pst_id}'
        try:
            response = requests.get(url, headers = HEADERS, timeout=120)
        except Exception as details:
            func = f"requests.get('{url}', headers = {HEADERS}, timeout=120)"
            e_code = "KAC-GCS-001"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            ScrVar.ex_array.append(e_code)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': 'fail'}
        if response.status_code != 200:
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': 'fail'}
        scheduled_count = 0
        delivered_count = 0
        opened_count = 0
        replied_count = 0
        attachment_open_count = 0
        macro_enabled_count = 0
        data_entered_count = 0
        reported_count = 0
        bounced_count = 0
        clicked_count = 0
        response = response.json()
        if ('scheduled_count' in response and response['scheduled_count'] is not None and
            response['scheduled_count'] != 'None' and response['scheduled_count'] != ''):
            scheduled_count = response['scheduled_count']
        if ('delivered_count' in response and response['delivered_count'] is not None and
            response['delivered_count'] != 'None' and response['delivered_count'] != ''):
            delivered_count = response['delivered_count']
        if ('opened_count' in response and response['opened_count'] is not None and
            response['opened_count'] != 'None' and response['opened_count'] != ''):
            opened_count = response['opened_count']
        if ('replied_count' in response and response['replied_count'] is not None and
            response['replied_count'] != 'None' and response['replied_count'] != ''):
            replied_count = response['replied_count']
        if ('attachment_open_count' in response and response['attachment_open_count'] is not None
            and response['attachment_open_count'] != 'None' and
            response['attachment_open_count'] != ''):
            attachment_open_count = response['attachment_open_count']
        if ('macro_enabled_count' in response and response['macro_enabled_count'] is not None and
            response['macro_enabled_count'] != 'None' and response['macro_enabled_count'] != ''):
            macro_enabled_count = response['macro_enabled_count']
        if ('data_entered_count' in response and response['data_entered_count'] is not None and
            response['data_entered_count'] != 'None' and response['data_entered_count'] != ''):
            data_entered_count = response['data_entered_count']
        if ('reported_count' in response and response['reported_count'] is not None and
            response['reported_count'] != 'None' and response['reported_count'] != ''):
            reported_count = response['reported_count']
        if ('bounced_count' in response and response['bounced_count'] is not None and
            response['bounced_count'] != 'None' and response['bounced_count'] != ''):
            bounced_count = response['bounced_count']
        if ('clicked_count' in response and response['clicked_count'] is not None and
            response['clicked_count'] != 'None' and response['clicked_count'] != ''):
            clicked_count = response['clicked_count']
        camp_stats = {'scheduled_count': scheduled_count, 'delivered_count': delivered_count,
                      'opened_count': opened_count, 'replied_count': replied_count,
                      'attachment_open_count': attachment_open_count,
                      'macro_enabled_count': macro_enabled_count,
                      'data_entered_count': data_entered_count, 'reported_count': reported_count,
                      'bounced_count': bounced_count, 'clicked_count': clicked_count}
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': camp_stats}
