"""Archives the logs and deletes archived files older than 30 days"""

import os
import shutil
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from datetime import datetime
from common.miscellaneous import Misc
from common.logging import TheLogs

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{BACKUP_DATE}-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{BACKUP_DATE}-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

def main():
    """Runs the specified stuff"""
    # LogCleanup.all_maintenance()

class LogCleanup:
    """Stuff for this script"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []

    @staticmethod
    def all_maintenance(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs all maintenance"""
        running_function = 'all_maintenance'
        start_timer = Misc.start_timer()
        archive_logs(main_log,ex_log,ex_file)
        archive_cleanup(30,main_log,ex_log,ex_file)
        Misc.end_timer(start_timer,rf'{ALERT_SOURCE}',running_function,LogCleanup.ex_cnt,
                       LogCleanup.fe_cnt)

    @staticmethod
    def delete_archives(num_of_days,paths,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Deletes archived log files"""
        f_cnt = 0
        for path in paths:
            today = datetime.today()
            os.chdir(path)
            for root,directories,files in os.walk(path,topdown=False):
                for name in files:
                    file_stamp = os.stat(os.path.join(root, name))[8]
                    file_time = datetime.fromtimestamp(file_stamp) - today
                    if file_time.days <= num_of_days and BACKUP_DATE not in name:
                        try:
                            os.remove(os.path.join(root, name))
                            f_cnt += 1
                        except Exception as details:
                            func = f'Unable to delete archive file: {name}'
                            e_code = "MLC-AC-001"
                            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
                            LogCleanup.fe_cnt += 1
                            LogCleanup.fe_array.append(e_code)
        return f_cnt

    @staticmethod
    def move_logs(paths,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Moves log files to the archive"""
        f_cnt = 0
        for path in paths:
            for file in os.listdir(path):
                backup_date = datetime.now().strftime("(%Y-%m-%d)_")
                if file.endswith('.log') and BACKUP_DATE not in file:
                    filename = rf'c:\\AppSec\\logs\\archive\\{backup_date}_{file}'
                    src_file = f'{path}{file}'
                    try:
                        file = open(src_file,'r',encoding='utf-8')
                        file.close()
                        if file.closed:
                            shutil.move(src_file,filename)
                        f_cnt += 1
                    except Exception as details:
                        func = f'Unable to back up {src_file}'
                        e_code = "MLC-AL-001"
                        TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
                        LogCleanup.fe_cnt += 1
                        LogCleanup.fe_array.append(e_code)
        return f_cnt

def archive_logs(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Moves current logs into the archive folder"""
    f_cnt = 0
    TheLogs.log_headline('ARCHIVING CURRENT LOG FILES',2,"#",main_log)
    paths = ["c:\\AppSec\\logs\\"]
    f_cnt = LogCleanup.move_logs(paths)
    TheLogs.log_info(f'{f_cnt} log_file(s) archived',2,"*",main_log)

def archive_cleanup(num_of_days,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Deletes archived logs older than the specified number of days"""
    f_cnt = 0
    TheLogs.log_headline(f'REMOVING LOG FILES OLDER THAN {num_of_days} DAYS',2,"#",main_log)
    paths = ["c:\\AppSec\\logs\\archive\\"]
    num_of_days = -1 * num_of_days
    f_cnt = LogCleanup.delete_archives(num_of_days,paths)
    TheLogs.log_info(f'{f_cnt} archived log file(s) deleted',2,"*",main_log)

if __name__ == '__main__':
    main()
