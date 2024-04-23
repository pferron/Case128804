"""This file updates RITM ticket information from SNow in the AppSec.SNowSecurityExceptions table"""

import os
import sys
import inspect
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.miscellaneous import Misc
from common.logging import TheLogs
from common.general import General
from maint.snow_exceptions_api_connections import SNowAPI
from maint.snow_exceptions_processing import SNowProc

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_SNOW_EXCEPTIONS = os.environ.get('SLACK_URL_SNOW_EXCEPTIONS')

def main():
    """Runs the specified stuff"""
    # To execute from the command line use the following schema:
    # python.exe c:\AppSec\scripts\maintenance_snow_ritm_processing.py "update_all_snow_exceptions(period='past_week')"
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()
    # To run the script, use one of the following period values pulling data for the
    # obviously-stated timeframe. Alternatively, you can use period=None or run the
    # update_all_snow_exceptions function without including a stated period, which will sync all
    # RITM tickets (in the IS18.x family) from SNow, but this will take quite a long time.
    # update_all_snow_exceptions(period='past_15_minutes')
    # update_all_snow_exceptions(period='hourly')
    # update_all_snow_exceptions(period='past_24_hours')
    # update_all_snow_exceptions(period='past_week')
    # update_all_snow_exceptions(period='past_month')
    # update_all_snow_exceptions(period='past_quarter')
    # update_all_snow_exceptions(period='past_week')
    # update_all_snow_exceptions(period='past_6_months')
    # update_all_snow_exceptions(period='past_12_months')

class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")
    running_function = None

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        if 'FatalCount' in dictionary:
            ScrVar.fe_cnt += dictionary['FatalCount']
        if 'ExceptionCount' in dictionary:
            ScrVar.ex_cnt = dictionary['ExceptionCount']

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ScrVar.src}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ScrVar.src}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ScrVar.src}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def update_all_snow_exceptions(period=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Runs the updates'''
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    p_p = ' FOR ALL TIME'
    if period is not None:
        p_p = str(period).replace('_',' ').upper()
        if p_p == 'HOURLY':
            p_p = " FOR THE PAST HOUR"
        else:
            p_p = f" FOR THE {p_p}"
    TheLogs.log_headline(f'PROCESSING ALL RITM TICKETS{p_p}',1,"!",main_log)
    TheLogs.log_headline('UPDATING APPROVERS LIST IN SNowSecurityApprovers',2,"#",main_log)
    approvers = SNowAPI.update_snow_approvers(main_log)
    ScrVar.update_exception_info(approvers)
    TheLogs.log_headline('PULLING UPDATES FROM SNOW',2,"#",main_log)
    exception_tickets = SNowAPI.process_exception_requests(period,main_log)
    ScrVar.update_exception_info(exception_tickets)
    updated = exception_tickets['Results']['updated']
    inserted = exception_tickets['Results']['added']
    TheLogs.log_info(f'RITM tickets updated in SNowSecurityExceptions: {updated}',2,"*",
                        main_log)
    TheLogs.log_info(f'RITM tickets added to SNowSecurityExceptions: {inserted}',2,"*",
                        main_log)
    TheLogs.log_headline('SYNCING RITM TICKETS WITH JiraIssues',2,"#",main_log)
    syncs = SNowProc.sync_with_jiraissues(main_log)
    ScrVar.update_exception_info(syncs)
    process_tickets = SNowProc.update_tool_and_jira_exceptions(main_log)
    ScrVar.update_exception_info(process_tickets)
    TheLogs.log_headline('CREATING ALERTS FOR PENDING APPROVALS',2,"#",main_log)
    alerts = SNowProc.alerts_for_pending_approvals(main_log)
    ScrVar.update_exception_info(alerts)
    TheLogs.log_headline('CREATING ALERTS FOR MISSING JIRA TICKETS',2,"#",main_log)
    alerts = SNowProc.alerts_for_missing_jira_tickets(main_log)
    ScrVar.update_exception_info(alerts)
    TheLogs.log_headline('PROCESSING COMPLETE',1,"!",main_log)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

if __name__ == "__main__":
    main()
