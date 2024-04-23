"""Interacts with the Bitbucket API and performs various updates, as necessary"""

import os
import sys
import inspect
import traceback
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.logging import TheLogs
from common.miscellaneous import Misc
from common.constants import BITBUCKET_URL
from common.database_generic import DBQueries

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
BITBUCKET_KEY = os.environ.get('BITBUCKET_KEY')
BITBUCKET_HEADER = os.environ.get('BITBUCKET_HEADER')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0
    start_timer = None
    running_function = ''
    src = ALERT_SOURCE.replace("-","\\")
    u_cnt = 0
    a_repos = []

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

class BitBucket():
    """Provides general functions for interacting with BitBucket"""

    @staticmethod
    def update_bitbucket(url=BITBUCKET_URL,repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Updates BitBucket information in ApplicationAutomation"""
        ScrVar.running_function = inspect.stack()[0][3]
        ScrVar.timed_script_setup(main_log,ex_log,ex_file)
        table = 'ApplicationAutomation'
        headers = {
        "Accept": "application/json",
        "Authorization": BITBUCKET_HEADER
        }
        reset_table = 0
        if repo is not None:
            url = f'{BITBUCKET_URL}/2.0/repositories/progfin-ondemand/{repo}/?pagelen=100&fields=%2B*.*.*'
        elif repo is None and url == BITBUCKET_URL:
            url = f'{url}/2.0/repositories/progfin-ondemand?pagelen=100&fields=%2Bvalues.*.*.*'
            reset_table = 1
        url = url.replace("/?pagelen=100/","/")
        try:
            response = requests.get(url,headers=headers,timeout=60)
        except Exception as e_details:
            func = f"requests.get('{url}',headers={headers},timeout=60)"
            e_code = "BB-UB-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.fe_cnt += 1
            ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
            return {"FatalCount":ScrVar.fe_cnt,"ExceptionCount":ScrVar.ex_cnt,
                    "UpdatedRepos":ScrVar.u_cnt,"AddedRepos":ScrVar.a_repos}
        if response.status_code == 200:
            bitbucket_next_url = None
            values = []
            response = response.json()
            if repo is not None:
                item = response
                repo = None
                commit_date = None
                updated_date = None
                main_branch = None
                language = None
                if 'type' in item:
                    if item['type'] == 'repository':
                        if 'slug' in item:
                            repo = item['slug']
                        if 'language' in item:
                            language = item['language']
                        if 'updated_on' in item:
                            ud = str(item['updated_on'])
                            ud = ud.split(".",1)[0].replace("T"," ").split("+",1)[0]
                            ud = datetime.strptime(ud,"%Y-%m-%d %H:%M:%S")-timedelta(hours=7)
                            updated_date = ud
                        if 'mainbranch' in item:
                            if 'type' in item['mainbranch']:
                                if item['mainbranch']['type'] == 'branch':
                                    if 'name' in item['mainbranch']:
                                        main_branch = item['mainbranch']['name']
                            if ('target' in item['mainbranch'] and
                                'date' in item['mainbranch']['target']):
                                cd = str(item['mainbranch']['target']['date'])
                                cd = cd.split("+",1)[0].replace("T"," ")
                                cd = datetime.strptime(cd,"%Y-%m-%d %H:%M:%S")-timedelta(hours=7)
                                commit_date = cd
                    repo_exists = BitBucket.check_if_repo_exists(repo,main_log)
                    if repo_exists is True:
                        aa_update = [{'SET':{'BitbucketLastCommit':commit_date,
                                             'BitbucketLastUpdated':updated_date,
                                             'BitbucketMainBranch':main_branch,
                                             'BitbucketLanguage':language,
                                             'RepoInBitBucket':1},
                                      'WHERE_EQUAL':{'Repo':repo}}]
                        try:
                            ScrVar.u_cnt += DBQueries.update_multiple(table,aa_update,'AppSec',
                                                                         show_progress=False,
                                                                         update_to_null=False)
                        except Exception as e_details:
                            func = f"ScrVar.u_cnt += DBQueries.update_multiple('{table}',)"
                            func += f"{aa_update},'AppSec',show_progress=False,update_to_null=False)"
                            e_code = "BB-UB-005"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
                    else:
                        aa_insert = [{'Repo':repo,'RepoInBitBucket':1,
                                      'BitbucketLastCommit':commit_date,
                                      'BitbucketLastUpdated':updated_date,
                                      'BitbucketMainBranch':main_branch,
                                      'BitbucketLanguage':language}]
                        try:
                            DBQueries.insert_multiple(table,aa_insert,'AppSec',show_progress=False,
                                                      verify_on=['Repo'])
                            ScrVar.a_repos.append(repo)
                        except Exception as e_details:
                            func = f"DBQueries.insert_multiple('{table}',{aa_insert},'AppSec',"
                            func += "show_progress=False,verify_on=['Repo'])"
                            e_code = "BB-UB-006"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
            else:
                if 'values' in response:
                    values = response['values']
                if 'next' in response:
                    bitbucket_next_url = response['next']
                if values != [] and len(values) > 0:
                    if reset_table == 1:
                        success = BitBucket.reset_in_bitbucket_aa(main_log=main_log,ex_log=ex_log,
                                                                  ex_file=ex_file)
                        if success is False:
                            func = 'BitBucket.reset_in_bitbucket_aa()'
                            e_details = 'Function returned a False value instead of True.'
                            notes = 'The script was unable to globally update the '
                            notes += 'RepoInBitbucket to 0 ApplicationAutomation in order to ensure '
                            notes += 'that only those found in Bitbucket while running the script '
                            notes += 'are appropriately marked as 1. Try running the script again.'
                            e_code = 'BB-UB-002'
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                                        notes=notes)
                            ScrVar.fe_cnt += 1
                            ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
                            return {"FatalCount":ScrVar.fe_cnt,"ExceptionCount":
                                    ScrVar.ex_cnt,"UpdatedRepos":ScrVar.u_cnt,"AddedRepos":
                                    ScrVar.a_repos}
                    for item in values:
                        repo = None
                        commit_date = None
                        updated_date = None
                        main_branch = None
                        language = None
                        if 'type' in item:
                            if item['type'] == 'repository':
                                if 'slug' in item:
                                    repo = item['slug']
                                    print(" "*10+f"*  Processing updates for {repo}"+" "*100,end="\r")
                                if 'language' in item:
                                    language = item['language']
                                if 'updated_on' in item:
                                    ud = str(item['updated_on'])
                                    ud = ud.split(".",1)[0].replace("T"," ").split("+",1)[0]
                                    ud = datetime.strptime(ud,"%Y-%m-%d %H:%M:%S")-timedelta(hours=7)
                                    updated_date = ud
                                if 'mainbranch' in item:
                                    if 'type' in item['mainbranch']:
                                        if item['mainbranch']['type'] == 'branch':
                                            if 'name' in item['mainbranch']:
                                                main_branch = item['mainbranch']['name']
                                if ('target' in item['mainbranch'] and
                                    'date' in item['mainbranch']['target']):
                                    cd = str(item['mainbranch']['target']['date'])
                                    cd = cd.split("+",1)[0].replace("T"," ")
                                    cd = datetime.strptime(cd,"%Y-%m-%d %H:%M:%S")-timedelta(hours=7)
                                    commit_date = cd
                        if repo is not None:
                            repo_exists = BitBucket.check_if_repo_exists(repo,main_log)
                            if repo_exists is True:
                                aa_update = [{'SET':{'BitbucketLastCommit':commit_date,
                                                     'BitbucketLastUpdated':updated_date,
                                                     'BitbucketMainBranch':main_branch,
                                                     'BitbucketLanguage':language,
                                                     'RepoInBitBucket':1},
                                              'WHERE_EQUAL':{'Repo':repo}}]
                                try:
                                    ScrVar.u_cnt += DBQueries.update_multiple(table,aa_update,
                                                                                 'AppSec',
                                                                                 show_progress=False,
                                                                                 update_to_null=False)
                                except Exception as e_details:
                                    func = f"DBQueries.update_multiple('{table}',{aa_update},"
                                    func += "'AppSec',show_progress=False,update_to_null=False)"
                                    e_code = "BB-UB-003"
                                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                               main_log,ex_file,rf'{ScrVar.src}',
                                                               inspect.stack()[0][3],
                                                               traceback.format_exc())
                                    ScrVar.ex_cnt += 1
                            else:
                                aa_insert = [{'Repo':repo,'RepoInBitBucket':1,
                                              'BitbucketLastCommit':commit_date,
                                              'BitbucketLastUpdated':updated_date,
                                              'BitbucketMainBranch':main_branch,
                                              'BitbucketLanguage':language}]
                                try:
                                    DBQueries.insert_multiple(table,aa_insert,'AppSec',show_progress=False,
                                                              verify_on=['Repo'])
                                    ScrVar.a_repos.append(repo)
                                except Exception as e_details:
                                    func = f"DBQueries.insert_multiple('{table}',{aa_insert},"
                                    func += "'AppSec',verify_on=['Repo'],show_progress=False)"
                                    e_code = "BB-UB-004"
                                    TheLogs.function_exception(func,e_code,e_details,ex_log,
                                                               main_log,ex_file,rf'{ScrVar.src}',
                                                               inspect.stack()[0][3],
                                                               traceback.format_exc())
                                    ScrVar.ex_cnt += 1
            if bitbucket_next_url is not None:
                BitBucket.next_page_of_updates(bitbucket_next_url,main_log=main_log)
        else:
            func = f"requests.get('{url}', headers='{headers}',timeout=60)"
            e_code = "BB-UB-007"
            e_details = f"API returned a {response.status_code} reponse code. A 200 reponse code "
            e_details += "was expected."
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3])
            ScrVar.fe_cnt += 1
        ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
        return {"FatalCount":ScrVar.fe_cnt,"ExceptionCount":ScrVar.ex_cnt,"UpdatedRepos":
                ScrVar.u_cnt,"AddedRepos":ScrVar.a_repos}

    @staticmethod
    def reset_in_bitbucket_aa(repo=None,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Clears out the Bitbucket data in ApplicationAutomation so it will be reset'''
        success = False
        sql = """UPDATE ApplicationAutomation SET RepoInBitbucket = 0"""
        if repo is not None:
            sql = f"""UPDATE ApplicationAutomation SET RepoInBitbucket = 0 WHERE Repo = '{repo}'"""
        try:
            DBQueries.update(sql,'AppSec')
            success = True
        except Exception as e_details:
            e_code = "BB-RIBA-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
        return success

    @staticmethod
    def check_if_repo_exists(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        '''Checks if the repo exists'''
        exists = False
        sql = f"""SELECT TOP 1 Repo FROM ApplicationAutomation WHERE
        Repo = '{repo}'"""
        try:
            check_repo = DBQueries.select(sql,'AppSec')
        except Exception as e_details:
            e_code = "BB-CIRE-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return exists
        if check_repo != []:
            exists = True
        return exists

    @staticmethod
    def next_page_of_updates(url,main_log=LOG):
        '''Checks if the repo exists'''
        BitBucket.update_bitbucket(url=url,main_log=main_log)
