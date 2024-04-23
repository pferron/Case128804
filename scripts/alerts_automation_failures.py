"""Issues Slack alerts when automation fails"""

import os
import sys
from dotenv import load_dotenv
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from automation_alerts.processing import ProcessAutomation
from common.alerts import Alerts
from common.general import General
from common.logging import TheLogs
from common.miscellaneous import Misc

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_ALERTS = os.environ.get('SLACK_URL_ALERTS')

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # alert_on_failed_runs('Every5Minutes')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []
    today = Misc.day_of_the_week()

def alert_on_failed_runs(run_for=ScrVar.today,main_log=LOG):
    """Executes based on AutomationFailures.today or when run_for is set to the name of any of
    the bit columns in the ScriptExecutionSchedule table in the AppSec database"""
    log_alert = "No alerts to send"
    use_slack_channel = SLACK_URL
    alert_id = 20
    if run_for in ('Every5Minutes','Hourly'):
        use_slack_channel = SLACK_URL_ALERTS
        alert_id = 21
    TheLogs.log_headline(f'SENDING ALERTS FOR {run_for}',2,"#",main_log)
    skipped = ProcessAutomation.get_missing_runs(run_for,main_log)
    if 'Results' in skipped:
        send_alert = Alerts.manual_alert(rf'{ALERT_SOURCE}',skipped['Results'],len(skipped['Results']),
                                        alert_id,use_slack_channel)
        if send_alert > 0:
            log_alert = 'Alert sent to Slack'
    TheLogs.log_info(log_alert,2,"*",main_log)

if __name__ == "__main__":
    main()
