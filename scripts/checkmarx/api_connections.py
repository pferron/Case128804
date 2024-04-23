"""Common functions for Checkmarx"""

import csv
from io import StringIO
import os
import requests
import sys
import time
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.constants import CX_USER, CX_BASE_URL
from datetime import datetime
from checkmarx.cx_common import CxCommon
from common.vuln_info import VulnDetails
from common.database_appsec import cx_select
from common.logging import TheLogs
from maint.checkmarx_database_queries import CxASDatabase

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
IGNORE_RESULTS = {'Info','Information','Low'}
CX_USER_KEY = os.environ.get('CX_USER_KEY')
CX_CLIENT_KEY = os.environ.get('CX_CLIENT_KEY')
BITBUCKET_HEADER = os.environ.get('BITBUCKET_HEADER')
BITBUCKET_REPO_URL = os.environ.get('BITBUCKET_REPO_URL')

class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    ex_cnt = 0

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

class CxAPI():
    """Connects to Checkmarx and the AppSec database to perform various tasks"""

    @staticmethod
    def checkmarx_connection():
        """Creates the connection to Checkmarx"""
        access_token = None
        url = f'{CX_BASE_URL}/cxrestapi/auth/identity/connect/token'
        payload = f"""username={CX_USER}&password={CX_USER_KEY}&grant_type=password"""
        payload += """&scope=management_and_orchestration_api sast_api&client_id="""
        payload += f"""management_and_orchestration_server&client_secret={CX_CLIENT_KEY}"""
        headers = {
            'Host': CX_BASE_URL.replace("https://",""),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            response = response.json()
            if 'access_token' in response:
                access_token = response['access_token']
        return access_token

    @staticmethod
    def get_checkmarx_projects(team_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Get all active projects for a specific team"""
        access_token = CxAPI.checkmarx_connection()
        project_list = None
        if access_token is not None:
            url = f'{CX_BASE_URL}/cxrestapi/help/projects?teamId={team_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            payload = {}
            response = requests.get(url=url,headers=headers,data=payload,timeout=60)
            if response.status_code == 200:
                response = response.json()
                project_list = []
                for project in response:
                    checkmarx_project_id = None
                    if 'id' in project:
                        checkmarx_project_id = project['id']
                    if 'name' in project:
                        repo = str(project['name']).split(" ", maxsplit=1)[0]
                    if 'owner' in project:
                        checkmarx_project_owner = project['owner']
                    project_list.append({'id' : checkmarx_project_id,
                                         'repo' : repo,
                                         'checkmarx_project_owner': checkmarx_project_owner})
        return project_list

    @staticmethod
    def cx_delete_project(cx_project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Delete a Checkmarx project"""
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{cx_project_id}"
        payload = '{\r\n     "deleteRunningScans": true\r\n}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json;v=1.0'
        }
        delete_project = requests.delete(url=url,headers=headers,data=payload,timeout=60)
        results = False
        if delete_project.status_code == 202:
            results = True
        return results

    @staticmethod
    def update_res_state(cx_scan_id,cx_path_id,state,comment,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Updates the result state for a single finding"""
        access_token = CxAPI.checkmarx_connection()
        # Use the following integers to update the state:
        # For 'To Verify':                  0
        # For 'Not Exploitable':            1
        # For 'Confirmed':                  2
        # For 'Urgent':                     3
        # For 'Proposed Not Exploitable':   4
        # For 'Tech Debt':                  5
        results = False
        url = f"{CX_BASE_URL}/cxrestapi/sast/scans/{cx_scan_id}/results/{cx_path_id}/labels"
        payload = '{\r\n  \"state\": ' + str(state) + ',\r\n  \"comment\": \"' + str(comment) + '\"\r\n}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json;v=1.0'
        }
        project_settings = requests.patch(url=url,headers=headers,data=payload,timeout=60)
        results = False
        if project_settings.status_code == 200:
            results = True
        return results

    @staticmethod
    def get_last_scan_data(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the last successful scan for a project"""
        last_scan = {}
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/sast/scans?"
        url += f"last=1&scanStatus=Finished&projectId={proj_id}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        get_scan = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if get_scan.status_code == 200:
            get_scan = get_scan.json()
            if get_scan:
                for scan in get_scan:
                    started = None
                    finished = None
                    duration = None
                    s_id = None
                    scan_type = None
                    correct_proj = False
                    scan_state = None
                    if 'project' in scan:
                        if 'id' in scan['project']:
                            correct_proj = True
                    if correct_proj is True:
                        if 'id' in scan:
                            s_id = scan['id']
                        if 'dateAndTime' in scan:
                            if 'startedOn' in scan['dateAndTime']:
                                started = scan['dateAndTime']['startedOn']
                                if started is not None:
                                    started = started.replace("T"," ")
                                    started = datetime.strptime(started.split(".",1)[0],
                                                                "%Y-%m-%d %H:%M:%S")
                            if 'finishedOn' in scan['dateAndTime']:
                                finished = scan['dateAndTime']['finishedOn']
                                if finished is not None:
                                    finished = finished.replace("T"," ")
                                    finished = datetime.strptime(finished.split(".",1)[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        if 'isIncremental' in scan:
                            if scan['isIncremental'] == 'False':
                                scan_type = 'Full'
                            else:
                                scan_type = 'Incremental'
                        if 'scanState' in scan:
                            scan_state = scan['scanState']
                    last_scan['ID'] = s_id
                    last_scan['Type'] = scan_type
                    last_scan['Finished'] = finished
                    if started is not None and finished is not None:
                        duration = finished - started
                    last_scan['Duration'] = duration
                    last_scan['Results'] = scan_state
        return last_scan

    @staticmethod
    def checkmarx_availability(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Ensures that Checkmarx is not returning 500 errors on basic API calls"""
        cx_available = False
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/sast/scans?"
        url += f"last=1&scanStatus=Finished&projectId={proj_id}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        get_scan = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if get_scan.status_code == 200:
            cx_available = True
        return cx_available

    @staticmethod
    def get_path_and_result_state(cx_similarity_id, cx_project_id,main_log=LOG,
                                  ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Get the path ID and result state for a similarity ID in a project"""
        return_data = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxarm/cxanalytics/SastResults?$filter=SimilarityId eq "
        url += f"{cx_similarity_id} and ProjectId eq {cx_project_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json;v=1.0'
        }
        sim_results = requests.get(url=url,headers=headers,timeout=60)
        if sim_results.status_code == 200:
            results = sim_results.json()
            if 'value' in results:
                results = results['value']
                if (len(results)) > 0:
                    return_data = []
                    results = results[0]
                    scan_id = None
                    path_id = None
                    current_state = None
                    if 'ScanId' in results:
                        scan_id = results['ScanId']
                    if 'Id' in results:
                        path_id = results['Id']
                    if 'StateName' in results:
                        current_state = results['StateName']
                    return_data.append({'cxScanId':scan_id,'cxPathId':path_id,
                                        'cxStateName': current_state})
                    if return_data:
                        return_data = return_data[0]
        return return_data

    @staticmethod
    def get_project_data(project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the project data for SASTProjects by repo and team ID"""
        cx_data = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{project_id}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        cx_projects = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if cx_projects.status_code == 200:
            project = cx_projects.json()
            if project != [] and project != {}:
                cx_project_id = project['id']
                cx_name = str(project['name'])
                repo = str(project['name']).split(" ",1)[0]
                branched_from = None
                from_exists = None
                cross_repo = None
                cx_scan = CxAPI.get_last_scan_data(cx_project_id,main_log,ex_log,ex_file)
                if 'originalProjectId' in project:
                    branched_from = project['originalProjectId']
                    from_exists = False
                    if branched_from != "" and branched_from is not None:
                        branched_from = int(branched_from)
                        from_exists = CxAPI.project_exists(branched_from)
                        cross_repo = CxASDatabase.check_cross_repo(repo,cx_project_id,main_log,
                                                                   ex_log,ex_file)
                        ScrVar.update_exception_info(cross_repo)
                        cross_repo = cross_repo['Results']
                last_scan_date = None
                repo_set = CxAPI.get_project_repo_set(cx_project_id,main_log,ex_log,ex_file)
                repo_set = repo_set['is_set']
                if 'Finished' in cx_scan:
                    if isinstance(cx_scan['Finished'],datetime):
                        last_scan_date = str(cx_scan['Finished'])
                cx_data = {'cxProjectId':cx_project_id,
                           'cxProjectName':cx_name,
                           'cxBaselineRepoSet':repo_set,
                           'cxTeamId':project['teamId'],
                           'LastScanDate':last_scan_date,
                           'BranchedFrom':branched_from,
                           'BranchedFromExists':from_exists,
                           'CrossRepoBranching':cross_repo}
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':cx_data}

    @staticmethod
    def get_project_repo_set(project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the sourcecode remoteSettings for SASTProjects by project ID"""
        is_set = False
        branch_name = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{project_id}/sourceCode/remoteSettings/git"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            project = response.json()
            if 'branch' in project:
                if 'branch' in project:
                    is_set = True
                    branch = str(project['branch']).split("/")
                    branch_name = branch[len(branch) - 1]
        return {'is_set':is_set,'branch':branch_name}

    @staticmethod
    def project_exists(project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the project data for SASTProjects by repo and team ID"""
        cx_data = False
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{project_id}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        cx_projects = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if cx_projects.status_code == 200:
            project = cx_projects.json()
            if project != [] and project != {}:
                cx_project_id = project['id']
                if cx_project_id is not None and cx_project_id != '':
                    cx_data = True
        return cx_data

    @staticmethod
    def get_repo_project_id(repo,project_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Gets the project data for SASTProjects by repo and project type
        ('baseline' or 'pipeline' should be passed through as project_type)"""
        cx_data = []
        access_token = CxAPI.checkmarx_connection()
        project_type = str(project_type).lower()
        search_for = f"projectName={repo}%20(Baseline)"
        if project_type == 'pipeline':
            search_for = f"projectName={repo}%20(Pipeline)"
        url = f"{CX_BASE_URL}/cxrestapi/projects/?{search_for}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        cx_projects = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if cx_projects.status_code == 200:
            cx_projects = cx_projects.json()
            if cx_projects != [] and cx_projects != {}:
                cx_data = []
                cx_project_id = None
                for project in cx_projects:
                    if 'id' in project:
                        cx_project_id = project['id']
                cx_data.append({'cxProjectId': cx_project_id})
                if cx_data:
                    cx_data = cx_data[0]
        return cx_data

    @staticmethod
    def get_result_state(cx_similarity_id,cx_project_id,cx_state_name,main_log=LOG,
                         ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the current state for a finding from Checkmarx"""
        status_change = None
        access_token = CxAPI.checkmarx_connection()
        query = f"$top=1&$filter=SimilarityId eq {cx_similarity_id} and ProjectId eq "
        query += f"{cx_project_id} and StateName ne '{cx_state_name}'"
        url = f"{CX_BASE_URL}/cxarm/cxanalytics/SastResults?{query}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json;v=1.0'
        }
        project_settings = requests.get(url=url,headers=headers,timeout=60)
        if project_settings.status_code == 200:
            results = None
            if 'value' in project_settings.json():
                status_change = {}
                results = project_settings.json()
            if 'value' in results:
                if results['value'] != []:
                    for item in results['value']:
                        cx_state_id = None
                        cx_state_name = None
                        if 'StateName' in item:
                            cx_state_name = item['StateName']
                            cx_state_id = CxCommon.get_result_state_id(cx_state_name)
                        status_change['cxStateId'] = cx_state_id
                        status_change['cxStateName'] = cx_state_name
        return status_change

    @staticmethod
    def get_cwe_id(cx_similarity_id,cx_project_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                   ex_file=EX_LOG_FILE):
        """Gets the CWE for a finding"""
        cx_cwe_id = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxarm/cxanalytics/SastResults?$top=1&$filter=SimilarityId eq "
        url += f"{cx_similarity_id} and ProjectId eq {cx_project_id}"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json;v=1.0'
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            json_data = response.json()
            if 'value' in json_data:
                json_data = response.json()['value']
                if json_data != []:
                    if 'Cweid' in json_data[0]:
                        cx_cwe_id = json_data[0]['Cweid']
        return cx_cwe_id

    @staticmethod
    def get_finding_details(scan_id,sim_id,cx_project_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Gets the cxSimilarityID, cxCWEID, cxCWETitle, cxCWEDescription, cxLastScanDate, and
        cxLastScanID for the specified finding"""
        cx_details_array = []
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxarm/cxanalytics/SastResults?$filter=SimilarityId eq {sim_id} and "
        url += f"ScanId eq {scan_id} and ProjectId eq {cx_project_id}"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json;v=1.0'
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            jsn = response.json()
            if 'value' in jsn:
                jsn = jsn['value']
                if jsn != []:
                    scan_date = None
                    sim_id = None
                    result_state = None
                    result_state_value = None
                    cwe_id = None
                    cwe_title = None
                    cwe_desc = None
                    cwe_link = None
                    for item in jsn:
                        cx_details = {}
                        if 'Date' in item:
                            scan_date = item['Date'].replace("T"," ").replace("Z"," ").split(".",1)[0]
                            scan_date = scan_date.strip()
                            scan_date = datetime.strptime(scan_date,'%Y-%m-%d %H:%M:%S')
                        if 'SimilarityId' in item:
                            sim_id = item['SimilarityId']
                        if 'StateName' in item:
                            result_state = item['StateName']
                        if result_state is not None:
                            result_state_value = CxCommon.get_result_state_id(result_state,main_log,
                                                                            ex_log,ex_file)
                        if 'Cweid' in item:
                            cwe_id = item['Cweid']
                            if cwe_id is not None:
                                cwe = VulnDetails.get_cwe(cwe_id,main_log,ex_log,ex_file)
                                if cwe != {}:
                                    if cwe['name'] is not None:
                                        cwe_title = cwe['name']
                                    if cwe['description'] is not None:
                                        cwe_desc = cwe['description']
                                    if cwe['link'] is not None:
                                        cwe_link = cwe['link']
                        cx_details['cxLastScanDate'] = str(scan_date)
                        cx_details['cxSimilarityID'] = sim_id
                        cx_details['cxResultState'] = result_state
                        cx_details['cxResultStateValue'] = result_state_value
                        cx_details['cxCWEID'] = cwe_id
                        cx_details['cxCWETitle'] = cwe_title
                        cx_details['cxCWEDescription'] = cwe_desc
                        cx_details['cxCWELink'] = cwe_link
                        cx_details['cxResultID'] = f"{item['ScanId']}-{item['Id']}"
                        cx_details_array.append(cx_details)
        return cx_details_array

    @staticmethod
    def get_finding_details_by_path(scan_id,path_id,cx_project_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Gets the cxSimilarityID, cxCWEID, cxCWETitle, cxCWEDescription, cxLastScanDate, and
        cxLastScanID for the specified finding"""
        cx_details = {}
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxarm/cxanalytics/SastResults?$top=1&$filter=Id eq {path_id} and "
        url += f"ScanId eq {scan_id} and ProjectId eq {cx_project_id}"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json;v=1.0'
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            jsn = response.json()
            if 'value' in jsn:
                jsn = jsn['value']
                if jsn != []:
                    jsn = jsn[0]
                    scan_date = None
                    sim_id = None
                    result_state = None
                    result_state_value = None
                    cwe_id = None
                    cwe_title = None
                    cwe_desc = None
                    cwe_link = None
                    if 'Date' in jsn:
                        scan_date = jsn['Date'].replace("T"," ").replace("Z"," ").split(".",1)[0]
                        scan_date = scan_date.strip()
                        scan_date = datetime.strptime(scan_date,'%Y-%m-%d %H:%M:%S')
                    if 'ScanId' in jsn:
                        scan_id = jsn['ScanId']
                    if 'SimilarityId' in jsn:
                        sim_id = jsn['SimilarityId']
                    if 'StateName' in jsn:
                        result_state = jsn['StateName']
                    if result_state is not None:
                        result_state_value = CxCommon.get_result_state_id(result_state,main_log,
                                                                          ex_log,ex_file)
                    if 'Cweid' in jsn:
                        cwe_id = jsn['Cweid']
                        if cwe_id is not None:
                            cwe = VulnDetails.get_cwe(cwe_id,main_log,ex_log,ex_file)
                            if cwe != {}:
                                if cwe['name'] is not None:
                                    cwe_title = cwe['name']
                                if cwe['description'] is not None:
                                    cwe_desc = cwe['description']
                                if cwe['link'] is not None:
                                    cwe_link = cwe['link']
                    cx_details['cxLastScanDate'] = str(scan_date)
                    cx_details['cxLastScanID'] = scan_id
                    cx_details['cxSimilarityID'] = sim_id
                    cx_details['cxResultState'] = result_state
                    cx_details['cxResultStateValue'] = result_state_value
                    cx_details['cxCWEID'] = cwe_id
                    cx_details['cxCWETitle'] = cwe_title
                    cx_details['cxCWEDescription'] = cwe_desc
                    cx_details['cxCWELink'] = cwe_link
        return cx_details

    @staticmethod
    def g_query_desc(cx_similarity_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the QueryId for a finding"""
        cx_query_description = None
        sql = f"""SELECT Description FROM CxDB.dbo.QueryDescription WHERE QueryId IN (SELECT TOP 1
        QueryId FROM CxDB.dbo.QueryVersion WHERE QueryVersionCode IN (SELECT TOP 1
        QueryVersionId from CxEntities.Result WHERE SimilarityId = {cx_similarity_id}))"""
        get_description = cx_select(sql)
        if get_description:
            cx_query_description = get_description[0][0].replace("'","")
        return cx_query_description

    @staticmethod
    def create_scan_results_json(report_id,scan_id,proj_id,cx_last_scan_date,main_log=LOG,
                                 ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the scan results"""
        print("                          *  report download",end="\r")
        scan_json = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/reports/sastScan/{report_id}"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/csv',
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=300)
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        csv_results = list()
        for dictionary in reader:
            csv_results.append(dictionary)
        if csv_results != []:
            print("                          *  report acquired",end="\r")
            scan_json = []
            for row in csv_results:
                cx_result_severity = row['Result Severity']
                if cx_result_severity not in IGNORE_RESULTS:
                    result_severity_value = 0
                    if cx_result_severity == "High":
                        result_severity_value = 1
                    elif cx_result_severity == "Medium":
                        result_severity_value = 2
                    cx_result_id = None
                    cx_result_description = None
                    sim_id = None
                    cx_result_state = None
                    cx_result_state_value = None
                    cx_query = None
                    cx_query_description = None
                    cx_cwe_id = None
                    cwe_id = None
                    cx_cwe_description = None
                    cx_cwe_link = None
                    cx_link = None
                    cx_owasp = None
                    cx_detection_date = None
                    if row['OWASP Top 10 2021'] is not None and row['OWASP Top 10 2021'] != '':
                        cx_owasp = row['OWASP Top 10 2021']
                    if row['Detection Date'] is not None and row['Detection Date'] != '':
                        cx_detection_date = datetime.strptime(row['Detection Date'],
                                                              '%m/%d/%Y %I:%M:%S %p')
                    if row['Result State'] is not None and row['Result State'] != '':
                        cx_result_state = row['Result State']
                        cx_result_state_value = CxCommon.get_result_state_id(cx_result_state)
                    if row['Link'] is not None and row['Link'] != '':
                        cx_link = row['Link']
                        path_id = cx_link.split('&')[2][7:]
                        cx_result_id = f"{scan_id}-{path_id}"
                    if cx_result_id is not None:
                        cx_result_description = CxAPI.get_result_description(scan_id,path_id,
                                                                                main_log,ex_log,
                                                                                ex_file)
                        sql = f"""SELECT SimilarityId from CxEntities.Result
                                WHERE ResultId = '{cx_result_id}'"""
                        get_similarity_id = None
                        try:
                            get_similarity_id = cx_select(sql)
                        except Exception:
                            get_similarity_id.close()
                            continue
                        if get_similarity_id:
                            sim_id = get_similarity_id[0][0]
                            cx_cwe_id = CxAPI.get_cwe_id(sim_id,proj_id,main_log,ex_log,ex_file)
                            if cx_cwe_id is not None and cx_cwe_id != '' and cx_cwe_id != 'None':
                                cwe_info = VulnDetails.get_cwe(cx_cwe_id,main_log,ex_log,ex_file)
                                cwe_id = cx_cwe_id
                                if cwe_info is not None:
                                    cx_cwe_description = cwe_info['description'].replace("'","")
                                    cx_cwe_title = cwe_info['name'].replace("'","")
                                    cx_cwe_link = cwe_info['link']
                    if row['Query'] is not None and row['Query'] != '':
                        cx_query = row['Query']
                        cx_query = cx_query.replace("'","")
                        cx_query_description = CxAPI.g_query_desc(sim_id)
                        cx_query_description = str(cx_query_description).replace("'","")
                    scan_json.append({'cxProjectID':proj_id,'cxSimilarityID':sim_id,
                                      'cxResultState':cx_result_state,
                                      'cxResultStateValue':cx_result_state_value,'cxQuery':cx_query,
                                      'cxQueryDescription':cx_query_description,
                                      'cxResultSeverity':cx_result_severity,
                                      'ResultSeverityValue':result_severity_value,
                                      'cxCWEID': cwe_id,'cxCWETitle':cx_cwe_title,
                                      'cxCWEDescription':cx_cwe_description,'cxCWELink':cx_cwe_link,
                                      'cxResultID':cx_result_id,
                                      'cxResultDescription':cx_result_description,
                                      'cxDetectionDate':str(cx_detection_date),'cxLink':cx_link,
                                      'cxOWASP':cx_owasp,'cxLastScanID':scan_id,
                                      'cxLastScanDate': cx_last_scan_date,'cxPathID': path_id})
        return scan_json

    @staticmethod
    def get_scan_report(report_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the scan report"""
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/reports/sastScan/{report_id}"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/csv',
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=300)
        results = csv.reader(response.text.replace("'", "").strip().split('\r\n'))
        headers = next(results)
        csv_results = []
        for row in results:
            record = {}
            for i, value in enumerate(row):
                if i in (0,21,22,23,25,26,27,28,30,31,32,35,37):
                    if value == '':
                        value = None
                    record[headers[i]] = value
            if record != {}:
                if record['Result Severity'] not in IGNORE_RESULTS:
                    csv_results.append(record)
        return csv_results

    @staticmethod
    def create_scan_report(scan_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Creates a scan report"""
        report_id = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/reports/sastScan"
        payload = f"reportType=CSV&scanId={scan_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json;v=1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 202:
            json_data = response.json()
            if 'reportId' in json_data:
                report_id = json_data['reportId']
        return report_id

    @staticmethod
    def scan_report_complete(report_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Determines if scan report is ready"""
        is_done = False
        if CxAPI.scan_report_status(report_id) == "Created":
            is_done = True
        return is_done

    @staticmethod
    def scan_report_status(report_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks the status of the scan report"""
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/reports/sastScan/{report_id}/status"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json;v=1.0',
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        report_status = None
        if response.status_code == 200:
            json_data = response.json()
            if 'status' in json_data:
                if 'value' in json_data['status']:
                    report_status = json_data['status']['value']
        return report_status

    @staticmethod
    def get_scan_results(scan_id,cx_proj_id,l_scan_date,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Gets the scan results in JSON format"""
        scan_results = None
        sql = f"""SELECT TOP 1 ID FROM CxDB.dbo.ScansReports WHERE ScanID = {scan_id} AND
                ReportStatusID = 2 ORDER BY ReportTime DESC"""
        g_rep_id = cx_select(sql)
        if g_rep_id:
            scan_results = CxAPI.create_scan_results_json(g_rep_id[0][0],scan_id,cx_proj_id,
                                                          l_scan_date,main_log,ex_log,ex_file)
        else:
            results = CxAPI.create_scan_report(scan_id)
            while not CxAPI.scan_report_complete(results):
                time.sleep(10)
                print("                         *  running report.",end="\r")
            scan_results = CxAPI.create_scan_results_json(results,scan_id,cx_proj_id,l_scan_date,
                                                          main_log,ex_log,ex_file)
        return scan_results

    @staticmethod
    def get_result_description(scan_id,path_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE):
        """Gets the short description for an individual result"""
        description = None
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/sast/scans/{scan_id}/results/{path_id}/shortDescription"
        payload = {}
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json;v=1.0',
        }
        response = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if response.status_code == 200:
            json_data = response.json()
            if 'shortDescription' in json_data:
                description = json_data['shortDescription'].replace("'","")
        return description

    @staticmethod
    def add_ticket_to_cx(result_id,jira_issue_key,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Syncs the Jira ticket to the finding in Checkmarx"""
        access_token = CxAPI.checkmarx_connection()
        results = False
        url = f"{CX_BASE_URL}/cxrestapi/sast/results/tickets"
        payload = '{\r\n  \"resultsId\": [\r\n\"' + str(result_id) + '\"\r\n],\r\n  \"ticketId\": \"' + str(jira_issue_key) + '\"\r\n}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json;v=1.0'
        }
        set_ticket = requests.post(url=url,headers=headers,data=payload,timeout=60)
        results = None
        if set_ticket.status_code == 204:
            results = True
        return results

    @staticmethod
    def launch_cx_scan(proj_id,comment,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Launches a scan for the specified project"""
        comment = str(comment).replace("'","").replace('"',"")
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/sast/scans"
        payload = '{\r\n     "projectId": ' + str(proj_id) + ',\r\n     "isIncremental": false,\r\n     "isPublic": true,\r\n     "forceScan": true,\r\n     "comment": "' + str(comment) + '"\r\n}'
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json;v=1.0'
        }
        proj_settings = requests.post(url=url,headers=headers,data=payload,timeout=60)
        success = False
        if proj_settings.status_code == 201:
            success = True
        return success

    @staticmethod
    def branch_project(repo,proj_id,branch_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                       ex_file=EX_LOG_FILE):
        """Creates a branch of a project"""
        if branch_type == 52:
            repo = f"{repo} (Baseline)"
        else:
            repo = f"{repo} (Pipeline)"
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{proj_id}/branch"
        payload = '{\r\n     "name": "' + str(repo) + '"\r\n}'
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json;v=1.0'
        }
        response = requests.post(url=url,headers=headers,data=payload,timeout=60)
        new_proj_id = None
        if response.status_code == 201:
            json_data = response.json()
            if 'id' in json_data:
                new_proj_id = json_data['id']
        return new_proj_id

    @staticmethod
    def set_project_team(repo,proj_id,branch_type,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Sets the owning team of a project"""
        if branch_type == 52:
            repo = f"{repo} (Baseline)"
        else:
            repo = f"{repo} (Pipeline)"
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{proj_id}"
        payload = '{\r\n    "name": "' + str(repo) + '",\r\n    "owningTeam": ' + str(branch_type) + ',\r\n    "CustomFields": []\r\n}'
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json;v=1.0'
        }
        response = requests.put(url=url,headers=headers,data=payload,timeout=60)
        success = False
        if response.status_code == 204:
            success = True
        return success

    @staticmethod
    def set_policy(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Sets the project policy to 3 (no High vulns)"""
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxarm/policymanager/projects/{proj_id}/policies"
        payload = '[{\r\n    "policyId": 3\r\n}]'
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json;v=1.0'
        }
        response = requests.put(url=url,headers=headers,data=payload,timeout=60)
        success = False
        if response.status_code == 200:
            success = True
        return success

    @staticmethod
    def set_repo(repo,proj_id,branch,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Sets the repo to be scanned for the project"""
        if branch is None:
            branch = "refs/heads/master"
        else:
            branch = f"refs/heads/{branch}"
        key = BITBUCKET_HEADER
        if BITBUCKET_HEADER is not None:
            key = BITBUCKET_HEADER.replace('Bearer ','')
        repo_url = f"{BITBUCKET_REPO_URL}{repo}/src"
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{proj_id}/sourceCode/remoteSettings/git"
        payload = '{\r\n    "url": "' + str(repo_url) + '",\r\n    "branch": "' + str(branch) + '",\r\n    "privateKey": "' + str(key) + '"\r\n}'
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json;v=1.0'
        }
        response = requests.post(url=url,headers=headers,data=payload,timeout=60)
        success = False
        if response.status_code == 204:
            success = True
        return success

    @staticmethod
    def get_project_details(cx_project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the project details for cxBaselineProjectDetails"""
        project_details = {}
        access_token = CxAPI.checkmarx_connection()
        url = f"{CX_BASE_URL}/cxrestapi/projects/{cx_project_id}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        cx_projects = requests.get(url=url,headers=headers,data=payload,timeout=60)
        if cx_projects.status_code == 200:
            cx_projects = cx_projects.json()
            if cx_projects != [] and cx_projects != {}:
                if 'id' in cx_projects:
                    cx_project_name = None
                    cx_repo = None
                    cx_related_projects = None
                    branch_name = None
                    cx_scan_id = None
                    ls_date = None
                    files_count = None
                    lines_of_code = None
                    apex = 0
                    asp = 0
                    cobol = 0
                    common = 0
                    cpp = 0
                    csharp = 0
                    dart = 0
                    go_lang = 0
                    groovy = 0
                    java = 0
                    javascript = 0
                    kotlin = 0
                    objc = 0
                    perl = 0
                    php = 0
                    plsql = 0
                    python = 0
                    rpg = 0
                    ruby = 0
                    scala = 0
                    swift = 0
                    vb6 = 0
                    vbnet = 0
                    vbscript = 0
                    unknown = 0
                    if 'name' in cx_projects:
                        cx_project_name = cx_projects['name']
                        cx_repo = str(cx_projects['name']).split(" ",1)[0].replace(",","").lower()
                    if 'relatedProjects' in cx_projects:
                        project_list = ''
                        for project in cx_projects['relatedProjects']:
                            project_list += f"{project}, "
                        project_list += 'DELETE'
                        project_list = str(project_list).replace(", DELETE","")
                        if project_list == 'DELETE':
                            project_list = None
                        cx_related_projects = project_list
                    get_branch = CxAPI.get_project_repo_set(cx_project_id)
                    if 'branch' in get_branch:
                        if get_branch['branch'] is not None:
                            branch = str(get_branch['branch']).split("/")
                            branch_name = branch[len(branch) - 1]
                    scan = CxAPI.get_last_scan_data(cx_project_id)
                    data_pulled = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if scan != {}:
                        if 'ID' in scan:
                            if (branch_name is not None and branch_name != ''
                                and branch_name != 'None'):
                                cx_scan_id = scan['ID']
                            if ('Finished' in scan and branch_name is not None and branch_name != ''
                                and branch_name != 'None'):
                                ls_date = str(scan['Finished'])
                            if 'Results' in scan:
                                if 'filesCount' in scan['Results']:
                                    files_count = scan['Results']['filesCount']
                                if 'linesOfCode' in scan['Results']:
                                    lines_of_code = scan['Results']['linesOfCode']
                                if 'languageStateCollection' in scan['Results']:
                                    array=scan['Results']['languageStateCollection']
                                    if len(array) > 0:
                                        for item in array:
                                            language = item['languageName'].lower()
                                            if language == 'apex':
                                                apex = 1
                                            elif language == 'asp':
                                                asp = 1
                                            elif language == 'cobol':
                                                cobol = 1
                                            elif language == 'common':
                                                common = 1
                                            elif language == 'cpp':
                                                cpp = 1
                                            elif language == 'csharp':
                                                csharp = 1
                                            elif language == 'dart':
                                                dart = 1
                                            elif language == 'go':
                                                go_lang = 1
                                            elif language == 'groovy':
                                                groovy = 1
                                            elif language == 'java':
                                                java = 1
                                            elif language == 'javascript':
                                                javascript = 1
                                            elif language == 'kotlin':
                                                kotlin = 1
                                            elif language == 'objc':
                                                objc = 1
                                            elif language == 'perl':
                                                perl = 1
                                            elif language == 'php':
                                                php = 1
                                            elif language == 'plsql':
                                                plsql = 1
                                            elif language == 'python':
                                                python = 1
                                            elif language == 'rpg':
                                                rpg = 1
                                            elif language == 'ruby':
                                                ruby = 1
                                            elif language == 'scala':
                                                scala = 1
                                            elif language == 'swift':
                                                swift = 1
                                            elif language == 'vb6':
                                                vb6 = 1
                                            elif language == 'vbnet':
                                                vbnet = 1
                                            elif language == 'vbscript':
                                                vbscript = 1
                                            else:
                                                unknown = 1
                                project_details['LastDataSync'] = data_pulled
                                project_details['cxProjectName'] = cx_project_name
                                project_details['Repo'] = cx_repo
                                project_details['cxRelatedProjects'] = cx_related_projects
                                project_details['branchScanned'] = branch_name
                                project_details['cxLastScanId'] = cx_scan_id
                                project_details['cxScannedDate'] = ls_date
                                project_details['cxFilesCount'] = files_count
                                project_details['cxLinesOfCode'] = lines_of_code
                                project_details['Apex'] = apex
                                project_details['ASP'] = asp
                                project_details['Cobol'] = cobol
                                project_details['Common'] = common
                                project_details['CPP'] = cpp
                                project_details['CSharp'] = csharp
                                project_details['Dart'] = dart
                                project_details['Go'] = go_lang
                                project_details['Groovy'] = groovy
                                project_details['Java'] = java
                                project_details['JavaScript'] = javascript
                                project_details['Kotlin'] = kotlin
                                project_details['Objc'] = objc
                                project_details['Perl'] = perl
                                project_details['PHP'] = php
                                project_details['PLSQL'] = plsql
                                project_details['Python'] = python
                                project_details['RPG'] = rpg
                                project_details['Ruby'] = ruby
                                project_details['Scala'] = scala
                                project_details['Swift'] = swift
                                project_details['VB6'] = vb6
                                project_details['VbNet'] = vbnet
                                project_details['VbScript'] = vbscript
                                project_details['Unknown'] = unknown
        return project_details
