'''Unit tests for the bitbucket script in common'''

import unittest
from unittest import mock
import sys
import os
import pytest
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.bitbucket import *

@mock.patch('common.bitbucket.Misc.start_timer')
def tests_scrvar_timed_script_setup(st):
    """Tests ScrVar.timed_script_setup"""
    ScrVar.timed_script_setup()
    assert st.call_count == 1

@mock.patch('common.bitbucket.Misc.end_timer')
@mock.patch('common.bitbucket.TheLogs.process_exception_count_only')
def tests_scrvar_timed_script_teardown(peco,et):
    """Tests ScrVar.timed_script_teardown"""
    ScrVar.timed_script_teardown()
    assert peco.call_count == 2
    assert et.call_count == 1

@mock.patch('common.bitbucket.BitBucket.next_page_of_updates')
@mock.patch('common.bitbucket.BitBucket.reset_in_bitbucket_aa')
@mock.patch('common.bitbucket.DBQueries.insert_multiple')
@mock.patch('common.bitbucket.DBQueries.update_multiple')
@mock.patch('common.bitbucket.BitBucket.check_if_repo_exists')
@mock.patch('common.bitbucket.ScrVar.timed_script_teardown')
@mock.patch('common.bitbucket.TheLogs.function_exception')
@mock.patch('common.bitbucket.requests.get')
@mock.patch('common.bitbucket.ScrVar.timed_script_setup')
@pytest.mark.parametrize("description,req_get_se,req_get_sc,req_get_rv,ex_func_cnt,cire_rv,cire_cnt,um_se,um_rv,um_cnt,im_se,im_cnt,riba_rv,riba_cnt,npou_cnt,fe_cnt,ex_cnt,url,repo",
                         [('Exception: req_get',Exception,None,None,1,None,0,None,None,0,None,0,None,0,0,1,0,BITBUCKET_URL,None),
                          ('All expected values, repo = appsec-ops, cire = True',None,200,{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}},0,True,1,None,1,1,None,0,True,0,0,0,0,None,'appsec-ops'),
                          ('Exception: um, repo = appsec-ops, cire = True',None,200,{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}},1,True,1,Exception,1,1,None,0,True,0,0,0,1,None,'appsec-ops'),
                          ('All expected values, repo = appsec-ops, cire = False',None,200,{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}},0,False,1,None,None,0,None,1,True,0,0,0,0,None,'appsec-ops'),
                          ('Exception: im, repo = appsec-ops, cire = True',None,200,{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}},1,False,1,None,None,0,Exception,1,True,0,0,0,1,None,'appsec-ops'),
                          ('All expected values, repo = None, cire = True, no next in req_get_rv',None,200,{'values':[{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}}]},0,True,1,None,1,1,None,0,True,1,0,0,0,BITBUCKET_URL,None),
                          ('Exception: um, repo = None, cire = True, no next in req_get_rv',None,200,{'values':[{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}}]},1,True,1,Exception,None,1,None,0,True,1,0,0,1,BITBUCKET_URL,None),
                          ('riba returns False, repo = None, cire = True, no next in req_get_rv',None,200,{'values':[{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}}]},1,None,0,None,None,0,None,0,False,1,0,1,0,BITBUCKET_URL,None),
                          ('All expected values, repo = None, cire = False, no next in req_get_rv',None,200,{'values':[{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}}]},0,False,1,None,None,0,None,1,True,1,0,0,0,BITBUCKET_URL,None),
                          ('Exception: im, repo = None, cire = False, next in req_get_rv',None,200,{'next':'url','values':[{'type':'repository','slug':'appsec-ops','language':'language','updated_on':'2023-01-11T01:10:15+0:00','mainbranch':{'type':'branch','name':'master','target':{'date':'2023-11-01T20:10:15+0:00',}}}]},1,False,1,None,None,0,Exception,1,True,1,1,0,1,BITBUCKET_URL,None),
                          ('Exception: req_get status code',None,404,None,1,None,0,None,None,0,None,0,None,0,0,1,0,BITBUCKET_URL,None)])
