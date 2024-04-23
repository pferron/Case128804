
import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from snow.snow_manager import SnowManager
from common.logging import TheLogs
from dataclasses import dataclass
import pysnow
from datetime import datetime
from typing import Dict

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".", 1)[0]
LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

@dataclass
class SNChangeManager(SnowManager):
    def get_change_by_number(self, change_number: int) -> int:
        query = pysnow.QueryBuilder().field('number').equals(change_number)
        return self.change_table.get(query=query).one()

    def get_changes_after_date(self, start_date):
        # Convert the local date/time to UTC before searching in ServiceNow
        utc_date = self.local_to_utc(start_date)
        query = pysnow.QueryBuilder().field('sys_created_on').greater_than(utc_date)
        return self.change_table.get(query=query).all()

    # This function returns all SNOW change records that were created after we began receiving
    # SNOW tasks
    def get_all_changes(self):
        query = (
            pysnow.QueryBuilder().
            field('sys_created_on').
            greater_than(datetime(2020, 9, 13, 16, 48, 44))
        )
        return self.change_table.get(query=query).all()

    def get_change_by_query(self, my_query: Dict[str, str]):
        response = self.change_table.get(query=my_query, stream=True)
        return response.one()

    def check_change_approval(self, change_number: int):
        query = (
            pysnow.QueryBuilder()
            .field('u_approval_for_string').equals(change_number)
            .AND().field('sys_updated_by').equals('chris.parliment')
            .OR().field('sys_updated_by').equals('chris.parliment@progleasing.com')
            .OR().field('sys_updated_by').equals('sean.mclaughlin')
            .OR().field('sys_updated_by').equals('sean.mclaughlin@progleasing.com')
            .OR().field('sys_updated_by').equals('john.mccutchen')
            .OR().field('sys_updated_by').equals('john.mccutchen@progleasing.com'))
        approvals = self.approval_table.get(query=query).all()
        if len(approvals) > 0:
            return approvals[0]['sys_updated_on']
        else:
            return ''
