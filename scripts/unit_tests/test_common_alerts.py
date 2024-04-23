'''Unit tests for common\alerts.py'''

import unittest
from unittest import mock
import sys
import os
import pytest
from common.alerts import *
parent = os.path.abspath('.')
sys.path.insert(1,parent)

@mock.patch('common.database_generic.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_rv,response_rv,task_number",
                         [('sql_sel_rv = []',[],None,'TASK1234'),
                          ("sql_sel_rv = [('CN','SYS',),]",[('CN','SYS',),],'<https://progleasing.service-now.com/nav_to.do?uri=%2Fx_prole_software_c_software_change_request_table.do%3Fsys_id%3DSYS|CN>','TASK1234')])
def test_alerts_create_change_ticket_link_by_task(sql_sel,description,sql_sel_rv,response_rv,
                                                  task_number):
    """Tests Alerts.create_change_ticket_link_by_task"""
    sql_sel.return_value = sql_sel_rv
    response = Alerts.create_change_ticket_link_by_task(task_number)
    assert sql_sel.call_count == 1
    assert response == response_rv

@mock.patch('common.database_generic.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_rv,response_rv,change_ticket",
                         [('sql_sel_rv = []',[],None,'TASK1234'),
                          ("sql_sel_rv = [('SYS',),]",[('SYS',),],'<https://progleasing.service-now.com/nav_to.do?uri=%2Fx_prole_software_c_software_change_request_table.do%3Fsys_id%3DSYS|TKT>','TKT')])
def test_alerts_create_change_ticket_link(sql_sel,description,sql_sel_rv,response_rv,
                                          change_ticket):
    """Tests Alerts.create_change_ticket_link"""
    sql_sel.return_value = sql_sel_rv
    response = Alerts.create_change_ticket_link(change_ticket)
    assert sql_sel.call_count == 1
    assert response == response_rv

@mock.patch('common.alerts.Alerts.send_slack_alert')
@mock.patch('common.database_generic.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_rv,sql_sel_cnt,ssa_rv,ssa_cnt,alert_source,array,i_count,alert_id,slack_url,log_file,manual_message,is_conjur,column_layout",
                         [("Conjur = True, i_count = 1",None,0,1,1,"test_common_alerts.py",None,1,26,"slack_url","file.log","manual_message",True,'slack_headers:Header\\Header\nItem\\Item'),
                          ("Conjur = False, i_count = 2",[('icon','ats','atm','ams','amm','ass','asm','slf')],1,1,1,"test_common_alerts.py",['item',{'item2':True}],2,26,"slack_url","file.log","manual_message",False,'slack_headers:Header\\Header\nItem\\Item')])
def test_manual_alert(sql_sel,ssa,
                      description,sql_sel_rv,sql_sel_cnt,ssa_rv,ssa_cnt,alert_source,array,i_count,
                      alert_id,slack_url,log_file,manual_message,is_conjur,column_layout):
    """Tests Alerts.manual_alert"""
    sql_sel.return_value = sql_sel_rv
    ssa.return_value = ssa_rv
    response = Alerts.manual_alert(alert_source,array,i_count,alert_id,slack_url,log_file=log_file,
                                   manual_message=manual_message,is_conjur=is_conjur,column_layout=column_layout)
    assert sql_sel.call_count == sql_sel_cnt
    assert ssa.call_count == ssa_cnt
    assert response == ssa_rv

@mock.patch('common.alerts.dict_to_text')
@mock.patch('common.alerts.list_to_text')
@mock.patch('common.alerts.WebhookClient.send')
@pytest.mark.parametrize("description,whc_snd_sc,whc_snc_cnt,ltt_cnt,dtt_cnt,title,alert_source,alert_message,manual_message,alert_subtext,array,exception_count,log_file,show_log_file,slack_url,column_layout,response_rv",
                         [("log_file = None, slack_url = None",None,0,0,0,'title','alert_source','alert_message','manual_message','alert_subtext','array',1,None,1,None,None,0),
                          ("whc_snd failure",400,1,0,0,'title','alert_source','alert_message','manual_message','alert_subtext',[],1,'log_file',1,'slack_url',None,0),
                          ("whc_snd success, alert_source = None, array is a list",200,1,1,0,'title',None,'alert_message','manual_message','alert_subtext',['array'],1,'log_file',0,'slack_url',None,1),
                          ("whc_snd success, array is a dict",200,1,0,1,'title','alert_source','alert_message','manual_message','alert_subtext',{'key':'value'},1,'log_file',0,'slack_url','slack_headers:1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n1\\2\\3\\4\\5\n',1)])
