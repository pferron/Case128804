"""Non-ProdSec updates for KnowBe4 database. Contact Lisa Struck before making any changes to
processing or the database and/or for assistance with obtaining an updated KnowBe4 API key"""

import os
import time
import inspect
import traceback
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.database_generic import DBQueries
from common.logging import TheLogs
from common.miscellaneous import Misc
from knowbe4.api_connections import KB4API

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
    # Runs all updates
    # process_knowbe4_updates()

class ScrVar():
    """Stuff for this script"""
    fe_cnt = 0
    ex_cnt = 0
    today = datetime.now().strftime('%A')
    start_timer = None
    src = ALERT_SOURCE.replace("-","\\")
    running_function = ''

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

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        if isinstance(dictionary,dict):
            if ('FatalCount' in dictionary and
                isinstance(dictionary['FatalCount'],int)):
                ScrVar.fe_cnt += dictionary['FatalCount']
            if ('ExceptionCount' in dictionary and
                isinstance(dictionary['ExceptionCount'],int)):
                ScrVar.ex_cnt = dictionary['ExceptionCount']

    @staticmethod
    def repeat_function(list_of_dicts,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        try:
            for cmd in list_of_dicts:
                if 'args' in cmd:
                    globals()[cmd['function']](*cmd['args'])
        except Exception as e_details:
            func = f"repeat_function({list_of_dicts})"
            e_code = "NK-RF-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                       traceback.format_exc())
            ScrVar.fe_cnt += 1

class KB4Updates():
    """Stuff for this script"""
    r_added = 0
    r_updated = 0
    r_removed = 0

    @staticmethod
    def get_all_user_groups(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves active user groups and syncs them to the UserGroups table"""
        group_cnt = 0
        time.sleep(2)
        try:
            user_groups = KB4API.get_user_groups(main_log)
        except Exception as e_details:
            func = "KB4API.get_user_groups"
            e_code = "NK-GAUG-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        ScrVar.update_exception_info(user_groups)
        if user_groups['Results'] != [] and isinstance(user_groups['Results'],list):
            try:
                group_cnt += DBQueries.insert_multiple('UserGroups',user_groups['Results'],
                                                       'KnowBe4',verify_on=['id'],
                                                       show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('UserGroups',{user_groups['Results']},"
                func += "'KnowBe4',verify_on=['id'],show_progress=False)"
                e_code = "NK-GAUG-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
        TheLogs.log_info(f'{group_cnt} group(s) synced',2,"*",main_log)

    @staticmethod
    def get_all_training_campaigns(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves active user groups and syncs them to the TrainingCampaigns table"""
        camp_cnt = 0
        time.sleep(2)
        try:
            campaigns = KB4API.get_training_campaigns(main_log)
        except Exception as e_details:
            func = "KB4API.get_training_campaigns"
            e_code = "NK-GATC-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        ScrVar.update_exception_info(campaigns)
        if campaigns['Results'] != [] and isinstance(campaigns['Results'],list):
            try:
                camp_cnt += DBQueries.insert_multiple('TrainingCampaigns',campaigns['Results'],
                                                      'KnowBe4',verify_on=['campaign_id'],
                                                      show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('TrainingCampaigns',{campaigns['Results']},"
                func += "'KnowBe4',verify_on=['campaign_id'],show_progress=False)"
                e_code = "NK-GATC-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
        TheLogs.log_info(f'{camp_cnt} campaign(s) synced',2,"*",main_log)

    @staticmethod
    def get_all_phishing_campaigns(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves active user groups and syncs them to the PhishingCampaigns table"""
        camp_cnt = 0
        time.sleep(2)
        try:
            campaigns = KB4API.get_phishing_campaigns(main_log)
        except Exception as e_details:
            func = "KB4API.get_phishing_campaigns"
            e_code = "NK-GAPC-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        ScrVar.update_exception_info(campaigns)
        if campaigns['Results'] != [] and isinstance(campaigns['Results'],list):
            try:
                camp_cnt += DBQueries.insert_multiple('PhishingCampaigns',campaigns['Results'],
                                                      'KnowBe4',verify_on=['campaign_id'],
                                                      show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('PhishingCampaigns',{campaigns['Results']},"
                func += "'KnowBe4',verify_on=['campaign_id'],show_progress=False)"
                e_code = "NK-GAPC-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
        TheLogs.log_info(f'{camp_cnt} campaign(s) synced',2,"*",main_log)

def process_knowbe4_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs all updates for KnowBe4 database"""
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    update_active_users(main_log,ex_log,ex_file)
    if ScrVar.today == 'Sunday':
        update_inactive_users(main_log,ex_log,ex_file)
    update_user_groups(main_log,ex_log,ex_file)
    update_training_campaigns(main_log,ex_log,ex_file)
    update_phishing_campaigns(main_log,ex_log,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_active_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the ActiveUserScores table in the KnowBe4 database"""
    TheLogs.log_headline("UPDATING THE ActiveUserScores TABLE",2,"#",main_log)
    try:
        DBQueries.clear_table('ActiveUserScores','KnowBe4')
    except Exception as e_details:
        func = "DBQueries.clear_table('ActiveUserScores','KnowBe4')"
        e_code = "NK-UAU-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    KB4Updates.r_added = 0
    get_all_users(1,'active',main_log)

def update_inactive_users(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the InactiveUserScores table in the KnowBe4 database"""
    TheLogs.log_headline("UPDATING THE InactiveUserScores TABLE",2,"#",main_log)
    try:
        DBQueries.clear_table('InactiveUserScores','KnowBe4')
    except Exception as e_details:
        func = "DBQueries.clear_table('InactiveUserScores','KnowBe4')"
        e_code = "NK-UIU-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    KB4Updates.r_added = 0
    get_all_users(1,'archived',main_log)

def update_user_groups(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the UserGroups table in the KnowBe4 database"""
    TheLogs.log_headline("UPDATING THE UserGroups TABLE",2,"#",main_log)
    try:
        DBQueries.clear_table('UserGroups','KnowBe4')
    except Exception as e_details:
        func = "DBQueries.clear_table('UserGroups','KnowBe4')"
        e_code = "NK-UUG-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    KB4Updates.get_all_user_groups(main_log)

def update_training_campaigns(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the TrainingCampaigns table in the KnowBe4 database"""
    TheLogs.log_headline("UPDATING THE TrainingCampaigns TABLE",2,"#",main_log)
    try:
        DBQueries.clear_table('TrainingCampaigns','KnowBe4')
    except Exception as e_details:
        func = "DBQueries.clear_table('TrainingCampaigns','KnowBe4')"
        e_code = "NK-UTC-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    KB4Updates.get_all_training_campaigns(main_log)

def update_phishing_campaigns(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the PhishingCampaigns table in the KnowBe4 database"""
    TheLogs.log_headline("UPDATING THE PhishingCampaigns TABLE",2,"#",main_log)
    try:
        DBQueries.clear_table('PhishingCampaigns','KnowBe4')
    except Exception as e_details:
        func = "DBQueries.clear_table('PhishingCampaigns','KnowBe4')"
        e_code = "NK-UPC-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    KB4Updates.get_all_phishing_campaigns(main_log)

def get_all_users(page,status,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Loops through users to update the appropriate database"""
    db_table = 'ActiveUserScores'
    if status == "archived":
        db_table = 'InactiveUserScores'
    user_cnt = 0
    time.sleep(2)
    print(f'          *  Processing page: {page}',end='\r')
    try:
        user_list = KB4API.get_users(page,status,main_log)
    except Exception as e_details:
        func = f"KB4API.get_users({page},'{status}')"
        e_code = "NK-GAU-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                   rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    ScrVar.update_exception_info(user_list)
    if user_list['Results'] != [] and isinstance(user_list['Results'],list):
        user_cnt = user_list['UserCount']
        try:
            KB4Updates.r_added += DBQueries.insert_multiple(db_table,user_list['Results'],
                                                            'KnowBe4',verify_on=['first_name',
                                                                                 'last_name','id'],
                                                            show_progress=False)
        except Exception as e_details:
            func = f"DBQueries.insert_multiple({db_table},{user_list['Results']},'KnowBe4',"
            func += "verify_on=['first_name','last_name'],show_progress=False)"
            e_code = "NK-GAU-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
    if int(user_cnt) < 500:
        TheLogs.log_info(f'{KB4Updates.r_added} user(s) synced',2,"*",main_log)
    else:
        page += 1
        ScrVar.repeat_function([{'function': 'get_all_users', 'args': [page,status,main_log]}],
                               main_log,ex_log,ex_file)

if __name__ == "__main__":
    main()