def test_bitbucket_update_bitbucket(tss,req_get,ex_func,tst,cire,um,im,riba,npou,
                                    description,req_get_se,req_get_sc,req_get_rv,ex_func_cnt,
                                    cire_rv,cire_cnt,um_se,um_rv,um_cnt,im_se,im_cnt,riba_rv,
                                    riba_cnt,npou_cnt,fe_cnt,ex_cnt,url,repo):
    """Tests BitBucket.update_bitbucket"""
    if req_get_se is not None:
        req_get.side_effect = req_get_se
    else:
        req_get_mock = mock.Mock(side_effect=req_get_se)
        req_get_mock = mock.Mock(status_code=req_get_sc)
        req_get_mock.json.return_value = req_get_rv
        req_get.return_value = req_get_mock
    cire.return_value = cire_rv
    um.side_effect = um_se
    um.return_value = um_rv
    im.side_effect = im_se
    riba.return_value = riba_rv
    BitBucket.update_bitbucket(url=url,repo=repo)
    assert tss.call_count == 1
    assert req_get.call_count == 1
    assert ex_func.call_count == ex_func_cnt
    assert tst.call_count == 1
    assert cire.call_count == cire_cnt
    assert um.call_count == um_cnt
    assert im.call_count == im_cnt
    assert riba.call_count == riba_cnt
    assert npou.call_count == npou_cnt
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('common.bitbucket.TheLogs.sql_exception')
@mock.patch('common.bitbucket.DBQueries.update')
@pytest.mark.parametrize("description,sql_upd_se,ex_sql_cnt,response_rv,fe_cnt,ex_cnt,repo",
                         [('All expected values, repo = appsec-ops',None,0,True,0,0,'appsec-ops'),
                          ('All expected values, repo = None',None,0,True,0,0,None),
                          ('Exception: sql_upd',Exception,1,False,1,0,None)])
def test_bitbucket_reset_in_bitbucket_aa(sql_upd,ex_sql,
                                         description,sql_upd_se,ex_sql_cnt,response_rv,
                                         fe_cnt,ex_cnt,repo):
    """Tests BitBucket.reset_in_bitbucket_aa"""
    sql_upd.side_effect = sql_upd_se
    response = BitBucket.reset_in_bitbucket_aa(repo)
    assert sql_upd.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('common.bitbucket.TheLogs.sql_exception')
@mock.patch('common.bitbucket.DBQueries.select')
@pytest.mark.parametrize("description,sql_sel_se,sql_sel_rv,ex_sql_cnt,response_rv,fe_cnt,ex_cnt,repo",
                         [("All expected values, sql_sel_rv = [('appsec-ops',),]",None,[('appsec-ops',),],0,True,0,0,'appsec-ops'),
                         ("All expected values, sql_sel_rv = []",None,[],0,False,0,0,None),
                         ('Exception: sql_sel',Exception,None,1,False,0,1,'appsec-ops')])
def test_bitbucket_check_if_repo_exists(sql_sel,ex_sql,
                                        description,sql_sel_se,sql_sel_rv,ex_sql_cnt,response_rv,
                                        fe_cnt,ex_cnt,repo):
    """Tests BitBucket.check_if_repo_exists"""
    sql_sel.side_effect = sql_sel_se
    sql_sel.return_value = sql_sel_rv
    response = BitBucket.check_if_repo_exists(repo)
    assert sql_sel.call_count == 1
    assert ex_sql.call_count == ex_sql_cnt
    assert response == response_rv
    assert ScrVar.fe_cnt == fe_cnt
    assert ScrVar.ex_cnt == ex_cnt
    ScrVar.fe_cnt = 0
    ScrVar.ex_cnt = 0

@mock.patch('common.bitbucket.BitBucket.update_bitbucket')
def test_bitbucket_next_page_of_updates(ub):
    BitBucket.next_page_of_updates('url')
    assert ub.call_count == 1

if __name__ == '__main__':
    unittest.main()
