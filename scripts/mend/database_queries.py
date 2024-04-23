"""SQL queries for Mend scripts"""

import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.database_appsec import update, select, delete_row

class ReportQueries():
    """For processing Mend reports"""
    @staticmethod
    def get_repos_with_product_token_on_file():
        '''Returns a list of repos with a product token in ApplicationAutomation'''
        results = []
        sql = """SELECT DISTINCT Repo FROM ApplicationAutomation WHERE wsProductToken IS NOT
        NULL ORDER BY Repo"""
        results = select(sql)
        return results

    @staticmethod
    def get_product_token(repo):
        '''Returns the product token'''
        token = None
        sql = f"""SELECT TOP 1 wsProductToken FROM ApplicationAutomation WHERE Repo = '{repo}'
        AND wsProductToken IS NOT NULL"""
        g_token = select(sql)
        if g_token != []:
            token = g_token[0][0]
        return token

    @staticmethod
    def alert_exists(repo,project_name,key_uuid,alert_uuid):
        '''Checks if alert exists in OSAlerts'''
        exists = False
        sql = f"""SELECT TOP 1 Repo FROM OSAlerts WHERE Repo = '{repo}' AND ProjectName =
        '{project_name}' AND KeyUuid = '{key_uuid}' AND AlertUuid = '{alert_uuid}'"""
        results = select(sql)
        if results != []:
            exists = True
        return exists

    @staticmethod
    def get_alerts_to_sync(repo):
        '''Gets the alerts to sync'''
        to_sync = []
        sql = f"""SELECT DISTINCT ProjectName, KeyUuid, PolicyViolated, AlertUuid, AlertStatus
        FROM OSAlerts WHERE Repo = '{repo}'"""
        to_sync = select(sql)
        return to_sync

    @staticmethod
    def get_ticket_by_finding_type(repo,project_name,finding_type,key_uuid):
        '''Returns the JiraIssueKey'''
        jik = None
        sql = f"""SELECT DISTINCT JiraIssueKey FROM OSFindings WHERE Repo = '{repo}' AND
        ProjectName = '{project_name}' AND FindingType = '{finding_type}' AND KeyUuid =
        '{key_uuid}' AND Status != 'Closed' AND JiraIssueKey IS NOT NULL"""
        g_jik = select(sql)
        if g_jik != []:
            jik = g_jik[0][0]
        return jik

    @staticmethod
    def get_libraries_missing_data(repo):
        '''Gets info for libraries that are missing data'''
        libraries = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.Library,
        OSFindings.ProjectName, OSFindings.KeyUuid FROM OSFindings INNER JOIN OSProjects ON
        OSProjects.wsProjectName = OSFindings.ProjectName AND OSProjects.wsProductName =
        OSFindings.Repo WHERE (((OSFindings.LicenseViolations IS NULL OR
        OSFindings.LicenseViolations = '' OR OSFindings.LicenseViolations = 'None') AND
        OSFindings.FindingType = 'License Violation') OR OSFindings.GroupId IS NULL OR
        OSFindings.Version IS NULL OR OSFindings.LibraryLocations IS NULL) AND Repo = '{repo}'"""
        libraries = select(sql)
        return libraries

    @staticmethod
    def get_project_info(repo):
        '''Gets the project names and tokens for a repo'''
        products = []
        sql = f"""SELECT DISTINCT wsProjectName, wsProjectToken FROM OSProjects WHERE
        wsProductName = '{repo}' AND wsActive = 1"""
        products = select(sql)
        return products

    @staticmethod
    def get_active_tech_debt(repo):
        '''Gets info for tech debt findings with active alerts'''
        active = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.ProjectName,
        OSFindings.KeyUuid, OSFindings.AlertUuid, OSFindings.AlertStatus,
        OSFindings.JiraIssueKey FROM OSFindings INNER JOIN OSProjects ON
        OSFindings.Repo = OSProjects.wsProductName AND OSFindings.ProjectName =
        OSProjects.wsProjectName WHERE Status = 'Tech Debt' AND AlertStatus != 'Ignored' AND
        Repo = '{repo}'"""
        active = select(sql)
        return active

    @staticmethod
    def get_no_fix_active(repo,msg):
        '''Gets info for findings with no fix available and active alerts'''
        nfa = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.ProjectName,
        OSFindings.KeyUuid, OSFindings.AlertUuid, OSFindings.AlertStatus, OSFindings.JiraIssueKey,
        OSFindings.IngestionStatus FROM OSFindings INNER JOIN OSProjects ON OSFindings.Repo =
        OSProjects.wsProductName AND OSFindings.ProjectName = OSProjects.wsProjectName WHERE
        FindingType = 'Vulnerability' AND Remediation = '{msg}' AND (Status != 'No Fix Available'
        OR (Status = 'No Fix Available' AND AlertStatus = 'Active')) AND Repo = '{repo}'"""
        nfa = select(sql)
        return nfa

    @staticmethod
    def get_false_positives_active(repo):
        '''Gets info for false positive findings with active alerts'''
        g_fp = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.ProjectName,
        OSFindings.KeyUuid, OSFindings.AlertUuid, OSFindings.AlertStatus,
        OSFindings.JiraIssueKey FROM OSFindings INNER JOIN OSProjects ON
        OSFindings.Repo = OSProjects.wsProductName AND OSFindings.ProjectName =
        OSProjects.wsProjectName WHERE Status = 'False Positive' AND AlertStatus != 'Ignored' AND
        Repo = '{repo}'"""
        g_fp = select(sql)
        return g_fp

    @staticmethod
    def get_not_exploitables_active(repo):
        '''Gets info for not exploitable findings with active alerts'''
        g_ne = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.ProjectName,
        OSFindings.KeyUuid, OSFindings.AlertUuid, OSFindings.AlertStatus,
        OSFindings.JiraIssueKey FROM OSFindings INNER JOIN OSProjects ON
        OSFindings.Repo = OSProjects.wsProductName AND OSFindings.ProjectName =
        OSProjects.wsProjectName WHERE Status = 'Not Exploitable' AND AlertStatus != 'Ignored' AND
        Repo = '{repo}'"""
        g_ne = select(sql)
        return g_ne

    @staticmethod
    def get_past_due_tickets(repo):
        '''Gets past due Jira tickets for Mend findings'''
        g_pd = []
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraDueDate FROM JiraIssues WHERE Source LIKE
        '%Mend%' AND JiraStatusCategory != 'Done' AND JiraIssueKey IN (SELECT DISTINCT
        JiraIssueKey FROM OSFindings WHERE Status NOT IN ('Past Due','False Positive',
        'No Fix Available','Not Exploitable') AND IngestionStatus !=
        'Past Due') AND JiraDueDate < GETDATE() AND Repo = '{repo}'"""
        g_pd = select(sql)
        return g_pd

    @staticmethod
    def get_alerts_to_reactivate(repo):
        '''Gets alerts that need to be reactivated'''
        reactivate_alerts = []
        sql = f"""SELECT DISTINCT OSProjects.wsProjectToken, OSFindings.ProjectName,
        OSFindings.KeyUuid, OSFindings.AlertUuid, OSFindings.AlertStatus,
        OSFindings.JiraIssueKey FROM OSFindings INNER JOIN OSProjects ON
        OSFindings.Repo = OSProjects.wsProductName AND OSFindings.ProjectName =
        OSProjects.wsProjectName WHERE OSFindings.Status NOT IN ('Tech Debt','Accepted',
        'No Fix Available','False Positive','Not Exploitable') AND
        (OSFindings.AlertStatus = 'Ignored' OR (OSFindings.FoundInLastScan = 1 AND
        OSFindings.AlertStatus = 'Library removed')) AND Repo = '{repo}'"""
        reactivate_alerts = select(sql)
        return reactivate_alerts

    @staticmethod
    def get_exceptions_to_process(repo):
        '''Gets security exceptions to process'''
        etp = []
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraDueDate, RITMTicket FROM JiraIssues WHERE
        JiraStatusCategory != 'Done' AND Source LIKE '%Mend%' AND JiraIssueKey IN (SELECT DISTINCT
        JiraIssueKey FROM OSFindings) AND JiraDueDate > GETDATE() AND ExceptionApproved = 1 AND
        Repo = '{repo}' ORDER BY JiraIssueKey"""
        etp = select(sql)
        return etp

    @staticmethod
    def get_findings_to_close(repo):
        '''Gets a list of findings that are no longer found'''
        ftc = []
        sql = f"""SELECT DISTINCT OSFindings.ProjectName, OSProjects.wsProjectToken,
        OSFindings.AlertUuid, OSFindings.AlertStatus, OSFindings.JiraIssueKey,
        OSFindings.KeyUuid, OSFindings.FindingType FROM OSFindings
        INNER JOIN OSProjects ON OSFindings.ProjectName = OSProjects.wsProjectName AND
        OSFindings.Repo = OSProjects.wsProductName
        WHERE OSFindings.FoundInLastScan = 0 AND
        (OSFindings.Status NOT IN ('False Positive','No Fix Available','Not Exploitable',
        'Closed In Ticket','Closed') OR (OSFindings.IngestionStatus = 'To Update' AND
        FoundInLastScan = 0 AND OSFindings.AlertStatus NOT IN ('Active', 'Library Removed')))
        AND IngestionStatus != 'Closed' AND OSFindings.Repo = '{repo}'"""
        ftc = select(sql)
        return ftc

    @staticmethod
    def get_license_violations(repo):
        '''Retrieves alerts for License Violations'''
        l_violations = []
        sql = f"""SELECT DISTINCT ProjectName, ProjectId, Severity, Library, KeyUuid, AlertUuid,
        AlertStatus FROM OSAlerts WHERE Repo = '{repo}' AND PolicyViolated LIKE
        '%Licenses%' AND AlertStatus != 'Library removed' ORDER BY Library, ProjectId"""
        l_violations = select(sql)
        return l_violations

    @staticmethod
    def check_if_finding_exists_vuln(repo,pj_name,keyuuid,vuln):
        '''Checks if the finding exists'''
        exists = False
        sql = f"""SELECT Repo FROM OSFindings WHERE Repo = '{repo}' AND ProjectName = '{pj_name}'
        AND KeyUuid = '{keyuuid}' AND Status != 'Closed' AND Vulnerability = '{vuln}'"""
        f_exists = select(sql)
        if f_exists:
            exists = True
        return exists

    @staticmethod
    def get_project_key(repo):
        '''Returns the JiraProjectKey'''
        proj_key = None
        sql = f"""SELECT TOP 1 JiraProjectKey FROM ApplicationAutomation WHERE Repo = '{repo}' AND
        JiraProjectKey IS NOT NULL"""
        proj_key = select(sql)[0][0]
        return proj_key

    @staticmethod
    def get_past_due_finding(jira_issue_key):
        '''Gets the details for a Past Due finding'''
        details = []
        sql = f"""SELECT DISTINCT OSFindings.AlertUuid, OSProjects.wsProjectToken FROM OSFindings
        INNER JOIN OSProjects ON OSFindings.ProjectName = OSProjects.wsProjectName AND
        OSFindings.Repo = OSProjects.wsProductName WHERE OSFindings.AlertStatus = 'Ignored' AND
        OSFindings.Status NOT IN ('Past Due','False Positive','No Fix Available','To Update',
        'Not Exploitable') AND OSFindings.JiraIssueKey = '{jira_issue_key}' AND
        OSFindings.IngestionStatus != 'Past Due'"""
        details = select(sql)
        return details

    @staticmethod
    def get_security_exceptions(jira_issue_key):
        '''Gets security exceptions to ignore'''
        details = []
        sql = f"""SELECT DISTINCT OSFindings.AlertUuid, OSProjects.wsProjectToken FROM OSFindings
        INNER JOIN OSProjects ON OSFindings.ProjectName = OSProjects.wsProjectName AND
        OSFindings.Repo = OSProjects.wsProductName WHERE AlertStatus = 'Active' AND JiraIssueKey =
        '{jira_issue_key}'"""
        details = select(sql)
        return details

    @staticmethod
    def clear_no_fix_available(repo):
        '''Removes No Fix Available findings from OSFindings'''
        sql = f"""DELETE FROM OSFindings WHERE Status = 'No Fix Available' AND Repo = '{repo}'"""
        delete_row(sql)

    @staticmethod
    def reset_found_in_last_scan_lv(repo):
        '''Reset FoundInLastScan in the OSFindings table for license violations'''
        sql = f"""UPDATE OSFindings SET FoundInLastScan = 0 WHERE Repo = '{repo}' AND
        FindingType = 'License Violation'"""
        update(sql)

    @staticmethod
    def reset_found_in_last_scan_vuln(repo,pj_name):
        '''Reset FoundInLastScan in the OSFindings table for vulnerabilities'''
        sql = f"""UPDATE OSFindings SET FoundInLastScan = 0 WHERE Repo = '{repo}' AND
        ProjectName = '{pj_name}' AND FindingType = 'Vulnerability'"""
        update(sql)
