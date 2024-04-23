"""Functions for maintenance_application_tables and database_appsec"""

import os
import traceback
import inspect
from datetime import datetime
from dotenv import load_dotenv
from common.logging import TheLogs
from common.database_generic import DBQueries

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0

class CxASDatabase():
    """"For database interaction"""

    @staticmethod
    def get_baselines_from_sastprojects(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns data from SASTProjects to update the Application and ApplicationAutomation
        tables"""
        r_data = []
        sql = """SELECT DISTINCT Repo, cxBaselineActive, cxBaselineProjectId, cxBaselineTeamId,
        cxBaselineProjectName, LastBaselineScan FROM SASTProjects
        WHERE cxBaselineProjectId IS NOT NULL AND cxBaselineActive = 1 ORDER BY Repo"""
        try:
            data = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-GBFS-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':r_data}
        if data != []:
            for item in data:
                r_data.append({'Repo':item[0],'cxActive':item[1],'cxProjectId':item[2],
                               'cxTeam':item[3],'CxProjectName':item[4],
                               'cxLastScanDate':item[5]})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':r_data}

    @staticmethod
    def set_all_sastprojects_inactive(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Resets all Baseline and Pipeline projects to inactive in SASTProjects"""
        sql = """UPDATE SASTProjects SET cxBaselineActive = 0, cxPipelineActive = 0"""
        try:
            DBQueries.update(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-SASI-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':False}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':True}

    @staticmethod
    def clear_checkmarx_data_from_aa(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Resets all Checkmarx info in ApplicationAutomation"""
        sql = """UPDATE ApplicationAutomation SET SASTActive = 0, cxProjectID = NULL,
        cxTeam = NULL"""
        try:
            DBQueries.update(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-CCDFAA-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':False}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':True}

    @staticmethod
    def get_repo_and_project_id(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the repo name and cxProjectID from ApplicationAutomation"""
        data = []
        if repo is None:
            sql = """SELECT DISTINCT Repo, cxProjectID FROM ApplicationAutomation
            WHERE cxProjectID IS NOT NULL AND cxLastScanDate >= DATEADD(hour,-12,GETDATE()) ORDER
            BY Repo"""
        else:
            sql = f"""SELECT DISTINCT Repo, cxProjectID FROM ApplicationAutomation
            WHERE cxProjectID IS NOT NULL AND Repo = '{repo}'"""
        try:
            results = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-GRAPI-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': data}

    @staticmethod
    def check_cross_repo(repo,project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the repo name and cxProjectID from ApplicationAutomation"""
        cross_repo = False
        sql = f"""SELECT DISTINCT Repo FROM SASTProjects WHERE (cxBaselineProjectId = {project_id}
        OR cxPipelineProjectId = {project_id}) AND Repo = '{repo}'"""
        try:
            results = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-CCR-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':cross_repo}
        cross_repo = True
        if results != []:
            cross_repo = False
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':cross_repo}

    @staticmethod
    def sastprojects_to_update(project_type,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the repo names and project IDs from SASTProjects for the specified project type
        ('baseline' or 'pipeline')"""
        project_type = project_type.lower()
        r_val = None
        if project_type == 'baseline':
            sql = """SELECT DISTINCT Repo, cxBaselineProjectId FROM SASTProjects
            WHERE cxBaselineProjectId IS NOT NULL ORDER BY Repo"""
        elif project_type == 'pipeline':
            sql = """SELECT DISTINCT Repo, cxPipelineProjectId FROM SASTProjects
            WHERE cxPipelineProjectId IS NOT NULL ORDER BY Repo"""
        else:
            e_code = 'MCDQ-STU-001'
            e_details = f"Specified project_type of {project_type} is not an option. "
            e_details += "Only 'baseline' and 'pipeline' are valid options for project_type."
            TheLogs.exception(e_details,e_code,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                              inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':r_val}
        try:
            results = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-STU-002'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':r_val}
        if results != []:
            r_val = []
            for item in results:
                r_val.append({'Repo':item[0],'cxProjectId':item[1]})
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':r_val}

    @staticmethod
    def get_results_to_confirm(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the repo name and cxProjectID from ApplicationAutomation"""
        data = []
        sql = f"""SELECT DISTINCT cxResultID FROM SASTFindings WHERE cxProjectID = {proj_id} AND
        cxResultState = 'To Verify' AND cxDetectionDate >= DATEADD(hour,-16,GETDATE())"""
        try:
            results = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-GRTC-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': data}
        for item in results:
            data.append({'Repo': item[0].split("-",1)[0], 'cxProjectID': item[0].split("-",1)[1]})
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': data}

    @staticmethod
    def clear_checkmarx_data_from_applications(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Resets all Checkmarx info in ApplicationAutomation"""
        sql = """UPDATE Applications SET CxActive = 0, CxProjectID = NULL, CxTeam = NULL"""
        try:
            DBQueries.update(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-CCDFA-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': False}
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': True}

    @staticmethod
    def clear_data_from_baselineprojectdetails(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Resets baseline Checkmarx info in cxBaselineProjectDetails"""
        if repo is None:
            sql = """DELETE FROM cxBaselineProjectDetails"""
        else:
            sql = f"""DELETE FROM cxBaselineProjectDetails WHERE Repo = '{repo}'"""
        try:
            DBQueries.delete_row(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-CDFB-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': False}
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': True}

    @staticmethod
    def clear_data_from_sastprojects(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Resets Checkmarx info in SASTProjects"""
        sql = """DELETE FROM SASTProjects"""
        try:
            DBQueries.delete_row(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-CDFS-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': False}
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': True}

    @staticmethod
    def get_active_repos(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets repos with active Checkmarx projects from ApplicationAutomation"""
        active_repos = []
        sql = """SELECT DISTINCT Repo FROM ApplicationAutomation WHERE cxProjectId IS NOT NULL
                AND (Retired IS NULL OR Retired = 0) ORDER BY Repo"""
        try:
            get_repos = DBQueries.select(sql,'AppSec')
        except Exception as details:
            e_code = "MCDQ-GAR-001"
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,
                    'Results': active_repos}
        if get_repos != []:
            for repo in get_repos:
                active_repos.append(repo[0])
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,
                'Results': active_repos}

    @staticmethod
    def update_branching_stats(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates BaselineBranchedFromExists, PipelineBranchedFromExists, and CrossRepoBranching
        in SASTFindings"""
        sql = """UPDATE SASTProjects SET BaselineBranchedFromExists = 1 WHERE BaselineBranchedFrom
        IS NOT NULL AND (BaselineBranchedFrom IN (SELECT DISTINCT cxPipelineProjectId FROM
        SASTProjects) OR BaselineBranchedFrom IN (SELECT DISTINCT cxBaselineProjectId FROM
        SASTProjects)) UPDATE SASTProjects SET BaselineBranchedFromExists = 0 WHERE
        BaselineBranchedFrom IS NOT NULL AND (BaselineBranchedFrom NOT IN (SELECT DISTINCT
        cxPipelineProjectId FROM SASTProjects) OR BaselineBranchedFrom NOT IN (SELECT DISTINCT
        cxBaselineProjectId FROM SASTProjects)) UPDATE SASTProjects SET
        PipelineBranchedFromExists = 0 WHERE PipelineBranchedFrom IS NOT NULL AND
        (PipelineBranchedFrom NOT IN (SELECT DISTINCT cxPipelineProjectId FROM SASTProjects WHERE
        cxPipelineProjectId IS NOT NULL) OR PipelineBranchedFrom NOT IN (SELECT DISTINCT
        cxBaselineProjectId FROM SASTProjects WHERE cxBaselineProjectId IS NOT NULL)) UPDATE
        SASTProjects SET PipelineBranchedFromExists = 1 WHERE PipelineBranchedFrom IS NOT NULL AND
        (PipelineBranchedFrom IN (SELECT DISTINCT cxPipelineProjectId FROM SASTProjects WHERE
        cxPipelineProjectId IS NOT NULL) OR PipelineBranchedFrom IN (SELECT DISTINCT
        cxBaselineProjectId FROM SASTProjects WHERE cxBaselineProjectId IS NOT NULL)) UPDATE
        SASTProjects SET CrossRepoBranching = 0 WHERE cxBaselineProjectId IS NOT NULL AND
        cxPipelineProjectId IS NOT NULL AND (BaselineBranchedFrom IS NOT NULL OR
        PipelineBranchedFrom IS NOT NULL) UPDATE SASTProjects SET CrossRepoBranching = 1 WHERE
        (BaselineBranchedFrom IS NOT NULL AND cxPipelineProjectId IS NOT NULL AND
        BaselineBranchedFrom != cxPipelineProjectId) OR (PipelineBranchedFrom IS NOT NULL AND
        cxBaselineProjectId IS NOT NULL AND PipelineBranchedFrom != cxBaselineProjectId)"""
        try:
            DBQueries.update(sql,'AppSec')
        except Exception as details:
            e_code = 'MCDQ-UBS-001'
            TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file,rf'{ALERT_SOURCE}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': False}
        return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': True}
