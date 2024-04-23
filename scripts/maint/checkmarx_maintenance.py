"""Functions for maintenance_checkmarx"""

import os
import traceback
import inspect
from datetime import datetime
from dotenv import load_dotenv
from common.logging import TheLogs
from checkmarx.api_connections import CxAPI
from maint.checkmarx_database_queries import CxASDatabase
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
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = 0
        exception_count = 0
        if 'FatalCount' in dictionary:
            fatal_count = dictionary['FatalCount']
        if 'ExceptionCount' in dictionary:
            exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

class CxMaint():
    """"For database interaction"""

    @staticmethod
    def base_sastprojects_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds new baseline and pipeline project numbers to SASTProjects"""
        ScrVar.reset_exception_counts()
        reset_active = CxASDatabase.set_all_sastprojects_inactive(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(reset_active)
        if reset_active['FatalCount'] > 0:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':False}
        update_sastprojects_by_project_type('baseline',main_log,ex_log,ex_file)
        update_sastprojects_by_project_type('pipeline',main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':True}

    @staticmethod
    def update_sastprojects_details(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates the data columns in SASTProjects"""
        ScrVar.reset_exception_counts()
        update_project_data_sastprojects('baseline',main_log,ex_log,ex_file)
        update_project_data_sastprojects('pipeline',main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def update_created_baseline_projects(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds new baseline and pipeline project numbers to SASTProjects"""
        ScrVar.reset_exception_counts()
        reset_active = CxASDatabase.set_all_sastprojects_inactive(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(reset_active)
        if reset_active['FatalCount'] > 0:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':False}
        update_sastprojects_by_project_type('baseline',main_log,ex_log,ex_file)
        update_project_data_sastprojects('baseline',main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':True}

    @staticmethod
    def update_baseline_projects(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates Checkmarx Baseline projects in ApplicationAutomation & Applications"""
        ScrVar.reset_exception_counts()
        projects = CxASDatabase.get_baselines_from_sastprojects(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(projects)
        projects = projects['Results']
        if projects != [] and projects is not None:
            update_appsec_data_table('ApplicationAutomation',projects,main_log,ex_log,ex_file)
            update_appsec_data_table('Applications',projects,main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def update_project_details(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates the cxBaselineProjectDetails table in the AppSec database"""
        ScrVar.reset_exception_counts()
        u_cnt = 0
        i_cnt = 0
        processed = 0
        TheLogs.log_headline(f'UPDATING DATA FOR ALL AVAILABLE PROJECTS',2,"#",main_log)
        explainer = 'Note that repos whose projects have been deleted will be left in the '
        explainer += 'cxBaselineProjectDetails in case their data is needed for future reference.'
        TheLogs.log_info(explainer,2,None,main_log)
        projects = CxASDatabase.get_baselines_from_sastprojects(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(projects)
        projects = projects['Results']
        if projects != []:
            total = len(projects)
            for project in projects:
                processed += 1
                print(f'          *  Processing {processed} of {total}',end='\r')
                u_proj = update_cxbaselineprojectdetails_for_project(project['cxProjectId'],main_log,ex_log,
                                                                  ex_file)
                u_cnt += u_proj['updated']
                i_cnt += u_proj['added']
        TheLogs.log_info(f'{u_cnt} project(s) updated',2,"*",main_log)
        TheLogs.log_info(f'{i_cnt} project(s) added',2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_project_data_sastprojects(project_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                                     ex_file=EX_LOG_FILE):
    '''Updates data for existing projects for the specified project type in SASTProjects'''
    u_cnt = 0
    processing = 0
    project_type = str(project_type).lower()
    p_label = str(project_type).capitalize()
    proj_label = f'cx{p_label}ProjectId'
    proj_name_label = f'cx{p_label}ProjectName'
    team_label = f'cx{p_label}TeamId'
    scan_label = f'Last{p_label}Scan'
    branch_label = f'{p_label}BranchedFrom'
    exists_label = f'{p_label}BranchedFromExists'
    TheLogs.log_headline(f'UPDATING {project_type.upper()} PROJECT DATA IN SASTProjects',2,"#",
                         main_log)
    project_list = CxASDatabase.sastprojects_to_update(project_type,main_log,ex_log,ex_file)
    ScrVar.update_exception_info(project_list)
    for item in project_list['Results']:
        repo_data = []
        processing += 1
        print(f"          *  Processing {processing} of {len(project_list['Results'])}",
              end="\r")
        p_data = CxAPI.get_project_data(item['cxProjectId'])
        ScrVar.update_exception_info(p_data)
        data = p_data['Results']
        if data is not None:
            repo_data = {'SET':{team_label:data['cxTeamId'],
                                proj_name_label:data['cxProjectName'],
                                scan_label:data['LastScanDate'],
                                branch_label:data['BranchedFrom'],
                                exists_label:data['BranchedFromExists'],
                                'CrossRepoBranching':data['CrossRepoBranching']},
                            'WHERE_EQUAL':{'Repo':item['Repo'],
                                           proj_label:data['cxProjectId']}}
            if project_type == 'baseline':
                is_repo_set = data['cxBaselineRepoSet']
                repo_data['SET']['cxBaselineRepoSet'] = is_repo_set
                if is_repo_set is False:
                    repo_data = [repo_data,{'SET':{scan_label:None},
                                            'WHERE_EQUAL':{'Repo':item['Repo'],
                                                           'cxBaselineRepoSet':0}}]
        try:
            u_cnt += DBQueries.update_multiple('SASTProjects',repo_data,'AppSec',
                                               show_progress=False)
        except Exception as e_details:
            func = f"DBQueries.update_multiple('SASTProjects',{repo_data},'AppSec',"
            func += "show_progress=False)"
            e_code = "CXM-UPDS-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.ex_cnt += 1
    TheLogs.log_info(f'{u_cnt} {project_type} project(s) updated',2,'*',main_log)

def update_sastprojects_by_project_type(project_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                                        ex_file=EX_LOG_FILE):
    """Updates SASTProjects for the specified project_type ('baseline' or 'pipeline' only)"""
    sp_i_cnt = 0
    sp_u_cnt = 0
    team = 52
    project_type = str(project_type).lower()
    p_label = str(project_type).capitalize()
    proj_label = f'cx{p_label}ProjectId'
    proj_active = f'cx{p_label}Active'
    team_label = f'cx{p_label}TeamId'
    projects = None
    if project_type.lower() == 'pipeline':
        team = 53
    TheLogs.log_headline(f'UPDATING CHECKMARX {project_type.upper()} PROJECTS IN SASTProjects',2,
                         "#",main_log)
    try:
        projects = CxAPI.get_checkmarx_projects(team,main_log,ex_log,ex_file)
    except Exception as e_details:
        func = f"CxAPI.get_checkmarx_projects({team})"
        e_code = "CXM-USBPT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
    if projects != [] and projects is not None:
        processing = 0
        for proj in projects:
            processing += 1
            print(f"          *  Processing {processing} of {len(projects)}",end="\r")
            repo = str(proj['repo']).split(" ",1)[0]
            p_id = proj['id']
            ins_sp = [{'Repo':repo,proj_label:p_id,proj_active:1,team_label:team}]
            upd_sp = [{'SET':{proj_label:p_id,proj_active:1,team_label:team},
                        'WHERE_EQUAL':{'Repo':repo,proj_label:p_id},
                        'WHERE_OR_VALUES_AND':{'Repo':repo,proj_label:None}}]
            try:
                sp_u_cnt += DBQueries.update_multiple('SASTProjects',upd_sp,'AppSec',
                                                      show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.update_multiple('SASTProjects',{upd_sp},'AppSec',"
                func += "show_progress=False)"
                e_code = "CXM-USBPT-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                ScrVar.ex_cnt += 1
            try:
                use_custom_filter = f"OR (Repo = '{repo}' AND {proj_label} IS NULL)"
                sp_i_cnt += DBQueries.insert_multiple('SASTProjects',ins_sp,'AppSec',
                                    verify_on=['Repo',proj_label],
                                    custom_filter=use_custom_filter,show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('SASTProjects',{ins_sp},'AppSec',verify_on="
                func += f"['Repo',{proj_label}],custom_filter={use_custom_filter},show_progress=False"
                e_code = "CXM-USBPT-003"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                ScrVar.ex_cnt += 1
    TheLogs.log_info(f'{p_label} projects updated for {sp_u_cnt} repos',2,'*',main_log)
    TheLogs.log_info(f'{sp_i_cnt} repos added with {project_type} project ID only',2,'*',main_log)

def update_appsec_data_table(table,projects,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the specified AppSec data table ('ApplicationAutomation' or 'Applications' only) with
    Checkmarx project information"""
    u_cnt = 0
    a_cnt = 0
    ins_repos = []
    upd_repos = []
    proj_id = 'cxProjectID'
    proj_active = 'SASTActive'
    team_label = 'cxTeam'
    ls_date_label = 'cxLastScanDate'
    if table == 'Applications':
        proj_id = 'cxProjectID'
        proj_active = 'CxActive'
        team_label = 'CxTeam'
        ls_date_label = 'LastSASTScanDate'
    TheLogs.log_headline(f'UPDATING CHECKMARX BASELINE PROJECTS IN {table}',2,"#",
                            main_log)
    clear_entries = {'Results':False}
    if table == 'ApplicationAutomation':
        clear_entries = CxASDatabase.clear_checkmarx_data_from_aa(main_log,ex_log,ex_file)
        ScrVar.update_exception_info(clear_entries)
    elif table == 'Applications':
        clear_entries = CxASDatabase.clear_checkmarx_data_from_applications(main_log,ex_log,
                                                                            ex_file)
        ScrVar.update_exception_info(clear_entries)
    if clear_entries['Results'] is True:
        for proj in projects:
            ins_repo = {'Repo':proj['Repo'],proj_id:proj['cxProjectId'],
                        proj_active:proj['cxActive'],team_label:proj['cxTeam'],
                        ls_date_label:proj['cxLastScanDate']}
            upd_repo = {'SET':{proj_id:proj['cxProjectId'],proj_active:proj['cxActive'],
                               team_label:proj['cxTeam'],ls_date_label:proj['cxLastScanDate']},
                        'WHERE_EQUAL':{'Repo':proj['Repo']}}
            if table == 'Applications':
                ins_repo['CxProjectName'] = proj['CxProjectName']
                upd_repo['CxProjectName'] = proj['CxProjectName']
            ins_repos.append(ins_repo)
            upd_repos.append(upd_repo)
    try:
        u_cnt += DBQueries.update_multiple(table,upd_repos,'AppSec',2)
    except Exception as e_details:
        func = f"DBQueries.update_multiple({table},{upd_repos},'AppSec',2)"
        e_code = "CXM-UADT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f'{u_cnt} existing line item(s) updated',2,'*',main_log)
    try:
        a_cnt += DBQueries.insert_multiple(table,ins_repos,'AppSec',level=2,verify_on=['Repo'])
    except Exception as e_details:
        func = f"DBQueries.insert_multiple({table},{ins_repos},'AppSec',level=2,"
        func += "verify_on=['Repo'])"
        e_code = "CXM-UADT-002"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f'{a_cnt} new line item(s) added',2,'*',main_log)

def update_cxbaselineprojectdetails_for_project(project_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                                                ex_file=EX_LOG_FILE):
    """Updates the specified repo's data in cxBaselineProjectDetails"""
    updated = 0
    added = 0
    data = CxAPI.get_project_details(project_id)
    if data != {}:
        try:
            added += DBQueries.insert_multiple('cxBaselineProjectDetails',data,'AppSec',level=2,
                                                verify_on=['Repo'])
        except Exception as e_details:
            func = f"DBQueries.insert_multiple('cxBaselineProjectDetails,{data},'AppSec',level=2,"
            func+= f"verify_on=['Repo']"
            e_code = "CXM-UCFP-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'updated':updated,'added':added}
        if added == 0:
            update_project = {'SET':{'LastDataSync':data['LastDataSync'],
                                     'cxProjectName':data['cxProjectName'],
                                     'cxRelatedProjects':data['cxRelatedProjects'],
                                     'branchScanned':data['branchScanned'],
                                     'cxLastScanId':data['cxLastScanId'],
                                     'cxScannedDate':data['cxScannedDate'],
                                     'cxFilesCount':data['cxFilesCount'],
                                     'cxLinesOfCode':data['cxLinesOfCode'],
                                     'Apex':data['Apex'],'ASP':data['ASP'],'Cobol':data['Cobol'],
                                     'Common':data['Common'],'CPP':data['CPP'],
                                     'CSharp':data['CSharp'],'Dart':data['Dart'],'Go':data['Go'],
                                     'Groovy':data['Groovy'],'Java':data['Java'],
                                     'JavaScript':data['JavaScript'],'Kotlin':data['Kotlin'],
                                     'Objc':data['Objc'],'Perl':data['Perl'],'PHP':data['PHP'],
                                     'PLSQL':data['PLSQL'],'Python':data['Python'],
                                     'RPG':data['RPG'],'Ruby':data['Ruby'],'Scala':data['Scala'],
                                     'Swift':data['Swift'],'VB6':data['VB6'],'VbNet':data['VbNet'],
                                     'VbScript':data['VbScript'],'Unknown':data['Unknown']},
                              'WHERE_EQUAL':{'Repo':data['Repo']}}
            try:
                updated += DBQueries.update_multiple('cxBaselineProjectDetails',update_project,
                                                     'AppSec')
            except Exception as e_details:
                func = f"update_multiple_in_table('cxBaselineProjectDetails,{update_project},"
                func += "'AppSec')"
                e_code = "CXM-UCFP-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                ScrVar.ex_cnt += 1
                return {'updated':updated,'added':added}
    return {'updated':updated,'added':added}