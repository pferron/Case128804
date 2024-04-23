"""Syncing result statuses from baseline to pipeline for Checkmarx"""

import os
import sys
import traceback
import inspect
from dotenv import load_dotenv
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from datetime import datetime
from common.database_appsec import select,update,delete_row,insert_multiple_into_table
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
    src = ALERT_SOURCE.replace("-","\\")

    @staticmethod
    def reset_exception_counts():
        """Used to reset fatal/regular exception counts"""
        ScrVar.fe_cnt = 0
        ScrVar.ex_cnt = 0

class PSActions:
    """Common actions for the CxPipelines class"""

    @staticmethod
    def get_findings_to_sync(status,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Retrieves the findings to sync for the given status"""
        sql = None
        results =[]
        match status:
            case 'Tech Debt':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE cxProjectID =
                {proj_id} AND cxResultState = 'Tech Debt' AND (TechDebtPipelineSync IS NULL OR
                TechDebtPipelineSync = 0)"""
            case 'Proposed Not Exploitable':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE cxProjectID =
                {proj_id} AND cxResultState = 'Proposed Not Exploitable' AND
                (ProposedNotExploitablePipelineSync IS NULL OR
                ProposedNotExploitablePipelineSync = 0)"""
            case 'Urgent':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE cxProjectID =
                {proj_id} AND cxResultState = 'Urgent' AND (UrgentPipelineSync IS NULL OR
                UrgentPipelineSync = 0)"""
            case 'Confirmed':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE cxProjectID =
                {proj_id} AND ((cxResultState = 'Confirmed' AND (ConfirmedPipelineSync IS NULL OR
                ConfirmedPipelineSync = 0) AND Status NOT IN ('Accepted','Past Due',
                'Not Exploitable')) OR (cxResultState NOT IN ('Confirmed','Not Exploitable') AND
                Status = 'Closed')) AND cxSimilarityID NOT IN (SELECT DISTINCT cxSimilarityID FROM
                JiraIssues WHERE RITMTicket IS NOT NULL AND JiraDueDate > GETDATE() AND Source =
                'Checkmarx' AND JiraStatusCategory != 'Done' AND cxSimilarityID NOT IN (SELECT
                DISTINCT cxSimilarityID FROM SASTFindings WHERE Status = 'Not Exploitable' AND
                cxProjectID = {proj_id}) AND cxProjectID = {proj_id} AND cxSimilarityID IN (SELECT
                DISTINCT cxSimilarityID FROM SASTFindings WHERE (ExceptionPipelineSync IS NULL OR
                ExceptionPipelineSync = 0) AND cxProjectID = {proj_id}))"""
            case 'Past Due':
                sql = f"""SELECT DISTINCT cxSimilarityID, cxResultState, cxResultID FROM
                SASTFindings WHERE cxProjectID = {proj_id} AND Status = 'Past Due' AND
                (PastDuePipelineSync IS NULL OR PastDuePipelineSync = 0)"""
            case 'Not Exploitable':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM SASTFindings WHERE cxProjectID =
                {proj_id} AND Status = 'Not Exploitable' AND (NotExploitablePipelineSync IS
                NULL OR NotExploitablePipelineSync = 0)"""
            case 'Accepted':
                sql = f"""SELECT DISTINCT cxSimilarityID FROM JiraIssues WHERE RITMTicket IS
                NOT NULL AND JiraDueDate > GETDATE() AND Source = 'Checkmarx' AND
                JiraStatusCategory != 'Done' AND cxSimilarityID NOT IN (SELECT DISTINCT
                cxSimilarityID FROM SASTFindings WHERE Status = 'Not Exploitable' AND cxProjectID =
                {proj_id}) AND cxProjectID = {proj_id} AND cxSimilarityID IN (SELECT DISTINCT
                cxSimilarityID FROM SASTFindings WHERE (ExceptionPipelineSync IS NULL OR
                ExceptionPipelineSync = 0) AND cxProjectID = {proj_id})"""
        if sql is not None:
            try:
                results = select(sql)
                # results = [('-952405625', )]
            except Exception as e_details:
                e_code = "PS-GFTS-001"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return []
        return results

    @staticmethod
    def get_pipeline_project_id(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Returns the corresponding cxPipelineProjectId for the specified cxBaselineProjectId"""
        pipeline_project = None
        sql = f"""SELECT cxPipelineProjectId FROM SASTProjects
        WHERE cxBaselineProjectId = {proj_id} AND cxPipelineProjectId IS NOT NULL"""
        try:
            results = select(sql)
            # results = [(10810, )]
        except Exception as e_details:
            e_code = "PS-GPPI-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        if results != []:
            pipeline_project = results[0][0]
        return pipeline_project

    @staticmethod
    def get_ticket_for_finding(status,proj_id,sim_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE):
        """Returns the corresponding Jira ticket and due date for the Baseline issue"""
        ticket_info = None
        add_to_query = ''
        match status:
            case 'Tech Debt':
                add_to_query = """ AND JiraStatusCategory != 'Done'"""
            case 'Proposed Not Exploitable':
                add_to_query = """ AND JiraStatusCategory != 'Done'"""
            case 'Urgent':
                add_to_query = """ AND JiraStatusCategory != 'Done'"""
            case 'Past Due':
                add_to_query = """ AND JiraStatusCategory != 'Done'"""
            case 'Not Exploitable':
                add_to_query = """ AND JiraStatusCategory != 'Done'"""
            case 'Accepted':
                add_to_query = """ AND JiraStatusCategory != 'Done' AND RITMTicket IS NOT NULL AND
                JiraDueDate > GETDATE()"""
        if proj_id == 10519:
            sql = f"""SELECT DISTINCT JiraIssueKey,JiraDueDate,RITMTicket FROM JiraIssues WHERE
            Source = 'Checkmarx' AND cxProjectId = {proj_id} AND cxSimilarityID LIKE '%{sim_id}%'
            {add_to_query} ORDER BY JiraDueDate"""
        else:
            sql = f"""SELECT DISTINCT JiraIssueKey,JiraDueDate,RITMTicket FROM JiraIssues WHERE
            Source = 'Checkmarx' AND cxProjectId = {proj_id} AND cxSimilarityID = {sim_id}
            {add_to_query} ORDER BY JiraDueDate"""
        try:
            results = select(sql)
            # results = [('AS-1189', datetime.date(2024, 3, 6), None)]
        except Exception as e_details:
            e_code = "PS-GTFF-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return None
        if results != []:
            ticket_info = {'JiraIssueKey':results[0][0],'JiraDueDate':results[0][1],
                           'RITMTicket':results[0][2]}
        else:
            ticket_info = {'JiraIssueKey':None,'JiraDueDate':None,
                           'RITMTicket':None}
        return ticket_info

    @staticmethod
    def get_pipeline_finding(pipeline_proj_id,sim_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Returns the corresponding Pipeline finding info for the Baseline issue"""
        return_info = None
        try:
            return_info = CxAPI.get_path_and_result_state(sim_id,pipeline_proj_id)
            # return_info = {'cxScanId': 1118025, 'cxPathId': 3, 'cxStateName': 'Not Exploitable'}
        except Exception as e_details:
            func = f"CxAPI.get_path_and_result_state({sim_id},{pipeline_proj_id})"
            e_code = "PS-GPF-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return return_info

    @staticmethod
    def set_result_state(state,scan_id,path_id,comment,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Sets the result state in Checkmarx and adds the specified comment"""
        state_set = False
        match state:
            case 'Tech Debt':
                set_state = 5
            case 'Proposed Not Exploitable':
                set_state = 4
            case 'Urgent':
                set_state = 3
            case 'Confirmed':
                set_state = 2
            case 'Past Due':
                set_state = 2
            case 'Not Exploitable':
                set_state = 1
            case 'Accepted':
                set_state = 1
        try:
            state_set = CxAPI.update_res_state(scan_id,path_id,set_state,comment)
            # set_state = True
        except Exception as e_details:
            func = f"CxAPI.update_res_state({scan_id},{path_id},{set_state},'{comment}')"
            e_code = "PS-SRS-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
        return state_set

    @staticmethod
    def set_ticket_in_checkmarx(result_id,ticket,main_log=LOG,ex_log=LOG_EXCEPTION,
                                ex_file=EX_LOG_FILE):
        """Sets the Jira ticket for the Checkmarx Pipeline finding"""
        try:
            CxAPI.add_ticket_to_cx(result_id,ticket)
        except Exception as e_details:
            func = f"CxAPI.add_ticket_to_cx('{result_id}','{ticket}')"
            e_code = "PS-STIC-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1

    @staticmethod
    def set_finding_sync(state,proj_id,sim_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                         ex_file=EX_LOG_FILE):
        """Sets the appropriate finding sync column in SASTFindings"""
        tech_debt_sync = 'NULL'
        proposed_ne_sync = 'NULL'
        urgent_sync = 'NULL'
        confirmed_sync = 'NULL'
        past_due_sync = 'NULL'
        exception_sync = 'NULL'
        not_exploitable_sync = 'NULL'
        add_sql = ''
        match state:
            case 'Tech Debt':
                tech_debt_sync = 1
            case 'Proposed Not Exploitable':
                proposed_ne_sync = 1
            case 'Urgent':
                urgent_sync = 1
            case 'Confirmed':
                confirmed_sync = 1
            case 'Past Due':
                past_due_sync = 1
            case 'Not Exploitable':
                not_exploitable_sync = 1
            case 'Accepted':
                exception_sync = 1
                add_sql = f"""UPDATE SASTFindings SET Status = 'Accepted' WHERE cxSimilarityID =
                {sim_id} AND cxProjectId = {proj_id} AND Status NOT IN ('Closed','To Close',
                'Closed In Ticket','Not Exploitable','Accepted') AND JiraIssueKey IS NOT NULL"""
        sql = f"""UPDATE SASTFindings SET ConfirmedPipelineSync = {confirmed_sync},
        ExceptionPipelineSync = {exception_sync}, NotExploitablePipelineSync =
        {not_exploitable_sync}, PastDuePipelineSync = {past_due_sync},
        ProposedNotExploitablePipelineSync = {proposed_ne_sync}, TechDebtPipelineSync =
        {tech_debt_sync}, UrgentPipelineSync = {urgent_sync} WHERE cxSimilarityID = {sim_id} AND
        cxProjectId = {proj_id}{add_sql}"""
        try:
            update(sql)
        except Exception as e_details:
            e_code = "PS-SFS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1

    @staticmethod
    def delete_old_scan(scan_type,scan_id,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Ensures that SASTScans only has the latest scans on file"""
        if scan_type == 'Baseline':
            proj_col = 'BaselineProjectID'
        else:
            proj_col = 'PipelineProjectID'
        sql = f"""DELETE FROM SASTScans WHERE ScanType = '{scan_type}' and ScanID != {scan_id} AND
        {proj_col} = {proj_id}"""
        try:
            delete_row(sql)
        except Exception as e_details:
            e_code = "PS-DOS-001"
            TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                  inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1

    @staticmethod
    def baseline_scan_exists(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Checks if the Baseline scan is logged in SASTScans already and returns info to insert
        if it is not"""
        exists = None
        try:
            baseline_scan = CxAPI.get_last_scan_data(proj_id)
        except Exception as e_details:
            func = f"CxAPI.get_last_scan_id({proj_id})"
            e_code = "PS-BSE-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return exists
        if baseline_scan != {}:
            sql = f"""SELECT ScanID FROM SASTScans WHERE BaselineProjectID = {proj_id} AND
            ScanID = {baseline_scan['ID']}"""
            try:
                check_scan = select(sql)
            except Exception as e_details:
                e_code = "PS-BSE-002"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return exists
            if check_scan == []:
                exists = {'BaselineProjectID':proj_id,'ScanType':'Baseline','ScanID':
                        baseline_scan['ID'],'ScanDate':baseline_scan['Finished']}
            if exists is not None:
                PSActions.delete_old_scan('Baseline',baseline_scan['ID'],proj_id,main_log,ex_log,
                                        ex_file)
        return exists

    @staticmethod
    def pipeline_scan_exists(proj_id,baseline_proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
        """Checks if the Pipeline scan is logged in SASTScans already and returns info to insert
        if it is not"""
        exists = None
        try:
            pipeline_scan = CxAPI.get_last_scan_data(proj_id)
        except Exception as e_details:
            func = f"CxAPI.get_last_scan_id({proj_id})"
            e_code = "PS-PSE-001"
            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                       inspect.stack()[0][3],traceback.format_exc())
            ScrVar.ex_cnt += 1
            return exists
        if pipeline_scan != {}:
            sql = f"""SELECT ScanID FROM SASTScans WHERE PipelineProjectID = {proj_id} AND
            ScanID = {pipeline_scan['ID']}"""
            try:
                check_scan = select(sql)
            except Exception as e_details:
                e_code = "PS-PSE-002"
                TheLogs.sql_exception(sql,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                      inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return exists
            if check_scan == []:
                exists = {'BaselineProjectID':baseline_proj_id,'PipelineProjectID':proj_id,
                          'ScanType':'Pipeline','ScanID':pipeline_scan['ID'],'ScanDate':
                          pipeline_scan['Finished']}
            if exists is not None:
                PSActions.delete_old_scan('Pipeline',pipeline_scan['ID'],proj_id,main_log,ex_log,
                                          ex_file)
        return exists

class CxPipelines():
    """Provides functions required to sync data to pipelines"""

    @staticmethod
    def update_scans(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the latest pipeline scan info to SASTScans"""
        new_scan = False
        to_add = []
        msg = f"ADDING THE LATEST SCANS TO THE DATABASE FOR PROJECT ID {proj_id}"
        TheLogs.log_headline(msg,2,"#",main_log)
        baseline_scan = PSActions.baseline_scan_exists(proj_id,main_log,ex_log,ex_file)
        # baseline_scan = {'BaselineProjectID':10915,'ScanType':'Pipeline','ScanID':1119564,
        # 'ScanDate':'2023-10-02 11:15:36'}
        if baseline_scan is not None and baseline_scan != {}:
            to_add.append(baseline_scan)
        pipeline_proj = PSActions.get_pipeline_project_id(proj_id,main_log,ex_log,ex_file)
        # pipeline_proj = 10810
        pipeline_scan = None
        if pipeline_proj is not None:
            pipeline_scan = PSActions.pipeline_scan_exists(pipeline_proj,proj_id,main_log,ex_log,
                                                           ex_file)
            # pipeline_scan = {'BaselineProjectID':10915,'PipelineProjectID':10810,'ScanType':
            # 'Pipeline','ScanID':1119564,'ScanDate':'2023-10-02 11:15:36'}
        if pipeline_scan is not None and pipeline_scan != {}:
            to_add.append(pipeline_scan)
        if len(to_add) > 0:
            try:
                insert_multiple_into_table('SASTScans',to_add)
                new_scan = True
            except Exception as e_details:
                func = f"insert_multiple_into_table('SASTScans',{to_add})"
                e_code = "PS-UPS-001"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,ScrVar.src,
                                           inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                return new_scan
        if new_scan is True:
            TheLogs.log_info(f"{len(to_add)} scan(s) added to the database",2,"*",main_log)
        else:
            TheLogs.log_info('No new scans found',2,"*",main_log)
        return new_scan

    @staticmethod
    def sync_findings_to_pipeline(proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Syncs the statuses from the baseline findings to the pipeline findings"""
        ScrVar.reset_exception_counts()
        needs_updates = False
        needs_updates = CxPipelines.update_scans(proj_id,main_log,ex_log,ex_file)
        if needs_updates is True:
            CxPipelines.sync_state_to_pipeline('Tech Debt',proj_id,main_log,ex_log,ex_file)
            CxPipelines.sync_state_to_pipeline('Proposed Not Exploitable',proj_id,main_log,ex_log,
                                            ex_file)
            CxPipelines.sync_state_to_pipeline('Urgent',proj_id,main_log,ex_log,ex_file)
            CxPipelines.sync_state_to_pipeline('Confirmed',proj_id,main_log,ex_log,ex_file)
            CxPipelines.sync_state_to_pipeline('Past Due',proj_id,main_log,ex_log,ex_file)
            CxPipelines.sync_state_to_pipeline('Not Exploitable',proj_id,main_log,ex_log,ex_file)
            CxPipelines.sync_state_to_pipeline('Accepted',proj_id,main_log,ex_log,ex_file)
        else:
            msg = f"SKIPPING PIPELINE STATUS SYNC FOR PROJECT ID {proj_id}"
            TheLogs.log_headline(msg,2,"#",main_log)
            TheLogs.log_info('No new scan(s) found',2,"*",main_log)
        return {'FatalCount': ScrVar.fe_cnt, 'ExceptionCount': ScrVar.ex_cnt}

    @staticmethod
    def sync_state_to_pipeline(sync_state,proj_id,main_log=LOG,ex_log=LOG_EXCEPTION,
                               ex_file=EX_LOG_FILE,log_lines=True):
        """Syncs the specified state to the pipeline"""
        set_cnt = 0
        hl_state = str(sync_state).upper()
        msg = f"SYNCING {hl_state} STATUS TO THE PIPELINE FOR PROJECT ID {proj_id}"
        if log_lines is True:
            TheLogs.log_headline(msg,2,"#",main_log)
        findings_to_sync = PSActions.get_findings_to_sync(sync_state,proj_id,main_log,ex_log,
                                                          ex_file)
        # findings_to_sync = [('-1007447064', ), ]
        if findings_to_sync != []:
            pipeline_proj = PSActions.get_pipeline_project_id(proj_id,main_log,ex_log,ex_file)
            # pipeline_proj = 10810
            if pipeline_proj is not None:
                for item in findings_to_sync:
                    sim_id = item[0]
                    pipeline_finding = None
                    pipeline_state = None
                    set_state = False
                    get_ticket = PSActions.get_ticket_for_finding(sync_state,proj_id,sim_id,
                                                                  main_log,ex_log,ex_file)
                    # get_ticket = {'JiraIssueKey': 'AS-1189',
                    # 'JiraDueDate': datetime.date(2024, 3, 6), 'RITMTicket': None}
                    if get_ticket is not None:
                        ticket = get_ticket['JiraIssueKey']
                        due_date = get_ticket['JiraDueDate']
                        ritm = get_ticket['RITMTicket']
                        comment = None
                        match sync_state:
                            case 'Tech Debt':
                                comment = f"Tech debt ticket {ticket} is due on {due_date}."
                            case 'Proposed Not Exploitable':
                                comment = 'ProdSec is in process of reviewing this finding.'
                                if ticket is not None:
                                    comment += f' Current ticket {ticket} is due on {due_date}.'
                            case 'Urgent':
                                comment = 'This finding has been marked as Urgent by ProdSec.'
                                if ticket is not None:
                                    comment += f' Current ticket {ticket} is due on {due_date}.'
                            case 'Confirmed':
                                comment = 'This finding has been Confirmed by ProdSec.'
                                if ticket is not None:
                                    comment += f' Current ticket {ticket} is due on {due_date}.'
                            case 'Past Due':
                                comment = 'This finding has been Confirmed by ProdSec. Current '
                                comment += f'ticket {ticket} was past due as of {due_date}.'
                            case 'Not Exploitable':
                                if ticket is not None:
                                    comment = 'This finding has been marked as Not Exploitable by '
                                    comment += f'ProdSec. Ticket {ticket} will be closed or '
                                    comment += 'cancelled.'
                                else:
                                    ticket = None
                                    comment = 'This finding has been marked as Not Exploitable by '
                                    comment += 'ProdSec.'
                            case 'Accepted':
                                comment = f'An exception has been granted in {ritm}. Jira ticket '
                                comment += f'{ticket} is now due on {due_date}.'
                        pipeline_finding = PSActions.get_pipeline_finding(pipeline_proj,sim_id,
                                                                          main_log,ex_log,ex_file)
                        # pipeline_finding = {'cxScanId': 1118025, 'cxPathId': 3,
                        # 'cxStateName': 'Not Exploitable'}
                    if pipeline_finding is not None and comment is not None:
                        path_id = pipeline_finding['cxPathId']
                        scan_id = pipeline_finding['cxScanId']
                        result_id = f"{scan_id}-{path_id}"
                        pipeline_state = pipeline_finding['cxStateName']
                        if pipeline_state != sync_state:
                            set_state = PSActions.set_result_state(sync_state,scan_id,path_id,
                                                                   comment,main_log,ex_log,ex_file)
                            if set_state is True:
                                set_cnt += 1
                                PSActions.set_ticket_in_checkmarx(result_id,ticket,main_log,ex_log,
                                                                  ex_file)
                    if set_state is True or pipeline_state == sync_state:
                        PSActions.set_finding_sync(sync_state,proj_id,sim_id)
        if log_lines is True:
            TheLogs.log_info(f"{sync_state} status synced for {set_cnt} finding(s)",2,"*",main_log)
        not_set = len(findings_to_sync)-set_cnt
        if not_set > 0 and log_lines is True:
            TheLogs.log_info(f'{not_set} {sync_state} Baseline findings not found in the Pipeline',
                             2,"*",main_log)
        return set_cnt
