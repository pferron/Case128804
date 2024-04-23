"""Commonly used Mend functions"""

import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
import json
import requests
from common.constants import WS_EMAIL, WS_URL, WS_REPORTS
from dotenv import load_dotenv
from datetime import datetime
from requests.auth import HTTPBasicAuth
from common.database_appsec import select, insert_multiple_into_table

load_dotenv()
WS_KEY = os.environ.get('WS_KEY_USER')
WS_ORG = os.environ.get('WS_TOKEN')

class MendAPI:
    """Provides general functions for interacting with Mend"""

    token = None
    token_created = datetime.strptime("2022-04-13 15:34:10.968427","%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def mend_connect():
        """Creates the bearer token"""
        new_token = None
        if ((datetime.now() - MendAPI.token_created).total_seconds()/60/60) < 30 and MendAPI.token:
            return MendAPI.token
        else:
            url = f"{WS_URL}/login"
            payload = json.dumps({
                'email': WS_EMAIL,
                'orgToken': WS_ORG,
                'userKey': WS_KEY
            })
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers = headers, data = payload, timeout=300)
            if response.status_code == 201 or response.status_code == 200:
                response = response.json()
                if 'retVal' in response:
                    if 'jwtToken' in response['retVal']:
                        MendAPI.token = response['retVal']['jwtToken']
                        MendAPI.token_created = datetime.now()
                        new_token = response['retVal']['jwtToken']
        return new_token

    @staticmethod
    def forbidden_licenses():
        """Builds an array of forbidden licenses from Reject Unapproved Licenses policy"""
        forbidden = []
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        url = f"{WS_URL}/orgs/{WS_ORG}/policies/d7a435c0-4a40-48ac-ab86-2d8bf50185f7"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                item = response['retVal']
                if 'filter' in item:
                    if 'licenses' in item['filter']:
                        for i in item['filter']['licenses']:
                            if 'name' in i:
                                name = i['name']
                                forbidden.append(name)
        return forbidden

    @staticmethod
    def get_violating_licenses(proj_id, library):
        """Retrieves license violations for a specific file"""
        ret_val = None
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        prohibited = str(MendAPI.forbidden_licenses())
        prohibited = prohibited.replace("[","").replace("]","").replace(", '",",").replace("'","")
        query = f"search=license:in:{prohibited};componentName:equals:{library}&sort=license"
        url = f"{WS_URL}/projects/{proj_id}/libraries/licenses?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                ret_val = []
                response = response['retVal']
                for i in response:
                    if 'name' in i:
                        ret_val.append(i['name'])
                if ret_val == []:
                    return None
                else:
                    ret_val = str(ret_val).replace("[","").replace("]","").replace(", '",",").replace("'","")
        return ret_val

    @staticmethod
    def get_missing_fields(pj_token, library):
        """Retrieves Version and GroupId for a specific file"""
        data = None
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = f"search=name:equals:{library}&optionalColumns=locations"
        url = f"{WS_URL}/projects/{pj_token}/libraries?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                data = {}
                locations = []
                group_id = None
                version = None
                response = response['retVal']
                licenses = MendAPI.get_violating_licenses(pj_token, library)
                for i in response:
                    if 'groupId' in i:
                        group_id = i['groupId']
                    if 'version' in i:
                        version = i['version']
                    if 'locations' in i:
                        for l in i['locations']:
                            if 'localPath' in l:
                                locations.append(l['localPath'])
                if locations == []:
                    locations = None
                else:
                    locations = sorted(set(locations))
                    locations = str(locations).replace("[","").replace("]","")
                    locations = locations.replace(", '",",").replace("'","")
                data['GroupId'] = group_id
                data['Version'] = version
                data['LicenseViolations'] = licenses
                data['LibraryLocations'] = locations
        return data

    @staticmethod
    def get_alerts(repo, prod_token):
        """Gets active alerts for a product from Mend"""
        alerts = []
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = "search=type:equals:POLICY_VIOLATIONS&pageSize=5000"
        url = f"{WS_URL}/products/{prod_token}/alerts/legal?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                response = response['retVal']
                for item in response:
                    policy = None
                    severity = None
                    pj_name = None
                    pj_token = None
                    pj_id = None
                    lib = None
                    key_uuid = None
                    comment = None
                    alert_uuid = None
                    ticket = None
                    in_findings = 0
                    if 'project' in item:
                        if 'name' in item['project']:
                            pj_name = item['project']['name']
                            if 'release' in pj_name.lower() or (repo == 'four' and
                                            (pj_name == 'master' or pj_name == 'develop' or
                                             pj_name == 'refs/heads/develop')):
                                if 'policyName' in item:
                                    policy = item['policyName']
                                    if 'Medium' in policy:
                                        severity = 'Medium'
                                    else:
                                        severity = 'High'
                                    if 'License' in policy:
                                        finding_type = 'License Violation'
                                    else:
                                        finding_type = 'Vulnerability'
                                sql = f"""SELECT TOP 1 wsProjectToken, wsProjectId FROM OSProjects
                                WHERE wsProjectName = '{pj_name}' AND wsProductName = '{repo}'"""
                                g_token = select(sql)
                                if g_token:
                                    pj_token = g_token[0][0]
                                    pj_id = g_token[0][1]
                                if 'component' in item:
                                    if 'name' in item['component']:
                                        lib = item['component']['name']
                                    if 'uuid' in item['component']:
                                        key_uuid = item['component']['uuid']
                                if 'alertInfo' in item:
                                    if 'detectedAt' in item['alertInfo']:
                                        d_date = str(item['alertInfo']['detectedAt'])
                                        d_date = d_date.replace("T"," ").replace("Z","")
                                    if 'status' in item['alertInfo']:
                                        status = str(item['alertInfo']['status'])
                                        status = status.replace("_"," ").capitalize()
                                    if 'comment' in item['alertInfo']:
                                        if item['alertInfo']['comment']:
                                            if 'comment' in item['alertInfo']['comment']:
                                                comment = item['alertInfo']['comment']['comment']
                                if 'uuid' in item:
                                    alert_uuid = item['uuid']
                                if pj_name is not None and key_uuid is not None:
                                    sql = f"""SELECT DISTINCT JiraIssueKey FROM OSFindings
                                    WHERE Repo = '{repo}' AND ProjectName = '{pj_name}' AND
                                    KeyUuid = '{key_uuid}'"""
                                    g_ticket = select(sql)
                                    if g_ticket:
                                        in_findings = 1
                                        if g_ticket[0][0] is not None:
                                            ticket = g_ticket[0][0]
                                if not (status == 'Library removed' and in_findings == 0):
                                    alerts.append({"ProjectName": pj_name,
                                                "ProjectToken": pj_token,
                                                "ProjectId": pj_id,
                                                "Library": lib,
                                                "KeyUuid": key_uuid,
                                                "Severity": severity,
                                                "DateDetected": d_date,
                                                "AlertStatus": status,
                                                "PolicyViolated": policy,
                                                "Comments": comment,
                                                "AlertUuid": alert_uuid,
                                                "JiraIssueKey": ticket,
                                                "InOSFindings": in_findings,
                                                "FindingType": finding_type
                                                })
        return alerts

    @staticmethod
    def reactivate_manually_ignored_alerts(repo,prod_token):
        """Gets active alerts for a product from Mend"""
        reactivated_cnt = 0
        comment = "Alert was initially ignored in an unauthorized fashion. Reactivating."
        reactivated_cnt += MendAPI.reactivate_vulnerabilities(repo,prod_token,comment)
        reactivated_cnt += MendAPI.reactivate_license_violations(repo,prod_token,comment)
        return reactivated_cnt

    @staticmethod
    def reactivate_vulnerabilities(repo,prod_token,comment):
        '''Reactivates manually-ignored vulnerabilities'''
        inserts = []
        reactivated_cnt = 0
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = "search=status:equals:IGNORE&pageSize=5000"
        url = f"{WS_URL}/products/{prod_token}/alerts/security?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                response = response['retVal']
                for item in response:
                    user = None
                    ignored_date = None
                    uuid = None
                    alert_type = None
                    project_name = None
                    project_id = None
                    title = None
                    library = None
                    group_id = None
                    if 'uuid' in item:
                        uuid = item['uuid']
                    if MendAPI.do_not_reactivate_alert(uuid) is True:
                        continue
                    if 'alertInfo' in item:
                        if 'status' in item['alertInfo']:
                            if item['alertInfo']['status'].lower() == 'ignored':
                                if 'comment' in item['alertInfo']:
                                    if 'userEmail' in item['alertInfo']['comment']:
                                        user = item['alertInfo']['comment']['userEmail']
                    if user != WS_EMAIL and user is not None:
                        if 'date' in item['alertInfo']['comment']:
                            ignored_date = item['alertInfo']['comment']['date']
                            ignored_date = ignored_date.split("Z",1)[0].replace("T"," ")
                        if 'type' in item:
                            alert_type = item['type']
                        if 'project' in item:
                            if 'uuid' in item['project']:
                                project_id = item['project']['uuid']
                            if 'name' in item['project']:
                                project_name = item['project']['name']
                        if 'name' in item:
                            title = item['name']
                        if 'component' in item:
                            if 'name' in item['component']:
                                library = item['component']['name']
                            if 'groupId' in item['component']:
                                group_id = item['component']['groupId']
                        inserts.append({'Repo':repo,'ProjectName':project_name,'AlertType':alert_type,
                                        'AlertUuid':uuid,'AlertTitle':title,'IgnoredBy':user,
                                        'IgnoredDate':ignored_date,'LibraryName':library,
                                        'GroupId':group_id})
                        activated = MendAPI.update_alert_status(project_id,uuid,'ACTIVE',comment)
                        if activated is True:
                            reactivated_cnt += 1
        insert_multiple_into_table('OSManuallyIgnoredAlerts',inserts)
        return reactivated_cnt

    @staticmethod
    def do_not_reactivate_alert(alert_uuid):
        """Checks OSFindings to see if we have manually set the Status for an item associated with
        the alert_uuid to 'False Positive'"""
        dnr = False
        sql = f"""SELECT Status FROM OSFindings WHERE (Status IN ('False Positive',
        'No Fix Available')) AND AlertUuid = '{alert_uuid}'"""
        check_it = select(sql)
        if check_it != []:
            dnr = True
        return dnr

    @staticmethod
    def reactivate_license_violations(repo,prod_token,comment):
        '''Reactivates manually-ignored license violations'''
        inserts = []
        reactivated_cnt = 0
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        query = "search=type:equals:POLICY_VIOLATIONS:status:equals:IGNORED&pageSize=5000"
        url = f"{WS_URL}/products/{prod_token}/alerts/legal?{query}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}'
            }
        response = requests.get(url, headers = headers, data = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'retVal' in response:
                response = response['retVal']
                for item in response:
                    user = None
                    ignored_date = None
                    uuid = None
                    alert_type = None
                    project_name = None
                    project_id = None
                    title = None
                    library = None
                    group_id = None
                    if 'alertInfo' in item:
                        if 'status' in item['alertInfo']:
                            if item['alertInfo']['status'].lower() == 'ignored':
                                if 'comment' in item['alertInfo']:
                                    if 'userEmail' in item['alertInfo']['comment']:
                                        user = item['alertInfo']['comment']['userEmail']
                    if user != WS_EMAIL and user is not None:
                        if 'date' in item['alertInfo']['comment']:
                            ignored_date = item['alertInfo']['comment']['date']
                            ignored_date = ignored_date.split("Z",1)[0].replace("T"," ")
                        if 'uuid' in item:
                            uuid = item['uuid']
                        if 'type' in item:
                            alert_type = item['type']
                        if 'project' in item:
                            if 'uuid' in item['project']:
                                project_id = item['project']['uuid']
                            if 'name' in item['project']:
                                project_name = item['project']['name']
                        if 'name' in item:
                            title = item['name']
                        if 'component' in item:
                            if 'name' in item['component']:
                                library = item['component']['name']
                            if 'groupId' in item['component']:
                                group_id = item['component']['groupId']
                        inserts.append({'Repo':repo,'ProjectName':project_name,'AlertType':alert_type,
                                        'AlertUuid':uuid,'AlertTitle':title,'IgnoredBy':user,
                                        'IgnoredDate':ignored_date,'LibraryName':library,
                                        'GroupId':group_id})
                        activated = MendAPI.update_alert_status(project_id,uuid,'ACTIVE',comment)
                        if activated is True:
                            reactivated_cnt += 1
        if inserts != []:
            insert_multiple_into_table('OSManuallyIgnoredAlerts',inserts)
        return reactivated_cnt

    @staticmethod
    def get_org_prod_vitals():
        """Returns a full list of Products in Mend"""
        products = []
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        payload = {
            'requestType': 'getAllProducts',
            'userKey': WS_KEY,
            'orgToken': WS_ORG
            }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(WS_REPORTS,headers=headers,json=payload,timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'products' in response:
                response = response['products']
                for item in response:
                    repo = None
                    product_token = None
                    if ('productName' in item and item['productName'] is not None and
                        not item['productName'].startswith('BBC_')):
                        repo = item['productName']
                    if ('productToken' in item and item['productName'] is not None and
                        not item['productName'].startswith('BBC_')):
                        product_token = item['productToken']
                    products.append({"Repo": repo,
                                     "wsProductToken": product_token})
        return products

    @staticmethod
    def apply_org_policies():
        """Ensures that Organization level policies are applied to inventory"""
        updated = False
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        url = f"{WS_URL}/orgs/{WS_ORG}/policies/apply"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        response = requests.post(url, headers = headers, data = payload, timeout=600)
        if response.status_code == 200:
            updated = True
        return updated

    @staticmethod
    def apply_product_policies(prod_token):
        """Ensures that Product level policies are applied to inventory"""
        updated = False
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        url = f"{WS_URL}/products/{prod_token}/policies/apply"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        response = requests.post(url, headers = headers, data = payload, timeout=600)
        if response.status_code == 200:
            updated = True
        return updated

    @staticmethod
    def delete_product(prod_token):
        """Deletes a product from Mend"""
        deleted = False
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        url = f"{WS_URL}/products/{prod_token}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {MendAPI.token}',
            'Content-Type': 'application/json'
            }
        response = requests.delete(url, headers = headers, data = payload, timeout=600)
        if response.status_code == 200:
            response = response.json()
            if 'errorCode' not in response:
                deleted = True
        return deleted

    @staticmethod
    def get_projects(repo, prod_token):
        """gets projects associated with product(repo)"""
        projects = []
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        payload = {
            'requestType': 'getProductProjectVitals',
            'userKey': WS_KEY,
            'productToken': prod_token
            }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(WS_REPORTS, headers = headers, json = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'projectVitals' in response:
                response = response['projectVitals']
                for item in response:
                    pj_name = ''
                    pj_token = None
                    last_updated = None
                    if 'name' in item:
                        pj_name = item['name']
                    if 'token' in item:
                        pj_token = item['token']
                    if 'id' in item:
                        pj_id = item['id']
                    if 'lastUpdatedDate' in item:
                        last_updated = str(item['lastUpdatedDate']).split(" +", 1)[0]
                    if (pj_name != '' and 'SAST' not in pj_name and
                        ('release' in pj_name.lower() or (repo == 'four' and
                            (pj_name == 'master' or pj_name == 'develop' or
                             pj_name == 'refs/heads/develop')))):
                        projects.append({"wsProjectName": pj_name,
                                        "wsProjectToken": pj_token,
                                        "wsProjectId": pj_id,
                                        "wsLastUpdatedDate": last_updated})
        return projects

    @staticmethod
    def vulnerability_report(repo, proj_token):
        """Gets the vulnerability report for a repo, including all release projects"""
        vulnerabilities = []
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        payload = {
            'requestType': 'getProjectVulnerabilityReport',
            'userKey': WS_KEY,
            'projectToken': proj_token,
            'format': 'json'
            }
        headers = {
            'Content-Type': 'application/json'
            }
        response = requests.post(WS_REPORTS, headers = headers, json = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            sync_severities = ['Critical', 'High', 'Medium']
            if 'vulnerabilities' in response:
                response = response['vulnerabilities']
                for item in response:
                    severity = None
                    sev_value = None
                    pj_n = None
                    pj_id = None
                    lib = None
                    g_id = None
                    key_uuid = None
                    version = None
                    v_date = None
                    v_name = None
                    v_url = None
                    fix = None
                    shield = None
                    if 'cvss3_severity' in item:
                        severity = str(item['cvss3_severity']).capitalize()
                        if severity in sync_severities:
                            if severity == 'Critical':
                                sev_value = 0
                            elif severity == 'High':
                                sev_value = 1
                            elif severity == 'Medium':
                                sev_value = 2
                            if 'project' in item:
                                pj_n = item['project'].replace("'","")
                                if pj_n != '' and ('release' in pj_n.lower() or (repo == 'four' and
                                            (pj_n == 'master' or pj_n == 'develop' or
                                             pj_n == 'refs/heads/develop'))):
                                    sql = f"""SELECT wsProjectId FROM OSProjects WHERE
                                    wsProductName = '{repo}' AND wsProjectName = '{pj_n}'"""
                                    g_pj_id = select(sql)
                                    if g_pj_id:
                                        if g_pj_id[0][0] is not None:
                                            pj_id = g_pj_id[0][0]
                                    if 'library' in item:
                                        if 'filename' in item['library']:
                                            lib = item['library']['filename']
                                        if 'groupId' in item['library']:
                                            g_id = item['library']['groupId']
                                        if 'keyUuid' in item['library']:
                                            key_uuid = item['library']['keyUuid']
                                        if 'version' in item['library']:
                                            version = item['library']['version']
                                        if 'resultingShield' in item['library']:
                                            shield = item['library']['resultingShield']
                                            shield = str(shield).capitalize()
                                    if 'publishDate' in item:
                                        v_date = item['publishDate']
                                    if 'name' in item:
                                        v_name = item['name']
                                    if 'url' in item:
                                        v_url = item['url']
                                    if 'topFix' in item:
                                        if 'fixResolution' in item['topFix']:
                                            fix = item['topFix']['fixResolution'].replace("'","")
                                    vulnerabilities.append({"Severity": severity,
                                                            "SeverityValue": sev_value,
                                                            "ProjectName": pj_n,
                                                            "ProjectId": pj_id,
                                                            "Library": lib,
                                                            "GroupId": g_id,
                                                            "KeyUuid": key_uuid,
                                                            "Version": version,
                                                            "VulnPublishDate": v_date,
                                                            "Vulnerability": v_name,
                                                            "VulnerabilityUrl": v_url,
                                                            "Remediation": fix,
                                                            "ResultingShield": shield})
        return vulnerabilities

    @staticmethod
    def update_alert_status(pj_token, alert_uuid, status, comment):
        """Updates the status of an alert in Mend"""
        updated = False
        while MendAPI.token is None:
            MendAPI.token = MendAPI.mend_connect()
        payload = {
            'requestType': 'setAlertsStatus',
            'userKey': WS_KEY,
            'orgToken': WS_ORG,
            'alertUuids': [alert_uuid],
            'comments': comment,
            "status": status
            }
        headers = {
            'Content-Type': 'application/json'
            }
        response = requests.post(WS_REPORTS, headers = headers, json = payload, timeout=300)
        if response.status_code == 200:
            response = response.json()
            if 'message' in response:
                if 'Successfully set the alert' in response['message']:
                    updated = True
        return updated