def test_alerts_send_slack_alert(whc_snd,ltt,dtt,description,whc_snd_sc,whc_snc_cnt,ltt_cnt,dtt_cnt,title,
                          alert_source,alert_message,manual_message,alert_subtext,array,
                          exception_count,log_file,show_log_file,slack_url,column_layout,response_rv):
    """Tests Alerts.send_slack_alert"""
    # whc_snd.status_code = whc_snd_sc
    resp_mock = mock.Mock(status_code=whc_snd_sc)
    whc_snd.return_value = resp_mock
    response = Alerts.send_slack_alert(title=title,alert_source=alert_source,
                                       alert_message=alert_message,manual_message=manual_message,
                                       alert_subtext=alert_subtext,array=array,
                                       exception_count=exception_count,log_file=log_file,
                                       show_log_file=show_log_file,slack_url=slack_url,
                                       column_layout=column_layout)
    assert ltt.call_count == ltt_cnt
    assert dtt.call_count == dtt_cnt
    assert whc_snd.call_count == whc_snc_cnt
    assert response == response_rv

@mock.patch('common.alerts.dict_to_text')
@mock.patch('common.alerts.list_to_text')
@pytest.mark.parametrize("description,ltt_rv,ltt_cnt,dtt_rv,dtt_cnt,item_list,response_rv",
                         [("item_list is a flat list",None,0,None,0,['item'],"\n>  item "),
                          ("item_list is empty",None,0,None,0,[],None),
                          ("item_list is a list with a nested list","\n>  item ",1,None,0,['item',['item']],"\n>  item \n>  item "),
                          ("item_list is a list with a nested dict",None,0,"\n*key:*  value\n \n>  *key2:*  value2 ",1,['item',{'key':'value','key2':'value2'}],"\n>  item  \n \n*key:*  value\n \n>  *key2:*  value2 ")])
def test_list_to_text(ltt,dtt,description,ltt_rv,ltt_cnt,dtt_rv,dtt_cnt,item_list,response_rv):
    """Tests list_to_text"""
    ltt.return_value = ltt_rv
    dtt.return_value = dtt_rv
    response = list_to_text(item_list=item_list)
    assert ltt.call_count == ltt_cnt
    assert dtt.call_count == dtt_cnt
    assert response == response_rv

@mock.patch('common.alerts.dict_to_text')
@mock.patch('common.alerts.list_to_text')
@pytest.mark.parametrize("description,ltt_rv,ltt_cnt,dtt_rv,dtt_cnt,item_dict,is_nested,response_rv",
                         [("item_dict is a dict with a nested list, is_nested = False","\n>  item ",1,None,0,{'key':'value','key2':['item']},False,"\n*key:*  value\n \n>  *key2:*\n>  item  "),
                          ("item_dict is a dict with a flat nested dict, is_nested = False",None,0,"\n>  *key:*  value \n>  *key2:*  value2 ",1,{'key':'value','key2':{'key':'value','key2':'value2'}},False,"\n*key:*  value\n \n>  *key2:*\n>  *key:*  value \n>  *key2:*  value2  "),
                          ("item_dict is a dict with a nested dict with a nested dict with a nested dict, is_nested = False",None,0,"\n>  *key:*  value \n>  *key2:*  \n>  {'key3':['item']} ",2,{'key':'value','key2':{'key':'value','key2':{'key3':['item']}}},False,"\n*key:*  value\n \n>  *key2:*\n>  *key:*value\n>  *key2:*\n>  *key:*  value \n>  *key2:*  \n>  {'key3':['item']}  "),
                          ("item_dict is a flat dict, is_nested = True",None,0,None,0,{'key':'value','key2':'value2'},True,"\n>  *key:*  value \n>  *key2:*  value2 ")])
def test_dict_to_text(ltt,dtt,description,ltt_rv,ltt_cnt,dtt_rv,dtt_cnt,item_dict,is_nested,
                      response_rv):
    """Tests dict_to_text"""
    ltt.return_value = ltt_rv
    dtt.return_value = dtt_rv
    response = dict_to_text(item_dict=item_dict,is_nested=is_nested)
    assert ltt.call_count == ltt_cnt
    assert dtt.call_count == dtt_cnt
    assert response == response_rv

if __name__ == '__main__':
    unittest.main()
