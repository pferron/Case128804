"""This file contains generic functions that are commonly used in other scripts"""

import json
from datetime import datetime
from slack_sdk.webhook import WebhookClient

class Alerts:
    """Functions for creating Slack Alerts"""

    @staticmethod
    def create_change_ticket_link_by_task(task_number):
        """Creates the change ticket link for Slack messages"""
        ch_lnk = None
        from common.database_generic import DBQueries
        sql = f"""SELECT snChangeRecords.snChangeNumber, snChangeRecords.snSysID from
        snChangeRecords JOIN snTaskRecords on snTaskRecords.snChangeRequest =
        snChangeRecords.snChangeNumber WHERE snTaskRecords.snTaskNumber ='{task_number}'"""
        query_response = DBQueries.select(sql,'AppSec')
        if query_response:
            change_ticket = query_response[0][0]
            sn_sys_id = query_response[0][1]
            ch_lnk = "<https://progleasing.service-now.com/nav_to.do?uri=%2Fx_prole_software_c_"
            ch_lnk += f"software_change_request_table.do%3Fsys_id%3D{sn_sys_id}|"
            ch_lnk += f"{change_ticket}>"
        return ch_lnk

    @staticmethod
    def create_change_ticket_link(change_ticket):
        """Creates the change ticket link for Slack messages"""
        ch_lnk = None
        from common.database_generic import DBQueries
        sql = f"""SELECT snChangeRecords.snSysID from snChangeRecords JOIN snTaskRecords on
        snTaskRecords.snChangeRequest = snChangeRecords.snChangeNumber WHERE
        snChangeRecords.snChangeNumber ='{change_ticket}'"""
        query_response = DBQueries.select(sql,'AppSec')
        if query_response:
            sn_sys_id = query_response[0][0]
            ch_lnk = "<https://progleasing.service-now.com/nav_to.do?uri=%2Fx_prole_software_c_"
            ch_lnk += f"software_change_request_table.do%3Fsys_id%3D{sn_sys_id}|"
            ch_lnk += f"{change_ticket}>"
        return ch_lnk

    @staticmethod
    def manual_alert(alert_source,array,i_count,alert_id,slack_url,
                     log_file=None,manual_message=None,is_conjur=False,column_layout=None,
                     exception_count=0):
        """Used to create alerts on the fly"""
        alerts_processed = 0
        # Values for Conjur alerts since their failure means you cannot get them from the database
        a_type = [('alert','Critical Conjur Alert','Critical Conjur Alerts',
                   'Conjur failed to retrieve secrets.','Conjur failed to retrieve secrets.',None,
                   None,0)]
        sql = """SELECT alert_icon, alert_title_single, alert_title_multiple, alert_message_single,
            alert_message_multiple, alert_subtext_single, alert_subtext_multiple, show_log_file
            FROM slackAlerts WHERE ID = '""" + str(alert_id) + """'"""
        if is_conjur is False:
            from common.database_generic import DBQueries
            a_type = DBQueries.select(sql,'AppSec')
        if a_type != []:
            show_log_file = 1
            title = None
            alert_message = None
            alert_subtext = None
            if a_type[0][7] is None or a_type[0][7] == 'None' or a_type[0][7] == 0:
                show_log_file = 0
            if a_type[0][1] is not None and a_type[0][1] != 'None':
                title = a_type[0][1]
                if a_type[0][1] is not None and a_type[0][1] != 'None':
                    title = f':{a_type[0][0]}:     {a_type[0][1]}     :{a_type[0][0]}:'
            if a_type[0][3] is not None and a_type[0][3] != 'None':
                alert_message = a_type[0][3].replace('`','```').replace('``````','```').replace('\\n','\n ')
            if a_type[0][5] is not None and a_type[0][5] != 'None':
                alert_subtext = a_type[0][5].replace('`','```').replace('`````````','```').replace('\\n','\n ')
            if i_count > 1:
                if a_type[0][2] is not None and a_type[0][2] != 'None':
                    title = a_type[0][2]
                    if a_type[0][0] is not None and a_type[0][0] != 'None':
                        title = f':{a_type[0][0]}:     {a_type[0][2]}     :{a_type[0][0]}:'
                if a_type[0][4] is not None and a_type[0][4] != 'None':
                    alert_message = a_type[0][4].replace('`','```').replace('`````````','```').replace('\\\\','\\').replace('\\n',' \n ')
                if a_type[0][6] is not None and a_type[0][6] != 'None':
                    alert_subtext = a_type[0][6].replace('`','```').replace('`````````','```').replace('\\\\','\\').replace('\\n',' \n ')
            if i_count > 0:
                alerts_processed = Alerts.send_slack_alert(title=title,alert_source=alert_source,
                                        alert_message=alert_message,manual_message=manual_message,
                                        alert_subtext=alert_subtext,array=array,
                                        exception_count=exception_count,log_file=log_file,
                                        show_log_file=show_log_file,slack_url=slack_url,
                                        column_layout=column_layout)
        return alerts_processed

    @staticmethod
    def send_slack_alert(title=None,alert_source=None,alert_message=None,manual_message=None,
                         alert_subtext=None,array=[],exception_count=0,log_file=None,
                         show_log_file=0,slack_url=None,column_layout=None):
        """Sends a Slack alert based on the values included"""
        alerts_processed = 0
        exceptions = None
        file = None
        if isinstance(exception_count,int):
            exceptions = str("{:,}".format(exception_count))
        if show_log_file == 1:
            file = 'Not Provided'
            date = datetime.now().strftime("%Y-%m-%d")
            if log_file is None and alert_source is not None:
                file = f'{date}-'
                file += str(alert_source).replace(".py","_exceptions.log")
            elif log_file is not None:
                file = log_file.split('\\')[-1]
        if alert_source is None:
            alert_source = 'Not Provided'
        create_blocks = []
        if slack_url is not None:
            if title is not None and title != 'None' and title != '':
                create_blocks.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title
                        }
                })
            if alert_source is not None and alert_source != 'None' and alert_source != '':
                create_blocks.append({
                    "type": "divider"
                })
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f'*Source:*\n{alert_source}'
                        }
                    ]
                })
            if alert_message is not None and alert_message != 'None' and alert_message != '':
                create_blocks.append({
                    "type": "divider"
                })
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n{alert_message}"
                        }
                    ]
                })
            if isinstance(exception_count,int) and exception_count > 0:
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f">  *Exception Count:* {exceptions}"
                        }
                    ]
                })
            if manual_message is not None and manual_message != 'None':
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"{manual_message}"
                        }
                    ]
                })
            if column_layout is not None and column_layout != 'None' and column_layout != '':
                to_array = column_layout.split('\n')
                for item in to_array:
                    item_fields = []
                    if 'slack_headers:' in item.lower():
                        item = item.replace('slack_headers:','')
                        item = item.split("\\")
                        for field in item:
                            if field != '':
                                item_fields.append({
                                    "type": "mrkdwn",
                                    "text": f"*{field}:*"
                                })
                    else:
                        item = item.split("\\")
                        for field in item:
                            if field != '':
                                item_fields.append({
                                    "type": "mrkdwn",
                                    "text": f"{field}"
                                })
                    create_blocks.append(
                        {
                        "type": "section",
                        "fields": item_fields
                        })
            if isinstance(array,list) and array != []:
                item_output = list_to_text(array)
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": item_output
                        }
                    ]
                })
            if isinstance(array,dict) and array != {}:
                item_output = dict_to_text(array)
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": item_output
                        }
                    ]
                })
            if alert_subtext is not None and alert_subtext != 'None' and alert_subtext != '':
                create_blocks.append({
                    "type": "divider"
                })
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"{alert_subtext}"
                        }
                    ]
                })
            if show_log_file == 1:
                create_blocks.append({
                    "type": "divider"
                })
                create_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f'*Log File:*\n{file}'
                        }
                    ]
                })
            block_chunks = []
            if len(create_blocks) > 50:
                for i in range(0,len(create_blocks),50):
                    block_chunks.append(create_blocks[i:i + 50])
                for block in block_chunks:
                    response = WebhookClient(slack_url).send(
                        text = str(title),
                        blocks = block
                    )
                    if response.status_code == 200:
                        alerts_processed = 1
            else:
                response = WebhookClient(slack_url).send(
                    text = str(title),
                    blocks = create_blocks
                )
                if response.status_code == 200:
                    alerts_processed = 1
        return alerts_processed

