"""If a repo has just a baseline/pipeline in Checkmarx, this script will branch that project
to create the missing baseline/pipeline"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.alerts import Alerts
from common.bitbucket import BitBucket
from common.database_appsec import select
from common.logging import TheLogs
from checkmarx.api_connections import CxAPI

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar:
    """Script-wide stuff"""
    ex_cnt = 0
    fe_cnt = 0
    p_cnt = 0
    b_cnt = 0

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        if 'FatalCount' in dictionary:
            ScrVar.fe_cnt += dictionary['FatalCount']
        if 'ExceptionCount' in dictionary:
            ScrVar.ex_cnt += dictionary['ExceptionCount']

class CxCreate():
    """Provides functions required to ensure repos have both a baseline and pipeline project"""

    @staticmethod
    def run_all(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """For nightly maintenance, runs through all existing Checkmarx projects to check for ones
        are missing a baseline/pipeline project"""
        the_scans = []
        created_projs = []
        failed_to_create = []
        sql = """SELECT DISTINCT SASTProjects.Repo, SASTProjects.cxBaselineProjectId,
        SASTProjects.cxPipelineProjectId FROM SASTProjects INNER JOIN ApplicationAutomation ON
        ApplicationAutomation.Repo = SASTProjects.Repo WHERE (ApplicationAutomation.Retired = 0 OR
        ApplicationAutomation.Retired IS NULL) AND (ApplicationAutomation.ManualRetired = 0 OR
        ApplicationAutomation.ManualRetired IS NULL) AND (ApplicationAutomation.ProjectOnHold = 0
        OR ApplicationAutomation.ProjectOnHold IS NULL) AND (ApplicationAutomation.ExcludeScans = 0
        OR ApplicationAutomation.ExcludeScans IS NULL) AND ((SASTProjects.cxBaselineProjectId IS
        NULL OR SASTProjects.cxBaselineActive = 0) AND SASTProjects.cxPipelineProjectId IS NOT NULL
        AND SASTProjects.cxPipelineActive = 1) AND SASTProjects.Repo NOT IN (SELECT DISTINCT Repo
        FROM SASTProjects WHERE cxBaselineProjectId IS NOT NULL) ORDER BY Repo"""
        try:
            all_repos = select(sql)
        except Exception as details:
            e_code = "PC-RA-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt,
                    'PipelineCount': ScrVar.p_cnt, 'BaselineCount': ScrVar.b_cnt}
        if all_repos:
            total = 0
            updated = 0
            for item in all_repos:
                total += 1
            for item in all_repos:
                updated += 1
                print(f'Checking repo {updated} of {total}',end='\r')
                if item[1] is None and item[2] is not None:
                    created = CxCreate.baseline_create(item[0],item[2],main_log,ex_log,ex_file)
                    if created['ProjectCreated'] is True:
                        is_set = '*ARE NOT SET*'
                        if created['repo_is_set'] is True:
                            is_set = 'are set and initial scan has been requested'
                            the_scans.append(item[0])
                        msg = f"{item[0]} (Baseline) created - Repo and schedule {is_set}"
                        created_projs.append(msg)
        Alerts.manual_alert(rf'{ALERT_SOURCE}',created_projs,len(created_projs),28,SLACK_URL)
        TheLogs.log_info(f'{ScrVar.b_cnt} baseline project(s) created',2,"*",main_log)
        return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt,
                'Results':the_scans}

    @staticmethod
    def baseline_create(repo,pipeline_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks whether a repo has a pipeline project but no baseline project - if the baseline
        project is missing, kicks off the process to branch the pipeline/create the baseline
        project"""
        created = False
        repo_is_set = False
        TheLogs.log_info(f"Creating baseline project for {repo}",2,"+",main_log)
        try:
            create_baseline = CxAPI.branch_project(repo,pipeline_id,52)
        except Exception as details:
            func = f"CxAPI.branch_project('{repo}',{pipeline_id},52)"
            e_code = "PC-BC-001"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
            ScrVar.ex_cnt += 1
            return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
        if create_baseline is not None:
            ScrVar.b_cnt += 1
            try:
                team_set = CxAPI.set_project_team(repo,create_baseline,52)
            except Exception as details:
                func = f"CxAPI.set_project_team('{repo}',{create_baseline},52)"
                e_code = "PC-BC-002"
                TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
                ScrVar.ex_cnt += 1
                return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
            if team_set is True:
                try:
                    set_policy = CxAPI.set_policy(create_baseline)
                except Exception as details:
                    func = f"CxAPI.set_policy({create_baseline})"
                    e_code = "PC-BC-003"
                    TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
                    ScrVar.ex_cnt += 1
                    return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
                if set_policy is True:
                    created = True
                    bb_update = BitBucket.update_bitbucket(repo=repo,main_log=main_log)
                    ScrVar.update_exception_info(bb_update)
                    sql = f"""SELECT cicd_branch_override FROM ApplicationAutomation
                    WHERE RepoInBitbucket = 1 AND Repo = '{repo}'"""
                    try:
                        get_branch = select(sql)
                    except Exception as details:
                        e_code = "PC-BC-004"
                        TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
                        ScrVar.ex_cnt += 1
                        return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
                    if get_branch:
                        try:
                            if get_branch[0] is not None:
                                set_repo = CxAPI.set_repo(repo, create_baseline, get_branch[0])
                            else:
                                set_repo = CxAPI.set_repo(repo, create_baseline, 'master')
                        except Exception as details:
                            if get_branch[0] is not None:
                                func = f"CxAPI.set_repo('{repo}',{create_baseline},"
                                func += f"'{get_branch[0]}')"
                            else:
                                func = f"CxAPI.set_repo('{repo}',{create_baseline},"
                                func += "'master')"
                            e_code = "PC-BC-005"
                            TheLogs.function_exception(func,e_code,details,ex_log,main_log,
                                                        ex_file)
                            ScrVar.ex_cnt += 1
                            return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
                        if set_repo is True:
                            repo_is_set = True
                            comment = 'Inital scan.'
                            try:
                                launch_scan = CxAPI.launch_cx_scan(create_baseline,comment)
                            except Exception as details:
                                func = f"CxAPI.launch_cx_scan({create_baseline},'{comment}')"
                                e_code = "PC-BC-006"
                                TheLogs.function_exception(func,e_code,details,ex_log,main_log,
                                                            ex_file)
                                ScrVar.ex_cnt += 1
                                return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}
                            if launch_scan is True:
                                message = f'Inital scan requested for {repo} (Baseline)'
                                TheLogs.log_info(message,2, "*",main_log)
        return {'Repo':repo,'ProjectCreated':created,'repo_is_set':repo_is_set}

    # IN CASE WE EVER NEED TO AUTO-CREATE MISSING PIPELINES
    # @staticmethod
    # def pipeline_create(repo,baseline_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Checks whether a repo has a baseline project but no pipeline project - if the pipeline
    #     project is missing, kicks off the process to branch the baseline/create the pipeline
    #     project"""
    #     TheLogs.log_headline(f"CREATING PIPELINE PROJECT FOR {repo}",2,"#",main_log)
    #     try:
    #         create_pipeline = CxAPI.branch_project(repo,baseline_id,53)
    #     except Exception as details:
    #         func = f"CxAPI.branch_project('{repo}',{baseline_id},53)"
    #         e_code = "PC-PC-001"
    #         TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.ex_cnt += 1
    #         return
    #     if create_pipeline is not None:
    #         ScrVar.p_cnt += 1
    #         try:
    #             team_set = CxAPI.set_project_team(repo,create_pipeline,53)
    #         except Exception as details:
    #             func = f"CxAPI.set_project_team('{repo}',{create_pipeline},53)"
    #             e_code = "PC-PC-002"
    #             TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
    #             ScrVar.ex_cnt += 1
    #             return
    #         if team_set is True:
    #             try:
    #                 set_policy = CxAPI.set_policy(create_pipeline)
    #             except Exception as details:
    #                 func = f"CxAPI.set_policy({create_pipeline})"
    #                 e_code = "PC-PC-003"
    #                 TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
    #                 ScrVar.ex_cnt += 1
    #                 return
    #             if set_policy is True:
    #                 TheLogs.log_info(f'{repo} (Pipeline) project {create_pipeline} created',2,
    #                                     "*",main_log)
    #                 ScrVar.p_cnt += 1
