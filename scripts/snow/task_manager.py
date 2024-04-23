
import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from dotenv import load_dotenv
from dataclasses import dataclass
from common.alerts import Alerts
from common.logging import TheLogs
from snow.snow_manager import SnowManager
from snow.change_manager import SNChangeManager
import pysnow

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".", 1)[0]
LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\snow-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_ALERTS = os.environ.get('SLACK_URL_ALERTS')

class ScrVar:
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []
    nraa_array = []

@dataclass
class SNTasksManager(SnowManager):
    def add_comment_to_task(self, task_number: str, comment: str, main_log=LOG) -> None:
        update = {'comments': comment}
        self.task_table.update(query={'number': task_number}, payload=update)
        TheLogs.log_info(f'{task_number} updated with comment: {comment}',2,"*",main_log)

    def pass_validation_on_task(self, task_number, change_number, main_log=LOG):
        ch_lnk = Alerts.create_change_ticket_link(change_number)
        if self.review_required_on_change(change_number):
            TheLogs.log_info(f'{task_number} cannot be set to passed validation due to review '
                             f'required on {change_number}',2,"*",main_log)
            msg = [f'*Change Ticket:* {change_number}']
            if ch_lnk is not None:
                msg = [f'*Change Ticket:* {ch_lnk}']
            try:
                Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 11, SLACK_URL_ALERTS)
            except Exception as details:
                func = 'pass_validation_on_task.if.review_required_on_change'
                e_code = "STM-001"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                ScrVar.fe_array.append(e_code)
                if ScrVar.fe_cnt > 0:
                    TheLogs.process_exceptions(ScrVar.fe_array, rf'{ALERT_SOURCE}', SLACK_URL, 1,
                                                        EX_LOG_FILE)
        else:
            sql = f"""
            UPDATE snTaskRecords
            SET snState = 3, StateText = 'Passed Validation' WHERE snTaskNumber = '{task_number}'
            """
            self.conn.query(sql)
            update = {'state': '3'}
            self.task_table.update(query={'number': task_number}, payload=update)
            TheLogs.log_info(f'{task_number} state set to passed validation in Service Now for '
                             f'{change_number}',2,"*",main_log)
            last_four_change = int(change_number[-4:])
            if last_four_change < 6500:
                msg = [f'*Task Updated:* {task_number}',f'*Change Ticket:* {change_number}',
                       '*Status:* Passed Validation; Ready for approval']
                if ch_lnk is not None:
                    msg = [f'*Task Updated:* {task_number}',f'*Change Ticket:* {ch_lnk}',
                           '*Status:* Passed Validation; Ready for approval']
                try:
                    Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 12, SLACK_URL_ALERTS)
                except Exception as details:
                    func = 'pass_validation_on_task.if < 6500'
                    e_code = "STM-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                    ScrVar.fe_cnt += 1
                    ScrVar.fe_array.append(e_code)
                    if ScrVar.fe_cnt > 0:
                        TheLogs.process_exceptions(ScrVar.fe_array, rf'{ALERT_SOURCE}', SLACK_URL, 1,
                                                            EX_LOG_FILE)

            else:
                TheLogs.log_info(f'Slack message not needed for {change_number}, CCSX #s above '
                                '6500 do not need manual approval',2,"*",main_log)

    def add_task_to_db(self, task, snow_change_manager: SNChangeManager, main_log=LOG) -> None:
        # Get the change request tied to this task
        change = snow_change_manager.get_change_by_query({'sys_id': task['parent']['value']})
        # Build the SQL statement to insert this task into the table
        sql = f"""INSERT INTO TESTING_snTaskRecords (snTaskNumber, snState, StateText,
        snChangeRequest, snSysCreatedOn, snSysUpdatedOn, highFindings) VALUES('{task['number']}',
        '{task['state']}', '{self.get_task_state_text(task['state'])}', '{change['number']}',
        '{self.utc_to_local(task['sys_created_on'])}',
        '{self.utc_to_local(task['sys_updated_on'])}', 0)"""
        self.conn.query(sql)
        TheLogs.log_info(f'{task["number"]} added to the database',2,"*",main_log)

    def fail_validation_on_task(self, task_number: str, change_number: str = "",
                                send_slack_message: bool = False, main_log = LOG) -> None:
        update = {'state': '4'}
        self.task_table.update(query={'number': task_number}, payload=update)
        TheLogs.log_info(f'{task_number} state set to failed validation in Service Now',2,"*",
                         main_log)
        sql = f"""
        UPDATE snTaskRecords
        SET snState = 4, StateText = 'Failed Validation' WHERE snTaskNumber = '{task_number}'
        """
        self.conn.query(sql)
        if send_slack_message:
            ch_lnk = Alerts.create_change_ticket_link(change_number)
            msg = [f'*Task Number:* {task_number}',f'*Change Ticket:* {change_number}']
            if ch_lnk is not None:
                msg = [f'*Task Number:* {task_number}',f'*Change Ticket:* {ch_lnk}']
            try:
                Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 13, SLACK_URL_ALERTS)
            except Exception as details:
                    func = 'fail_validation_on_task'
                    e_code = "STM-003"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                    ScrVar.fe_cnt += 1
                    ScrVar.fe_array.append(e_code)
                    if ScrVar.fe_cnt > 0:
                        TheLogs.process_exceptions(ScrVar.fe_array, rf'{ALERT_SOURCE}', SLACK_URL, 1,
                                                            EX_LOG_FILE)


    def get_task(self, task_number):
        response = self.task_table.get(query={'number': task_number}, stream=True)
        return response.one()

    def get_all_tasks(self):
        query = (
            pysnow.QueryBuilder()
            .field('short_description')
            .equals('Run Security Scans')
            .AND()
            .field('parent')
            .not_equals('')
        )
        return self.task_table.get(query=query).all()

    def get_tasks_after_date(self, start_date):
        utc_date = self.local_to_utc(start_date)
        query = (
            pysnow.QueryBuilder()
            .field('short_description')
            .equals('Run Security Scans')
            .AND()
            .field('sys_created_on')
            .greater_than(utc_date)
        )
        return self.task_table.get(query=query).all()

    def get_all_open_tasks(self):
        query = (
            pysnow.QueryBuilder()
            .field('short_description')
            .equals('Run Security Scans')
            .AND()
            .field('state')
            .equals('1')
        )
        return self.task_table.get(query=query).all()

    def get_task_for_change(self, change_number: int) -> int:
        query = pysnow.QueryBuilder().field('number').equals(change_number)
        change = self.change_table.get(query=query).one()
        query = (
            pysnow.QueryBuilder()
            .field('parent').equals(change['sys_id'])
            .AND()
            .field('short_description').equals('Run Security Scans')
        )
        return self.task_table.get(query=query).one()

    def review_required_on_change(self, change_number):
        sql = f"""
        SELECT ReviewRequired
        FROM snchangeRecords
        WHERE snChangeNumber = '{change_number}'
        """
        return self.conn.query(sql)[0][0]

    @staticmethod
    def get_task_state_text(index):
        state_text = ['Unused', 'Open', 'Cancelled', 'Passed Validation', 'Failed Validation']
        if int(index) > 4:
            return "Unknown"
        return state_text[int(index)]
