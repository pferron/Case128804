"""Updates the Checkmarx findings in SAST Findings"""

#  These are required
import os
import sys
import time
import traceback
import inspect
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from common.alerts import Alerts
from common.logging import TheLogs
from common.database_appsec import (select,update,insert,delete_row,update_multiple_in_table,
                                    insert_multiple_into_table)
from checkmarx.api_connections import CxAPI
from checkmarx.cx_common import CxCommon

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
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class CxReports():
    """Processes latest scan results"""

    @staticmethod
    def update_all_baseline_states(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Auto-updates 'Tech Debt', 'Closed', 'Closed in Ticket', and 'Not Exploitable' to ensure
        the baseline states are properly reflected"""
        ScrVar.reset_exception_counts()
        CxReports.baseline_state_updates(proj_id,'Tech Debt',main_log,ex_log,ex_file)
        CxReports.baseline_state_updates(proj_id,'Past Due',main_log,ex_log,ex_file)
        CxReports.baseline_state_updates(proj_id,'Closed',main_log,ex_log,ex_file)
        CxReports.baseline_state_updates(proj_id,'Closed in Ticket',main_log,ex_log,ex_file)
        CxReports.baseline_state_updates(proj_id,'Not Exploitable',main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def baseline_state_updates(proj_id,state,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE):
        """Pass through state of 'Tech Debt', 'Closed', or 'Closed in Ticket' to ensure the
        baseline states are properly reflected"""
        set_cnt = 0
        sql = None
        headline_text = str(state).upper()
        updates = []
        TheLogs.log_headline(f'UPDATING BASELINE FINDINGS WITH {headline_text} STATES',2,"#",
                             main_log)
        match state:
            case 'Tech Debt':
                sync_state = 5
                sql = f"""SELECT DISTINCT SASTFindings.cxResultID, JiraIssues.JiraIssueKey,
                JiraIssues.JiraDueDate, SASTFindings.cxTicketSet FROM SASTFindings INNER JOIN
                JiraIssues ON JiraIssues.JiraIssueKey=SASTFindings.JiraIssueKey WHERE
                SASTFindings.Status='Tech Debt' AND SASTFindings.cxResultStateValue!=5 AND
                SASTFindings.JiraIssueKey IS NOT NULL AND JiraIssues.JiraStatusCategory!='Done'
                AND JiraIssues.RITMTicket IS NULL AND (JiraIssues.ExceptionApproved IS NULL OR
                JiraIssues.ExceptionApproved=0) AND SASTFindings.cxProjectID={proj_id} AND
                JiraIssues.JiraDueDate>GETDATE()"""
                set_status = 'Tech Debt'
                set_i_status = 'Reported'
            case 'Past Due':
                sync_state = 2
                sql = f"""SELECT DISTINCT SASTFindings.cxResultID, JiraIssues.JiraIssueKey,
                JiraIssues.JiraDueDate, SASTFindings.cxTicketSet FROM SASTFindings INNER JOIN
                JiraIssues ON JiraIssues.JiraIssueKey=SASTFindings.JiraIssueKey WHERE
                SASTFindings.cxResultStateValue!=2 AND SASTFindings.JiraIssueKey IS NOT NULL AND
                JiraIssues.JiraStatusCategory!='Done' AND SASTFindings.cxProjectID={proj_id} AND
                JiraIssues.JiraDueDate<GETDATE()"""
                set_status = 'Past Due'
                set_i_status = 'Reported'
            case 'Closed':
                sync_state = 2
                sql = f"""SELECT DISTINCT SASTFindings.cxResultID, JiraIssues.JiraIssueKey,
                JiraIssues.JiraDueDate, SASTFindings.cxTicketSet FROM SASTFindings INNER JOIN
                JiraIssues ON JiraIssues.JiraIssueKey=SASTFindings.JiraIssueKey WHERE
                SASTFindings.cxResultStateValue!=2 AND SASTFindings.JiraIssueKey IS NOT NULL AND
                JiraIssues.JiraStatusCategory='Done' AND SASTFindings.cxProjectID={proj_id} AND
                SASTFindings.Status!='Not Exploitable'"""
                set_status = 'Closed'
                set_i_status = 'Closed'
            case 'Closed in Ticket':
                sync_state = 2
                sql = f"""SELECT DISTINCT SASTFindings.cxResultID, JiraIssues.JiraIssueKey,
                JiraIssues.JiraDueDate, SASTFindings.cxTicketSet FROM SASTFindings INNER JOIN
                JiraIssues ON JiraIssues.JiraIssueKey=SASTFindings.JiraIssueKey WHERE
                SASTFindings.cxResultStateValue!=2 AND SASTFindings.JiraIssueKey IS NOT NULL AND
                JiraIssues.JiraStatusCategory='Done' AND SASTFindings.cxProjectID={proj_id} AND
                SASTFindings.Status='Closed in Ticket'"""
                set_status = 'Closed in Ticket'
                set_i_status = 'Closed in Ticket'
            case 'Not Exploitable':
                sync_state = 1
                sql = f"""SELECT DISTINCT cxResultID, JiraIssueKey, cxTicketSet, cxTicketSet FROM
                SASTFindings WHERE SASTFindings.cxProjectID={proj_id} AND
                SASTFindings.cxSimilarityID IN (SELECT DISTINCT cxSimilarityID FROM SASTFindings
                WHERE SASTFindings.cxProjectID={proj_id} AND SASTFindings.Status =
                'Not Exploitable' AND cxResultStateValue = 1) AND cxResultStateValue!=1"""
                set_status = 'Not Exploitable'
                set_i_status = 'Not Exploitable'
        if sql is not None:
            try:
                get_results = select(sql)
            except Exception as e_details:
                e_code = "RP-BSU-001"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                    inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return
            if get_results != []:
                for item in get_results:
                    result_id = item[0]
                    scan_id = result_id.split("-",1)[0]
                    path_id = result_id.split("-",1)[1]
                    ticket = item[1]
                    due_date = str(item[2])
                    match state:
                        case 'Tech Debt':
                            comment = f"Tech debt ticket {ticket} is due on {due_date}."
                        case 'Past Due':
                            comment = 'This finding has been Confirmed by ProdSec. Current '
                            comment += f'ticket {ticket} was past due as of {due_date}.'
                        case 'Closed':
                            comment = f'The ticket {ticket} for this finding has been closed '
                            comment += 'and the finding is not noted as Not Exploitable. '
                            comment += 'Therefore, the state of this finding is being reverted to '
                            comment += 'Confirmed so it will reprocess if it ever reappears in '
                            comment += 'future scans.'
                        case 'Closed in Ticket':
                            comment = f'This finding has been closed in the ticket {ticket} '
                            comment += 'because it is no longer found in scans. Therefore, the '
                            comment += 'state of this finding is being reverted to Confirmed so '
                            comment += 'it will reprocess if it ever reappears in future scans.'
                        case 'Not Exploitable':
                            comment = 'This finding has been marked as Not Exploitable by '
                            comment += f'ProdSec. Ticket {ticket} will be closed or cancelled.'
                    state_set = CxAPI.update_res_state(scan_id,path_id,sync_state,comment)
                    if state_set is True:
                        set_cnt += 1
                        updates.append({'SET':{'cxResultState':state,
                                                'cxResultStateValue':sync_state,
                                                'Status':set_status,
                                                'IngestionStatus':set_i_status},
                                        'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                        'cxResultID':result_id}})
                    if (item[3] is None or item[3] == 0):
                        ticket_set = CxAPI.add_ticket_to_cx(result_id,ticket)
                        if ticket_set is True:
                            updates.append({'SET':{'cxTicketSet':1},
                                            'WHERE_EQUAL':{'cxProjectID':proj_id,
                                                            'cxResultID':result_id}})
        try:
            update_multiple_in_table('SASTFindings',updates)
        except Exception as e_details:
            func = f"update_multiple_in_table('SASTFindings',{updates})"
            e_code = "RP-BSU-002"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f'{set_cnt} findings set to {state} in the baseline project',2,"*",
                         main_log)

    @staticmethod
    def auto_confirm_findings(cx_proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Automatically confirms any findings that are currently in To Very state"""
        count = 0
        comment = 'Confirming finding.'
        state_name = 'Confirmed'
        state = 2
        updates = []
        headline = 'AUTO-CONFIRMING NEW FINDINGS'
        sql = """SELECT DISTINCT cxResultID FROM SASTFindings WHERE (((cxResultState = 'To Verify'
        OR Status = 'New') AND cxQuery NOT IN (SELECT DISTINCT cxQuery FROM
        SASTAutoConfirmExclusions WHERE ExclusionExpires IS NULL OR ExclusionExpires <= GETDATE()))
        OR (cxResultState NOT IN ('Confirmed','Not Exploitable') AND Status = 'Closed')) AND
        cxResultState != 'Not Exploitable'"""
        if cx_proj_id != 'All' and cx_proj_id is not None:
            sql += f""" AND cxProjectID = '{cx_proj_id}'"""
            headline += f" FOR PROJECT ID {cx_proj_id}"
        TheLogs.log_headline(headline,2,"#",main_log)
        try:
            get_results = select(sql)
        except Exception as e_details:
            e_code = "RP-ACF-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return
        if get_results != []:
            for result in get_results:
                cx_scan_id = result[0].split("-",1)[0]
                cx_path_id = result[0].split("-",1)[1]
                try:
                    updated = CxAPI.update_res_state(cx_scan_id,cx_path_id,state,comment,main_log,
                                                     ex_log,ex_file)
                except Exception as e_details:
                    func = f"CxAPI.update_res_state({cx_scan_id},{cx_path_id},'{state}',"
                    func += f"'{comment}')"
                    e_code = "RP-ACF-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               rf'{ScrVar.src}',inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if updated is True:
                    count += 1
                    updates.append({'SET': {'cxResultState': state_name,
                                            'cxResultStateValue': state},
                                            'WHERE_EQUAL': {'cxProjectID': cx_proj_id,
                                                            'cxResultID': result[0]},
                                            'WHERE_NOT': None})
        try:
            update_multiple_in_table('SASTFindings',updates)
        except Exception as e_details:
            func = f"update_multiple_in_table('SASTFindings',{updates})"
            e_code = "RP-ACF-003"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                        traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f'{count} findings confirmed',2,"*",main_log)

    @staticmethod
    def update_results(proj_id,reprocess,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Pulls the latest Checkmarx scan report (this may take a while) and then updates the
        SASTFindings table"""
        ScrVar.reset_exception_counts()
        TheLogs.log_headline(f'RUNNING REPORTING UPDATES FOR PROJECT ID {proj_id}',2,"#",main_log)
        scan_id = None
        report_id = None
        missing_similarity_ids = 0
        try:
            g_last_scan = CxAPI.get_last_scan_data(proj_id,main_log,ex_log,ex_file)
        except Exception as e_details:
            e_code = "RP-UR-001"
            func = f"CxAPI.get_last_scan_id({proj_id})"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.fe_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                    'missing_similarity_ids': missing_similarity_ids}
        if g_last_scan != {}:
            scan_id = 0
            if 'ID' in g_last_scan:
                scan_id = g_last_scan['ID']
                scan_date = g_last_scan['Finished']
            if scan_id is not None or scan_id != 0:
                if reprocess == 0:
                    reprocess = CxReports.check_scan_processed(scan_id,proj_id,main_log,ex_log,
                                                               ex_file)
            if reprocess == 1 and scan_id is not None and scan_id != 0:
                TheLogs.log_info('Pulling latest scan report',2,"*",main_log)
                report = []
                report_id = CxReports.run_cx_report(scan_id,main_log)
                if report_id is not None:
                    report, missing_similarity_ids = CxReports.scan_report_to_process(report_id,
                                                                                   proj_id,
                                                                                   scan_id,
                                                                                   main_log,
                                                                                   ex_log,
                                                                                   ex_file)
                    if report != []:
                        TheLogs.log_info('Updating SASTFindings',2,"*",main_log)
                        CxReports.update_sastfindings(report,proj_id,scan_id,scan_date,main_log,
                                                      ex_log,ex_file)
                    else:
                        TheLogs.log_info('No findings to add or update',2,"!",main_log)
                        sql = f"""UPDATE SASTFindings SET FoundInLastScan = 0 WHERE cxProjectID =
                        {proj_id}"""
                        try:
                            update(sql)
                        except Exception as e_details:
                            e_code = "RP-UR-002"
                            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,
                                                  rf'{ScrVar.src}',inspect.stack()[0][3],
                                                  traceback.format_exc())
                            ScrVar.ex_cnt += 1
                        processed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                TheLogs.log_info('Latest scan has already been processed or no scan exists',2,"*",
                                main_log)
            if report_id is not None and report_id != 0 and missing_similarity_ids == 0:
                processed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = f"""INSERT INTO cxResultsProcessed (cxProjectID, cxScanID, cxReportID,
                ProcessedDateTime) VALUES ({proj_id},{scan_id},{report_id},'{processed}')"""
                try:
                    insert(sql)
                except Exception as e_details:
                    e_code = "RP-UR-003"
                    TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                          inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.ex_cnt += 1
                sql = f"""DELETE FROM cxResultsProcessed WHERE ProcessedDateTime NOT IN (SELECT
                TOP 1 ProcessedDateTime FROM cxResultsProcessed WHERE cxProjectID = {proj_id} AND
                cxScanID = {scan_id} AND cxReportID = {report_id} AND cxReportID != 0 ORDER BY
                ProcessedDateTime DESC) AND cxProjectID = {proj_id}"""
                try:
                    delete_row(sql)
                except Exception as e_details:
                    e_code = "RP-UR-004"
                    TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                          inspect.stack()[0][3],traceback.format_exc())
                    ScrVar.ex_cnt += 1
            CxReports.auto_confirm_findings(proj_id,main_log,ex_log,ex_file)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt,
                'missing_similarity_ids': missing_similarity_ids}

    @staticmethod
    def check_scan_processed(scan_id,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Determines whether the latest scan has been processed"""
        to_process = 1
        if scan_id is not None and scan_id != 0:
            sql = f"""SELECT cxProjectID FROM cxResultsProcessed WHERE cxProjectID = {proj_id} AND
            cxScanID = {scan_id} AND cxReportID IS NOT NULL AND cxReportID != 0"""
            try:
                processed = select(sql)
            except Exception as e_details:
                e_code = "RP-CSP-001"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return to_process
            if processed:
                to_process = 0
        return to_process

    @staticmethod
    def run_cx_report(scan_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Runs a report and creates JSON for processing"""
        report_id = None
        if scan_id is not None:
            try:
                report_id = CxAPI.create_scan_report(scan_id,main_log,ex_log,ex_file)
            except Exception as e_details:
                e_code = "RP-RCR-001"
                func = f"CxAPI.create_scan_report({scan_id})"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
        return report_id

    @staticmethod
    def scan_report_to_process(report_id,proj_id,scan_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Runs a report and creates JSON for processing"""
        return_dict = []
        missing_similarity_ids = 0
        if report_id is not None:
            try:
                while not CxAPI.scan_report_complete(report_id,main_log,ex_log,ex_file):
                    time.sleep(10)
            except Exception as e_details:
                e_code = "RP-SRTP-001"
                func = f"CxAPI.scan_report_complete({report_id})"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return
        try:
            report = CxAPI.get_scan_report(report_id,main_log,ex_log,ex_file)
        except Exception as e_details:
            e_code = "RP-SRTP-002"
            func = f"CxAPI.get_scan_report({report_id})"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return
        if report is not None:
            row_cnt = 0
            for row in report:
                source = ''
                src_file = ''
                src_obj = ''
                destination = ''
                dest_file = ''
                dest_obj = ''
                if row['SrcFileName'] is not None:
                    source += f"{row['SrcFileName']}"
                    src_file = row['SrcFileName']
                    if row['Name'] is not None:
                        source += f"; Object: {row['Name']}"
                        src_obj = row['Name']
                    if row['Line'] is not None:
                        source += f"; Line: {row['Line']}"
                        if row['Column'] is not None:
                            source += f"; Column: {row['Column']}"
                if row['DestFileName'] is not None:
                    destination += f"{row['DestFileName']}"
                    dest_file = row['DestFileName']
                    if row['DestName'] is not None:
                        destination += f"; Object: {row['DestName']}"
                        dest_obj = row['DestName']
                    if row['DestLine'] is not None:
                        destination += f"; Line: {row['DestLine']}"
                        if row['DestColumn'] is not None:
                            destination += f"; Column: {row['DestColumn']}"
                scan = None
                path = None
                result_id = None
                description = None
                if row['Link'] is not None:
                    item = row['Link'].split("?",1)[1].split("&")
                    for values in item:
                        values = values.split("=",1)
                        var_name = values[0]
                        value = values[1]
                        if var_name == 'scanid':
                            scan = value
                        elif var_name == 'pathid':
                            path = value
                    if scan is not None and path is not None:
                        result_id = f"{scan}-{path}"
                        try:
                            description = CxAPI.get_result_description(scan,path,main_log,
                                                                        ex_log,ex_file)
                        except Exception as e_details:
                            e_code = "RP-SRTP-003"
                            func = f"CxAPI.get_result_description({scan},{path})"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,rf'{ScrVar.src}',inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                try:
                    details = CxAPI.get_finding_details_by_path(scan,path,proj_id,main_log,ex_log,
                                                        ex_file)
                except Exception as e_details:
                    e_code = "RP-SRTP-004"
                    func = f"CxAPI.get_finding_details({scan},{path},{proj_id})"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               rf'{ScrVar.src}',inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                sim_id = None
                cwe_id = None
                cwe_title = None
                cwe_description = None
                cwe_link = None
                cx_ls_date = None
                rs_val = None
                sev_val = None
                if details != {}:
                    if details['cxResultStateValue'] is not None:
                        rs_val = details['cxResultStateValue']
                    if row['Result Severity'] is not None:
                        sev_val = CxCommon.get_severity_id(row['Result Severity'],main_log,ex_log,
                                                           ex_file)
                    if details['cxSimilarityID'] is not None:
                        sim_id = details['cxSimilarityID']
                    if details['cxCWEID'] is not None:
                        cwe_id = details['cxCWEID']
                    if details['cxCWETitle'] is not None:
                        cwe_title = details['cxCWETitle']
                    if details['cxCWEDescription'] is not None:
                        cwe_description = details['cxCWEDescription']
                    if details['cxCWELink'] is not None:
                        cwe_link = details['cxCWELink']
                    if details['cxLastScanDate'] is not None:
                        cx_ls_date = details['cxLastScanDate']
                if sim_id is not None:
                    return_dict.append({'cxResultState':row['Result State'],
                                'cxResultStateValue':rs_val,
                                'cxQuery':row['Query'],
                                'cxResultSeverity':row['Result Severity'],
                                'cxResultSeverityValue':sev_val,
                                'cxLink':row['Link'],
                                'cxSource':source,
                                'SourceFile':src_file,
                                'SourceObject':src_obj,
                                'cxDestination':destination,
                                'DestinationFile':dest_file,
                                'DestinationObject':dest_obj,
                                'cxResultID':result_id,
                                'cxResultDescription':description,
                                'cxDetectionDate':str(row['Detection Date']),
                                'cxLastScanID':scan_id,
                                'cxLastScanDate':cx_ls_date,
                                'cxCWEID':cwe_id,
                                'cxCWETitle':cwe_title,
                                'cxCWEDescription':cwe_description,
                                'cxCWELink':cwe_link,
                                'cxSimilarityID':sim_id})
                else:
                    missing_similarity_ids += 1
                row_cnt += 1
        return return_dict, missing_similarity_ids

    @staticmethod
    def update_sastfindings(report,proj_id,scan_id,scan_date,main_log=LOG,ex_log=LOG_EXCEPTION,
                            ex_file=EX_LOG_FILE):
        """Inserts new findings into and updated existing findings in SASTFindings"""
        f_cnt = 0
        a_cnt = 0
        u_array = []
        i_array = []
        sql = f"""UPDATE SASTFindings SET FoundInLastScan = 0 WHERE cxProjectID = {proj_id}"""
        try:
            update(sql)
        except Exception as e_details:
            e_code = "RP-US-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        for item in report:
            sql = f"""SELECT cxResultID, Status, JiraIssueKey, cxResultState FROM SASTFindings
            WHERE cxProjectID = {proj_id} AND cxSimilarityID = {item['cxSimilarityID']} AND
            SourceFile = '{item['SourceFile']}' AND SourceObject = '{item['SourceObject']}' AND
            DestinationFile = '{item['DestinationFile']}' AND DestinationObject =
            '{item['DestinationObject']}' AND Status != 'Closed'"""
            try:
                exists = select(sql)
            except Exception as e_details:
                e_code = "RP-US-002"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if exists:
                update_info = {'SET': {'FoundInLastScan':1,
                                        'cxResultState':item['cxResultState'],
                                        'cxResultStateValue':item['cxResultStateValue'],
                                        'cxSource':item['cxSource'],
                                        'cxDestination':item['cxDestination'],
                                        'cxResultID':item['cxResultID'],
                                        'cxResultDescription':item['cxResultDescription'],
                                        'cxLink':item['cxLink'],
                                        'cxLastScanID':scan_id,
                                        'cxLastScanDate':scan_date,
                                        'cxCWEID':item['cxCWEID'],
                                        'cxCWETitle':item['cxCWETitle'],
                                        'cxCWEDescription':item['cxCWEDescription'],
                                        'cxCWELink':item['cxCWELink']},
                                'WHERE_EQUAL':{'cxSimilarityID':item['cxSimilarityID'],
                                               'cxResultID':exists[0][0]},
                                'WHERE_NOT_IN':{'Status':['Closed','Not Exploitable']}}
                if exists[0][1] == 'Not Exploitable':
                    update_info['SET']['Status'] = 'Not Exploitable'
                if exists[0][2] is None and exists[0][3] == 'Confirmed':
                    update_info['SET']['Status'] = 'To Ticket'
                u_array.append(update_info)
            else:
                i_array.append({'FoundInLastScan':1,
                                'cxProjectID':proj_id,
                                'IngestionStatus':'New',
                                'Status':'New',
                                'cxResultState':item['cxResultState'],
                                'cxResultStateValue':item['cxResultStateValue'],
                                'cxLastScanID':scan_id,
                                'cxLastScanDate':scan_date,
                                'cxQuery':item['cxQuery'],
                                'cxResultSeverity':item['cxResultSeverity'],
                                'ResultSeverityValue':item['cxResultSeverityValue'],
                                'cxLink':item['cxLink'],
                                'cxSource':item['cxSource'],
                                'SourceFile':item['SourceFile'],
                                'SourceObject':item['SourceObject'],
                                'cxDestination':item['cxDestination'],
                                'DestinationFile':item['DestinationFile'],
                                'DestinationObject':item['DestinationObject'],
                                'cxResultID':item['cxResultID'],
                                'cxResultDescription':item['cxResultDescription'],
                                'cxDetectionDate':item['cxDetectionDate'],
                                'cxCWEID':item['cxCWEID'],
                                'cxCWETitle':item['cxCWETitle'],
                                'cxCWEDescription':item['cxCWEDescription'],
                                'cxCWELink':item['cxCWELink'],
                                'cxSimilarityID':item['cxSimilarityID']})
        try:
            f_cnt += update_multiple_in_table('SASTFindings',u_array)
        except Exception as e_details:
            e_code = "RP-US-003"
            func = f"update_multiple_in_table('SASTFindings',{u_array})"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        try:
            a_cnt += insert_multiple_into_table('SASTFindings',i_array)
        except Exception as e_details:
            e_code = "RP-US-004"
            func = f"insert_multiple_into_table('SASTFindings',{i_array})"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{f_cnt} finding(s) updated",3,"*",main_log)
        TheLogs.log_info(f"{a_cnt} finding(s) added",3,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def update_finding_statuses(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Ensure the proper IngestionStatus and Status values are set for each finding"""
        ScrVar.reset_exception_counts()
        acc_cnt = 0
        ne_cnt = 0
        o_cnt = 0
        c_cnt = 0
        pd_cnt = 0
        td_cnt = 0
        tc_cnt = 0
        cntkt_cnt = 0
        dntkt_cnt = 0
        totkt_cnt = 0
        new_cnt = 0
        TheLogs.log_headline(f'UPDATING FINDING STATUSES FOR PROJECT ID {proj_id}',2,"#",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Accepted', IngestionStatus = 'Reported'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NOT NULL AND JiraIssueKey IN (SELECT
        JiraIssueKey FROM JiraIssues WHERE Source = 'Checkmarx' AND JiraStatusCategory != 'Done'
        AND RITMTicket IS NOT NULL AND ExceptionApproved = 1 AND ExceptionApproved IS NOT NULL AND
        cxProjectID = {proj_id} AND JiraDueDate >= GETDATE()) AND Status NOT IN
        ('Closed In Ticket', 'Not Exploitable', 'To Update')"""
        try:
            acc_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{acc_cnt} finding(s) set to Accepted",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Not Exploitable', IngestionStatus =
        'Not Exploitable' WHERE cxProjectID = {proj_id} AND cxResultState = 'Not Exploitable'
        UPDATE SASTFindings SET Status = 'To Update', IngestionStatus = 'To Update' WHERE
        cxProjectID = {proj_id} AND cxResultState = 'Not Exploitable' AND JiraIssueKey IS NOT
        NULL AND (NotExploitableInTicket != 1 OR NotExploitableInTicket IS NULL)"""
        try:
            ne_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-002"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        sql = f"""UPDATE SASTFindings SET NotExploitableInTicket = 1, TicketClosed = 1,
        AcctCompComment = 1 WHERE cxProjectID = {proj_id} AND cxResultState = 'Not Exploitable' AND
        JiraIssueKey IN (SELECT DISTINCT JiraIssueKey FROM JiraIssues WHERE JiraStatusCategory =
        'Done' AND cxProjectID = {proj_id})"""
        try:
            update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-003"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{ne_cnt} finding(s) set to Not Exploitable",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Tech Debt', IngestionStatus = 'Reported'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NOT NULL AND JiraIssueKey IN (SELECT
        JiraIssueKey FROM JiraIssues WHERE Source = 'Checkmarx' AND TechDebt = 1 AND RITMTicket IS
        NULL AND JiraStatusCategory != 'Done' AND JiraDueDate >= GETDATE()) AND Status NOT IN
        ('Accepted','Not Exploitable','Closed In Ticket','To Close','Closed','To Update')"""
        try:
            td_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-004"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{td_cnt} finding(s) set to Tech Debt",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Open', IngestionStatus = 'Reported' WHERE
        cxProjectID = {proj_id} AND FoundInLastScan = 1 AND Status NOT IN ('Accepted',
        'Not Exploitable','Tech Debt','Closed In Ticket','To Update') AND JiraIssueKey IS NOT NULL"""
        try:
            o_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-005"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{o_cnt} finding(s) set to Open",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Past Due', IngestionStatus = 'Reported'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NOT NULL AND JiraIssueKey IN (SELECT
        JiraIssueKey FROM JiraIssues WHERE Source = 'Checkmarx' AND cxProjectID = {proj_id} AND
        JiraStatusCategory != 'Done' AND JiraDueDate < GETDATE()) AND Status NOT IN
        ('Closed In Ticket','To Close')"""
        try:
            pd_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-006"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{pd_cnt} finding(s) set to Past Due",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Cannot Ticket', IngestionStatus =
        'On Hold' WHERE cxProjectID = {proj_id} AND cxProjectID IN (SELECT cxProjectID FROM
        ApplicationAutomation WHERE JiraProjectKey IS NULL OR JiraIssueParentKey IS NULL) AND
        JiraIssueKey IS NULL AND Status != 'Do Not Ticket'"""
        try:
            cntkt_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-007"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{cntkt_cnt} finding(s) set to Cannot Ticket",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Do Not Ticket', IngestionStatus =
        'On Hold' WHERE cxProjectID = {proj_id} AND cxProjectID IN (SELECT cxProjectID FROM
        ApplicationAutomation WHERE ExcludeTickets IS NOT NULL AND ExcludeTickets = 1) AND
        JiraIssueKey IS NULL AND Status != 'Cannot Ticket'"""
        try:
            dntkt_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-008"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{dntkt_cnt} finding(s) set to Do Not Ticket",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'To Close', IngestionStatus = 'To Close'
        WHERE cxProjectID = {proj_id} AND FoundInLastScan = 0 AND Status NOT IN
        ('Not Exploitable','Closed In Ticket','Closed','Cannot Ticket','Do Not Ticket') AND
        JiraIssueKey IS NOT NULL"""
        try:
            tc_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-009"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{tc_cnt} finding(s) set to To Close",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'Closed', IngestionStatus = 'Ticket Closed'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NOT NULL AND Status !=
        'Not Exploitable' AND JiraIssueKey IN (SELECT JiraIssueKey FROM JiraIssues WHERE Source =
        'Checkmarx' AND cxProjectID = {proj_id} AND JiraStatusCategory = 'Done') AND Status NOT IN
        ('Closed','New','To Ticket','To Update','New')"""
        try:
            c_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-010"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        sql = f"""UPDATE SASTFindings SET Status = 'Closed', IngestionStatus = 'Closed'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NULL AND Status NOT IN
        ('Not Exploitable','Closed') AND FoundInLastScan = 0 AND Status = 'New'"""
        try:
            c_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-011"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{c_cnt} finding(s) set to Closed",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'To Ticket', IngestionStatus = 'To Ticket'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NULL AND Status = 'New' AND
        cxResultState = 'Confirmed' AND FoundInLastScan = 1"""
        try:
            totkt_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-012"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{totkt_cnt} finding(s) set to To Ticket",2,"*",main_log)
        sql = f"""UPDATE SASTFindings SET Status = 'New', IngestionStatus = 'New'
        WHERE cxProjectID = {proj_id} AND JiraIssueKey IS NULL AND cxResultState =
        'To Verify'"""
        try:
            new_cnt += update(sql)
        except Exception as e_details:
            e_code = "RP-UFS-013"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"{new_cnt} finding(s) set to New",2,"*",main_log)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def reset_closed_findings(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """When a Jira ticket is closed, this resets the status to Confirmed"""
        msg = f'RESETTING CHECKMARX FINDING STATUSES FOR CLOSED TICKETS FOR PROJECT ID {proj_id}'
        TheLogs.log_headline(msg,3,"#",main_log)
        sql = f"""SELECT DISTINCT cxSimilarityID, cxLastScanID, JiraIssueKey FROM SASTFindings
        WHERE Status = 'Closed' AND cxProjectID = {proj_id} AND cxResultState != 'Not Exploitable'
        ORDER BY cxSimilarityID"""
        try:
            closed_sims = select(sql)
        except Exception as e_details:
            e_code = "RP-RCF-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return
        if closed_sims:
            for item in closed_sims:
                sim_id = item[0]
                last_scan_id = item[1]
                ticket = item[2]
                comment = f"Jira ticket {ticket} has been closed. Thus, this finding is being "
                comment += "reset to Confirmed result state."
                try:
                    get_finding = CxAPI.get_path_and_result_state(sim_id,proj_id,last_scan_id,
                                                                  main_log,ex_log,ex_file)
                except Exception as e_details:
                    func = f"CxAPI.get_path_and_result_state({sim_id},{proj_id},"
                    func += f"{last_scan_id})"
                    e_code = "RP-RCF-002"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                               rf'{ScrVar.src}',inspect.stack()[0][3],
                                               traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if get_finding:
                    cx_path_id = None
                    cx_state_name = None
                    res_id = None
                    if 'cxPathId' in get_finding:
                        cx_path_id = get_finding['cxPathId']
                        res_id = f"{last_scan_id}-{cx_path_id}"
                    if 'cxStateName' in get_finding:
                        cx_state_name = get_finding['cxStateName']
                    if cx_state_name != 'Confirmed':
                        try:
                            CxAPI.update_res_state(last_scan_id,cx_path_id,2,comment,main_log,
                                                   ex_log,ex_file)
                        except Exception as e_details:
                            func = f"CxAPI.update_result_state({last_scan_id}, "
                            func += f"{cx_path_id}, 2, '{comment}')"
                            e_code = "RP-RCF-003"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,rf'{ScrVar.src}',inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        if res_id is not None and ticket is not None:
                            try:
                                CxAPI.add_ticket_to_cx(res_id,ticket,main_log,ex_log,ex_file)
                            except Exception as e_details:
                                func = f"CxAPI.add_ticket_to_cx({res_id},'{ticket}')"
                                e_code = "RP-RCF-004"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                           ex_file,rf'{ScrVar.src}',inspect.stack()[0][3],
                                                           traceback.format_exc())
                                ScrVar.ex_cnt += 1
                                continue

    @staticmethod
    def sync_ticket_closed_status(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Updates TicketClosed in SASTFindings based on the status of the Jira ticket"""
        updated = 0
        if proj_id is None:
            msg = 'SYNCING CLOSED TICKETS FROM JiraIssues TO SASTFindings FOR ALL PROJECTS'
        else:
            msg = f'SYNCING CLOSED TICKETS FROM JiraIssues TO SASTFindings FOR PROJECT ID {proj_id}'
        TheLogs.log_headline(msg,3,"#",main_log)
        sql = """UPDATE SASTFindings SET TicketClosed = 1 WHERE JiraIssueKey IS NOT NULL
        AND JiraIssueKey IN (SELECT JiraIssueKey FROM JiraIssues WHERE (JiraStatusCategory = 'Done' OR
        JiraStatus = 'Sign Off Needed')) AND (TicketClosed != 1 OR
        TicketClosed IS NULL)"""
        if proj_id is not None:
            sql += f" AND cxProjectID = {proj_id}"
        try:
            updated += update(sql)
        except Exception as e_details:
            e_code = 'RP-STCS-001'
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"TicketClosed set to 1 for {updated} finding(s)",3,"*",main_log)
        updated = 0
        msg = f'SYNCING OPEN TICKETS FROM JiraIssues TO SASTFindings FOR PROJECT ID {proj_id}'
        TheLogs.log_headline(msg,3,"#",main_log)
        sql = """UPDATE SASTFindings SET TicketClosed = 0 WHERE JiraIssueKey IS NOT NULL AND
        JiraIssueKey IN (SELECT JiraIssueKey FROM JiraIssues WHERE (JiraStatusCategory != 'Done'
        AND JiraStatus != 'Sign Off Needed')) AND (TicketClosed != 0 OR TicketClosed IS NULL) AND
        Status NOT IN ('Closed','Not Exploitable')"""
        if proj_id is not None:
            sql += f" AND cxProjectID = {proj_id}"
        try:
            updated += update(sql)
        except Exception as e_details:
            e_code = 'RP-STCS-002'
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        TheLogs.log_info(f"TicketClosed set to 0 for {updated} finding(s)",3,"*",main_log)

    @staticmethod
    def alert_on_findings_needing_manual_review(main_log=LOG,ex_log=LOG_EXCEPTION,
                                                ex_file=EX_LOG_FILE):
        """Gets a list of any findings in To Verify state to return in an alert"""
        ScrVar.reset_exception_counts()
        to_alert = []
        sql = """SELECT DISTINCT cxQuery FROM SASTFindings WHERE cxResultState = 'To Verify'
        AND FoundInLastScan = 1 AND Status != 'Not Exploitable' ORDER BY cxQuery"""
        try:
            queries = select(sql)
        except Exception as e_details:
            e_code = 'RP-AOFNMR-001'
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}
        if queries != []:
            for item in queries:
                repo_list = []
                repos = CxReports.get_alert_repos(item[0],main_log,ex_log,ex_file)
                if repos != []:
                    for repo in repos:
                        repo_list.append(repo[0])
                to_alert.append({'cxQuery':item[0],'Repo(s)':repo_list})
            Alerts.manual_alert(rf'{ScrVar.src}',to_alert,len(to_alert),22,SLACK_URL)
        return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

    @staticmethod
    def get_alert_repos(cx_query,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Gets"""
        repos = []
        sql = f"""SELECT DISTINCT ApplicationAutomation.Repo FROM ApplicationAutomation
        INNER JOIN SASTFindings ON ApplicationAutomation.cxProjectID =
        SASTFindings.cxProjectID WHERE SASTFindings.cxResultState = 'To Verify' AND
        SASTFindings.cxQuery = '{cx_query}' AND FoundInLastScan = 1
        ORDER BY ApplicationAutomation.Repo"""
        try:
            repos = select(sql)
        except Exception as e_details:
            e_code = 'RP-GAR-001'
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return repos
