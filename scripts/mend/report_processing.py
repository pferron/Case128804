"""Runs maintenance scripts for updating Mend reports"""

import os
import sys
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from common.logging import TheLogs
from common.jira_functions import GeneralTicketing
from common.database_appsec import insert_multiple_into_table, update_multiple_in_table
from maintenance_jira_issues import update_jiraissues_for_tool_and_repo
from mend.api_connections import MendAPI
from mend.database_queries import ReportQueries

BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

class ScrVar():
    """Script-wide stuff"""
    process_product = 1
    fe_cnt = 0
    ex_cnt = 0
    cct_array = []

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class MendReports():
    """For processing Mend reports"""
    @staticmethod
    def single_repo_updates(repo,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs all of the updates for a single repo"""
        ScrVar.reset_exception_counts()
        TheLogs.log_headline(f'PROCESSING MEND REPORTING FOR {repo}',2,"#",main_log)
        try:
            get_token = ReportQueries.get_product_token(repo)
        except Exception as details:
            func = f"ReportQueries.get_product_token('{repo}')"
            e_code = "RP-SRU-001"
            TheLogs.function_exception(func,e_code,details,ex_log,main_log,ex_file)
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if get_token is not None:
            prod_token = get_token
            TheLogs.log_headline(f'REACTIVATING ALERTS IGNORED THROUGH THE UI FOR {repo}',3,"#",
                                 main_log)
            re_cnt = 0
            try:
                re_cnt += MendAPI.reactivate_manually_ignored_alerts(repo,prod_token)
            except Exception as details:
                func = f"MendAPI.reactivate_manually_ignored_alerts('{repo}','{prod_token}')"
                e_code = "RP-SRU-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
            TheLogs.log_info(f'{re_cnt} alert(s) reactivated',3,"*",main_log)
            TheLogs.log_headline(f'APPLYING PRODUCT POLICIES TO INVENTORY FOR {repo}',3,"#",
                                 main_log)
            try:
                product_policy = MendAPI.apply_product_policies(prod_token)
            except Exception as details:
                func = f"MendAPI.apply_product_policies('{prod_token}')"
                e_code = "RP-SRU-003"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
            if product_policy is True:
                TheLogs.log_info('Product policies successfully applied',3,"*",main_log)
                if ScrVar.fe_cnt == 0:
                    mend_vulnerability_report(repo,prod_token,main_log)
                if ScrVar.fe_cnt == 0:
                    sync_mend_alerts(repo,prod_token,main_log)
                if ScrVar.fe_cnt == 0:
                    sync_license_violations(repo,prod_token,main_log)
                if ScrVar.fe_cnt == 0:
                    sync_alerts_to_findings(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    update_missing_data(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    process_tech_debt(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    process_no_fix_available(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    process_false_positives(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    process_not_exploitables(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    process_past_due(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    findings_to_close(repo,main_log)
                if ScrVar.fe_cnt == 0:
                    reactivate_alerts(repo,main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def sync_mend_alerts(repo, prod_token,main_log=LOG):
    """Retrieves all alerts"""
    n_cnt = 0
    u_cnt = 0
    updates = []
    inserts = []
    TheLogs.log_headline(f'PROCESSING ALERTS FOR {repo}',3,"#",main_log)
    try:
        p_alerts = MendAPI.get_alerts(repo, prod_token)
    except Exception as details:
        func = f"MendAPI.get_alerts('{repo}', '{prod_token}')"
        e_code = "RP-SMA-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if p_alerts:
        for alert in p_alerts:
            if alert['ProjectToken'] is not None:
                try:
                    exists = ReportQueries.alert_exists(repo,alert['ProjectName'],alert['KeyUuid'],
                                                        alert['AlertUuid'])
                except Exception as details:
                    func = f"ReportQueries.alert_exists('{repo}','{alert['ProjectName']}',"
                    func += f"'{alert['KeyUuid']}','{alert['AlertUuid']}')"
                    e_code = "RP-SMA-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    continue
                if exists is True:
                    updates.append({'SET':{"DateDetected":alert['DateDetected'],'AlertStatus':
                                           alert['AlertStatus'],'InOSFindings':
                                           alert['InOSFindings'],'JiraIssueKey':
                                           alert['JiraIssueKey'],'Comments':alert['Comments']},
                                    'WHERE_EQUAL':{'Repo':repo,'ProjectName':alert['ProjectName'],
                                                   'KeyUuid':alert['KeyUuid'],'AlertUuid':
                                                   alert['AlertUuid']},
                                    'WHERE_NOT':None})
                else:
                    inserts.append({'Repo':repo,'ProductToken':prod_token,
                                    'ProjectName':alert['ProjectName'],'ProjectId':
                                    alert['ProjectId'],'Library':alert['Library'],'KeyUuid':
                                    alert['KeyUuid'],'Severity':alert['Severity'],'DateDetected':
                                    alert['DateDetected'],'AlertStatus':alert['AlertStatus'],
                                    'PolicyViolated':alert['PolicyViolated'],'AlertUuid':
                                    alert['AlertUuid'],'InOSFindings':alert['InOSFindings'],
                                    'ProjectToken':alert['ProjectToken']})
    try:
        u_cnt += update_multiple_in_table('OSAlerts',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{updates})"
        e_code = "RP-SMA-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{u_cnt} alert(s) updated",3,"*",main_log)
    try:
        n_cnt += insert_multiple_into_table('OSAlerts',inserts)
    except Exception as details:
        func = f"insert_multiple_into_table('OSAlerts',{inserts})"
        e_code = "RP-SMA-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{n_cnt} alert(s) added",3,"*",main_log)

def sync_alerts_to_findings(repo,main_log=LOG):
    """Ensures the AlertUuid and AlertStats are correct in OSFindings"""
    u_cnt = 0
    u_array = []
    TheLogs.log_headline(f'SYNCING ALERT INFO TO OSFindings FOR {repo}',3,"#",main_log)
    try:
        g_alerts = ReportQueries.get_alerts_to_sync(repo)
    except Exception as details:
        func = f"ReportQueries.get_alerts_to_sync('{repo}')"
        e_code = "RP-SATF-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if g_alerts:
        for alrt in g_alerts:
            f_type = 'Vulnerability'
            if 'Unapproved Licenses' in alrt[2]:
                f_type = 'License Violation'
            if alrt[4] != 'Library removed':
                u_array.append({'SET':{'AlertUuid':alrt[3],'AlertStatus':alrt[4]},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':alrt[0],'KeyUuid':alrt[1],
                                            'FindingType':f_type},
                                'WHERE_NOT':{'Status':'Closed'}})
            else:
                u_array.append({'SET':{'AlertUuid':alrt[3],'AlertStatus':alrt[4]},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':alrt[0],'KeyUuid':alrt[1],
                                            'FindingType':f_type}})
                u_array.append({'SET':{'AlertUuid':alrt[3],'AlertStatus':alrt[4],},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':alrt[0],'KeyUuid':alrt[1],
                                            'FindingType':f_type,'JiraIssueKey':None}})
    try:
        u_cnt += update_multiple_in_table('OSFindings',u_array)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{u_array})"
        e_code = "RP-SATF-002"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    TheLogs.log_info(f"{u_cnt} alert(s) updated",3,"*",main_log)

def sync_license_violations(repo,prod_token,main_log=LOG):
    """Pulls license violations into OSFindings from the processed alerts and updates the library
    and license information"""
    u_cnt = 0
    n_cnt = 0
    at_cnt = 0
    f_type = "License Violation"
    updates = []
    a_updates = []
    inserts = []
    TheLogs.log_headline(f'PROCESSING LICENSE VIOLATIONS FOR {repo}',3,"#",main_log)
    try:
        l_violations = ReportQueries.get_license_violations(repo)
    except Exception as details:
        func = f'get_license_violations({repo},{main_log})'
        e_code = "RP-SLV-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    try:
        ReportQueries.reset_found_in_last_scan_lv(repo)
    except Exception as details:
        func = f'reset_found_in_last_scan_lv({repo})'
        e_code = "RP-SLV-002"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if l_violations:
        for item in l_violations:
            try:
                exists = ReportQueries.get_ticket_by_finding_type(repo,item[0],f_type,item[4])
            except Exception as details:
                func = f"ReportQueries.get_ticket_by_finding_type('{repo}','{item[0]}','{f_type}',"
                func += f"'{item[4]}')"
                e_code = "RP-SLV-003"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.ex_cnt += 1
                continue
            l_seen = str(datetime.now()).split('.',1)[0]
            if exists != [] and exists is not None:
                ticket = exists
                updates.append({'SET':{'LastSeen':l_seen,'AlertUuid':item[5],'AlertStatus':item[6],
                                       'FoundInLastScan':1},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':item[0],'FindingType':
                                               f_type,'KeyUuid':item[4]}})
                if ticket is not None:
                    a_updates.append({'SET':{'JiraIssueKey':ticket},
                                    'WHERE_EQUAL':{'Repo':repo,'ProjectName':item[0],
                                                   'KeyUuid':item[4]}})
            else:
                if item[6] != 'Library removed':
                    inserts.append({'Repo':repo,'ProductToken':prod_token,'ProjectName':item[0],
                                    'ProjectId':item[1],'FindingType':f_type,'Severity':'High',
                                    'SeverityValue':1,'Library':item[3],'KeyUuid':item[4],
                                    'AlertUuid':item[5],'AlertStatus':item[6],'LastSeen':l_seen,
                                    'FoundInLastScan':1,'IngestionStatus':'To Update','Status':
                                    'New'})
    try:
        u_cnt += update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = 'RP-SLV-004'
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{u_cnt} license violation(s) updated",3,"*",main_log)
    try:
        at_cnt += update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = 'RP-SLV-005'
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"Tickets added to {at_cnt} {f_type} alerts",3,"*",main_log)
    try:
        n_cnt += insert_multiple_into_table('OSFindings',inserts)
    except Exception as details:
        func = f"insert_multiple_into_table('OSFindings',{inserts})"
        e_code = 'RP-SLV-006'
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{n_cnt} license violation(s) added",3,"*",main_log)

def update_missing_data(repo,main_log=LOG):
    """If GroupId, Version, and/or LicenseViolations are NULL, look up the data"""
    u_cnt = 0
    t_cnt = 0
    u_array = []
    t_array = []
    TheLogs.log_headline(f'UPDATING MISSING FIELDS FOR {repo}',3,"#",main_log)
    try:
        g_libs = ReportQueries.get_libraries_missing_data(repo)
    except Exception as details:
        func = f"ReportQueries.get_libraries_missing_data('{repo}')"
        e_code = "RP-UMD-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if g_libs:
        for lib in g_libs:
            proj_token = lib[0]
            library = lib[1]
            pj_name = lib[2]
            key_uuid = lib[3]
            try:
                fields = MendAPI.get_missing_fields(proj_token, library)
            except Exception as details:
                func = f"MendAPI.get_missing_fields('{proj_token}', '{library}')"
                e_code = "RP-UMD-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.ex_cnt += 1
                continue
            if fields is not None:
                lib_locations = 'not available'
                if fields['LibraryLocations'] is not None and fields['LibraryLocations'] != '':
                    lib_locations = fields['LibraryLocations']
                u_array.append({'SET':{'GroupId':fields['GroupId'],'Version':fields['Version'],
                                       'LicenseViolations':fields['LicenseViolations'],
                                       'LibraryLocations':lib_locations},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':pj_name,'Library':library,
                                               'KeyUuid':key_uuid}})
                u_array.append({'SET':{'IngestionStatus':'To Update'},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':pj_name,'Library':library,
                                               'KeyUuid':key_uuid,'Status':'New'},
                                'WHERE_NOT':{'LibraryLocations':None}})
    try:
        update_multiple_in_table('OSFindings',u_array)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{u_array})"
        e_code = "RP-UMD-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"Fields updated for {u_cnt} finding(s)",3,"*",main_log)
    try:
        update_multiple_in_table('OSFindings',t_array)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{t_array})"
        e_code = "RP-UMD-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{t_cnt} finding(s) marked as To Ticket",3,"*",main_log)

def mend_vulnerability_report(repo,prod_token,main_log=LOG):
    """Retrieves the vulnerability report and updates OSFindings"""
    try:
        projects = ReportQueries.get_project_info(repo)
    except Exception as details:
        func = f"ReportQueries.get_project_info('{repo}')"
        e_code = "RP-MVR-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if projects:
        u_cnt = 0
        n_cnt = 0
        inserts = []
        updates = []
        for proj in projects:
            u_cnt = 0
            n_cnt = 0
            pj_name = proj[0]
            pj_token = proj[1]
            TheLogs.log_headline(f'PROCESSING VULNERABILITIES FOR {repo} ({pj_name})',3,"#",
                                 main_log)
            try:
                report = MendAPI.vulnerability_report(repo,pj_token)
            except Exception as details:
                func = f"MendAPI.vulnerability_report('{repo}','{pj_token}')"
                e_code = "RP-MVR-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.ex_cnt += 1
                continue
            try:
                ReportQueries.reset_found_in_last_scan_vuln(repo,pj_name)
            except Exception as details:
                func = f"reset_found_in_last_scan_vuln({repo},{pj_name})"
                e_code = "RP-MVR-003"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.ex_cnt += 1
            if report != []:
                for vuln in report:
                    exists = False
                    try:
                        exists = ReportQueries.check_if_finding_exists_vuln(repo,
                                                                            vuln['ProjectName'],
                                                                            vuln['KeyUuid'],
                                                                            vuln['Vulnerability'])
                    except Exception as details:
                        func = f"check_if_finding_exists_vuln({repo},{vuln['ProjectName']},"
                        func += f"{vuln['KeyUuid']},{vuln['Vulnerability']})"
                        e_code = "RP-MVR-004"
                        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                                   EX_LOG_FILE)
                        ScrVar.ex_cnt += 1
                        continue
                    if exists is True:
                        l_seen = str(datetime.now()).split('.',1)[0]
                        updates.append({'SET': {'FoundInLastScan':1,'LastSeen':l_seen,
                                                'ResultingShield':vuln['ResultingShield'],
                                                'VulnerabilityUrl':vuln['VulnerabilityUrl'],
                                                'SeverityValue':vuln['SeverityValue']},
                                                'WHERE_EQUAL': {'Repo':repo,'ProjectName':
                                                                vuln['ProjectName'],
                                                                'Vulnerability':
                                                                vuln['Vulnerability'],'KeyUuid':
                                                                vuln['KeyUuid']},
                                                'WHERE_NOT': {'Status':'Closed'}})
                    else:
                        if vuln['ResultingShield'] != 'Green' or vuln['ResultingShield'] is None:
                            l_seen = str(datetime.now()).split('.',1)[0]
                            inserts.append({'Repo':repo,'ProductToken':prod_token,'LastSeen':
                                            l_seen,'FoundInLastScan':1,'IngestionStatus':'To Update',
                                            'Status':'New','FindingType':'Vulnerability',
                                            'ProjectName':vuln['ProjectName'],'Severity':
                                            vuln['Severity'],'SeverityValue':vuln['SeverityValue'],
                                            'ProjectId':vuln['ProjectId'],'Library':
                                            vuln['Library'],'GroupId':vuln['GroupId'],'KeyUuid':
                                            vuln['KeyUuid'],'Version':vuln['Version'],
                                            'VulnPublishDate':vuln['VulnPublishDate'],
                                            'Vulnerability':vuln['Vulnerability'],
                                            'VulnerabilityUrl':vuln['VulnerabilityUrl'],
                                            'Remediation':vuln['Remediation'],
                                            'ResultingShield':vuln['ResultingShield']})
            try:
                u_cnt += update_multiple_in_table('OSFindings',updates)
            except Exception as details:
                func = f"update_multiple_in_table('OSFindings',{updates})"
                e_code = "RP-MVR-005"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                           EX_LOG_FILE)
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f"{u_cnt} vulnerabilities updated",3,"*",main_log)
            try:
                n_cnt += insert_multiple_into_table('OSFindings',inserts)
            except Exception as details:
                func = f"insert_multiple_into_table('OSFindings',{inserts})"
                e_code = "RP-MVR-006"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                           EX_LOG_FILE)
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f"{n_cnt} vulnerabilities added",3,"*",main_log)

def process_tech_debt(repo,main_log=LOG):
    """Ensures that alerts are ignored for findings with a Tech Debt status"""
    u_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'IGNORING TECH DEBT ALERTS FOR {repo}',3,"#",main_log)
    try:
        td_to_ignore = ReportQueries.get_active_tech_debt(repo)
    except Exception as details:
        func = f"ReportQueries.get_active_tech_debt('{repo}')"
        e_code = "RP-PTD-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        return
    if td_to_ignore:
        for t_d in td_to_ignore:
            comment = f"To be addressed in tech debt ticket {t_d[5]}."
            if t_d[3] is not None and (t_d[4] is None or t_d[4] != 'Ignored'):
                try:
                    a_ignored = MendAPI.update_alert_status(t_d[0],t_d[3],'IGNORED',comment)
                except Exception as details:
                    func = f"MendAPI.update_alert_status('{t_d[0]}','{t_d[3]}','IGNORED', "
                    func += f"'{comment}')"
                    e_code = "RP-PTD-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    continue
                if a_ignored is True:
                    u_cnt +=1
                    updates.append({'SET':{'AlertStatus':'Ignored'},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':t_d[3]}})
                    a_updates.append({'SET':{'AlertStatus':'Ignored','Comments':comment,
                                             'JiraIssueKey':t_d[5]},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':t_d[3]}})
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-PTD-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-PTD-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{u_cnt} alert(s) ignored",3,"*",main_log)

def process_no_fix_available(repo,main_log=LOG):
    """Where no fix is available, update status to No Fix Available and ignore the alert"""
    c_cnt = 0
    i_cnt = 0
    updates = []
    a_updates = []
    nf_rem = 'Upgrade to version no_fix'
    TheLogs.log_headline(f'PROCESSING NO FIX AVAILABLE FOR {repo}',3,"#",main_log)
    try:
        fp_findings = ReportQueries.get_no_fix_active(repo,nf_rem)
    except Exception as details:
        func = f"ReportQueries.get_no_fix_active('{repo}','{nf_rem}')"
        e_code = "RP-PNFA-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        return
    if fp_findings:
        comment = "No fix is available for this vulnerability. Ignoring for now."
        for f_p in fp_findings:
            if f_p[3] is not None and (f_p[4] is None or f_p[4] != 'Ignored'):
                try:
                    a_ignored = MendAPI.update_alert_status(f_p[0],f_p[3],'IGNORED',comment)
                except Exception as details:
                    func = f"MendAPI.update_alert_status('{f_p[0]}','{f_p[3]}','IGNORED',"
                    func += f"'{comment}')"
                    e_code = "RP-PNFA-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    continue
                if a_ignored is True:
                    i_cnt += 1
                    updates.append({'SET':{'AlertStatus':'Ignored'},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3],'Remediation':
                                                   nf_rem}})
                    a_updates.append({'SET':{'AlertStatus':'Ignored','Comments':comment},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3]}})
            if f_p[5] is not None and f_p[6] != 'Closed':
                try:
                    closed = GeneralTicketing.close_or_cancel_jira_ticket(repo,f_p[5],comment,
                                                                          'Mend OS')
                except Exception as details:
                    func = f"GeneralTicketing.close_or_cancel_jira_ticket('{repo}','{f_p[5]}',"
                    func += f"'{comment}','Mend OS')"
                    e_code = "RP-PNFA-003"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    ScrVar.cct_array.append(f_p[5])
                    continue
                if closed is False:
                    ScrVar.cct_array.append(f_p[5])
                else:
                    c_cnt += 1
                    updates.append({'SET':{'Status':'No Fix Available','IngestionStatus':'Closed'},
                                    'WHERE_EQUAL':{'Repo':repo,'ProjectName':f_p[1],'Remediation':
                                                   nf_rem,'KeyUuid':f_p[2],'JiraIssueKey':f_p[5],
                                                   'FindingType':'Vulnerability'}})
            else:
                c_cnt += 1
                updates.append({'SET':{'Status':'No Fix Available','IngestionStatus':'Closed'},
                                'WHERE_EQUAL':{'Repo':repo,'ProjectName':f_p[1],'Remediation':
                                                nf_rem,'KeyUuid':f_p[2],'JiraIssueKey':None,
                                                'FindingType':'Vulnerability'}})
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-PNFA-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{i_cnt} alert(s) ignored",3,"*",main_log)
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-PNFA-005"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{c_cnt} ticket(s) closed or cancelled",3,"*",main_log)
    if c_cnt > 0:
        try:
            ReportQueries.clear_no_fix_available(repo)
        except Exception as details:
            func = f"ReportQueries.clear_no_fix_available('{repo}')"
            e_code = "RP-PNFA-006"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
        try:
            g_pk = ReportQueries.get_project_key(repo)
        except Exception as details:
            func = f"get_project_key('{repo})"
            e_code = "RP-PNFA-007"
            TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.ex_cnt += 1
            g_pk = None
        if g_pk is not None:
            update_jiraissues_for_tool_and_repo(repo,'mend os',main_log,LOG_EXCEPTION,EX_LOG_FILE)

def process_false_positives(repo,main_log=LOG):
    """When item is marked as False Positive, ignore the alert"""
    i_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'PROCESSING FALSE POSITIVES FOR {repo}',3,"#",main_log)
    try:
        fp_findings = ReportQueries.get_false_positives_active(repo)
    except Exception as details:
        func = f"ReportQueries.get_false_positives_active('{repo}')"
        e_code = "RP-PFP-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        return
    if fp_findings:
        comment = "This finding has been marked as a False Positive by ProdSec."
        for f_p in fp_findings:
            if f_p[3] is not None and (f_p[4] is None or f_p[4] != 'Ignored'):
                try:
                    a_ignored = MendAPI.update_alert_status(f_p[0],f_p[3],'IGNORED',comment)
                except Exception as details:
                    func = f"MendAPI.update_alert_status('{f_p[0]}','{f_p[3]}','IGNORED',"
                    func += f"'{comment}')"
                    e_code = "RP-PFP-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    continue
                if a_ignored is True:
                    i_cnt += 1
                    updates.append({'SET':{'AlertStatus':'Ignored'},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3]}})
                    a_updates.append({'SET':{'AlertStatus':'Ignored','Comments':comment},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3]}})
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-PFP-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-PFP-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{i_cnt} alert(s) ignored",3,"*",main_log)

def process_not_exploitables(repo,main_log=LOG):
    """When item is marked as Not Exploitable, ignore the alert"""
    i_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'PROCESSING NOT EXPLOITABLES FOR {repo}',3,"#",main_log)
    try:
        fp_findings = ReportQueries.get_not_exploitables_active(repo)
    except Exception as details:
        func = f"ReportQueries.get_not_exploitables_active('{repo}')"
        e_code = "RP-PNE-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        return
    if fp_findings:
        comment = "This finding has been marked as a Not Exploitable by ProdSec."
        for f_p in fp_findings:
            if f_p[3] is not None and (f_p[4] is None or f_p[4] != 'Ignored'):
                try:
                    a_ignored = MendAPI.update_alert_status(f_p[0],f_p[3],'IGNORED',comment)
                except Exception as details:
                    func = f"MendAPI.update_alert_status('{f_p[0]}','{f_p[3]}','IGNORED',"
                    func += f"'{comment}')"
                    e_code = "RP-PNE-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                    continue
                if a_ignored is True:
                    i_cnt += 1
                    updates.append({'SET':{'AlertStatus':'Ignored'},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3]}})
                    a_updates.append({'SET':{'AlertStatus':'Ignored','Comments':comment},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':f_p[3]}})
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-PNE-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-PNE-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{i_cnt} alert(s) ignored",3,"*",main_log)

def process_past_due(repo,main_log=LOG):
    """Ensures past due items are identified for ticketing updates and their alerts are active"""
    u_cnt = 0
    a_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'PROCESSING PAST DUE FINDINGS FOR {repo}',3,"#",main_log)
    try:
        has_pd = ReportQueries.get_past_due_tickets(repo)
    except Exception as details:
        func = f"ReportQueries.get_past_due_tickets('{repo}')"
        e_code = "RP-PPD-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if has_pd:
        for p_d in has_pd:
            comment = f"{p_d[0]} was due on {p_d[1]}. Reactivating alert."
            try:
                to_reactivate = ReportQueries.get_past_due_finding(p_d[0])
            except Exception as details:
                func = f"get_past_due_finding('{p_d[0]}')"
                e_code = "RP-PPD-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.ex_cnt += 1
                continue
            if to_reactivate != []:
                for t_r in to_reactivate:
                    try:
                        updated = MendAPI.update_alert_status(t_r[1],t_r[0],'Active',comment)
                    except Exception as details:
                        func = f"MendAPI.update_alert_status('{t_r[1]}','{t_r[0]}','Active',"
                        func += f"'{comment}')"
                        e_code = "RP-PPD-003"
                        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                                   EX_LOG_FILE)
                        ScrVar.ex_cnt += 1
                        continue
                    if updated is True:
                        a_cnt += 1
                        updates.append({'SET':{'AlertStatus':'Active','IngestionStatus':'To Update'},
                                        'WHERE_EQUAL':{'JiraIssueKey':p_d[0],'AlertUuid':t_r[0]}})
                        a_updates.append({'SET':{'AlertStatus':'Active'},
                                        'WHERE_EQUAL':{'ProjectToken':t_r[1],'AlertUuid':t_r[0]}})
            else:
                updates.append({'SET':{'IngestionStatus':'To Update',},
                                'WHERE_EQUAL':{'JiraIssueKey':p_d[0]},
                                'WHERE_NOT':{'IngestionStatus':'Past Due'}})
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-PPD-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{u_cnt} finding(s) updated",3,"*",main_log)
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-PPD-005"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{a_cnt} alert(s) reactivated",3,"*",main_log)

def reactivate_alerts(repo,main_log=LOG):
    """Ensures alerts for all applicable findings are set to active"""
    a_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'REACTIVATING APPLICABLE ALERTS FOR {repo}',3,"#",main_log)
    try:
        to_reactivate = ReportQueries.get_alerts_to_reactivate(repo)
    except Exception as details:
        func = f"ReportQueries.get_alerts_to_reactivate('{repo}')"
        e_code = "RP-RA-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.fe_cnt += 1
        return
    if to_reactivate:
        for r_a in to_reactivate:
            comment = f"To be addressed in {r_a[0]}."
            try:
                updated = MendAPI.update_alert_status(r_a[0],r_a[3],'Active',comment)
            except Exception as details:
                func = f"MendAPI.update_alert_status('{r_a[0]}', '{r_a[3]}', 'Active', "
                func += f"'{comment}')"
                e_code = "RP-RA-002"
                TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                            EX_LOG_FILE)
                ScrVar.ex_cnt += 1
                continue
            if updated is True:
                a_cnt += 1
                updates.append({'SET':{'AlertStatus':'Active'},
                                'WHERE_EQUAL':{'JiraIssueKey':r_a[5],'AlertUuid':r_a[3]}})
                a_updates.append({'SET':{'AlertStatus':'Active'},
                                'WHERE_EQUAL':{'ProjectToken':r_a[0],'AlertUuid':r_a[3]}})
    try:
        update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-RA-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-RA-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{a_cnt} alert(s) reactivated",3,"*",main_log)

def findings_to_close(repo,main_log=LOG):
    """Updates status to To Close when findings are not found in last scan"""
    a_cnt = 0
    u_cnt = 0
    updates = []
    a_updates = []
    TheLogs.log_headline(f'PROCESSING FINDINGS TO CLOSE FOR {repo}',3,"#",main_log)
    try:
        has_tc = ReportQueries.get_findings_to_close(repo)
    except Exception as details:
        func = f"ReportQueries.get_findings_to_close('{repo}')"
        e_code = "RP-FTC-001"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
        return
    if has_tc:
        for t_c in has_tc:
            if t_c[3] != 'Active' and t_c[3] != 'Library Removed':
                comment = 'No longer found in scans. Reactivating alert.'
                updated = False
                try:
                    updated = MendAPI.update_alert_status(t_c[1],t_c[2],'Active',comment)
                except Exception as details:
                    func = f"MendAPI.update_alert_status('{t_c[1]}','{t_c[2]}','Active',"
                    func += f"'{comment}')"
                    e_code = "RP-FTC-002"
                    TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,
                                               EX_LOG_FILE)
                    ScrVar.ex_cnt += 1
                if updated is True:
                    a_cnt += 1
                    updates.append({'SET':{'AlertStatus':'Active'},
                                    'WHERE_EQUAL':{'Repo':repo,'AlertUuid':t_c[2],
                                                   'ProjectName':t_c[0]}})
                    a_updates.append({'SET':{'AlertStatus':'Active'},
                                      'WHERE_EQUAL':{'Repo':repo,'AlertUuid':t_c[2],
                                                     'ProjectName':t_c[0]}})
            if t_c[4] is not None:
                updates.append({'SET':{'IngestionStatus':'To Update'},
                                'WHERE_EQUAL':{'KeyUuid':t_c[5],'ProjectName':t_c[0],'Repo':repo,
                                               'FindingType':t_c[6],'FoundInLastScan':0},
                                'WHERE_NOT':{'JiraIssueKey':None},
                                'WHERE_NOT_IN':{'IngestionStatus':['Closed','To Update']}})
    try:
        update_multiple_in_table('OSAlerts',a_updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSAlerts',{a_updates})"
        e_code = "RP-FTC-003"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{a_cnt} alert(s) reactivated",3,"*",main_log)
    try:
        u_cnt += update_multiple_in_table('OSFindings',updates)
    except Exception as details:
        func = f"update_multiple_in_table('OSFindings',{updates})"
        e_code = "RP-FTC-004"
        TheLogs.function_exception(func,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
        ScrVar.ex_cnt += 1
    TheLogs.log_info(f"{u_cnt} finding(s) updated",3,"*",main_log)
