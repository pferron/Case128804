"""Runs all necessary scripts to maintain Mend info in the database and related Jira tickets"""

import os
import inspect
import traceback
from datetime import datetime
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from common.miscellaneous import Misc
from common.general import General
from common.logging import TheLogs
from bitsight.api_connections import BitSightAPI
from bitsight.database import DBQueries

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
    # BitSight.update_all_bitsight()

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
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

class BitSight():
    """BitSight specific stuff"""
    @staticmethod
    def update_all_bitsight(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Sequentially runs all of the updates"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        update_bitsight_inventory(main_log,ex_log,ex_file)
        update_bitsight_rating_details(main_log,ex_log,ex_file)
        update_bitsight_progholdings(main_log,ex_log,ex_file)
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_bitsight_inventory(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the BitSightInventory table"""
    i_cnt = 0
    TheLogs.log_headline('UPDATING THE BitSightInventory TABLE',2,"#",main_log)
    try:
        inventory = BitSightAPI.fetch_companies()
    except Exception as e_details:
        func = "BitSightAPI.fetch_companies()"
        e_code = "NB-UBI-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if inventory is not None:
        try:
            clear_table = DBQueries.clear_table('BitSightInventory')
        except Exception as e_details:
            func = "DBQueries.clear_table('BitSightInventory')"
            e_code = "NB-UBI-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        if clear_table is True:
            try:
                i_cnt = DBQueries.insert_into_table('BitSightInventory',inventory)
            except Exception as e_details:
                func = f"DBQueries.insert_into_table('BitSightInventory',{inventory})"
                e_code = "NB-UBI-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
    TheLogs.log_info('BitSightInventory was successfully updated',2,"*",main_log)

def update_bitsight_rating_details(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the BitSightRatingDetails table"""
    i_cnt = 0
    TheLogs.log_headline('UPDATING THE BitSightRatingDetails TABLE',2,"#",main_log)
    try:
        companies = DBQueries.ratings_details_available()
    except Exception as e_details:
        func = "DBQueries.ratings_details_available()"
        e_code = "NB-UBRD-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if companies is not None:
        try:
            clear_table = DBQueries.clear_table('BitSightRatingDetails')
        except Exception as e_details:
            func = "DBQueries.clear_table('BitSightRatingDetails')"
            e_code = "NB-UBRD-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        if clear_table is True:
            try:
                inventory = BitSightAPI.fetch_ratings_details(companies)
            except Exception as e_details:
                func = f"BitSightAPI.fetch_ratings_details({companies})"
                e_code = "NB-UBRD-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
            if inventory is not None:
                try:
                    i_cnt = DBQueries.insert_into_table('BitSightRatingDetails',inventory)
                except Exception as e_details:
                    func = f"DBQueries.insert_into_table('BitSightRatingDetails',{inventory})"
                    e_code = "NB-UBRD-004"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.fe_cnt += 1
                    return
    TheLogs.log_info('BitSightRatingDetails was successfully updated',2,"*",main_log)

def update_bitsight_progholdings(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the BitSightProgHoldings table"""
    i_cnt = 0
    TheLogs.log_headline('UPDATING THE BitSightProgHoldings TABLE',2,"#",main_log)
    try:
        companies = DBQueries.get_watchlist()
    except Exception as e_details:
        func = "DBQueries.get_watchlist()"
        e_code = "NB-UBP-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if companies is not None:
        try:
            clear_table = DBQueries.clear_table('BitSightProgHoldings')
        except Exception as e_details:
            func = "DBQueries.clear_table('BitSightProgHoldings')"
            e_code = "NB-UBP-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        if clear_table is True:
            try:
                inventory = BitSightAPI.fetch_prog_holdings(companies)
            except Exception as e_details:
                func = f"BitSightAPI.fetch_prog_holdings({companies})"
                e_code = "NB-UBP-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
            if inventory is not None:
                try:
                    i_cnt = DBQueries.insert_into_table('BitSightProgHoldings',inventory)
                except Exception as e_details:
                    func = f"DBQueries.insert_into_table('BitSightProgHoldings',{inventory})"
                    e_code = "NB-UBP-004"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.fe_cnt += 1
                    return
    TheLogs.log_info('BitSightProgHoldings was successfully updated',2,"*",main_log)

def update_bitsight_score_changes(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the BitSightScoreChange table"""
    i_cnt = 0
    updates = []
    TheLogs.log_headline('UPDATING THE BitSightScoreChange TABLE',2,"#",main_log)
    try:
        current = BitSightAPI.fetch_current_scores()
    except Exception as e_details:
        func = "BitSightAPI.fetch_current_scores()"
        e_code = "NB-UBSC-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if current is not None and current != []:
        try:
            previous = BitSightAPI.fetch_previous_scores()
        except Exception as e_details:
            func = "BitSightAPI.fetch_previous_scores()"
            e_code = "NB-UBSC-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return
        if previous is not None and previous != []:
            try:
                updates = General.combine_dictionaries_in_list_of_dictionaries(current,previous)
            except Exception as e_details:
                func = f"General.combine_dictionaries_in_list_of_dictionaries({current},{previous})"
                e_code = "NB-UBSC-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
        if updates != []:
            try:
                clear_table = DBQueries.clear_table('BitSightScoreChange')
            except Exception as e_details:
                func = "DBQueries.clear_table('BitSightScoreChange')"
                e_code = "NB-UBSC-004"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                return
            if clear_table is True:
                try:
                    i_cnt = DBQueries.insert_into_table('BitSightScoreChange',updates)
                except Exception as e_details:
                    func = f"DBQueries.insert_into_table('BitSightScoreChange',{updates})"
                    e_code = "NB-UBSC-005"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.fe_cnt += 1
                    return
                if i_cnt != 0:
                    try:
                        DBQueries.update_score_change()
                    except Exception as e_details:
                        func = "DBQueries.update_score_change()"
                        e_code = "NB-UBSC-006"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                        ScrVar.fe_cnt += 1
                    try:
                        DBQueries.no_score_change()
                    except Exception as e_details:
                        func = "DBQueries.no_score_change()"
                        e_code = "NB-UBSC-007"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                        ScrVar.fe_cnt += 1
    TheLogs.log_info('BitSightScoreChange was successfully updated',2,"*",main_log)

if __name__ == "__main__":
    main()