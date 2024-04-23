"""Runs all necessary scripts to maintain Mend info in the database and related Jira tickets"""

import os
import sys
import inspect
import traceback
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from common.miscellaneous import Misc
from common.logging import TheLogs
from common.general import General
from mend.general_maintenance import MendMaint
from mend.report_processing import MendReports
from mend.ticket_creation_and_closure import MendTickets
from mend.data_sync import MendSync
from mend.deleted_project_handling import DeletedProjects

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        globals()[cmd['function']]()
    # MendRepos.run_all_mend()
    # MendRepos.onboard_single_repo('four',True)

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

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

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ALERT_SOURCE}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

@dataclass
class MendRepos():
    """For use with onboarding a single repo"""
    @staticmethod
    def onboard_single_repo(repo,nightly=False,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Runs the minimum scripts required to onboard a single repo"""
        step = 2
        if nightly is False:
            step = 1
            repo_mend_maintenance(repo,main_log,ex_log,ex_file)
            step += 1
        if ScrVar.fe_cnt == 0:
            process_mend_findings(repo,step,main_log,ex_log,ex_file)
            step += 1
            if ScrVar.fe_cnt == 0:
                process_mend_tickets(repo,step,main_log,ex_log,ex_file)
                step += 1
            do_mend_cleanup(repo,step,main_log,ex_log,ex_file)
            step += 1
        if nightly is False:
            TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,ScrVar.src,SLACK_URL,ex_file)
            TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,ScrVar.src,SLACK_URL,ex_file)

    @staticmethod
    def run_all_mend(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs all of the steps"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        run_all_mend_maintenance(1,main_log,ex_log,ex_file)
        repos = MendMaint.get_all_mend_repos(main_log)
        ScrVar.update_exception_info(repos)
        if repos['Results'] != []:
            for repo in repos['Results']:
                MendRepos.onboard_single_repo(repo,True,main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt}

def run_all_mend_maintenance(step,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''syncs Mend data for all'''
    TheLogs.log_headline(f'STEP {step}: Updating base Mend information',1,"#",LOG)
    try:
        result = MendMaint.all_mend_maintenance(None,main_log)
    except Exception as e_details:
        func = "MendMaint.all_mend_maintenance(None)"
        e_code = "TM-RAMM-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(result)
    TheLogs.log_headline(f'STEP {step}: Complete',1,"#",LOG)

def cmd_line_run_all(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """For executing run_all_mend from the command line"""
    MendRepos.run_all_mend(main_log,ex_log,ex_file)

def repo_mend_maintenance(repo,step,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''syncs Mend data for repo'''
    TheLogs.log_headline(f'STEP {step}: Syncing Mend information for {repo}',1,"#",main_log)
    try:
        result = MendMaint.all_mend_maintenance(repo,main_log)
    except Exception as e_details:
        func = f"MendMaint.all_mend_maintenance('{repo}')"
        e_code = "TM-RMM-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(result)
    del_projects = DeletedProjects.cancel_tickets_for_deleted_projects(main_log=LOG)
    ScrVar.update_exception_info(del_projects)
    TheLogs.log_headline(f'STEP {step}: Complete',1,"#",main_log)

def process_mend_findings(repo,step,main_log=LOG,ex_log=LOG_EXCEPTION,
                                    ex_file=EX_LOG_FILE):
    '''processes Mend findings for repo'''
    TheLogs.log_headline(f'STEP {step}: Processing findings for {repo}',1,"#",main_log)
    try:
        result = MendReports.single_repo_updates(repo,main_log)
    except Exception as e_details:
        func = f"MendReports.single_repo_updates('{repo}')"
        e_code = "TM-PMF-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(result)
    TheLogs.log_headline(f'STEP {step}: Complete',1,"#",main_log)

def process_mend_tickets(repo,step,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''processes Mend tickets for repo'''
    TheLogs.log_headline(f'STEP {step}: Handling Jira tickets for {repo}',1,"#",main_log)
    try:
        result = MendTickets.single_repo_ticketing(repo,main_log)
    except Exception as e_details:
        func = f"MendTickets.single_repo_ticketing('{repo}')"
        e_code = "TM-PMT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(result)
    TheLogs.log_headline(f'STEP {step}: Complete',1,"#",main_log)

def do_mend_cleanup(repo,step,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Mend db cleanup for repo'''
    TheLogs.log_headline(f'STEP {step}: Cleaning up the database for {repo}',1,"#",main_log)
    try:
        result = MendSync.single_repo_updates(repo,main_log)
    except Exception as e_details:
        func = f"MendSync.single_repo_updates('{repo}')"
        e_code = "TM-DMC-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(result)
    TheLogs.log_headline(f'STEP {step}: Complete',1,"#",main_log)

if __name__ == "__main__":
    main()
