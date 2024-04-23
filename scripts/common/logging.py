"""This file contains general and exception logging"""

import logging
import textwrap
import math
from datetime import datetime
from common.database_generic import DBQueries
from common.alerts import Alerts

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")

class LogFilter(object):
    """Sets up the log filter"""
    def __init__(self,level):
        self.__level = level
    def filter(self,log_record):
        """Define the filter"""
        return log_record.levelno == self.__level

class TheLogs:
    """Has all of the stuff for logging"""
    wrap_exception = textwrap.TextWrapper(
        width = 100,
        drop_whitespace = True,
        break_long_words = False,
        break_on_hyphens = False,
        replace_whitespace = False
    )

    wrap_log = textwrap.TextWrapper(
        width = 100,
        subsequent_indent = ' '*24,
        drop_whitespace = True,
        break_long_words = False,
        break_on_hyphens = False,
        replace_whitespace = False
    )

    @staticmethod
    def set_alert_source(os_path_dirname,os_path_basename):
        """Use to generate the alert source for files"""
        set_dir = str(os_path_dirname.lower().split("\\")[-1]) + "-"
        if set_dir == "scripts-":
            set_dir = ''
        result = f"{set_dir}{os_path_basename}"
        return result

    @staticmethod
    def set_log_file(alert_source):
        """Use to generate the file path for log files"""
        base_name = alert_source.split(".",1)[0]
        log_file = rf"C:\AppSec\logs\{BACKUP_DATE}-{base_name}.log"
        return log_file

    @staticmethod
    def set_exceptions_log_file(alert_source):
        """Use to generate the file path for exceptions log files"""
        base_name = alert_source.split(".",1)[0]
        log_file = rf"C:\AppSec\logs\{BACKUP_DATE}-{base_name}_exceptions.log"
        return log_file

    @staticmethod
    def exception_headline(headline):
        """Formats the exception log headlines"""
        new_headline = ">"*(math.floor((75-len(headline))/2) - 2) + "  " + str(headline) + "  "
        new_headline += "<"*(math.ceil((75-len(headline))/2) - 2) + "\n"
        return new_headline

    @staticmethod
    def setup_logging(log_file,log_level=logging.INFO):
        """Sets up logging with exceptions logged to a separate file"""
        logging.getLogger(log_file).propagate=False
        log = logging.getLogger(log_file)
        for hdlr in log.handlers[:]:
            log.removeHandler(hdlr)
        fmt = logging.Formatter('%(asctime)s     %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        p_fmt = logging.Formatter(None,None)
        TheLogs.logs = logging.getLogger('logs')
        log_handler = logging.FileHandler(log_file,delay=True)
        log_handler.setLevel(log_level)
        log_handler.addFilter(LogFilter(log_level))
        log_handler.setFormatter(fmt)
        log.setLevel(log_level)
        log.addHandler(log_handler)
        logging.disable(level=logging.DEBUG)
        return log

    @staticmethod
    def log_headline(headline,level,symbol,main_log):
        """Formats the normal log headlines"""
        if symbol is not None:
            log_headline = " "*5*(level-1)+f"{symbol}"*3+f"  {headline}  "+f"{symbol}"*3
        else:
            log_headline = " "*5*(level-1)+f"{headline}"
        main_log.info(log_headline)
        print(log_headline)

    @staticmethod
    def log_info(text,level,symbol,main_log):
        """Formats the normal log headlines"""
        if symbol is not None:
            log_text = " "*5*level+f"{symbol}  {text}"
        else:
            log_text = " "*5*level+f"{text}"
        main_log.info(log_text)
        print(log_text)

    @staticmethod
    def exception(custom_message,exception_code,exception_log,main_log,log_file,source_file=None,
                  parent_function=None,stack_trace=None,notes=None):
        """Formats generic exceptions"""
        end = "\n\n" + "-" * 150 + "\n\n"
        headline = f'EXCEPTION {exception_code} HAS OCCURRED'
        headline = TheLogs.exception_headline(headline)
        message = f"{headline}"
        if source_file is not None:
            message += f"\nSource File:\n{source_file}\n"
        if parent_function is not None:
            message += f"\nParent Function:\n{parent_function}\n"
        if custom_message is not None:
            message += f"\nMessage:\n{custom_message}\n"
        if notes is not None:
            message += f"\nNotes:\n{notes}\n"
        if stack_trace is not None and not stack_trace.startswith('NoneType: None'):
            message += f"\nStack Trace:\n{stack_trace}\n"
        message += f"{end}"
        exception_log.info(message)
        main_message = f"{headline}" + " " * 24 + f"Check log: {log_file}"
        main_log.info(main_message)
        print(main_message)

    @staticmethod
    def sql_exception(sql,exception_code,exception_details,exception_log,main_log,log_file,
                      source_file=None,parent_function=None,stack_trace=None,notes=None):
        """Formats SQL exceptions"""
        end = "\n\n" + "-" * 150 + "\n\n"
        headline = f'SQL EXCEPTION {exception_code} HAS OCCURRED'
        headline = TheLogs.exception_headline(headline)
        message = f"{headline}"
        if source_file is not None:
            message += f"\nSource File:\n{source_file}\n"
        if parent_function is not None:
            message += f"\nParent Function:\n{parent_function}\n"
        if sql is not None:
            message += f"\nQuery Attempted:\n{sql}\n"
        if exception_details is not None:
            message += f"\nException Details:\n{exception_details}\n"
        if notes is not None:
            message += f"\nNotes:\n{notes}\n"
        if stack_trace is not None and not stack_trace.startswith('NoneType: None'):
            message += f"\nStack Trace:\n{stack_trace}\n"
        message += f"{end}"
        exception_log.info(message)
        main_message = f"{headline}" + " " * 24 + f"Check log: {log_file}"
        main_log.info(main_message)
        print(main_message)

    @staticmethod
    def function_exception(function,exception_code,exception_details,exception_log,main_log,
                           log_file,source_file=None,parent_function=None,stack_trace=None,
                           notes=None):
        """Formats function exceptions"""
        end = "\n\n" + "-" * 150 + "\n\n"
        headline = f'FUNCTION EXCEPTION {exception_code} HAS OCCURRED'
        headline = TheLogs.exception_headline(headline)
        message = f"{headline}"
        if source_file is not None:
            message += f"\nSource File:\n{source_file}\n"
        if parent_function is not None:
            message += f"\nParent Function:\n{parent_function}\n"
        if function is not None:
            message += f"\nFunction Attempted:\n{function}\n"
        if exception_details is not None:
            message += f"\nException Details:\n{exception_details}\n"
        if notes is not None:
            message += f"\nNotes:\n{notes}\n"
        if stack_trace is not None and not stack_trace.startswith('NoneType: None'):
            message += f"\nStack Trace:\n{stack_trace}\n"
        message += f"{end}"
        exception_log.info(message)
        main_message = f"{headline}" + " " * 24 + f"Check log: {log_file}"
        main_log.info(main_message)
        print(main_message)

    @staticmethod
    def process_exceptions(exception_array,alert_source,slack_url,alert_id,log_file,
                           manual_message=None):
        """Processes exceptions thrown"""
        processed = 0
        if (((isinstance(exception_array,list) and exception_array != []) or
             (isinstance(exception_array,dict) and exception_array != {})) and
             slack_url is not None and alert_id is not None and isinstance(alert_id,int)):
            if isinstance(exception_array,list):
                exception_array = sorted(set(exception_array))
            exception_count = len(exception_array)
            processed = Alerts.manual_alert(alert_source=alert_source,array=exception_array,
                                            i_count=exception_count,alert_id=alert_id,
                                            slack_url=slack_url,log_file=log_file,
                                            manual_message=manual_message)
        return processed

    @staticmethod
    def process_exception_count_only(exception_count,alert_id,alert_source,slack_url,log_file,
                                     manual_message=None):
        '''Sends an alert if exceptions were thrown during the script run'''
        processed = 0
        if (exception_count > 0 and alert_id is not None and isinstance(alert_id,int)
            and slack_url is not None):
            processed = Alerts.manual_alert(alert_source=alert_source,array=[],
                                            i_count=exception_count,alert_id=alert_id,
                                            slack_url=slack_url,log_file=log_file,
                                            manual_message=manual_message,
                                            exception_count=exception_count)
        return processed
