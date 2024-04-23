"""Commonly used functions for Mend SCA ticketing"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from common.database_appsec import select, update
from common.jira_functions import GeneralTicketing
parent = os.path.abspath('.')
sys.path.insert(1,parent)

load_dotenv()
WS_ORG = os.environ.get('WS_TOKEN')

class MendTicketing():
    """Provides functions required to create and update Mend SCA tickets"""
    @staticmethod
    def tickets_needed(repo):
        """Identifies Mend SCA group IDs that need tickets"""
        needs_tickets = None
        tickets_needed = None
        sql = f"""UPDATE OSFindings SET IngestionStatus = 'To Update' WHERE ((Status = 'New' AND
        LibraryLocations IS NOT NULL AND FoundInLastScan = 1)
        OR (Status NOT IN ('Closed','Closed In Ticket') AND
        IngestionStatus NOT IN ('Closed','False Positive','Project Removed','Security Exception')
        AND FoundInLastScan = 0 AND JiraIssueKey IS NOT NULL)) AND Repo = '{repo}'
        UPDATE OSFindings SET IngestionStatus = 'To Update', Status = 'Closed' WHERE
        FoundInLastScan = 0 AND JiraIssueKey IS NULL AND Status != 'Closed' AND
        (Status != 'Accepted' AND FindingType != 'License Violation') AND Repo = '{repo}'"""
        try:
            update(sql)
        except Exception:
            needs_tickets = None
        sql = f"""SELECT DISTINCT GroupId, FindingType FROM OSFindings WHERE IngestionStatus =
        'To Update' AND Repo = '{repo}'"""
        try:
            tickets_needed = select(sql)
        except Exception:
            needs_tickets = None
        if tickets_needed:
            needs_tickets = []
            for ticket in tickets_needed:
                needs_tickets.append({'GroupId': ticket[0], 'FindingType': ticket[1]})
        return needs_tickets

    @staticmethod
    def fp_and_ne_to_close(repo):
        """Identifies Mend SCA tickets for False Positive and Not Exploitable findings
        that have not been processed"""
        array = None
        tickets = None
        sql = f"""SELECT DISTINCT JiraIssueKey, Status FROM OSFindings
        WHERE JiraIssueKey IS NOT NULL AND Status IN ('False Positive', 'Not Exploitable') AND
        Repo = '{repo}' AND IngestionStatus != 'Closed' ORDER BY JiraIssueKey"""
        try:
            tickets = select(sql)
        except Exception:
            array = None
        if tickets:
            array = []
            for item in tickets:
                if not any(d['JiraIssueKey'] == item[0] for d in array):
                    array.append({'JiraIssueKey': item[0], 'FPCount': 0, 'NECount': 0})
                for i in array:
                    if item[0] == i['JiraIssueKey']:
                        if item[1] == 'False Positive':
                            i['FPCount'] = i['FPCount'] + 1
                        elif item[1] == 'Not Exploitable':
                            i['FPCount'] = i['FPCount'] + 1
        return array

    @staticmethod
    def create_jira_descriptions(repo,deleted_project=False,deleted_to_update=[],deleted_ticket=None):
        """Creates Jira descriptions for similarity IDs for a project"""
        jira_descriptions = []
        if deleted_project is False:
            try:
                need_tickets = MendTicketing.tickets_needed(repo)
            except Exception:
                return
        else:
            need_tickets = deleted_to_update
        if need_tickets is not None and need_tickets != []:
            for group in need_tickets:
                desc = ''
                sum_type = ''
                group_id = group['GroupId']
                v_type = group['FindingType']
                if deleted_project is False:
                    try:
                        MendTicketing.dedupe_mend_tickets(group_id, repo)
                    except Exception:
                        continue
                try:
                    base = MendTicketing.get_base_fields(group_id, v_type, repo)
                except Exception:
                    continue
                try:
                    severity = MendTicketing.get_severity(group_id, repo)
                except Exception:
                    continue
                if deleted_project is False:
                    try:
                        jira_issue = MendTicketing.get_jira_ticket(group_id, group['FindingType'],
                                                                   repo)
                    except Exception:
                        continue
                else:
                    jira_issue = deleted_ticket
                try:
                    has_lv = MendTicketing.get_vuln_license_violations(group_id, repo)
                except Exception:
                    continue
                if jira_issue is not None:
                    past_due = GeneralTicketing.check_past_due(jira_issue)
                    if past_due is True:
                        desc += 'h1. {color:red}*>>>>>  TICKET IS PAST DUE  <<<<<*{color}\n'
                updated_date = datetime.now().strftime("%B %d, %Y")
                desc += f"h6. Ticket updated by automation on {updated_date}.\n"
                if has_lv != {} and v_type != 'License Violation':
                    desc += f"\nh1. *{group_id} has 1 or more licenses in violation of our Open "
                    desc += f"Source Standard (PROG-IS18.05). Please address {has_lv['Ticket']}, "
                    desc += f"due {has_lv['DueDate']}.*\n"
                if group['FindingType'] == 'Vulnerability':
                    vulns = MendTicketing.get_vuln_fields(group_id, repo)
                    sum_type = 'Open Source Vulnerability:'
                    l_cnt = 0
                    desc += "\nh2. *Vulnerability Reference:*\n"
                    for vuln in vulns:
                        sev = vuln['Severity']
                        vln = vuln['Vulnerability']
                        url = vuln['VulnerabilityUrl']
                        rem = vuln['Remediation']
                        rem_l = 'Remediation'
                        color= 'darkgray'
                        if sev == "Critical":
                            color = 'darkred'
                        elif sev == "High":
                            color = 'red'
                        elif sev == "Medium":
                            color = 'orange'
                        c_s = '{color:' + str(color) + '}'
                        c_e = '{color}'
                        if url is not None:
                            desc += f"\n *[{vln}|{url}]* - {c_s}*{sev}*{c_e} \r*{rem_l}:* {rem}\n"
                        else:
                            desc += f"\n *{vln}* - {c_s}*{sev}*{c_e} \r*{rem_l}:* {rem}\n"
                    desc += "\nh2. *Detected In:*\n"
                    desc += "{color:purple}New{color} - Added to ticket during update\r-crossed"
                    desc += " out- - No longer found in scans\n"
                    desc += f"\n*{group_id} is detected in the following location(s):*\n"
                    l_cnt = 0
                    for row in base:
                        l_cnt += 1
                        status = row['Status']
                        pj_name = row['ProjectName']
                        pj_id = row['ProjectId']
                        library = row['Library']
                        key_uuid = row['KeyUuid']
                        locations = row['LibraryLocations'].split(",")
                        active = row['FoundInLastScan']
                        link = "https://saas.whitesourcesoftware.com/Wss/WSS.html#!libraryDetails;"
                        link += f"uuid={key_uuid};project={pj_id};orgToken={WS_ORG}"
                        desc += f"\n||#{l_cnt} - {library} in {pj_name}||\n"
                        if active == 0 or active is False or status in ('Closed','Closed in Ticket',
                                                                        'False Positive',
                                                                        'Project Deleted'):
                            desc += "|"
                            for lib in locations:
                                desc += f"-{lib}-\n"
                            desc += "|\n"
                        elif active == 1 or active is True:
                            desc += '|'
                            c_s = ''
                            c_e = ''
                            if status == 'New':
                                c_s = "{color:purple}"
                                c_e = "{color}"
                            for lib in locations:
                                desc += f"{c_s}{lib}{c_e}\r"
                            desc += f"[See details in Mend|{link}]|\n"
                elif group['FindingType'] == 'License Violation':
                    sum_type = 'Unapproved Open Source License Use:'
                    desc += "\nh2. *Overview:*\nApplication is using an unapproved license that "
                    desc += "puts all Prog entities at legal risk. Please reference *[the Prog "
                    desc += "Open Source Standard (PROG-IS18.05)|https://progleasing.sharepoint"
                    desc += ".com/:w:/r/Policies/_layouts/15/Doc.aspx?sourcedoc=%7B06841CF8-EF34-"
                    desc += "400E-A2CD-8C9BDA009A85%7D&file=IS18.05%20Open%20Source%20Standard%20"
                    desc += "-%20Published.docx&action=default&mobileredirect=true&cid=06c1d483-"
                    desc += "5786-4d93-a975-dedbbcb18a6f]* for additional information.\n"
                    desc += "\nh2. *Remediation:*\nEliminate use of this library in the """
                    desc += "application.\n\nh2. *Detected In:*\n"
                    desc += "{color:purple}New{color} - Added to ticket during update\r-crossed "
                    desc += "out- - No longer found in scans\n"
                    desc += f"\n*{group_id} is detected in the following location(s):*\n"
                    l_cnt = 0
                    for row in base:
                        l_cnt += 1
                        status = row['Status']
                        pj_name = row['ProjectName']
                        pj_id = row['ProjectId']
                        library = row['Library']
                        key_uuid = row['KeyUuid']
                        locations = row['LibraryLocations'].split(",")
                        vios = row['LicenseViolations'].replace(",",", ")
                        active = row['FoundInLastScan']
                        link = "https://saas.whitesourcesoftware.com/Wss/WSS.html#!libraryDetails;"
                        link += f"uuid={key_uuid};project={pj_id};orgToken={WS_ORG}"
                        desc += f"\n||#{l_cnt} - {library} in {pj_name}||\n"
                        if active == 1 or status == 'Security Exception' or active is True:
                            c_s = ''
                            c_e = ''
                            if status == 'New':
                                c_s = "{color:purple}"
                                c_e = "{color}"
                            locs = ''
                            for lib in locations:
                                locs += f"{c_s}{lib}{c_e}\n"
                            desc += f"|{c_s}*License(s) in violation of policy:* {vios}{c_e}\n"
                            desc += f"{locs}\n[See details in Mend|{link}]|\n"
                        elif active == 0 or active is False:
                            fixed = ''
                            for lib in locations:
                                fixed += f"-{lib}-\n"
                            desc += f"|-*License(s) in violation of policy:* {vios}-\n{fixed}|"
                desc += "\n----\n\n_To gain access to Mend for more details [enter a "
                desc += "request here|https://progleasing.service-now.com/prognation?"
                desc += "id=sc_cat_item&sys_id=3b99c4ed1b251150fe43db56dc4bcb40&sysparm_category="
                desc += "3f5579401b173890fe43db56dc4bcb6b]._\n\nTo ensure policies and standards "
                desc += "are adhered to, please reference the [Vulnerability Workflow|"
                desc += "https://progfin.atlassian.net/wiki/spaces/IS/pages/1725890700/"
                desc += "Vulnerability+Workflow] on Confluence."
                summary = None
                if base:
                    summary = f"{sum_type} {group_id} - {repo}"
                if group_id is not None and summary is not None:
                    jira_descriptions.append({'ExistingTicket': jira_issue,
                                            'Severity': severity,
                                            'Summary': summary,
                                            'Description': desc,
                                            'GroupId': group_id})
        return jira_descriptions

    @staticmethod
    def get_base_fields(group_id, finding_type, repo):
        """Gets the all necessary base fields for creating Jira descriptions"""
        base_fields = []
        sql = f"""SELECT DISTINCT ProjectName, ProjectId, Library,
        KeyUuid, LibraryLocations, LicenseViolations, Status, FoundInLastScan, Version FROM
        OSFindings WHERE GroupId = '{group_id}' AND repo = '{repo}' AND FindingType =
        '{finding_type}' AND GroupId IS NOT NULL ORDER BY FoundInLastScan DESC, Status,
        ProjectName, Library, LibraryLocations"""
        get_fields = select(sql)
        if get_fields:
            for row in get_fields:
                append = False
                if base_fields != []:
                    for d in base_fields:
                        if 'ProjectName' in d and 'KeyUuid' in d:
                            if not any(d['ProjectName'] == row[0] and d['KeyUuid'] ==
                                       row[4] for d in base_fields):
                                append = True
                else:
                    append = True
                if append is True:
                    pj_name = row[0]
                    pj_id = row[1]
                    lib = row[2]
                    key = row[3]
                    lib_loc = row[4]
                    violations = row[5]
                    status = row[6]
                    active = row[7]
                    version = row[8]
                    base_fields.append({'ProjectName': pj_name,
                                        'ProjectId': pj_id,
                                        'Library': lib,
                                        'KeyUuid': key,
                                        'LibraryLocations': lib_loc,
                                        'LicenseViolations': violations,
                                        'Status': status,
                                        'FoundInLastScan': active,
                                        'Version': version})
        return base_fields

    @staticmethod
    def get_severity(group_id, repo):
        """Gets the all necessary base fields for creating Jira descriptions"""
        severity = 'High'
        sql = f"""SELECT DISTINCT Severity, SeverityValue FROM OSFindings
        WHERE GroupId = '{group_id}' and repo = '{repo}' ORDER BY SeverityValue"""
        get_severity = select(sql)
        if get_severity:
            severity = get_severity[0][0]
        return severity

    @staticmethod
    def get_vuln_fields(group_id, repo):
        """Gets the all necessary vulnerabiltiy fields for creating Jira descriptions"""
        vuln_fields = []
        sql = f"""SELECT DISTINCT Vulnerability, Severity, SeverityValue FROM
        OSFindings WHERE GroupId = '{group_id}' AND repo = '{repo}' AND FindingType =
        'Vulnerability' ORDER BY SeverityValue"""
        get_vulns = select(sql)
        if get_vulns:
            vuln_list = []
            for vuln in get_vulns:
                vulnerability = vuln[0]
                severity = vuln[1]
                vuln_list.append({'Vulnerability': vulnerability, 'Severity': severity})
            vuln_list = list(
                {
                    dictionary['Vulnerability']: dictionary
                    for dictionary in vuln_list
                }.values()
            )
            for vuln in vuln_list:
                remediation = None
                sql = f"""SELECT DISTINCT Remediation FROM  OSFindings WHERE GroupId =
                '{group_id}' AND repo = '{repo}' AND FindingType = 'Vulnerability' AND
                Vulnerability = '{vuln['Vulnerability']}' AND Remediation IS NOT NULL"""
                get_rem = select(sql)
                if get_rem:
                    remediation = get_rem[0][0]
                link = f"https://www.mend.io/vulnerability-database/{vuln['Vulnerability']}"
                vuln_fields.append({'Vulnerability': vuln['Vulnerability'],
                                 'Severity': vuln['Severity'],
                                 'Remediation': remediation,
                                 'VulnerabilityUrl': link})
            vuln_fields = list(
                {
                    dictionary['Vulnerability']: dictionary
                    for dictionary in vuln_fields
                }.values()
                )
        return vuln_fields

    @staticmethod
    def get_vuln_license_violations(group_id, repo):
        """Determines if a library with a vulnerability also has a license violation"""
        l_violation = {}
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraDueDate FROM JiraIssues WHERE wsGroupId =
        '{group_id}' AND Repo = '{repo}' AND Source = 'Mend OS' AND JiraSummary LIKE
        '%Unapproved Open Source License Use%' AND JiraStatusCategory != 'Done' ORDER BY
        JiraDueDate"""
        get_violations = select(sql)
        if get_violations:
            l_violation = {}
            l_violation['Ticket'] = get_violations[0][0]
            l_violation['DueDate'] = get_violations[0][1]
        return l_violation

    @staticmethod
    def get_jira_ticket(group_id, finding_type, repo):
        """If an open Jira ticket exists for the group ID and finding type, return it"""
        if finding_type == 'Vulnerability':
            summary_field = f'Open Source Vulnerability: {group_id} - {repo}'
            stat_cat = "AND JiraStatusCategory != 'Done'"
        else:
            summary_field = f'Unapproved Open Source License Use: {group_id} - {repo}'
            stat_cat = "AND (JiraStatusCategory != 'Done' OR (JiraStatusCategory = 'Done' AND "
            stat_cat += "JiraDueDate > GETDATE() AND RITMTicket IS NOT NONE AND "
            stat_cat += "ExceptionApproved = 1))"
        ticket = None
        sql = f"""SELECT JiraIssueKey, JiraDueDate FROM JiraIssues WHERE wsGroupId = '{group_id}'
        AND Repo = '{repo}' AND Source = 'Mend OS' AND JiraSummary LIKE '%{summary_field}%'
        {stat_cat} ORDER BY JiraDueDate DESC"""
        get_ticket = select(sql)
        if get_ticket:
            ticket = get_ticket[0][0]
        return ticket

    @staticmethod
    def dedupe_mend_tickets(group_id, repo):
        """Dedups open Jira tickets"""
        success = False
        sql = f"""SELECT JiraIssueKey, CreatedDateTime, JiraStatusCategory FROM
                JiraIssues WHERE wsGroupId = '{group_id}' AND Repo = '{repo}' AND JiraSummary LIKE
                '%Open Source Vulnerability:%' AND JiraStatusCategory != 'Done' ORDER BY
                case when JiraStatusCategory = 'In Progress' then 1
                when JiraStatusCategory = 'To Do' then 2
                else 3 end asc, RITMTicket DESC, CreatedDateTime"""
        try:
            jira_tickets = select(sql)
        except Exception:
            return False
        if jira_tickets != []:
            jira_ticket = jira_tickets[0][0]
            jira_tickets.pop(0)
            for ticket in jira_tickets:
                close_ticket = ticket[0]
                comment = f"Duplicate of {jira_ticket}."
                comment += "Findings will be consolidated."
                try:
                    success = GeneralTicketing.cancel_jira_ticket(repo,close_ticket,
                                                                    comment)
                except Exception:
                    return False
                if success is True:
                    sql = f"""UPDATE OSFindings SET JiraIssueKey = '{jira_ticket}',
                            Status = 'New', IngestionStatus = 'To Update'
                            WHERE JiraIssueKey = '{close_ticket}'"""
                    try:
                        update(sql)
                    except Exception:
                        return success
        return success
