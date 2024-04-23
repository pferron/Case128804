
import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
import pysnow
import pytz
from common.constants import SNOW_INSTANCE, SNOW_USER
from dotenv import load_dotenv
from dataclasses import dataclass, field
from datetime import datetime
from common.logging import TheLogs
from common.database_sql_server_connection import SQLServerConnection
from pytz import timezone

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".", 1)[0]
LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SNOW_KEY = os.environ.get('SNOW_KEY')


@dataclass
class SnowManager:
    conn: SQLServerConnection = field(default_factory=SQLServerConnection)
    client: pysnow.Client = pysnow.Client(instance=SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)

    def __post_init__(self):
        self.task_table = self.client.\
            resource(api_path='/table/x_prole_software_c_software_change_task')
        self.change_table = self.client.\
            resource(api_path='/table/x_prole_software_c_software_change_request_table')
        self.app_table = self.client.resource(api_path='/table/cmdb_ci_service_auto')
        self.cmdb_table = self.client.resource(api_path='/table/cmdb_ci_appl')
        self.jira_table = self.client.resource(api_path='/table/u_jira_projects')
        self.group_table = self.client.resource(api_path='/table/sys_user_group')
        self.approval_table = self.client.resource(api_path='/table/sysapproval_approver')
        self.user_table = self.client.resource(api_path='/table/sys_user')

    def get_jira_key(self, jira_key):
        query = pysnow.QueryBuilder().field('sys_id').equals(jira_key)
        return self.jira_table.get(query=query).all()

    def get_sn_jira_project_key(self, jira_key: str) -> str:
        return self.get_jira_key(jira_key)[0]['u_project_key']

    def get_app_owned_by(self, group_id: str) -> str:
        if group_id:
            # Query for software change task
            response = self.group_table.get(query={'sys_id': group_id}, stream=True)
            try:
                return response.one()['name']
            except:
                return ''
        else:
            return ''

    # This function will extract the Name of the managed_by group from SNow
    def get_app_managed_by(self, user_id: str) -> str:
        if user_id:
            # Query for software change task
            response = self.user_table.get(query={'sys_id': user_id}, stream=True)
            try:
                v = response.one()['name']
                return response.one()['name']
            except:
                return ''
        else:
            return ''

    def get_snow_app(self, repo):
        query = (
            pysnow.QueryBuilder()
            .field('name')
            .equals(repo)
            .AND()
            .field('used_for')
            .equals('Production')
        )
        return self.cmdb_table.get(query=query).all()

    def get_all_snow_apps(self):
        query = (
            pysnow.QueryBuilder()
            .field('name')
            .not_equals('')
            .AND().
            field('used_for').
            equals('Production')
        )
        return self.app_table.get(query=query).all()

    def get_snow_apps_after_date(self, date):
        query = (
            pysnow.QueryBuilder()
            .field('name')
            .not_equals('')
            .AND()
            .field('used_for')
            .equals('Production')
            .AND()
            .field('sys_updated_on')
            .greater_than(date)
        )
        return self.app_table.get(query=query).all()

    @staticmethod
    def get_datetime(time_zone: str) -> datetime:
        if time_zone == 'local':
            current_time = datetime.now(timezone('US/Mountain'))
        else:
            current_time = datetime.now(timezone('UTC'))
        current_time = current_time.replace(tzinfo=None)
        return current_time

    @staticmethod
    def local_to_utc(mst_dt):
        # If we get a null string, we need to just sent it right back or else we
        # will have conversion errors
        if mst_dt == '':
            return ''
        # Set the incomming timezone (local) to MST
        local_tz = pytz.timezone('US/Mountain')
        # Set the return timezone to UTC
        utc_tz = pytz.timezone('UTC')
        # Convert the incoming date string to date time object
        mst_dt = local_tz.localize(mst_dt)
        # mst_dt = local_tz.localize(datetime.strptime(mst_dt, '%Y-%m-%d %H:%M:%S'))
        # Convert the local (MST) date to UTC
        utc_dt = mst_dt.astimezone(utc_tz)
        # Retuen the UTC tz datetime object as a string
        return utc_dt

    @staticmethod
    def utc_to_local(utc_dt: str) -> str:
        # If we get a null string, we need to just sent it right back or else
        # we will have conversion errors
        if not utc_dt:
            return ''
        # Set the incoming timezone to UTC
        utc_tz = pytz.timezone('UTC')
        # Set the return timezone (local) to MST
        local_tz = pytz.timezone('US/Mountain')
        # Convert the incoming date string to date time object
        utc_dt = utc_tz.localize(datetime.strptime(utc_dt, '%Y-%m-%d %H:%M:%S'))
        # Convert the UTC date to the local timezone
        local_dt = utc_dt.astimezone(local_tz)
        # Retuen the local tz datetime object as a string
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')