def list_to_text(item_list):
    """Converts a list to Slack-formatted text"""
    item_text = ''
    for item in item_list:
        if not isinstance(item,list) and not isinstance(item,dict):
            item_text += f"\n>  {item} "
        elif isinstance(item,list) and item != []:
            item_text += list_to_text(item)
        elif isinstance(item,dict) and item != {}:
            item_text += ' \n ' + dict_to_text(item)
    if item_text == '':
        item_text = None
    return item_text

def dict_to_text(item_dict,is_nested=False):
    """Converts a dict to Slack-formatted text - the first key/value pair in a dictionary is
    returned as a 'subheader' in the Slack message"""
    keys = list(item_dict.keys())
    start_with = f'\n*{keys[0]}:*  {item_dict[keys[0]]}\n '
    if is_nested is True:
        start_with = f'\n>  *{keys[0]}:*  {item_dict[keys[0]]} '
    item_text = start_with
    k_cnt = 0
    for key in keys[1:]:
        k_cnt += 1
        if isinstance(item_dict[keys[k_cnt]],list):
            if item_dict[keys[k_cnt]] != []:
                get_list_text = list_to_text(item_dict[keys[k_cnt]])
                item_text += f'\n>  *{key}:*{get_list_text} '
        elif isinstance(item_dict[keys[k_cnt]],dict):
            if item_dict[keys[k_cnt]] != {}:
                get_list_text = dict_to_text(item_dict[keys[k_cnt]],True)
                if "{" in get_list_text:
                    to_add = ''
                    sl_dict = item_dict[keys[k_cnt]]
                    sl_keys = list(sl_dict.keys())
                    for sl_key in sl_keys:
                        if isinstance(sl_dict[sl_key],list):
                            get_list = list_to_text(sl_dict[sl_key])
                        elif isinstance(sl_dict[sl_key],dict):
                            get_list = dict_to_text(sl_dict[sl_key],True)
                        else:
                            get_list = sl_dict[sl_key]
                        to_add += f'\n>  *{sl_key}:*{get_list}'
                    get_list_text = to_add
                item_text += f'\n>  *{key}:*{get_list_text} '
        else:
            if item_dict[key] is not None and item_dict[key] != '':
                item_text += f'\n>  *{key}:*  {item_dict[key]} '
    return item_text
