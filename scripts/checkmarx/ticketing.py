"""Commonly used functions for Checkmarx ticketing"""

import os
import sys
import traceback
import inspect
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from common.alerts import Alerts
from common.database_appsec import (select,update_multiple_in_table,insert_multiple_into_table,
                                    update)
from common.jira_functions import GeneralTicketing
from common.vuln_info import VulnDetails
from common.logging import TheLogs
from checkmarx.api_connections import CxAPI
from checkmarx.report_processing import CxReports

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

class ScrVar():
    """For use in any of the functions"""
    ex_cnt = 0
    fe_cnt = 0
    src = ALERT_SOURCE.replace("-","\\")
    disclaimer = "\n----\n\n_For access to "
    req_link = "https://progleasing.service-now.com/prognation?id=sc_cat_item"
    req_link += "&sys_id=ccb2c9671b9d9110fe43db56dc4bcb18"
    req_link += "&sysparm_category=3f5579401b173890fe43db56dc4bcb6b"
    vw_link = "https://progfin.atlassian.net/wiki/spaces/IS/pages/1725890700/"
    vw_link += "Vulnerability+Workflow"
    nep_link = "https://progfin.atlassian.net/wiki/spaces/IS/pages/1376553354/"
    nep_link += "Non-exploitable+Process"
    disclaimer += f"Checkmarx, [enter a request here|{req_link}]."
    disclaimer += "_\n\nTo ensure policies and standards are adhered to, please "
    disclaimer += f"reference the [Vulnerability Workflow|{vw_link}]"
    disclaimer += " on Confluence.\n\nIf you believe this vulnerability is not "
    disclaimer += "exploitable, please {color:red}*do not close the ticket*{color}. Refer to "
    disclaimer += f"the [Non-Exploitable Process|{nep_link}] for the procedure for the "
    disclaimer += "correct workflow for non-exploitable status.\n\n "

    @staticmethod
    def update_exception_info(dictionary):
        """Adds counts and codes for exceptions returned from child scripts"""
        fatal_count = dictionary['FatalCount']
        exception_count = dictionary['ExceptionCount']
        ScrVar.fe_cnt += fatal_count
        ScrVar.ex_cnt += exception_count

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class CxTicketing():
    """Provides functions required to create and update Checkmarx tickets"""

    @staticmethod
    def create_and_update_tickets_by_query_src_and_dest(repo,proj_id,main_log=LOG,
                                                                  ex_log=LOG_EXCEPTION,
                                                                  ex_file=EX_LOG_FILE):
        """Groups findings by cxQuery, SourceFile/SourceObject, and DestinationFile/
        DestinationObject to create tickets"""
        t_updates = []
        t_inserts = []
        j_updates = []
        n_tkt = []
        u_tkt = []
        ScrVar.reset_exception_counts()
        TheLogs.log_headline(f'CREATING & UPDATING JIRA TICKETS FOR {repo}',2,"#",main_log)
        try:
            jira_info = GeneralTicketing.get_jira_info(repo,'Checkmarx')
        except Exception as e_details:
            func = f"GeneralTicketing.get_jira_info('{repo}','Checkmarx')"
            e_code = "CT-CAUTBQSAD-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if jira_info == [] or jira_info is None:
            TheLogs.log_info('No Jira info on file - cannot create tickets',2,"!",main_log)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        to_ticket = CxTicketing.get_needed_queries(proj_id,main_log,ex_log,ex_file)
        if to_ticket == []:
            TheLogs.log_info('No ticket creation/updates needed',2,"*",main_log)
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        tech_debt_boarded = jira_info[0][3]
        descs = CxTicketing.create_jira_descriptions_by_query_src_and_dest(to_ticket,proj_id,repo,
                                                                           tech_debt_boarded,
                                                                           main_log,ex_log,ex_file)
        if descs == {}:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        to_link = descs['LinkTickets']
        updates = descs['Descriptions']
        if updates == []:
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        for issue in updates:
            update_issue = None
            related_issues = None
            set_status = 'Open'
            set_i_status = 'Reported'
            if issue['RelatedTickets'] != {} and issue['RelatedTickets'] is not None:
                if issue['RelatedTickets']['ToAppend'] != []:
                    update_issue = issue['RelatedTickets']['ToAppend'][0]
                    statuses = CxTicketing.get_issue_status_to_set(update_issue,main_log,ex_log,
                                                                   ex_file)
                    set_status = statuses[0]
                    set_i_status = statuses[1]
                if issue['RelatedTickets']['Related'] != []:
                    related_issues = issue['RelatedTickets']['Related']
            if update_issue is not None:
                jira_title = issue['Summary']
                if jira_info[0][1] == 'PROG':
                    t_date = GeneralTicketing.get_ticket_due_date(update_issue,main_log,ex_log,
                                                                  ex_file)
                    if t_date['Results'] is not None:
                        jira_title = f"{jira_title} - {t_date['Results']}"
                try:
                    GeneralTicketing.update_jira_ticket(update_issue,repo,issue['Description'],
                                                        issue['Summary'])
                except Exception as e_details:
                    func = f"GeneralTicketing.update_jira_ticket('{update_issue}','{repo}',"
                    func += f"'{issue['Description']}','{issue['Summary']}')"
                    e_code = "CT-CAUTBQSAD-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                u_tkt.append(update_issue)
            else:
                try:
                    due_date = GeneralTicketing.set_due_date(issue['Severity'],tech_debt_boarded)
                except Exception as e_details:
                    func = f"GeneralTicketing.set_due_date('{issue['Severity']}',"
                    func += f"{tech_debt_boarded})"
                    e_code = "CT-CAUTBQSAD-003"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                try:
                    print('trying to ticket...')
                    update_issue = GeneralTicketing.create_jira_ticket(repo,jira_info[0][1],
                                                                issue['Summary'],
                                                                issue['Description'],
                                                                issue['Severity'],issue['Labels'],
                                                                due_date,jira_info[0][2])
                    # if "key='" in update_issue:
                    #     update_issue = update_issue.split("key='",1)[1].split("'",1)[0]
                    pk = jira_info[0][2].split("-",1)[0]
                    t_inserts.append({'Repo':repo,'OriginalEpic':jira_info[0][2],
                                    'OriginalEpicProjectKey':pk,'CurrentEpic':jira_info[0][2],
                                    'CurrentEpicProjectKey':pk,'JiraIssueKey':update_issue,
                                    'JiraProjectKey':pk,'OldJiraIssueKey':update_issue,
                                    'OldJiraProjectKey':pk,'cxProjectID':proj_id,'cxSimilarityID':
                                    issue['SimilarityIDs'],'JiraPriority':issue['Severity'],
                                    'JiraSummary':issue['Summary'],'JiraDueDate':due_date,
                                    'AssignedDueDate':due_date,'CreatedDateTime':datetime.now(),
                                    'Source':'Checkmarx'})
                    n_tkt.append(update_issue)
                except Exception as e_details:
                    func = f"GeneralTicketing.create_jira_ticket('{repo}','{jira_info[0][1]}',"
                    func += f"'{issue['Summary']}','{issue['Description']}','{issue['Severity']}',"
                    func += f"{issue['Labels']},'{due_date}','{jira_info[0][2]}')"
                    e_code = "CT-CAUTBQSAD-004"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
            ticket_set = CxTicketing.cx_ticket_set(update_issue,main_log,ex_log,ex_file)
            for item in issue['Findings']:
                rep_date = datetime.now()
                j_updates.append({'SET':{'cxSimilarityID':issue['SimilarityIDs']},
                                  'WHERE_EQUAL':{'JiraIssueKey':update_issue}})
                if set_status == 'Accepted':
                    t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':set_status,
                                            'IngestionStatus':set_i_status,'ReportedDate':rep_date},
                                      'WHERE_EQUAL':{'Status':'To Ticket','cxProjectID':proj_id,
                                                     'cxResultID':item},
                                      'WHERE_NOT_IN':{'Status':['False Positive','Not Exploitable']}})
                    t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':set_status,
                                            'IngestionStatus':set_i_status},
                                      'WHERE_EQUAL':{'Status':'To Update','cxProjectID':proj_id,
                                                    'cxResultID':item,'FoundInLastScan':1},
                                      'WHERE_NOT_IN':{'Status':['False Positive','Not Exploitable']}})
                else:
                    t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':set_status,
                                            'IngestionStatus':set_i_status,'ReportedDate':rep_date},
                                      'WHERE_EQUAL':{'Status':'To Ticket','cxProjectID':proj_id,
                                                     'cxResultID':item}})
                    t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':set_status,
                                            'IngestionStatus':set_i_status},
                                      'WHERE_EQUAL':{'Status':'To Update','cxProjectID':proj_id,
                                                    'cxResultID':item,'FoundInLastScan':1}})
                t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':'Closed In Ticket',
                                         'IngestionStatus':'Closed'},
                                    'WHERE_EQUAL':{'Status':'To Update','cxProjectID':proj_id,
                                                   'cxResultID':item,'FoundInLastScan':0}})
                t_updates.append({'SET':{'JiraIssueKey':update_issue,'Status':'Not Exploitable',
                                         'IngestionStatus':'Not Exploitable',
                                         'NotExploitableInTicket':1},
                                    'WHERE_EQUAL':{'IngestionStatus':'Not Exploitable',
                                                   'cxProjectID':proj_id,'cxResultID':item}})
                if ticket_set == 0:
                    try:
                        added_to_cx = CxAPI.add_ticket_to_cx(item,update_issue,main_log,ex_log,ex_file)
                        if added_to_cx is True:
                            t_updates.append({'SET':{'cxTicketSet':1},
                                            'WHERE_EQUAL':{'JiraIssueKey':update_issue}})
                            ticket_set = 1
                    except Exception as e_details:
                        func = f"CxAPI.add_ticket_to_cx('{item}','{update_issue}')"
                        e_code = "CT-CAUTBQSAD-005"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                ScrVar.src,inspect.stack()[0][3],
                                                traceback.format_exc())
                        ScrVar.ex_cnt += 1
            if to_link is True and related_issues is not None:
                try:
                    GeneralTicketing.add_related_ticket(update_issue,related_issues)
                except Exception as e_details:
                    func = f"GeneralTicketing.add_related_ticket('{update_issue}',"
                    func += f"'{related_issues}')"
                    e_code = "CT-CAUTBQSAD-006"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
        try:
            update_multiple_in_table('SASTFindings',t_updates)
        except Exception as e_details:
            func = f"update_multiple_in_table('SASTFindings',{t_updates})"
            e_code = "CT-CAUTBQSAD-007"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        try:
            update_multiple_in_table('JiraIssues',j_updates)
        except Exception as e_details:
            func = f"update_multiple_in_table('JiraIssues',{j_updates})"
            e_code = "CT-CAUTBQSAD-008"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        try:
            insert_multiple_into_table('JiraIssues',t_inserts)
        except Exception as e_details:
            func = f"insert_multiple_into_table('JiraIssues',{t_inserts})"
            e_code = "CT-CAUTBQSAD-009"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        try:
            update_multiple_in_table('ApplicationAutomation',
                                        [{'SET':{'cxTechDebtBoarded':1},
                                        'WHERE_EQUAL':{'cxProjectID':proj_id}}])
        except Exception as e_details:
            func = "update_multiple_in_table('ApplicationAutomation',[{SET:{"
            func += "'cxTechDebtBoarded':1},'WHERE_EQUAL':{'cxProjectID':" + str(proj_id)
            func += "}}])"
            e_code = "CT-CAUTBQSAD-010"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        n_cnt = len(n_tkt)
        TheLogs.log_info(f"{n_cnt} ticket(s) created",2,"*",main_log)
        for tkt in n_tkt:
            TheLogs.log_info(tkt,3,"-",main_log)
        u_cnt = len(u_tkt)
        TheLogs.log_info(f"{u_cnt} ticket(s) updated",2,"*",main_log)
        for tkt in u_tkt:
            TheLogs.log_info(tkt,3,"-",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def cx_ticket_set(jira_issue,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Checks whether the ticket has been set in Checkmard findings"""
        ticket_set = 0
        sql = f"""SELECT cxTicketSet FROM SASTFindings WHERE JiraIssueKey = '{jira_issue}' AND
        cxTicketSet = 1"""
        try:
            is_set = select(sql)
        except Exception as e_details:
            e_code = "CT-CTS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return ticket_set
        if is_set != []:
            ticket_set = 1
        return ticket_set

    @staticmethod
    def get_issue_status_to_set(jira_issue,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Ensures the ticket is still open and pulls back the status to set in SASTFindings"""
        set_status = 'Open'
        set_i_status = 'Reported'
        sql = f"""SELECT TOP 1 JiraDueDate, TechDebt, RITMTicket, ExceptionApproved FROM JiraIssues
        WHERE JiraIssueKey = '{jira_issue}' AND JiraStatusCategory != 'Done'"""
        try:
            ticket_info = select(sql)
        except Exception as e_details:
            e_code = "CT-GISTS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return set_status, set_i_status
        if ticket_info != []:
            if ticket_info[0][2] is not None and ticket_info[0][3] == 1:
                set_status = 'Accepted'
                set_i_status = 'Reported'
            if ticket_info[0][1] == 1:
                set_status = 'Tech Debt'
                set_i_status = 'Reported'
            if ticket_info[0][0] is not None:
                due_date = datetime.strptime(str(ticket_info[0][0]),'%Y-%m-%d')
                today = datetime.now()
                if due_date.date() < today.date():
                    set_status = 'Past Due'
                    set_i_status = 'Reported'
        return set_status, set_i_status

    @staticmethod
    def create_jira_descriptions_by_query_src_and_dest(queries_to_ticket,proj_id,repo,
                                                       tech_debt_boarded,main_log=LOG,
                                                       ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Creates descriptions to pass through to the Jira API"""
        all_descriptions = {}
        descriptions = []
        try:
            link_tickets = GeneralTicketing.has_related_link_type(repo)
        except Exception as e_details:
            func = f"GeneralTicketing.has_related_link_type('{repo}')"
            e_code = "CT-CJDBQSAD-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return all_descriptions
        if tech_debt_boarded == 1:
            labels = ['security_finding', repo.lower()]
        else:
            labels = ['security_finding','tech_debt',repo.lower()]
        for query in queries_to_ticket:
            desc_details = {}
            findings_list = []
            sims = ''
            cx_query = query[0]
            source_file = query[1]
            source_name = source_file.split("/")[-1]
            dest_file = query[2]
            dest_name = dest_file.split("/")[-1]
            line_cnt = int(query[3])
            is_pd = ''
            sum_files = f"{source_name} to {dest_name}"
            summary = f'SAST Finding: {cx_query} ({sum_files}) - {repo}'
            desc_details['Summary'] = summary
            updated_date = datetime.now().strftime("%B %d, %Y")
            td_message = f"Updated by automation on {updated_date}"
            tkt_des = "{panel:bgColor=#deebff}" + str(td_message) + "{panel}\n"
            desc_details['Severity'] = CxTicketing.get_most_severe(cx_query,proj_id,main_log,
                                                                   ex_log,ex_file)
            desc_details['Labels'] = labels
            desc_details['RelatedTickets'] = CxTicketing.get_related_tickets_by_query(summary,
                                                                                      main_log,
                                                                                      ex_log,
                                                                                      ex_file)
            if desc_details['RelatedTickets'] != {} and desc_details['RelatedTickets'] is not None:
                if desc_details['RelatedTickets']['ToAppend'] != []:
                    jira_issue = desc_details['RelatedTickets']['ToAppend'][0]
                    past_due = False
                    if jira_issue is not None:
                        try:
                            past_due = GeneralTicketing.check_past_due(jira_issue)
                        except Exception as e_details:
                            func = f"GeneralTicketing.check_past_due('{jira_issue}')"
                            e_code = "CT-CJDBQSAD-002"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                    if past_due is True:
                        is_pd = '\n{panel:bgColor=#ffebe6}*THIS TICKET IS PAST DUE*{panel}\n'
            sim_ids = CxTicketing.get_sim_ids_by_query_src_and_dest(cx_query,source_file,
                                                                              dest_file,proj_id,
                                                                              main_log,ex_log,
                                                                              ex_file)
            if sim_ids == []:
                continue
            get_query_desc = CxTicketing.get_query_fields(sim_ids[0],proj_id,main_log,ex_log,
                                                          ex_file)
            if get_query_desc != {}:
                if get_query_desc['QueryDescription'] is not None:
                    tkt_des += f"\nh2. *Overview:*\n{get_query_desc['QueryDescription']}\n"
            add_cwes = ''
            for item in sim_ids:
                sims += f'{item},'
                get_cwes = CxTicketing.get_cwe_details(item,proj_id,main_log,ex_log,ex_file)
                if get_cwes is not None:
                    add_cwes += get_cwes['CWEs']
            if add_cwes != '':
                tkt_des += f"{get_cwes['CWEs']}\n"
            tkt_des += "\nh2. *Finding Details:*\n{quote}*Source File:*\r" + str(source_file)
            tkt_des += "\n*Destination File:*\r" + str(dest_file) + "{quote}"
            tkt_des += "\n|{panel:bgColor=#fffae6}Added during update{panel}|{panel:bgColor=#e3fcef}No longer seen in scans{panel}|\n"
            for item in sim_ids:
                sim_id = item
                findings = CxTicketing.get_findings_for_query_src_and_dest(cx_query,
                                                                    proj_id,sim_id,main_log,
                                                                    ex_log,ex_file)
                if findings == []:
                    continue
                tkt_des += f'\nh3. *For Similarity ID {sim_id}:*\n'
                if line_cnt > 54:
                    tkt_des += '\n||Source & Link||Destination||\n'
                else:
                    tkt_des += '\n||Description & Link||Source & Destination||\n'
                for fdg in findings:
                    findings_list.append(fdg[6])
                    t = ''
                    te = ''
                    if fdg[4] == 0 or fdg[4] is None or fdg[5] in ('To Close','Closed in Ticket'):
                        t = '{panel:bgColor=#e3fcef}'
                        te = '{panel}'
                    if fdg[5] in ('To Ticket','To Update'):
                        t = '{panel:bgColor=#fffae6}'
                        te = '{panel}'
                    full_source = fdg[0].split("; ")
                    s_object = f'{full_source[1].replace("Object: ","")}'
                    s_line = f'{full_source[2].replace("Line: ","")}'
                    s_col = f'{full_source[3].replace("Column: ","")}'
                    f_source_obs = f"*Source Object:* {s_object}\r*Line:* {s_line}\r"
                    f_source_obs += f"*Column:* {s_col}\n"
                    f_source = f_source_obs.replace("None","N/A")
                    full_dest = fdg[1].split("; ")
                    d_object = full_dest[1].replace("Object: ","")
                    d_line = full_dest[2].replace("Line: ","")
                    d_col = full_dest[3].replace("Column: ","")
                    f_dest_obs = f"*Destination Object:* {d_object}\r*Line:* {d_line}\r"
                    f_dest_obs += f"*Column:* {d_col}\n"
                    f_dest = f_dest_obs.replace("None","N/A")
                    s_to_d = f"{t}{f_source} \n{f_dest}{te}"
                    f_link = f"*[See in Checkmarx|{fdg[3]}]*"
                    if line_cnt > 54:
                        tkt_des += f"|{t}{f_source}{te}\n{f_link}|{t}{f_dest}{te}|\n"
                    else:
                        tkt_des += f"|{fdg[2]}\n{f_link}|{s_to_d}|\n"
            tkt_des = f'{is_pd}{tkt_des}{ScrVar.disclaimer}'
            sims = sims[:-2]
            desc_details['SimilarityIDs'] = sims
            desc_details['Description'] = tkt_des
            desc_details['Findings'] = findings_list
            descriptions.append(desc_details)
        all_descriptions = {'Descriptions':descriptions,'LinkTickets':link_tickets}
        return all_descriptions

    @staticmethod
    def get_sim_ids_by_query_src_and_dest(cx_query,source,destination,proj_id,
                                                    main_log=LOG,ex_log=LOG_EXCEPTION,
                                                    ex_file=EX_LOG_FILE):
        """Gets a list of the similarity IDs to include in the by-query ticket"""
        results = []
        sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE
        cxProjectID = {proj_id} AND cxQuery = '{cx_query}' AND SourceFile = '{source}' AND
        DestinationFile = '{destination}' AND Status != 'Closed' AND (TicketClosed IS NULL OR
        TicketClosed != 1) AND cxResultState != 'To Verify' ORDER BY cxSimilarityID"""
        try:
            similarity_ids = select(sql)
        except Exception as e_details:
            e_code = "CT-GSIBQ-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return results
        if similarity_ids != []:
            for sim_id in similarity_ids:
                results.append(sim_id[0])
        return results

    @staticmethod
    def get_findings_for_query_src_and_dest(cx_query,proj_id,sim_id,main_log=LOG,
                                                      ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the line items to include in the query-based ticket"""
        results = []
        sql = f"""SELECT DISTINCT cxSource, cxDestination, cxResultDescription, cxLink,
        FoundInLastScan, Status, cxResultID FROM SASTFindings WHERE cxProjectID = {proj_id} AND
        cxQuery = '{cx_query}' AND Status != 'Closed' AND (TicketClosed IS NULL OR
        TicketClosed != 1) AND cxResultState != 'To Verify' AND cxSimilarityID = {sim_id}"""
        try:
            results = select(sql)
        except Exception as e_details:
            e_code = "CT-GFFQSAD-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return results
        return results

    @staticmethod
    def create_and_update_tickets(repo,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                                  ex_file=EX_LOG_FILE):
        """Creates new/updates existing tickets for a repo"""
        ScrVar.reset_exception_counts()
        n_cnt = 0
        n_tkt = []
        u_cnt = 0
        u_tkt = []
        insert_array = []
        update_array = []
        TheLogs.log_headline(f'CREATING & UPDATING JIRA TICKETS FOR {repo}',2,"#",main_log)
        to_ticket = CxTicketing.tickets_needed(proj_id,main_log,ex_log,ex_file)
        if to_ticket != []:
            try:
                jira_info = GeneralTicketing.get_jira_info(repo,'Checkmarx')
            except Exception as e_details:
                func = f"GeneralTicketing.get_jira_info('{repo}','Checkmarx)"
                e_code = "CT-CAUT-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
            jira_descriptions = []
            if jira_info != []:
                jira_descriptions = CxTicketing.create_jira_descriptions(to_ticket,proj_id,repo,
                                                                         main_log,ex_log,ex_file)
            if jira_descriptions != []:
                for item in jira_descriptions:
                    labels = None
                    td_status = None
                    proj_key = jira_info[0][1]
                    epic = jira_info[0][2]
                    td_boarded = jira_info[0][3]
                    s_u = ''
                    if td_boarded == 1:
                        labels = ['security_finding', repo.lower()]
                        td_status = 0
                        s_u = 'Open'
                    else:
                        labels = ['security_finding','tech_debt',repo.lower()]
                        td_status = 1
                        s_u = 'Tech Debt'
                    sim_id = item['cxSimilarityId']
                    update_ticket = item['ExistingTicket']
                    severity = item['Severity']
                    summary = item['Summary']
                    description = item['Description']
                    lnk_rel_tickets = None
                    if update_ticket is not None:
                        if jira_info[0][1] == 'PROG':
                            t_date = GeneralTicketing.get_ticket_due_date(update_ticket,main_log,ex_log,
                                                                        ex_file)
                            if t_date['Results'] is not None:
                                summary = f"{summary} - {t_date['Results']}"
                        try:
                            GeneralTicketing.update_jira_ticket(update_ticket,
                                                                repo,
                                                                description,
                                                                summary)
                        except Exception as e_details:
                            func = f"GeneralTicketing.update_jira_ticket('{update_ticket}',"
                            func+= f"'{repo}','{description}','{summary}')"
                            e_code = "CT-CAUT-002"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                        ex_file,ScrVar.src,
                                                        inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        u_tkt.append(update_ticket)
                        r_date = str(datetime.now()).split('.',1)[0]
                        update_array.append({'SET':{'JiraIssueKey':update_ticket,
                                                    'IngestionStatus':'Reported'},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':None}})
                        update_array.append({'SET':{'ReportedDate':r_date},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':update_ticket,
                                                            'ReportedDate':None}})
                        update_array.append({'SET':{'Status':s_u},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':update_ticket},
                                                'WHERE_NOT_IN':{'Status':['Accepted',
                                                                        'Not Exploitable',
                                                                        'Tech Debt',s_u,
                                                                        'Closed',
                                                                        'Closed In Ticket']}})
                        update_array.append({'SET':{'Status':'Closed In Ticket',
                                                    'IngestionStatus':'Closed In Ticket'},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':update_ticket},
                                                'CUSTOM_OR':["Status = 'To Close'",
                            "Status IN ('Tech Debt','Accepted','Open') AND FoundInLastScan = 0"]})
                        update_array.append({'SET':{'NotExploitableInTicket':1},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':update_ticket,
                                                            'Status':'Not Exploitable'}})
                        lnk_rel_tickets = update_ticket
                    else:
                        add_comment = None
                        try:
                            due_date = GeneralTicketing.set_due_date(severity,td_boarded)
                        except Exception as e_details:
                            func = f"GeneralTicketing.set_due_date('{severity}','{td_boarded}')"
                            e_code = "CT-CAUT-003"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                        ex_file,ScrVar.src,
                                                        inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        try:
                            repo_exceptions = GeneralTicketing.has_repo_exceptions(repo,due_date,main_log,
                                                                                ex_log,ex_file)
                            # {'RITMTicket':None,'Standard':None,'ApprovedDate':None,'Duration':None,'Due':None}
                        except Exception as e_details:
                            func = f"GeneralTicketing.has_repo_exceptions('{repo}','{due_date}')"
                            e_code = "CT-CAUT-004"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                        ex_file,ScrVar.src,
                                                        inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        if repo_exceptions['Due'] is not None:
                            due_date = repo_exceptions['Due']
                            add_comment = f"Security exception {repo_exceptions['RITMTicket']} to "
                            add_comment += f"{repo_exceptions['Standard']} was approved for "
                            add_comment += f"{repo_exceptions['Duration']} month(s) on "
                            add_comment += f"{str(repo_exceptions['Approved'])}. Due date is extended to "
                            add_comment += f"{str(repo_exceptions['Due'])}."
                        if jira_info[0][1] == 'PROG':
                            summary = f"{summary} - {due_date}"
                        try:
                            t_new = GeneralTicketing.create_jira_ticket(repo,proj_key,summary,
                                                                        description,severity,
                                                                        labels,due_date,epic)
                        except Exception as e_details:
                            func = f"GeneralTicketing.create_jira_ticket('{repo}',"
                            func+= f"'{proj_key}','{summary}','{description}',"
                            func+= f"'{severity}','{labels}','{due_date}','{epic}')"
                            e_code = "CT-CAUT-005"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                        ex_file,ScrVar.src,
                                                        inspect.stack()[0][3],
                                                        traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        n_tkt.append(t_new)
                        if add_comment is not None:
                            try:
                                GeneralTicketing.add_comment_to_ticket(repo,t_new,add_comment)
                            except Exception as e_details:
                                func = f"GeneralTicketing.add_comment_to_ticket('{repo}',"
                                func += f"'{t_new}','{add_comment}')"
                                e_code = "CT-CAUT-006"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                           ex_file,ScrVar.src,inspect.stack()[0][3],
                                                           traceback.format_exc())
                                ScrVar.ex_cnt += 1
                        created = str(datetime.now()).split('.',1)[0]
                        insert_array.append({'Repo':repo,'OriginalEpic':epic,
                                                'OriginalEpicProjectKey':proj_key,
                                                'CurrentEpic':epic,'CurrentEpicProjectKey':
                                                proj_key,'JiraIssueKey':t_new,
                                                'JiraProjectKey':proj_key,'cxProjectID':
                                                proj_id,'cxSimilarityID':sim_id,'JiraSummary':
                                                summary,'JiraPriority':severity,'JiraDueDate':
                                                due_date,'AssignedDueDate':due_date,
                                                'JiraStatus':'Backlog','JiraStatusCategory':
                                                'To Do','TechDebt':td_status,
                                                'CreatedDateTime':created,
                                                'Source':'Checkmarx'})
                        update_array.append({'SET':{'Status':'Open',
                                                    'IngestionStatus':'Reported',
                                                    'JiraIssueKey':t_new},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id},
                                                'WHERE_NOT_IN':{'Status':['Accepted',
                                                                        'Not Exploitable',
                                                                        'Tech Debt',s_u,
                                                                        'Closed',
                                                                        'Closed In Ticket']}})
                        update_array.append({'SET':{'ReportedDate':created},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'ReportedDate':None,
                                                            'JiraIssueKey':t_new}})
                        update_array.append({'SET':{'Status':s_u},
                                                'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxSimilarityID':sim_id,
                                                            'JiraIssueKey':t_new},
                                                'WHERE_NOT_IN':{'Status':['Accepted',
                                                                        'Not Exploitable',
                                                                        'Tech Debt',s_u,
                                                                        'Closed',
                                                                        'Closed In Ticket']}})
                        lnk_rel_tickets = t_new
                    if (item['RelatedTickets'] != [] and item['RelatedTickets'] is not None
                        and lnk_rel_tickets is not None):
                        for tkt in item['RelatedTickets']:
                            try:
                                GeneralTicketing.add_related_ticket(lnk_rel_tickets,
                                                                item['RelatedTickets'])
                            except Exception as e_details:
                                func = f"GeneralTicketing.add_related_ticket({lnk_rel_tickets},"
                                func += f"{item['RelatedTickets']})"
                                e_code = "CT-CAUT-007"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                           ex_file,ScrVar.src,
                                                           inspect.stack()[0][3],
                                                           traceback.format_exc())
                                ScrVar.ex_cnt += 1

            try:
                update_multiple_in_table('SASTFindings',update_array)
            except Exception as e_details:
                func = f"update_multiple_in_table('SASTFindings',{update_array})"
                e_code = "CT-CAUT-008"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            try:
                insert_multiple_into_table('JiraIssues',insert_array)
            except Exception as e_details:
                func = f"insert_multiple_into_table('JiraIssues',{update_array})"
                e_code = "CT-CAUT-009"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
        sql = f"""UPDATE ApplicationAutomation SET cxTechDebtBoarded = 1 WHERE Repo = '{repo}' AND
            (cxTechDebtBoarded IS NULL OR cxTechDebtBoarded = 0) UPDATE Applications SET
            TechDebtBoarded = 1 WHERE Repo = '{repo}' AND (TechDebtBoarded IS NULL OR
            TechDebtBoarded = 0)"""
        try:
            update(sql)
        except Exception as e_details:
            e_code = "CT-CAUT-010"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        n_cnt = len(n_tkt)
        TheLogs.log_info(f"{n_cnt} ticket(s) created",2,"*",main_log)
        for tkt in n_tkt:
            TheLogs.log_info(tkt,3,"-",main_log)
        u_cnt = len(u_tkt)
        TheLogs.log_info(f"{u_cnt} ticket(s) updated",2,"*",main_log)
        for tkt in u_tkt:
            TheLogs.log_info(tkt,3,"-",main_log)
        if u_cnt > 0 or n_cnt > 0:
            u_statuses = CxReports.update_finding_statuses(proj_id,main_log,ex_log,ex_file)
            ScrVar.update_exception_info(u_statuses)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def close_or_cancel_not_exploitable(repo,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                                        ex_file=EX_LOG_FILE):
        """If a finding is marked as Not Exploitable and the ticket is open, close it"""
        ScrVar.reset_exception_counts()
        cl_cnt = 0
        ne_array = []
        msg = f'CLOSING OR CANCELLING TICKETS FOR NOT EXPLOITABLE FINDINGS FOR {repo}'
        TheLogs.log_headline(msg,3,"#",main_log)
        sql= f"""SELECT DISTINCT JiraIssueKey FROM SASTFindings WHERE cxProjectID = {proj_id}
        AND Status = 'Not Exploitable' AND (TicketClosed IS NULL OR TicketClosed = 0) AND
        JiraIssueKey IS NOT NULL AND JiraIssueKey NOT IN (SELECT DISTINCT JiraIssueKey FROM
        SASTFindings WHERE cxProjectID = 10519 AND Status != 'To Close' AND Status !=
        'Closed In Ticket' AND JiraIssueKey IS NOT NULL) AND (AcctCompComment = 0 OR
        AcctCompComment IS NULL) AND (TicketClosed = 0 OR TicketClosed IS NULL) AND JiraIssueKey
        NOT IN (SELECT DISTINCT JiraIssueKey FROM SASTFindings WHERE cxProjectID = {proj_id} AND
        FoundInLastScan = 1 AND Status != 'Not Exploitable')"""
        try:
            to_close = select(sql)
        except Exception as e_details:
            e_code = "CT-COCNE-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if to_close != []:
            for item in to_close:
                ticket = item[0]
                comment = "Findings on this ticket have been marked as Not Exploitable by ProdSec."
                try:
                    closed = GeneralTicketing.close_or_cancel_jira_ticket(repo,ticket,comment,
                                                                          'Checkmarx')
                except Exception as e_details:
                    func = f"GeneralTicketing.close_or_cancel_jira_ticket('{repo}','{ticket}',"
                    func += f"'{comment}','Checkmarx')"
                    e_code = "CT-COCNE-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if closed is True:
                    ne_array.append(ticket)
                    sql = f"""UPDATE SASTFindings SET TicketClosed = 1, AcctCompComment = 1 WHERE
                    JiraIssueKey = '{ticket}'"""
                    try:
                        update(sql)
                    except Exception as e_details:
                        e_code = "CT-COCNE-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              ScrVar.src,inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
        cl_cnt = len(ne_array)
        TheLogs.log_info(f"{cl_cnt} Not Exploitable ticket(s) closed or cancelled",2,"*",main_log)
        if len(ne_array) > 0:
            for ticket in ne_array:
                TheLogs.log_info(ticket,3,"-",main_log)
            u_statuses = CxReports.update_finding_statuses(proj_id,main_log,ex_log,ex_file)
            ScrVar.update_exception_info(u_statuses)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def close_or_cancel_tickets(repo, proj_id, main_log=LOG,ex_log=LOG_EXCEPTION,
                                ex_file=EX_LOG_FILE):
        """Closes or cancels tickets that have no active findings"""
        ScrVar.reset_exception_counts()
        cl_cnt = 0
        cannot_close = []
        closed_array = []
        TheLogs.log_headline(f'CLOSING OR CANCELLING ELIGIBLE TICKETS FOR {repo}',3,"#",main_log)
        sql = f"""SELECT DISTINCT JiraIssueKey FROM SASTFindings WHERE cxProjectID = {proj_id}
        AND (Status = 'To Close' OR Status = 'Closed In Ticket') AND JiraIssueKey IS NOT NULL AND
        JiraIssueKey NOT IN (SELECT DISTINCT JiraIssueKey FROM SASTFindings WHERE cxProjectID =
        {proj_id} AND FoundInLastScan = 1 AND JiraIssueKey IS NOT NULL) AND JiraIssueKey IN
        (SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE cxProjectID = {proj_id} AND
        JiraStatusCategory != 'Done') AND JiraIssueKey NOT IN (SELECT DISTINCT JiraIssueKey FROM
        SASTFindings WHERE FoundInLastScan = 1 AND Status != 'Not Exploitable' AND  cxProjectID =
        {proj_id})"""
        try:
            to_close = select(sql)
        except Exception as e_details:
            e_code = "CT-COCT-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if to_close:
            for item in to_close:
                ticket = item[0]
                comment = "All instance(s) of this finding are no longer present in scans."
                try:
                    closed = GeneralTicketing.close_or_cancel_jira_ticket(repo,ticket,comment,
                                                                          'Checkmarx')
                except Exception as e_details:
                    func = f"GeneralTicketing.close_or_cancel_jira_ticket('{repo}', '{ticket}', "
                    func += f"'{comment}','Checkmarx')"
                    e_code = "CT-COCT-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if closed is True:
                    closed_array.append(ticket)
                    sql = f"""UPDATE SASTFindings SET TicketClosed = 1, AcctCompComment = 1 WHERE
                    JiraIssueKey = '{ticket}'"""
                    try:
                        update(sql)
                    except Exception as e_details:
                        e_code = "CT-COCT-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              ScrVar.src,inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                else:
                    cannot_close.append(ticket)
        cl_cnt = len(closed_array)
        TheLogs.log_info(f"{cl_cnt} ticket(s) closed or cancelled",2,"*",main_log)
        if len(closed_array) > 0:
            for ticket in closed_array:
                TheLogs.log_info(ticket,3,"-",main_log)
            u_statuses = CxReports.update_finding_statuses(proj_id,main_log,ex_log,ex_file)
            ScrVar.update_exception_info(u_statuses)
        try:
            Alerts.manual_alert(ScrVar.src,cannot_close,len(cannot_close),25,SLACK_URL)
        except Exception as e_details:
            func = f"Alerts.manual_alert('{ScrVar.src}','{cannot_close}',{len(cannot_close)},25,"
            func += f"'{SLACK_URL}')"
            e_code = "CT-COCT-004"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        ScrVar.src,inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.ex_cnt += 1
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_related_tickets(proj_id,sim_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns existing tickets for the similarity ID and project to determine whether a new
        ticket is necessary and/or if previously closed tickets should be linked"""
        append_tickets = []
        related_tickets = []
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraStatusCategory, JiraDueDate, JiraResolutionDate
        FROM JiraIssues WHERE cxProjectID = {proj_id} AND cxSimilarityID = {sim_id} ORDER BY
        JiraStatusCategory, JiraResolutionDate DESC, JiraDueDate"""
        try:
            tickets = select(sql)
        except Exception as e_details:
            e_code = "CT-GRT-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'ToAppend':None,'Related':None}
        if tickets != []:
            for item in tickets:
                if item[1] == 'Done':
                    related_tickets.append(item[0])
                else:
                    if item[1] == 'To Do':
                        append_tickets.append(item[0])
                    else:
                        related_tickets.append(item[0])
        results = {'ToAppend':append_tickets,'Related':related_tickets}
        return results

    @staticmethod
    def get_related_tickets_by_query(summary,main_log=LOG,ex_log=LOG_EXCEPTION,
                                     ex_file=EX_LOG_FILE):
        """Returns existing tickets for the cxQuery and project to determine whether a new
        ticket is necessary and/or if previously closed tickets should be linked"""
        append_tickets = []
        related_tickets = []
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraStatusCategory, JiraDueDate, JiraResolutionDate
        FROM JiraIssues WHERE JiraSummary LIKE '{summary}%' ORDER BY JiraStatusCategory,
        JiraResolutionDate DESC, JiraDueDate"""
        try:
            tickets = select(sql)
        except Exception as e_details:
            e_code = "CT-GRTBQ-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'ToAppend':None,'Related':None}
        if tickets != []:
            for item in tickets:
                if item[1] == 'Done':
                    related_tickets.append(item[0])
                else:
                    if item[1] == 'To Do':
                        append_tickets.append(item[0])
                    else:
                        related_tickets.append(item[0])
        results = {'ToAppend':append_tickets,'Related':related_tickets}
        return results

    @staticmethod
    def get_needed_sims(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Pulls the SimilarityID for findings that need ticketing"""
        result = []
        sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE
        Status IN ('To Close','To Ticket','To Update') AND cxProjectID = {proj_id}"""
        try:
            sim_ids = select(sql)
        except Exception as e_details:
            e_code = "CT-GNS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return result
        if sim_ids != []:
            for sim in sim_ids:
                result.append(sim[0])
        return result

    @staticmethod
    def get_needed_queries(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Pulls the cxQuery for findings that need ticketing"""
        queries = []
        sql = f"""SELECT DISTINCT cxQuery, SourceFile, DestinationFile, COUNT(cxQuery) FROM
        SASTFindings WHERE ((Status IN ('To Close','To Ticket','To Update') OR (cxResultState =
        'Not Exploitable' AND (NotExploitableInTicket IS NULL OR NotExploitableInTicket = 0) AND
        JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE JiraStatusCategory !=
        'Done')))) AND cxProjectID = {proj_id} GROUP BY cxQuery, SourceFile, DestinationFile
        ORDER BY cxQuery, SourceFile, DestinationFile"""
        try:
            queries = select(sql)
        except Exception as e_details:
            e_code = "CT-GNQ-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return queries

    @staticmethod
    def get_most_severe(cx_query,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the highest severity for the given query/project"""
        severity = 'High'
        sql = f"""SELECT TOP 1 cxResultSeverity, ResultSeverityValue FROM SASTFindings WHERE
        cxProjectID = {proj_id} AND cxQuery = '{cx_query}' AND ((Status IN ('To Close','To Ticket','To Update') OR (cxResultState =
        'Not Exploitable' AND (NotExploitableInTicket IS NULL OR NotExploitableInTicket = 0) AND
        JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE JiraStatusCategory !=
        'Done')))) ORDER BY ResultSeverityValue, cxResultSeverity"""
        try:
            get_sev = select(sql)
        except Exception as e_details:
            e_code = "CT-GMS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return severity
        if get_sev != []:
            severity = get_sev[0][0]
        return severity

    @staticmethod
    def tickets_needed(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Identifies Checkmarx projects that need tickets"""
        sim_ids = []
        restart = 0
        sim_ids = CxTicketing.get_needed_sims(proj_id,main_log,ex_log,ex_file)
        if sim_ids != []:
            for sid in sim_ids:
                restart += CxTicketing.check_finding_state(sid,proj_id,main_log,ex_log,ex_file)
        if restart > 0:
            u_statuses = CxReports.update_finding_statuses(proj_id,main_log,ex_log,ex_file)
            ScrVar.update_exception_info(u_statuses)
            sim_ids = CxTicketing.get_needed_sims(proj_id,main_log,ex_log,ex_file)
        return sim_ids

    @staticmethod
    def can_ticket(project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Identifies if Jira information is available for the project"""
        can_ticket = False
        sql = f"""SELECT DISTINCT Repo FROM ApplicationAutomation WHERE JiraProjectKey IS NOT NULL
        AND JiraIssueParentKey IS NOT NULL AND cxProjectId = '{project_id}'"""
        try:
            has_info = select(sql)
        except Exception as e_details:
            e_code = "CT-TN-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':can_ticket}
        if has_info:
            can_ticket = True
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,'Results':can_ticket}

    @staticmethod
    def check_finding_state(sim_id,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Updates the state of finding(s) for a single similarity ID"""
        updates = 0
        u_array = []
        ls_id = None
        last_scan = {}
        try:
            last_scan = CxAPI.get_last_scan_data(proj_id,main_log,ex_log,ex_file)
        except Exception as e_details:
            func = f"CxAPI.get_last_scan_id({proj_id})"
            e_code = "CT-CFS-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return updates
        if 'ID' in last_scan:
            ls_id = last_scan['ID']
            sql = f"""SELECT DISTINCT cxResultID, cxLastScanID FROM SASTFindings
            WHERE cxProjectID = {proj_id} AND cxSimilarityID = {sim_id} ORDER BY cxResultID"""
            try:
                findings = select(sql)
            except Exception as e_details:
                e_code = "CT-CFS-002"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return updates
            if findings != []:
                for item in findings:
                    scan_id = item[0].split("-",1)[0]
                    path_id = item[0].split("-",1)[1]
                    ls_id = item[1]
                    try:
                        details = CxAPI.get_finding_details_by_path(scan_id,path_id,proj_id,
                                                                    main_log,ex_log,ex_file)
                    except Exception as e_details:
                        func = f"CxAPI.get_finding_details_by_path({ls_id},{sim_id},{proj_id})"
                        e_code = "CT-CFS-003"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   ScrVar.src,inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if details != {}:
                        u_array.append({'SET':{'cxResultState':details['cxResultState'],
                                            'cxResultStateValue':details['cxResultStateValue']},
                                        'WHERE_EQUAL':{'cxSimilarityID':sim_id,
                                                       'cxProjectID':proj_id,
                                                        'cxResultID':item[0],
                                                        'cxResultState':details['cxResultState']}})
            try:
                updates += update_multiple_in_table('SASTFindings',u_array)
            except Exception as e_details:
                func = f"update_multiple_in_table('SASTFindings',{u_array})"
                e_code = "CT-CFS-004"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           ScrVar.src,inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
        return updates

    @staticmethod
    def create_jira_descriptions(similarity_id_list,proj_id,repo,main_log=LOG,
                                 ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Creates Jira descriptions for similarity IDs for a project"""
        jira_descriptions = []
        try:
            link_tickets = GeneralTicketing.has_related_link_type(repo)
        except Exception as e_details:
            func = f"GeneralTicketing.get_jira_info('{repo}','Checkmarx)"
            e_code = "CT-CJD-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                        inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return jira_descriptions
        for finding in similarity_id_list:
            desc = ''
            jira_issues = CxTicketing.check_for_other_tickets(finding,proj_id,repo,main_log,
                                                              ex_log,ex_file)
            if jira_issues is not None:
                past_due = False
                jira_issue = None
                if jira_issues['ToAppend'] != []:
                    jira_issue = jira_issues['ToAppend'][0]
                if jira_issue is not None:
                    try:
                        past_due = GeneralTicketing.check_past_due(jira_issue)
                    except Exception as e_details:
                        func = f"GeneralTicketing.check_past_due('{jira_issue}')"
                        e_code = "CT-CJD-002"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                ScrVar.src,inspect.stack()[0][3],
                                                traceback.format_exc())
                        ScrVar.ex_cnt += 1
                if past_due is True:
                    desc += 'h1. {color:red}*>>>>>  TICKET IS PAST DUE  <<<<<*{color}\n'
            updated_date = datetime.now().strftime("%B %d, %Y")
            desc += f"h6. Ticket updated by automation on {updated_date}."
            query = CxTicketing.get_query_fields(finding,proj_id,main_log,ex_log,ex_file)
            summary = None
            if query:
                summary = f"SAST Finding: {query['QueryName']} - {repo}"
                if query['QueryDescription'] is not None:
                    desc += f"\nh2. *Overview:*\n{query['QueryDescription']}"
            related_tkts = jira_issues['Related']
            if link_tickets is False and (related_tkts != [] or related_tkts is not None):
                desc += "\nh2. *Related tickets:*\n"
                for tkt in related_tkts:
                    desc += f'[{tkt}]\n'
                related_tkts = []
            severity = CxTicketing.get_severity(finding,proj_id,main_log,ex_log,ex_file)
            cwes = CxTicketing.get_cwe_details(finding,proj_id,main_log,ex_log,ex_file)
            if cwes:
                desc += cwes['CWEs']
            vulns = CxTicketing.get_vulns(finding,proj_id,main_log,ex_log,ex_file)
            if vulns is not None:
                desc += vulns['Vulnerabilities']
            if desc != '' and vulns is not None:
                desc += f"\nh6. *cxSimilarityID:* {finding}\n----\n"
                desc = f'{desc}{ScrVar.disclaimer}'
                level = 'regular'
                if len(desc) > 60000:
                    level = 'super'
                if len(desc) > 30000:
                    desc = f"h6. Ticket updated by automation on {updated_date}."
                    if query:
                        if query['QueryDescription'] is not None:
                            desc += f"\nh2. *Overview:*\n{query['QueryDescription']}"
                    if cwes:
                        desc += cwes['CWEs']
                    vulns = CxTicketing.get_vulns_compact(finding,proj_id,level,main_log,ex_log,
                                                          ex_file)
                    if vulns is not None:
                        desc += vulns['Vulnerabilities']
                    if desc != '' and vulns is not None:
                        desc = f'{desc}{ScrVar.disclaimer}'
            jira_descriptions.append({'cxSimilarityId':finding,'ExistingTicket':jira_issue,
                                        'Severity':severity,'Summary':summary,'Description':
                                        desc,'RelatedTickets':related_tkts})
        return jira_descriptions

    @staticmethod
    def get_query_fields(similarity_id,project_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Gets the query fields for a similarity ID for us in creating Jira descriptions"""
        query_fields = {}
        sql = f"""SELECT DISTINCT cxQuery, cxQueryDescription FROM SASTFindings WHERE
        cxSimilarityID = {similarity_id} AND cxProjectID = {project_id} ORDER BY
        cxQueryDescription DESC"""
        try:
            get_query = select(sql)
        except Exception as e_details:
            e_code = "CT-GQF-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return query_fields
        if get_query:
            description = get_query[0][1]
            if description is None:
                try:
                    description = CxAPI.g_query_desc(similarity_id,main_log,ex_log,ex_file)
                except Exception as e_details:
                    func = f"CxAPI.g_query_desc({similarity_id})"
                    e_code = "CT-GQF-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    return query_fields
                if description is not None:
                    sql = f"""UPDATE SASTFindings SET cxQueryDescription = '{description}'
                        WHERE cxSimilarityID = {similarity_id} AND cxProjectID = {project_id}"""
                    try:
                        update(sql)
                    except Exception as e_details:
                        e_code = "CT-GQF-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              ScrVar.src,inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        return query_fields
            query_fields['QueryName'] = get_query[0][0]
            query_fields['QueryDescription'] = description
        return query_fields

    @staticmethod
    def get_cwe_details(sim_id, project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets details necessary to create a ticket"""
        cwes = None
        sql = f"""SELECT DISTINCT cxCWEID, cxCWETitle, cxCWEDescription, cxCWELink,
        cxResultSeverity, ResultSeverityValue FROM SASTFindings WHERE cxSimilarityID = {sim_id} AND
        cxProjectID = {project_id} AND cxCWEID IS NOT NULL ORDER BY ResultSeverityValue, cxCWEID"""
        try:
            get_cwes = select(sql)
        except Exception as e_details:
            e_code = "CT-GQF-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return cwes
        if get_cwes:
            desc = "\nh2. *CWE Reference:*\n"
            for item in get_cwes:
                cwe = item[0]
                cwe_t = item[1]
                cwe_d = item[2]
                cwe_l = item[3]
                sev_txt = item[4]
                sev_value = item[5]
                sev_color = '172B4D'
                if sev_value < 2:
                    sev_color = 'bf2600'
                else:
                    sev_color = 'ff991f'
                sev_txt = "{color:#" + str(sev_color) + "}*" + str(sev_txt) + "*{color}"
                if cwe_t is None or cwe_d is None or cwe_l is None:
                    try:
                        cwe_info = VulnDetails.get_cwe(cwe,main_log,ex_log,ex_file)
                    except Exception as e_details:
                        func = f"VulnDetails.get_cwe('{cwe}')"
                        e_code = "CT-GQF-002"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   ScrVar.src,inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        return cwes
                    if cwe_info is not None and cwe_info != {}:
                        cwe_t = cwe_info['name']
                        cwe_d = cwe_info['description']
                        cwe_l = cwe_info['link']
                        if cwe_t is not None or cwe_d is not None or cwe_l is not None:
                            sql = f"""UPDATE SASTFindings SET cxCWEID = {cwe}"""
                            if cwe_t is not None:
                                sql += f", cxCWETitle = '{cwe_t}'"
                            if cwe_d is not None:
                                sql += f", cxCWEDescription = '{cwe_d}'"
                            if cwe_l is not None:
                                sql += f", cxCWELink = '{cwe_l}'"
                            sql += f" WHERE cxCWEID = {cwe}"
                            try:
                                update(sql)
                            except Exception as e_details:
                                e_code = "CT-GQF-003"
                                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                                      ScrVar.src,inspect.stack()[0][3],
                                                      traceback.format_exc())
                                ScrVar.ex_cnt += 1
                                return cwes
                if cwe_l is not None:
                    desc += f"* *[CWE-{cwe}"
                else:
                    desc += "* *CWE-{cwe}"
                if cwe_t is not None:
                    desc += f": {cwe_t}"
                if cwe_l is not None:
                    desc += f"|{cwe_l}]"
                desc += f"* - {sev_txt}\n"
                if cwe_d is not None:
                    desc += f"{cwe_d}\n"
            cwes = {'CWEs': desc}
        return cwes

    @staticmethod
    def get_severity(sim_id,project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets the top severity for a finding"""
        severity = None
        sql = f"""SELECT TOP 1 cxResultSeverity FROM SASTFindings WHERE cxSimilarityID =
            {sim_id} AND cxProjectID = {project_id} ORDER BY ResultSeverityValue"""
        try:
            top_sev = select(sql)
        except Exception as e_details:
            e_code = "CT-GS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return severity
        if top_sev != []:
            severity = top_sev[0][0]
        return severity

    @staticmethod
    def get_vulns(sim_id,project_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets vulnerability details for ticketing"""
        vulns = None
        sql = f"""SELECT DISTINCT cxLink, cxResultDescription, FoundInLastScan, Status, cxResultID,
        cxSource, cxDestination, cxLastScanDate FROM SASTFindings WHERE cxSimilarityID = {sim_id}
        AND cxProjectID = {project_id} AND Status NOT IN ('Not Exploitable', 'Closed') ORDER BY
        FoundInLastScan DESC, Status DESC, cxLastScanDate DESC"""
        try:
            get_vulns = select(sql)
        except Exception as e_details:
            e_code = "CT-GV-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return vulns
        if get_vulns != []:
            vuln_cnt = 0
            for item in get_vulns:
                vuln_cnt += 1
            if vuln_cnt == 1:
                desc = "\nh2. *Instance:*\n"
            else:
                desc = "\nh2. *Instances:*\n"
            desc += "{panel:bgColor=#fffae6}Added during update{panel}\n{panel:bgColor=#e3fcef}No longer seen in scans{panel}"
            i = 0
            for item in get_vulns:
                description = None
                status = item[3]
                description = item[1]
                if description is None:
                    scan_id = item[4].split("-",1)[0]
                    path = item[4].split("-",1)[1]
                    try:
                        description = CxAPI.get_result_description(scan_id,path,main_log,ex_log,
                                                                   ex_file)
                    except Exception as e_details:
                        func = f"CxAPI.get_result_description({scan_id},{path})"
                        e_code = "CT-GV-002"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   ScrVar.src,inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        return vulns
                    if description is not None:
                        sql = f"""UPDATE SASTFindings SET cxResultDescription =
                            '{description}' WHERE cxSimilarityID = {sim_id} AND cxProjectID =
                            {project_id}"""
                        try:
                            update(sql)
                        except Exception as e_details:
                            e_code = "CT-GV-003"
                            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                                  ScrVar.src,inspect.stack()[0][3],
                                                  traceback.format_exc())
                            ScrVar.ex_cnt += 1
                n_c = ''
                e_c = ''
                if item[1] is not None or description is not None:
                    i += 1
                    if status == 'To Ticket':
                        n_c = "{panel:bgColor=#fffae6}"
                        e_c = "{panel}"
                    if status == 'To Close' or status == 'Closed In Ticket':
                        n_c = "{panel:bgColor=#e3fcef}"
                        e_c = "{panel}"
                    source_data = f"*Source:*\rNot available, check details link"
                    dest_data = f"*Destination:*\rNot available, check details link"
                    desc += f"\n||Instance #{i}||\n"
                    if item[5] is not None:
                        data = item[5].split("; ",4)
                        source_data = f"{n_c}*Source:*\rFile: {data[0]}\r"
                        source_data += f"{data[1]}\r{data[2]}\r{data[3]}{e_c}"
                    else:
                        source_data = f"*Source:*\rNot available, check details link"
                    if item[6] is not None:
                        data = item[6].split("; ",4)
                        dest_data = f"*Destination:*\rFile: {data[0]}\r"
                        dest_data += f"{data[1]}\r{data[2]}\r{n_c}{data[3]}"
                    else:
                        dest_data = f"*Destination:*\rNot available, check details link"
                    link = f"*[See details in Checkmarx|{item[0]}]*"
                    if vuln_cnt < 21:
                        desc += f"|{n_c}{item[1]}\r{source_data}\r\r{dest_data}\r{e_c}{link}|\r"
                    else:
                        desc += f"|{n_c}{source_data}\r{dest_data}{e_c}\r{link}|\r"
            vulns = {'Vulnerabilities': desc}
        return vulns

    @staticmethod
    def get_vulns_compact(sim_id,project_id,level='regular',main_log=LOG,ex_log=LOG_EXCEPTION,
                          ex_file=EX_LOG_FILE):
        """Attempts to shorten the description to meet the 4000 character threshold"""
        vulns = None
        sql = f"""SELECT DISTINCT cxLink, FoundInLastScan, Status, cxResultID,
        cxSource, cxDestination, cxLastScanDate FROM SASTFindings WHERE cxSimilarityID = {sim_id}
        AND cxProjectID = {project_id} AND Status NOT IN ('Not Exploitable', 'Closed') ORDER BY
        cxLastScanDate, cxSource, cxDestination"""
        try:
            get_vulns = select(sql)
        except Exception as e_details:
            e_code = "CT-GVC-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return vulns
        if get_vulns != []:
            vuln_cnt = 0
            for item in get_vulns:
                vuln_cnt += 1
            if vuln_cnt == 1:
                desc = "\nh2. *Instance:*\n*Note:* The length of the details for this ticket "
                desc += "exceed the 32750 character maximum for Jira ticket descriptions. Click "
                desc += "the occurrence number below for full details."
            else:
                desc = f"\nh2. *{vuln_cnt} Instances:*\n*Note:* The length of the details for "
                desc += "this ticket exceed the 32750 character maximum for Jira ticket "
                desc += "descriptions. Click the occurrence numbers below for full details."
            desc += "{color:purple}New{color} - Added to ticket during update\r-crossed out- - No "
            desc += "longer found in scans"
            i = 0
            items = ''
            for item in get_vulns:
                status = item[2]
                n_c = ''
                e_c = ''
                source = item[4].split("; Line",1)[0]
                destination = item[5].split("; Line",1)[0]
                if item[1] is not None:
                    i += 1
                    if status == 'To Ticket':
                        n_c = "{color:purple}"
                        e_c = "{color}"
                    if status == 'To Close' or status == 'Closed In Ticket' or item[1] == 0:
                        n_c = "-"
                        e_c = "-"
                    if level == 'regular':
                        items += f"# {n_c}*[{item[3]}|{item[0]}]:*{e_c}\r{n_c}Source: {source}{e_c}\r{n_c}Destination: {destination} {e_c}\n"
                    elif level == 'super':
                        items += f"# {n_c}Source: {source}{e_c}\r{n_c}Destination: {destination} {e_c}\n"
            if items != '':
                desc = f"{desc}{items}\n"
                vulns = {'Vulnerabilities': desc}
        return vulns

    @staticmethod
    def check_for_other_tickets(similarity_id,project_id,repo,main_log=LOG,ex_log=LOG_EXCEPTION,
                                 ex_file=EX_LOG_FILE):
        """Checks for (and fixes) open duplicate tickets, then returns a list of related tickets"""
        result = None
        sql = f"""SELECT DISTINCT JiraIssueKey, JiraDueDate FROM JiraIssues
        WHERE cxSimilarityID = '{similarity_id}' AND cxProjectID = {project_id} AND
        JiraStatusCategory != 'Done' AND JiraDueDate >= DATEADD(day,14,GETDATE())
        ORDER BY JiraDueDate"""
        try:
            jira_tickets = select(sql)
        except Exception as e_details:
            e_code = "CT-CFOT-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return result
        if jira_tickets != []:
            if len(jira_tickets) == 1:
                result = jira_tickets[0][0]
            elif len(jira_tickets) > 1:
                result = jira_tickets[0][0]
                i = -1
                for ticket in jira_tickets:
                    i += 1
                    if i > 0:
                        close_ticket = ticket[0]
                        comment = f"Duplicate of {result}."
                        comment += "Findings will be consolidated."
                        cancelled = False
                        try:
                            cancelled = GeneralTicketing.cancel_jira_ticket(repo,close_ticket,
                                                                            comment,main_log,
                                                                            ex_log,ex_file)
                        except Exception as e_details:
                            func = f"GeneralTicketing.cancel_jira_ticket('{repo}',"
                            func += f"'{close_ticket}','{comment}'"
                            e_code = "CT-CFOT-002"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,ScrVar.src,
                                                       inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                        if cancelled is True:
                            sql = f"""UPDATE SASTFindings SET JiraIssueKey = NULL,
                                    Status = 'To Ticket' WHERE JiraIssueKey = {close_ticket}"""
                            try:
                                update(sql)
                            except Exception as e_details:
                                e_code = "CT-CFOT-003"
                                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                                      ScrVar.src,inspect.stack()[0][3],
                                                      traceback.format_exc())
                                ScrVar.ex_cnt += 1
        result = CxTicketing.get_related_tickets(project_id,similarity_id,main_log,ex_log,ex_file)
        return result

    @staticmethod
    def add_tickets_to_cx(repo,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds Jira ticket numbers to Checkmarx findings"""
        ScrVar.reset_exception_counts()
        a_cnt = 0
        TheLogs.log_headline(f'ADDING JIRA TICKETS TO CHECKMARX FINDINGS FOR {repo}',2,"*",
                             main_log)
        sql = f"""SELECT DISTINCT cxResultID, JiraIssueKey FROM SASTFindings WHERE
        JiraIssueKey IS NOT NULL AND cxProjectID = {proj_id} AND (cxTicketSet IS NULL OR
        cxTicketSet = 0) ORDER BY JiraIssueKey"""
        try:
            tickets = select(sql)
        except Exception as e_details:
            e_code = "CT-ATTC-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if tickets != []:
            for ticket in tickets:
                res_id = ticket[0]
                jira_ticket = ticket[1]
                added = False
                try:
                    added = CxAPI.add_ticket_to_cx(res_id, jira_ticket)
                except Exception as e_details:
                    func = f"CxAPI.add_ticket_to_cx('{res_id}', '{jira_ticket}')"
                    e_code = "CT-ATTC-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               ScrVar.src,inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if added is True:
                    sql = f"""UPDATE SASTFindings SET cxTicketSet = 1 WHERE cxProjectID =
                        {proj_id} AND cxResultID = '{res_id}'"""
                    try:
                        a_cnt += update(sql)
                    except Exception as e_details:
                        e_code = "CT-ATTC-003"
                        TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                              ScrVar.src,inspect.stack()[0][3],
                                              traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
        TheLogs.log_info(f"Ticket info added to {a_cnt} finding(s)",2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
