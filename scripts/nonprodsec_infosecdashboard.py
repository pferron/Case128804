"""Updates the InfoSecDashboard database. DO NOT MAKE CHANGES UNLESS YOU CHECK WITH LISA FIRST!"""

import datetime
import os
import inspect
import traceback
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from dotenv import load_dotenv
from datetime import datetime
from common.jira_functions import GeneralTicketing
from common.database_generic import DBQueries
from common.logging import TheLogs
from common.miscellaneous import Misc
from infosecdashboard.database import IFDQueries

load_dotenv()
BACKUP_DATE = datetime.now().strftime("%Y-%m-%d")
ALERT_SOURCE = TheLogs.set_alert_source(os.path.dirname(__file__),os.path.basename(__file__))
LOG_FILE = TheLogs.set_log_file(ALERT_SOURCE)
EX_LOG_FILE = TheLogs.set_exceptions_log_file(ALERT_SOURCE)
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')

def main():
    """Runs the specified stuff"""
    # infosecdashboard_updates()

class ScrVar():
    """Stuff for script"""
    ex_cnt = 0
    fe_cnt = 0
    db_default = 'InfoSecDashboard'
    starting_at = 0
    u_tickets_cnt = 0
    i_tickets_cnt = 0
    u_sub_cnt = 0
    i_sub_cnt = 0
    ticket_updates = []
    ticket_inserts = []
    subtask_updates = []
    subtask_inserts = []
    start_timer = None
    src = ALERT_SOURCE.replace("-","\\")
    running_function = ''

    @staticmethod
    def timed_script_setup(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the starting timer stuff"""
        ScrVar.start_timer = Misc.start_timer()

    @staticmethod
    def timed_script_teardown(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
        """Adds the ending timer stuff"""
        TheLogs.process_exception_count_only(ScrVar.fe_cnt,1,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        TheLogs.process_exception_count_only(ScrVar.ex_cnt,2,rf'{ALERT_SOURCE}',SLACK_URL,ex_file)
        Misc.end_timer(ScrVar.start_timer,rf'{ALERT_SOURCE}',ScrVar.running_function,ScrVar.ex_cnt,
                       ScrVar.fe_cnt)

def infosecdashboard_updates(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Runs all updates"""
    ScrVar.running_function = inspect.stack()[0][3]
    ScrVar.timed_script_setup(main_log,ex_log,ex_file)
    update_programs(main_log,ex_log,ex_file)
    update_projects_and_epics(main_log,ex_log,ex_file)
    update_tickets_and_tasks(main_log,ex_log,ex_file)
    ScrVar.timed_script_teardown(main_log,ex_log,ex_file)
    return {'FatalCount':ScrVar.fe_cnt,'ExceptionCount':ScrVar.ex_cnt}

def update_programs(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the programs on file"""
    all_updates = 0
    all_adds = 0
    TheLogs.log_headline('UPDATING ALL PROGRAMS ON FILE',2,"#",main_log)
    try:
        jira_projects = IFDQueries.get_projects(main_log)
    except Exception as e_details:
        func = "DBQueries.get_projects()"
        e_code = "NI-UP-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if jira_projects != [] and jira_projects is not None:
        for project in jira_projects:
            updates = []
            inserts = []
            a_programs = 0
            u_programs = 0
            jira_key = project[0]
            project_name = project[1]
            TheLogs.log_headline(f'Updating programs for {project_name}',3,"-",main_log)
            try:
                programs = GeneralTicketing.get_child_programs(jira_key)
            except Exception as e_details:
                func = f"GeneralTicketing.get_child_programs('{jira_key}')"
                e_code = "NI-UP-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if programs != [] and programs is not None:
                for program in programs:
                    try:
                        i_exists = IFDQueries.check_if_program_exists(program['IssueKey'])
                    except Exception as e_details:
                        func = f"DBQueries.check_if_program_exists({program['IssueKey']})"
                        e_code = "NI-UP-003"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if i_exists is True:
                        updates.append({'SET': {'JiraProjectName':project_name,
                                                'ProgramName':program['ProgramName'],
                                                'Labels':program['Labels'],
                                                'Priority':program['Priority'],
                                                'State':program['State'],
                                                'JiraStatusCategory':program['JiraStatusCategory'],
                                                'Reporter':program['Reporter'],
                                                'Assignee':program['Assignee'],
                                                'CreatedDate':program['CreatedDate'],
                                                'DueDate':program['DueDate'],
                                                'StartDate':program['StartDate'],
                                                'UpdatedDate':program['UpdatedDate'],
                                                'ResolutionDate':program['ResolutionDate']},
                                            'WHERE_EQUAL': {'ProgramKey':program['IssueKey']},
                                            'WHERE_NOT': None})
                    else:
                        inserts.append({'JiraProjectName':project_name,
                                        'ProgramKey':program['IssueKey'],
                                        'ProgramName':program['ProgramName'],
                                        'Labels':program['Labels'],
                                        'Priority':program['Priority'],
                                        'State':program['State'],
                                        'JiraStatusCategory':program['JiraStatusCategory'],
                                        'Reporter':program['Reporter'],
                                        'Assignee':program['Assignee'],
                                        'CreatedDate':program['CreatedDate'],
                                        'DueDate':program['DueDate'],
                                        'StartDate':program['StartDate'],
                                        'UpdatedDate':program['UpdatedDate'],
                                        'ResolutionDate':program['ResolutionDate']})
            try:
                u_programs += DBQueries.update_multiple('JiraPrograms',updates,ScrVar.db_default,
                                                        show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.update_multiple('JiraPrograms',{updates},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UP-004"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            all_updates += u_programs
            u_programs_lng = f"{u_programs} program(s) updated"
            TheLogs.log_info(u_programs_lng,3,"-",main_log)
            try:
                a_programs += DBQueries.insert_multiple('JiraPrograms',inserts,ScrVar.db_default,
                                                        show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('JiraPrograms',{updates},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UP-005"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            all_adds += a_programs
            a_programs_lng = f"{a_programs} program(s) added"
            TheLogs.log_info(a_programs_lng,3,"-",main_log)
    TheLogs.log_headline('PROGRAM UPDATES SUMMARY (ALL PROJECTS)',3,'*',main_log)
    all_updates_lng = f"{all_updates} program(s) updated"
    TheLogs.log_info(all_updates_lng,3,"*",main_log)
    all_adds_lng = f"{all_adds} program(s) added"
    TheLogs.log_info(all_adds_lng,3,"*",main_log)

def update_projects_and_epics(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the JiraProjects and JiraEpics tables"""
    ta_projects_cnt = 0
    tu_projects_cnt = 0
    ta_epics_cnt = 0
    tu_epics_cnt = 0
    TheLogs.log_headline('UPDATING PROJECTS & EPICS ON FILE',2,"#",main_log)
    try:
        jira_projects = IFDQueries.get_projects(main_log)
    except Exception as e_details:
        func = f"IFDQueries.get_projects()"
        e_code = "NI-UPAE-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                    rf'{ScrVar.src}',inspect.stack()[0][3],
                                    traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if jira_projects != []:
        for project in jira_projects:
            a_projects_cnt = 0
            u_projects_cnt = 0
            a_epics_cnt = 0
            u_epics_cnt = 0
            a_projects = []
            u_projects = []
            a_epics = []
            u_epics = []
            TheLogs.log_headline(f'Updating projects & epics for {project[1]}',3,"-",main_log)
            try:
                jira_programs = IFDQueries.get_programs_for_project(project[1],main_log)
            except Exception as e_details:
                func = f"IFDQueries.get_programs_for_project('{project[1]}')"
                e_code = "NI-UPAE-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if jira_programs != []:
                for program in jira_programs:
                    prog_key = program[0]
                    prog_name = program[1]
                    try:
                        p_info = GeneralTicketing.get_child_projects(prog_key)
                    except Exception as e_details:
                        func = f"GeneralTicketing.get_child_projects('{prog_key}')"
                        e_code = "NI-UPAE-003"
                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                   rf'{ScrVar.src}',inspect.stack()[0][3],
                                                   traceback.format_exc())
                        ScrVar.ex_cnt += 1
                        continue
                    if p_info != [] and p_info is not None:
                        for proj in p_info:
                            proj_key = proj['IssueKey']
                            proj_name = proj['Summary']
                            try:
                                proj_exists = IFDQueries.check_if_project_exists(proj_key,main_log)
                            except Exception as e_details:
                                func = f"IFDQueries.check_if_project_exists('{proj_key}')"
                                e_code = "NI-UPAE-004"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                    ex_file,rf'{ScrVar.src}',inspect.stack()[0][3],
                                                    traceback.format_exc())
                                ScrVar.ex_cnt += 1
                                continue
                            if proj_exists is True:
                                u_projects.append({'SET': {'ProjectName':proj_name,
                                                           'ProgramName':prog_name,
                                                           'ProgramKey':prog_key,
                                                           'JiraProjectName':project[1],
                                                           'Labels':proj['Labels'],
                                                           'Priority':proj['Priority'],
                                                           'State':proj['State'],
                                                           'JiraStatusCategory':
                                                           proj['JiraStatusCategory'],
                                                           'Reporter':proj['Reporter'],
                                                           'Assignee':proj['Assignee'],
                                                           'CreatedDate':proj['CreatedDate'],
                                                           'DueDate':proj['DueDate'],
                                                           'StartDate':proj['StartDate'],
                                                           'UpdatedDate':proj['UpdatedDate'],
                                                           'ResolutionDate':proj['ResolutionDate']},
                                                    'WHERE_EQUAL': {'ProjectKey':proj_key},
                                                    'WHERE_NOT': None})
                            else:
                                a_projects.append({'ProjectName':proj_name,
                                                   'ProgramName':prog_name,
                                                   'ProjectKey':proj_key,
                                                   'ProgramKey':prog_key,
                                                   'JiraProjectName':project[1],
                                                   'Labels':proj['Labels'],
                                                   'Priority':proj['Priority'],
                                                   'State':proj['State'],
                                                   'JiraStatusCategory':proj['JiraStatusCategory'],
                                                   'Reporter':proj['Reporter'],
                                                   'Assignee':proj['Assignee'],
                                                   'CreatedDate':proj['CreatedDate'],
                                                   'DueDate':proj['DueDate'],
                                                   'StartDate':proj['StartDate'],
                                                   'UpdatedDate':proj['UpdatedDate'],
                                                   'ResolutionDate':proj['ResolutionDate']})
                            try:
                                child_epics = GeneralTicketing.get_child_epics(proj['IssueKey'])
                            except Exception as e_details:
                                func = f"GeneralTicketing.get_child_epics('{proj['IssueKey']}')"
                                e_code = "NI-UPAE-005"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                           ex_file,rf'{ScrVar.src}',
                                                           inspect.stack()[0][3],
                                                           traceback.format_exc())
                                ScrVar.ex_cnt += 1
                                continue
                            if child_epics != []:
                                for epic in child_epics:
                                    try:
                                        e_exists = IFDQueries.check_if_epic_exists(epic['IssueKey'],
                                                                                   main_log)
                                    except Exception as e_details:
                                        func = f"IFDQueries.check_if_epic_exists('{epic['IssueKey']}')"
                                        e_code = "NI-UPAE-006"
                                        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                                ex_file,rf'{ScrVar.src}',
                                                                inspect.stack()[0][3],
                                                                traceback.format_exc())
                                        ScrVar.ex_cnt += 1
                                        continue
                                    if e_exists is True:
                                        u_epics.append({'SET': {'JiraProjectName':project[1],
                                                                'ProjectName':proj_name,
                                                                'ProgramKey':prog_key,
                                                                'ProgramName':prog_name,
                                                                'ProjectKey':proj_key,
                                                                'EpicName':epic['Summary'],
                                                                'Labels':epic['Labels'],
                                                                'Priority':epic['Priority'],
                                                                'State':epic['State'],
                                                                'JiraStatusCategory':
                                                                epic['JiraStatusCategory'],
                                                                'Reporter':epic['Reporter'],
                                                                'Assignee':epic['Assignee'],
                                                                'CreatedDate':epic['CreatedDate'],
                                                                'DueDate':epic['DueDate'],
                                                                'StartDate':epic['StartDate'],
                                                                'UpdatedDate':epic['UpdatedDate'],
                                                                'ResolutionDate':
                                                                epic['ResolutionDate']},
                                                        'WHERE_EQUAL': {'EpicKey':epic['IssueKey']},
                                                        'WHERE_NOT': None})
                                    else:
                                        a_epics.append({'JiraProjectName':project[1],
                                                        'ProjectName':proj_name,
                                                        'ProgramKey':prog_key,
                                                        'ProgramName':prog_name,
                                                        'ProjectKey':proj_key,
                                                        'EpicName':epic['Summary'],
                                                        'EpicKey':epic['IssueKey'],
                                                        'Labels':epic['Labels'],
                                                        'Priority':epic['Priority'],
                                                        'State':epic['State'],
                                                        'JiraStatusCategory':
                                                        epic['JiraStatusCategory'],
                                                        'Reporter':epic['Reporter'],
                                                        'Assignee':epic['Assignee'],
                                                        'CreatedDate':epic['CreatedDate'],
                                                        'DueDate':epic['DueDate'],
                                                        'StartDate':epic['StartDate'],
                                                        'UpdatedDate':epic['UpdatedDate'],
                                                        'ResolutionDate':epic['ResolutionDate']})
            try:
                a_projects_cnt += DBQueries.insert_multiple('JiraProjects',a_projects,ScrVar.db_default,
                                                        show_progress=False)
                ta_projects_cnt += a_projects_cnt
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('JiraProjects',{a_projects},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UPAE-007"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{a_projects_cnt} project(s) added',3,"-",main_log)
            try:
                u_projects_cnt += DBQueries.update_multiple('JiraProjects',u_projects,ScrVar.db_default,
                                                        show_progress=False)
                tu_projects_cnt += u_projects_cnt
            except Exception as e_details:
                func = f"DBQueries.update_multiple('JiraPrograms',{u_projects},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UPAE-008"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{u_projects_cnt} project(s) updated',3,"-",main_log)
            try:
                a_epics_cnt += DBQueries.insert_multiple('JiraEpics',a_epics,ScrVar.db_default,
                                                        show_progress=False)
                ta_epics_cnt += a_epics_cnt
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('JiraEpics',{a_epics},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UPAE-009"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{a_epics_cnt} epic(s) added',3,"-",main_log)
            try:
                u_epics_cnt += DBQueries.update_multiple('JiraEpics',u_epics,ScrVar.db_default,
                                                        show_progress=False)
                tu_epics_cnt += u_epics_cnt
            except Exception as e_details:
                func = f"DBQueries.update_multiple('JiraEpics',{u_epics},'{ScrVar.db_default}',"
                func += "show_progress=False)"
                e_code = "NI-UPAE-010"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{u_epics_cnt} epic(s) updated',3,"-",main_log)
    TheLogs.log_headline('UPDATED PROJECTS & EPICS SUMMARY (ALL PROJECTS)',3,"*",main_log)
    TheLogs.log_info(f'{ta_projects_cnt} project(s) added',3,"*",main_log)
    TheLogs.log_info(f'{tu_projects_cnt} project(s) updated',3,"*",main_log)
    TheLogs.log_info(f'{ta_epics_cnt} epic(s) added',3,"*",main_log)
    TheLogs.log_info(f'{tu_epics_cnt} epic(s) updated',3,"*",main_log)

def update_tickets_and_tasks(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    """Updates the tickets and tasks on file"""
    a_tkts = 0
    u_tkts = 0
    a_tsks = 0
    u_tsks = 0
    TheLogs.log_headline('UPDATING ALL TICKETS & TASKS',2,"#",main_log)
    try:
        project_list = IFDQueries.get_projects(main_log)
    except Exception as e_details:
        func = "IFDQueries.get_projects()"
        e_code = "NI-UTAT-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                rf'{ScrVar.src}',inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if project_list != [] and project_list is not None:
        for project in project_list:
            ScrVar.u_tickets_cnt = 0
            ScrVar.i_tickets_cnt = 0
            ScrVar.u_sub_cnt = 0
            ScrVar.i_sub_cnt = 0
            ScrVar.ticket_updates = []
            ScrVar.ticket_inserts = []
            ScrVar.subtask_updates = []
            ScrVar.subtask_inserts = []
            proj_name = project[1]
            use_table = project[2]
            if use_table is None:
                use_table = f"Jira{proj_name}".replace(" ","")
            try:
                table_exists = IFDQueries.check_if_table_exists(use_table,main_log)
            except Exception as e_details:
                func = f"IFDQueries.check_if_table_exists('{use_table}')"
                e_code = "NI-UTAT-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                        rf'{ScrVar.src}',inspect.stack()[0][3],
                                        traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if table_exists is True:
                try:
                    jt_update = [{'SET':{'InfoSecDashboardTable':use_table},
                                  'WHERE_EQUAL':{'JiraProjectName':proj_name}}]
                    DBQueries.update_multiple('JiraTeams',jt_update,ScrVar.db_default,
                                              show_progress=False)
                except Exception as e_details:
                    func = f"DBQueries.update_multiple('JiraTeams',{jt_update},"
                    func += f"{ScrVar.db_default},show_progress=False)"
                    e_code = "NI-UTAT-003"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                TheLogs.log_headline(f'Updating tickets & tasks for {proj_name}',3,"-",main_log)
                try:
                    get_epics = IFDQueries.get_epics_for_project(proj_name,main_log)
                except Exception as e_details:
                    func = f"IFDQueries.get_epics_for_project('{proj_name}')"
                    e_code = "NI-UTAT-004"
                    TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                            rf'{ScrVar.src}',inspect.stack()[0][3],
                                            traceback.format_exc())
                    ScrVar.ex_cnt += 1
                    continue
                if get_epics != []:
                    for epic in get_epics:
                        e_key = epic
                        try:
                            get_jira_issues_for_epic(e_key,1,use_table,main_log)
                        except Exception as e_details:
                            func = f"get_issues_for_epic('{e_key}',1,{use_table})"
                            e_code = "NI-UTAT-005"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                                       rf'{ScrVar.src}',inspect.stack()[0][3],
                                                       traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
            try:
                u_tkts += DBQueries.update_multiple(use_table,ScrVar.ticket_updates,
                                                    ScrVar.db_default,show_progress=False)
                ScrVar.u_tickets_cnt += u_tkts
            except Exception as e_details:
                func = f"DBQueries.update_multiple('{use_table}',{ScrVar.ticket_updates},"
                func += f"'{ScrVar.db_default}',show_progress=False)"
                e_code = "NI-UTAT-006"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{u_tkts} ticket(s) updated',3,"-",main_log)
            try:
                a_tkts += DBQueries.insert_multiple(use_table,ScrVar.ticket_inserts,
                                                    ScrVar.db_default,show_progress=False)
                ScrVar.i_tickets_cnt += a_tkts
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('{use_table}',{ScrVar.ticket_inserts},"
                func += f"'{ScrVar.db_default}',show_progress=False)"
                e_code = "NI-UTAT-007"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{a_tkts} ticket(s) added',3,"-",main_log)
            try:
                u_tsks += DBQueries.update_multiple(use_table,ScrVar.subtask_updates,
                                                    ScrVar.db_default,show_progress=False)
                ScrVar.u_sub_cnt += u_tsks
            except Exception as e_details:
                func = f"DBQueries.update_multiple('{use_table}',{ScrVar.subtask_updates},"
                func += f"'{ScrVar.db_default}',show_progress=False)"
                e_code = "NI-UTAT-008"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{u_tsks} task(s) updated',3,"-",main_log)
            try:
                a_tsks += DBQueries.insert_multiple(use_table,ScrVar.subtask_inserts,
                                                    ScrVar.db_default,show_progress=False)
                ScrVar.i_sub_cnt += a_tsks
            except Exception as e_details:
                func = f"DBQueries.insert_multiple('{use_table}',{ScrVar.subtask_inserts},"
                func += f"'{ScrVar.db_default}',show_progress=False)"
                e_code = "NI-UTAT-009"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
            TheLogs.log_info(f'{a_tsks} task(s) added',3,"-",main_log)
            try:
                updated_day = datetime.now()
                team_update = [{'SET': {'LastSyncDate':updated_day},
                                'WHERE_EQUAL': {'JiraProjectName':proj_name}}]
                DBQueries.update_multiple('JiraTeams',team_update,ScrVar.db_default,
                                          show_progress=False)
            except Exception as e_details:
                func = f"DBQueries.update_multiple('JiraTeams',{team_update},"
                func += f"'{ScrVar.db_default}',show_progress=False)"
                e_code = "NI-UTAT-010"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,
                                           rf'{ScrVar.src}',inspect.stack()[0][3],
                                           traceback.format_exc())
                ScrVar.ex_cnt += 1
    TheLogs.log_headline('SUMMARY OF TICKET & TASK UPDATES',3,"*",main_log)
    TheLogs.log_info(f'{ScrVar.u_tickets_cnt} ticket(s) updated',3,"*",main_log)
    TheLogs.log_info(f'{ScrVar.i_tickets_cnt} ticket(s) added',3,"*",main_log)
    TheLogs.log_info(f'{ScrVar.u_sub_cnt} tasks(s) updated',3,"*",main_log)
    TheLogs.log_info(f'{ScrVar.i_sub_cnt} task(s) added',3,"*",main_log)

def get_jira_issues_for_epic(epic_key,start_at,use_table,main_log=LOG,ex_log=LOG_EXCEPTION,
                             ex_file=EX_LOG_FILE):
    """Updates the Jira issues in the specified project table"""
    i_cnt = 0
    ScrVar.starting_at = start_at
    try:
        issues = GeneralTicketing.get_child_issues(epic_key,start_at)
    except Exception as e_details:
        func = f"GeneralTicketing.get_child_issues('{epic_key}',{start_at})"
        e_code = "NI-GJIFE-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1
        return
    if issues != []:
        for issue in issues:
            i_cnt += 1
            try:
                issue_exists = IFDQueries.check_if_issue_exists(use_table,issue['IssueKey'],
                                                                main_log)
            except Exception as e_details:
                func = f"IFDQueries.check_if_issue_exists(use_table,'{issue['IssueKey']}')"
                e_code = "NI-GJIFE-002"
                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                        inspect.stack()[0][3],traceback.format_exc())
                ScrVar.ex_cnt += 1
                continue
            if issue_exists is True:
                ScrVar.ticket_updates.append({'SET': {'EpicIssueKey':epic_key,
                                        'IssueType':issue['IssueType'],
                                        'Summary':issue['Summary'],
                                        'Labels':issue['Labels'],
                                        'Priority':issue['Priority'],
                                        'State':issue['State'],
                                        'JiraStatusCategory':issue['JiraStatusCategory'],
                                        'Reporter':issue['Reporter'],
                                        'Assignee':issue['Assignee'],
                                        'CreatedDate':issue['CreatedDate'],
                                        'DueDate':issue['DueDate'],
                                        'StartDate':issue['StartDate'],
                                        'UpdatedDate':issue['UpdatedDate'],
                                        'ResolutionDate':issue['ResolutionDate']},
                                    'WHERE_EQUAL': {'IssueKey':issue['IssueKey'],
                                                    'SubTaskIssueKey':None},
                                    'WHERE_NOT': None})
            else:
                ScrVar.ticket_inserts.append({'EpicIssueKey':epic_key,
                                'IssueType':issue['IssueType'],
                                'Summary':issue['Summary'],
                                'Labels':issue['Labels'],
                                'Priority':issue['Priority'],
                                'State':issue['State'],
                                'JiraStatusCategory':issue['JiraStatusCategory'],
                                'Reporter':issue['Reporter'],
                                'Assignee':issue['Assignee'],
                                'CreatedDate':issue['CreatedDate'],
                                'DueDate':issue['DueDate'],
                                'StartDate':issue['StartDate'],
                                'UpdatedDate':issue['UpdatedDate'],
                                'ResolutionDate':issue['ResolutionDate'],
                                'IssueKey':issue['IssueKey'],
                                'SubTaskIssueKey':None})
            if issue['SubtaskCount'] > 0:
                if issue['Subtasks'] != []:
                    for subtask in issue['Subtasks']:
                        try:
                            task = GeneralTicketing.get_task_json(subtask)
                        except Exception as e_details:
                            func = f"GeneralTicketing.get_task_json('{subtask}')"
                            e_code = "NI-GJIFE-003"
                            TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                       ex_file,rf'{ScrVar.src}',
                                                       inspect.stack()[0][3],traceback.format_exc())
                            ScrVar.ex_cnt += 1
                            continue
                        if task != {} and task is not None:
                            try:
                                subtask_exists = IFDQueries.check_if_subtask_exists(use_table,
                                                                                    subtask,
                                                                                    main_log)
                            except Exception as e_details:
                                func = f"IFDQueries.check_if_subtask_exists('{use_table}','{subtask}')"
                                e_code = "NI-GJIFE-004"
                                TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,
                                                        ex_file,rf'{ScrVar.src}',
                                                        inspect.stack()[0][3],traceback.format_exc())
                                ScrVar.ex_cnt += 1
                                continue
                            if subtask_exists is True:
                                ScrVar.subtask_updates.append({'SET': {'EpicIssueKey':epic_key,
                                                            'IssueKey':issue['IssueKey'],
                                                            'IssueType':task['IssueType'],
                                                            'Summary':task['Summary'],
                                                            'Labels':task['Labels'],
                                                            'Priority':task['Priority'],
                                                            'State':task['State'],
                                                            'JiraStatusCategory':
                                                            task['JiraStatusCategory'],
                                                            'Reporter':task['Reporter'],
                                                            'Assignee':task['Assignee'],
                                                            'CreatedDate':task['CreatedDate'],
                                                            'DueDate':task['DueDate'],
                                                            'StartDate':task['StartDate'],
                                                            'UpdatedDate':task['UpdatedDate'],
                                                            'ResolutionDate':task['ResolutionDate']},
                                                    'WHERE_EQUAL': {'SubTaskIssueKey':subtask},
                                                    'WHERE_NOT': None})
                            else:
                                ScrVar.subtask_inserts.append({'EpicIssueKey':epic_key,
                                                    'IssueKey':issue['IssueKey'],
                                                    'IssueType':task['IssueType'],
                                                    'Summary':task['Summary'],
                                                    'Labels':task['Labels'],
                                                    'Priority':task['Priority'],
                                                    'State':task['State'],
                                                    'JiraStatusCategory':
                                                    task['JiraStatusCategory'],
                                                    'Reporter':task['Reporter'],
                                                    'Assignee':task['Assignee'],
                                                    'CreatedDate':task['CreatedDate'],
                                                    'DueDate':task['DueDate'],
                                                    'StartDate':task['StartDate'],
                                                    'UpdatedDate':task['UpdatedDate'],
                                                    'ResolutionDate':task['ResolutionDate'],
                                                    'SubTaskIssueKey':subtask})
        if i_cnt == 50:
            ScrVar.starting_at = start_at + i_cnt
            to_run = [{'function':'get_jira_issues_for_epic',
                        'args':[epic_key,ScrVar.starting_at,use_table,main_log]}]
            repeat_function(to_run,main_log,ex_log,ex_file)

def repeat_function(list_of_dicts,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    '''When a function needs to be repeated, pass it through this'''
    try:
        for cmd in list_of_dicts:
            if 'args' in cmd:
                globals()[cmd['function']](*cmd['args'])
    except Exception as e_details:
        func = f"repeat_function({list_of_dicts})"
        e_code = "NI-RF-001"
        TheLogs.function_exception(func,e_code,e_details,ex_log,main_log,ex_file,rf'{ScrVar.src}',
                                   inspect.stack()[0][3],traceback.format_exc())
        ScrVar.fe_cnt += 1

if __name__ == "__main__":
    main()