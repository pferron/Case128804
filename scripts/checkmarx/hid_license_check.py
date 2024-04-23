'''Runs a function that checks for Checkmarx License Hardware ID (HID) mismatch'''

import os
import sys
import inspect
from dotenv import load_dotenv
from slack_sdk.webhook import WebhookClient
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.logging import TheLogs
from common.miscellaneous import Misc

load_dotenv()
parent = os.path.abspath('.')
sys.path.insert(1,parent)
ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\checkmarx-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\checkmarx-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_CX')

class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")

def checkmarx_license_check(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''runs all functions for license HID check'''
    success = True
    TheLogs.log_headline('CHECKING CHECKMARX HID LICENSE MISMATCH',2,"#",main_log)
    hid_number = read_hid_file(main_log,ex_log,ex_file)
    lic_number = read_license_file(main_log,ex_log,ex_file)
    hid_compare = lic_hid_compare(hid_number,lic_number,main_log,ex_log,ex_file)
    if not hid_compare:
        hid_mismatch_slack_send(hid_number,lic_number,main_log,ex_log,ex_file)
    TheLogs.log_headline('END CHECKING CHECKMARX HID LICENSE MISMATCH',2,"#",main_log)
    if ScrVar.fe_cnt > 0:
        success = False
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Success':success}

def read_hid_file(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''opens and extracts HID from the Checkmarx hardware ID file'''
    #contents of HardwareId.txt example '#2962603912311611063739_0000:0000:0000:0000:24576:64:10:10'
    file = 'C:/AppSec/checkmarx/HardwareId.txt'
    # file = 'C:/Users/john.mccutchen/Documents/Security-Local/Checkmarx/HID/HardwareId.txt'
    with open(file, encoding = 'utf8') as hid_file_contents:
        hid_string_file = str(hid_file_contents.read())
        hid_number = hid_string_file.split('_', maxsplit=1)[0]
        hid_number = ''.join(i for i in hid_number if i.isdigit())
        return hid_number

def read_license_file(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''opens and extracts HID from the Checkmarx hardware ID file'''
    # contents of license file, HID is the second item in comma separate list 'HID=#2962603912311611063739'
    file = 'C:/AppSec/checkmarx/License.cxl'
    # file = 'C:/Users/john.mccutchen/Documents/Security-Local/Checkmarx/Licenses/License.cxl'
    with open(file) as lic_file_contents:
        lic_string_file = str(lic_file_contents.read())
        lic_split = lic_string_file.split(',')[1]
        license_number = lic_split.split('=')[1]
        license_number = ''.join(i for i in license_number if i.isdigit())
        return license_number

def lic_hid_compare(hid_number,lic_number,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''compares HID found on server and Checkmarx license'''
    if hid_number == lic_number:
        TheLogs.log_info(f'Checkmarx license has the corrent HID, HID: {hid_number}, License HID: {lic_number}',2,"*",main_log)
        return True
    else:
        TheLogs.log_info(f'Checkmarx license HID does not match HID, HID: {hid_number}, License HID: {lic_number}',2,"*",main_log)
        return False

def hid_mismatch_slack_send(hid_number,lic_number,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''Slack message for Checkmarx Mismatch alert to appsec-cx-alerts channel'''
    webhook = WebhookClient(SLACK_URL)
    response = webhook.send(
			blocks = [
				{
					"type": "header",
					"text": {
						"type": "plain_text",
						"text": ":alert: Checkmarx License no longer matches HID :alert:",
					}
				},
				{
					"type": "section",
					"fields": [
						{
							"type": "mrkdwn",
							"text": f"*HID:*\n {hid_number}"
						},
						{
							"type": "mrkdwn",
							"text": f"*License HID:*\n {lic_number}"
						}
					]
				},
				{
					"type": "context",
					"elements": [
						{
							"type": "mrkdwn",
							"text": "Reach out to Checkmarx CSM ASAP to get a new license. Provide new HID above. \n\nOnce a new license is received <https://progfin.atlassian.net/wiki/spaces/IS/pages/2659123260/Importing+New+License|follow these instructions>"
						}
					]
				}
			]
        )
    if response.status_code == 200:
        TheLogs.log_info('SLACK MESSAGE SENT FOR HID MISMATCH',2,"*",main_log)
    elif response.status_code == 400:
        function='hid_mismatch_slack_send()'
        code = 'HLC-HMSS-001'
        TheLogs.function_exception(function,code,'Unable to send Slack alert for Checkmarx HID mismatch',ex_log,main_log,ex_file)
        ScrVar.fe_cnt += 1
