"""Performs database backups. NOTE: This script will fail unless run from SLC-PRDAPPMX01"""

import calendar
import os
import inspect
import traceback
import pyodbc
import sys
from dotenv import load_dotenv
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from common.constants import DB_SERVER, DB_USER
from common.general import General
from common.logging import TheLogs
from common.miscellaneous import Misc
from datetime import date, datetime

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
DB_KEY = os.environ.get('DB_KEY')


class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    #  Add the name of any database on SLC-PRDAPPMX01 to this array to create backups for it.
    databases = [{'databaseName': 'AppSec', 'backupDay': 'All'},
                         {'databaseName': 'BitSight', 'backupDay': 'Sunday'},
                         {'databaseName': 'InfoSecDashboard', 'backupDay': 'Sunday'},
                         {'databaseName': 'JiraInfo', 'backupDay': 'Friday'},
                         {'databaseName': 'KnowBe4', 'backupDay': 'Sunday'},
                         {'databaseName': 'Metrics', 'backupDay': 'Friday'},
                         {'databaseName': 'PenetrationTesting', 'backupDay': 'Friday'}]

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

def main():
    "Runs the specified stuff"
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        globals()[cmd['function']]()

def backup_databases(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    "Performs the database backups"
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    TheLogs.log_headline('BACKING UP THE AppSec DATABASE',2,"#",main_log)
    server_backup_path = 'c:\\SQLBackups\\'
    folder_exists = os.path.exists(server_backup_path)
    if not folder_exists:
        os.makedirs(server_backup_path)
    today = date.today()
    dotw = calendar.day_name[today.weekday()]
    for item in ScrVar.databases:
        database = item['databaseName']
        backup_day = item['backupDay']
        server_backup_path = 'c:\\SQLBackups\\' + str(database) + '\\'
        folder_exists = os.path.exists(server_backup_path)
        if not folder_exists:
            os.makedirs(server_backup_path)
        if backup_day == 'All' or backup_day == dotw:
            try:
                database_connection = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                                            'Server=' + str(DB_SERVER) + ';'
                                                            'Database=' + str(database) + ';'
                                                            'UID=' + str(DB_USER) + ';'
                                                            'PWD=' + str(DB_KEY))
                database_connection.autocommit = True
                backup_date = datetime.now()
                backup_date = backup_date.strftime("%m%d%Y_%H%M%S")
                database_path = f"{server_backup_path}{database}_FULL_{backup_date}.bak"
                cur = database_connection.cursor()
                cur.execute('BACKUP DATABASE ? TO DISK=?', [database, database_path])
                while cur.nextset():
                    pass
                cur.close()
            except Exception as details:
                func = "pyodbc.connect(Driver={SQL Server Native Client 11.0}; "
                func += f"Server='{DB_SERVER}'; "
                func += f"Database='{database}'; "
                func += f"UID='{DB_USER}'; "
                func += f"PWD='{DB_KEY}')"
                e_code = 'ASDB-DB-001'
                TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,
                                        rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                        traceback.format_exc())
                ScrVar.fe_cnt += 1
                ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
                return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt}
            file_exists = os.path.exists(database_path)
            if file_exists:
                TheLogs.log_info(f'{database} has been backed up to {database_path}',2,"*",
                                 main_log)
            else:
                details = f'{database} backup failed for unknown reasons. Please try executing '
                details += 'the script from the server.'
                e_code = 'ASDB-DB-002'
                TheLogs.exception(details,e_code,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
                ScrVar.fe_cnt += 1
                ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
                return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt}
            database_connection.close()
    try:
        cleanup_database_backups(main_log,ex_log,ex_file)
    except Exception as details:
        func = f"cleanup_database_backups()"
        e_code = 'ASDB-DB-003'
        TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt}
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt}

# Cleans up the backup folders by deleting files older than 30 days
def cleanup_database_backups(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    "Deletes database backups older than 30 days"
    TheLogs.log_headline('REMOVING DATABASE BACKUP FILES OLDER THAN 30 DAYS',2,"#",main_log)
    c_cnt = 0
    for database in ScrVar.databases:
        path = "c:\\SQLBackups\\" + str(database['databaseName']) + "\\"
        try:
            today = datetime.today()
            os.chdir(path)
            for root,directories,files in os.walk(path,topdown=False):
                for name in files:
                    t_s = os.stat(os.path.join(root, name))[8]
                    filetime = datetime.fromtimestamp(t_s) - today
                    if filetime.days <= -30:
                        os.remove(os.path.join(root, name))
                        c_cnt += 1
        except Exception as details:
            func = "See stack trace for details."
            e_code = 'ASDB-BC-001'
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file,
                                        rf'{ALERT_SOURCE}',inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{c_cnt} old database file(s) removed",2,"*",main_log)

if __name__ == '__main__':
    main()
