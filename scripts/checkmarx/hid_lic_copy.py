'''this file is to be used to troubleshoot copying a file from Checkmarx server to Automation server'''

import os
import sys
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
import inspect
import traceback
from datetime import datetime
from dotenv import load_dotenv
import smbclient.shutil
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.constants import CX_SERVER_USER
from common.logging import TheLogs
from common.miscellaneous import Misc

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
PASSWORD = os.environ.get('CX_SERVER_PASS')

class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

def copy_file(source,destination,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """function to copy file from remote server"""
    try:
        smbclient.shutil.copyfile(source,destination,username=CX_SERVER_USER,password=PASSWORD)
        TheLogs.log_info(f'File: {source} copied to {destination}',2,"*",LOG)
    except Exception as e_details:
        func = f"copy_file({source}, {destination})"
        e_code = "CX-HID-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return 'fail'
    return 'success'

def copy_from_cx_server(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''runs copy file function to copy current HID/LIC files to automation server'''
    is_copied = False
    lic_source = r'\\vdc-prdsecscn01\c$\Program Files\Checkmarx\Licenses\License.cxl'
    lic_destination = r'C:\AppSec\checkmarx\License.cxl'
    hid_source = r'\\vdc-prdsecscn01\c$\Program Files\Checkmarx\HID\HardwareId.txt'
    hid_destination = r'C:\AppSec\checkmarx\HardwareId.txt'
    TheLogs.log_headline('COPYING CHECKMARX HID AND LICENSE FILES TO AUTOMATION SERVER',2,"#",main_log)
    lic_file_copied = copy_file(lic_source,lic_destination)
    hid_file_copied = copy_file(hid_source,hid_destination)
    if lic_file_copied and hid_file_copied == 'success':
        TheLogs.log_headline('CHECKMARX HID AND LICENSE FILES COPIED SUCCESSFULLY',2,"#",main_log)
        is_copied = True
    else:
        TheLogs.log_headline('SOMETHING WENT WRONG COPYING CHECKMARX HID AND LICENSE FILES, CHECK EXCEPTIONS',2,"#",main_log)
        ScrVar.fe_cnt += 1
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'IsCopied':is_copied}
