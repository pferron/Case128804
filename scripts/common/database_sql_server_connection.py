import logging
import os
import pyodbc
from common.constants import DB_SERVER, DB_USER
from dotenv import load_dotenv
from dataclasses import dataclass, field
from common.logging import TheLogs

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
KEY = os.environ.get('DB_KEY')
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')


@dataclass
class SQLServerConnection:
    database: str = 'AppSec'
    # driver: str = 'SQL Server Native Client 11.0'
    driver: str = 'SQL Server Native Client 11.0'
    server: str = DB_SERVER
    user: str = DB_USER
    key: str = KEY
    source: str = ''  # what filename the connection is being called from
    log_file: str = ''  # location for logs, format = "C:\\AppSec\\logs\\{LOG_BASE_NAME}.log"
    exception_log_file: str = ''  # location for exception logs, format = "C:\\AppSec\\logs\\{LOG_BASE_NAME}_exceptions.log"
    func: str = ''  # function being run when exception occurred
    e_code: str = ''  # exception code
    e_details: str = None  # exception details
    fe_count: int = 0  # fatal exception count
    fe_array: list[str] = field(default_factory=list)  # fatal exception array for e_codes

    def __post_init__(self):
        self.connection = pyodbc.connect(f'Driver={{{self.driver}}};'
                                         f'Server={self.server};'
                                         f'Database={self.database};'
                                         f'UID={self.user};'
                                         f'PWD={self.key}')
        self.cursor = self.connection.cursor()

    def query(self, sql):
        try:
            self.cursor.execute(sql)
            if any(x in ('INSERT', 'UPDATE', 'DELETE') for x in sql.split(" ")):
                self.cursor.commit()
            else:
                return self.cursor.fetchall()
        except pyodbc.ProgrammingError as e:
            logging.error(e)

    def query_with_logs(self, sql, main_log=LOG):
        '''this will connect to database with exceptions built in.
        required attributes for this Class to update from connecting file are log_file, exception_log_file
        e_code, source, func. See alerts_team_notifs.py for example set up and use'''
        log_exception = TheLogs.setup_logging(self.exception_log_file)
        try:
            self.cursor.execute(sql)
            if any(x in ('INSERT', 'UPDATE', 'DELETE') for x in sql.split(" ")):
                self.cursor.commit()
                return self.cursor.rowcount
            else:
                return self.cursor.fetchall()
        except pyodbc.ProgrammingError as e_cont:
            self.e_code = 'SQL-CONNECT-01'
            self.e_details = f"\n{e_cont}"
            self.e_details += "FUNCTION THAT WAS RUN: " + self.func
            TheLogs.sql_exception(sql, self.e_code, self.e_details, log_exception, main_log, self.exception_log_file)
            self.fe_array.append(self.e_code)
            self.fe_count += 1
            return self.fe_count, self.fe_array


    def __del__(self):
        self.cursor.close()
        self.connection.close()
