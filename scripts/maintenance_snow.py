import os
import pysnow
os.environ['CALLED_FROM'] = f"{os.path.dirname(__file__)}\{os.path.basename(__file__)}"
from appsec_secrets import Conjur
os.environ['CALLED_FROM'] = 'Unset'
from common.alerts import Alerts
from common.constants import SNOW_INSTANCE, SNOW_USER
from common.logging import TheLogs
from common.database_appsec import select, update, insert
from common.general import General
from common.miscellaneous import Misc
from snow.task_manager import SNTasksManager
from datetime import datetime
import sys
import pytz
from dotenv import load_dotenv

load_dotenv()
ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".", 1)[0]
LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
SLACK_URL_ALERTS = os.environ.get('SLACK_URL_ALERTS')
TASK_TABLE = None
CHANGE_TABLE = None
APP_TABLE = None
APPROVAL_TABLE = None
GROUP_TABLE = None
USER_TABLE = None
JIRA_TABLE = None
snJiraProjectKey = ''
SNOW_KEY = os.environ.get('SNOW_KEY')


def main():
    """Runs the specified stuff"""
    run_cmd = General.cmd_processor(sys.argv)
    for cmd in run_cmd:
        if 'args' in cmd:
            globals()[cmd['function']](*cmd['args'])
        else:
            globals()[cmd['function']]()

def every_5_minutes():
    """Runs every 5 minutes"""
    running_function = "every_5_minutes"
    start_timer = Misc.start_timer()
    process_new_records()
    Misc.end_timer(start_timer, rf'{ALERT_SOURCE}', running_function, 0, 0)

# This function is used to create the global object of the task_table to be used to make API calls to SNOW on the tasks table
# If the global object has not been created, the funciton will create it and return it to the caller.
# If the global object has been created, the function simply returns the object to the caller
def task_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global TASK_TABLE
    if not TASK_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        TASK_TABLE = c.resource(api_path='/table/x_prole_software_c_software_change_task')
    return TASK_TABLE


# This function is used to create the global object of the CHANGE_TABLE to be used to make API calls to SNOW on the changes table
# If the global object has not been created, the funciton will create it and return it to the caller.
# If the global object has been created, the function simply returns the object to the caller
def change_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global CHANGE_TABLE
    if not CHANGE_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        CHANGE_TABLE = c.resource(api_path='/table/x_prole_software_c_software_change_request_table')
    return CHANGE_TABLE

# This function is used to create the global object of the APP_TABLE to be used to make API calls to SNOW on the app table
# If the global object has not been created, the funciton will create it and return it to the caller.
# If the global object has been created, the function simply returns the object to the caller
def app_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global APP_TABLE
    if not APP_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        APP_TABLE = c.resource(api_path='/table/cmdb_ci_service_auto')
    return APP_TABLE

def cmdb_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global CMDB_TABLE
    # Create client object
    c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
    # Set the table to make the call against
    CMDB_TABLE = c.resource(api_path='/table/cmdb_ci_appl')
    return CMDB_TABLE

def jira_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global JIRA_TABLE
    if not JIRA_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        JIRA_TABLE = c.resource(api_path='/table/u_jira_projects')
    return JIRA_TABLE

# This function returns all SNOW application records with a subcategory of Application and a name that is not null
def getsnJiraProjectKey(jira_key):
    # Set the query so that it will return all changes starting with the system date that we began getting SNOW tasks
    for key in getJiraKey(jira_key):
        snJiraProjectKey = key['u_project_key']
    return snJiraProjectKey

def getJiraKey(jira_key):
    # Set the query so that it will return all changes starting with the system date that we began getting SNOW tasks
    my_query = pysnow.QueryBuilder()
    my_query.field('sys_id').equals(jira_key)
    return jira_table().get(query=my_query).all()

def user_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global USER_TABLE
    if not USER_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        USER_TABLE = c.resource(api_path='/table/sys_user')
    return USER_TABLE

def group_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global GROUP_TABLE
    if not GROUP_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        GROUP_TABLE = c.resource(api_path='/table/sys_user_group')
    return GROUP_TABLE

# This function is used to create the global object of the APPROVAL_TABLE to be used to make API calls to SNOW on the approval table
# If the global object has not been created, the funciton will create it and return it to the caller.
# If the global object has been created, the function simply returns the object to the caller
def approval_table():
    # Must use the global declaration since we are changing the value of the global variable in this fuction
    global APPROVAL_TABLE
    if not APPROVAL_TABLE:
        # Create client object
        c = pysnow.Client(instance = SNOW_INSTANCE, user=SNOW_USER, password=SNOW_KEY)
        # Set the table to make the call against
        APPROVAL_TABLE = c.resource(api_path='/table/sysapproval_approver')
    return APPROVAL_TABLE

# This function will take in a UTC date string and convert it to Mountain time.
# We use this function to get the local time and write it to our database so that we can verify when a record was created in local time
# Input and return are strings like YY-MM-DD HH-MM-SS
def utc_to_local(utc_dt):
    # If we get a null string, we need to just sent it right back or else we will have conversion errors
    if utc_dt == '':
        return ''
    # Set the incoming timezone to UTC
    utc_tz = pytz.timezone('UTC')
    # Set the return timezone (local) to MST
    local_tz = pytz.timezone('US/Mountain')
    # Convert the incoming date string to date time object
    utc_dt = utc_tz.localize(datetime.strptime(utc_dt, '%Y-%m-%d %H:%M:%S'))
    # Convert the UTC date to the local timezone
    local_dt = utc_dt.astimezone(local_tz)
    # Retuen the local tz datetime object as a string
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')

# This function will take in a MST date convert it to UTC.
# Input and return are date objects
def local_to_utc(mst_dt):
    # If we get a null string, we need to just sent it right back or else we will have conversion errors
    if mst_dt == '':
        return ''
    # Set the incomming timezone (local) to MST
    local_tz = pytz.timezone('US/Mountain')
    # Set the return timezone to UTC
    utc_tz = pytz.timezone('UTC')
    # Convert the incoming date string to date time object
    mst_dt = local_tz.localize(mst_dt)
    #mst_dt = local_tz.localize(datetime.strptime(mst_dt, '%Y-%m-%d %H:%M:%S'))
    # Convert the local (MST) date to UTC
    utc_dt = mst_dt.astimezone(utc_tz)
    # Retuen the UTC tz datetime object as a string
    return utc_dt

# This function is used to pull back a single SNOW task record that matches the request task number
# The return is the SNOW record in dict format
def get_task(taskNumber):
    # Query for software change task
    response = task_table().get(query={'number': taskNumber}, stream=True)
    for record in response.all():
        print(record)
    return response.one()

# This function will return all the software change tasks from SNOW
# The return is an array if SNOW records as an array of dict objects
def get_all_tasks():
    my_query = pysnow.QueryBuilder()
    my_query.field('short_description').equals('Run Security Scans').AND().field('parent').not_equals('')
    return task_table().get(query=my_query).all()

# This function will return all the software change tasks that were created after a specified date
def get_tasks_after_date(startDate):
    # Convert the local date/time to UTC before searching in ServiceNow
    utc_date = local_to_utc(startDate)
    my_query = pysnow.QueryBuilder()
    my_query.field('short_description').equals('Run Security Scans').AND().field('sys_created_on').greater_than(utc_date)
    return task_table().get(query=my_query).all()

# This function will return all the software change tasks for 'run security scans' that are in an 'open' state.  The numeric value for open is '1'
# The return is all open snow tasks records as an array of dict objects
def get_all_open_tasks():
    my_query = pysnow.QueryBuilder()
    my_query.field('short_description').equals('Run Security Scans').AND().field('state').equals('1')
    #count = 0
    #for record in change_table().get(query=my_query).all():
    #    print(record['number'])
    #    count += 1
    #print(count)
    return task_table().get(query=my_query).all()

# This function will return all the software changes that were created after a specified date
def get_changes_after_date(startDate):
    # Convert the local date/time to UTC before searching in ServiceNow
    utc_date = local_to_utc(startDate)
    my_query = pysnow.QueryBuilder()
    #startDate = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')
    my_query.field('sys_created_on').greater_than(utc_date)
    return change_table().get(query=my_query).all()

# This function returns all SNOW chang records that were created after we began receiving SNOW tasks
def get_all_changes():
    # Set the query so that it will return all changes starting with the system date that we began getting SNOW tasks
    my_query = pysnow.QueryBuilder()
    my_query.field('sys_created_on').greater_than(datetime(2020,9,13,16,48,44))
    return change_table().get(query=my_query).all()

# This function returns the snow change record for the submitted change number
def get_change_by_number(change_number):
    my_query = pysnow.QueryBuilder()
    my_query.field('number').equals(change_number)
    return change_table().get(query=my_query).one()

# This function will return the snow change record for the criteria passed in
# The input needs to be a dict object that contains 1 key and 1 value - i.e {'number': 'CCSX0001234'} or {'sys_id': 'a84440e21b7d685007028408624bcb09}
# The return is a SNOW record that matches the query as a Dict object
def get_change_by_query(my_query):
    # Query for software changes
    response = change_table().get(query=my_query, stream=True)
    #for record in response.all():
    #    print(record)
    return response.one()

# This is just a placeholder function used to perform different queries against the SNOW API
def execute_query():
    count = 0
    my_query = pysnow.QueryBuilder()
    #my_query.field('estimated_production_date').less_than(datetime(2021, 1, 31)).AND().field('status').less_than(9)
    my_query.field('status').not_equals('9').AND().field('status').not_equals('10').AND().field('status').not_equals('11').AND().field('estimated_production_date').less_than(datetime(2021, 2, 2))
    for record in change_table().get(query=my_query).all():
        print('Change Request: ' + record['number'] + ' - Status: ' + record['status'] + ' - Estimated Production Date: ' + record['estimated_production_date'])
        count += 1
    print(count)
    my_query = pysnow.QueryBuilder()
    #my_query.field('estimated_production_date').less_than(datetime(2021, 1, 31)).AND().field('status').less_than(9)
    my_query.field('status').not_equals('1').AND().field('status').not_equals('2').AND().field('status').not_equals('5').AND().field('status').not_equals('6').AND().field('status').not_equals('7').AND().field('status').not_equals('8').AND().field('status').not_equals('9').AND().field('status').not_equals('10').AND().field('status').not_equals('11')
    for record in change_table().get(query=my_query).all():
        print('Change Request: ' + record['number'] + ' - Status: ' + record['status'] + ' - Estimated Production Date: ' + record['estimated_production_date'])
    return

def validate_open_tasks():
    sql = "SELECT snTaskNumber as taskNumber from snTaskRecords WHERE StateText = 'Open'"
    for row in select(sql):
        task = get_task(row.taskNumber)
        print(row.taskNumber + ' - ' + task['state'])
    return

def process_all_updates():
    running_function = "process_all_updates"
    start_timer = Misc.start_timer()
    TheLogs.log_headline('Processing Update SNOW records Started',1,"#",LOG)
    process_change_updates()
    process_task_updates()
    process_app_updates()
    TheLogs.log_headline('Processing Update SNOW Records Complete',1,"#",LOG)
    Misc.end_timer(start_timer, rf'{ALERT_SOURCE}', running_function, 0, 0)
    return

def process_task_updates():
    TheLogs.log_headline('Processing task updates',2,"#",LOG)
    updates = 0
    for task in get_all_tasks():
        if task_in_table(task['number']) is not None:
            update_task_db(task)
            updates += 1
    TheLogs.log_info(f'{updates} snow tasks updated in the table',1,"*",LOG)
    return

def task_in_table(task_number):
    sql = f"SELECT TOP 1 count(*) FROM snTaskRecords WHERE snTaskNumber = '{task_number}'"
    task_exists = select(sql)
    if task_exists:
        return task_exists[0][0]
    return None

def write_task_db(task):
    # Get the change request tied to this task
    change = get_change_by_query({'sys_id': task['parent']['value']})
    # Build the SQL statement to insert this task into the table
    sql = """INSERT INTO snTaskRecords (snTaskNumber, snState, StateText, snChangeRequest, snSysCreatedOn, snSysUpdatedOn, highFindings)
                        VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', 0)"""
    sql = sql.format(task['number'], task['state'], get_task_state_text(task['state']), change['number'], utc_to_local( task['sys_created_on']), utc_to_local(task['sys_updated_on']))
    insert(sql)
    return

def update_task_db(task):
    # Get the change request tied to this task
    change = get_change_by_query({'sys_id': task['parent']['value']})
    # Build the SQL statement to insert this task into the table
    sql = """UPDATE snTaskRecords set snState = '{0}', StateText = '{1}', snChangeRequest = '{2}', snSysUpdatedOn = '{3}'
                        WHERE snTaskNumber = '{4}'"""
    sql = sql.format(task['state'], get_task_state_text(task['state']), change['number'], utc_to_local(task['sys_updated_on']), task['number'])
    update(sql)
    return

def process_change_updates():
    TheLogs.log_headline('Processing software change updates',2,"#",LOG)
    updates = 0
    for change in get_all_changes():
        if change['number'] == 'CCSX0003987':
            print("pause")
        if change_in_table(change['number']) is not None:
            update_change_db(change)
            updates += 1
    # Set the '1900-01-01 00:00:00' dates back to NULL.  When updating the SNOW dates in the DB, the SNOW dates are '' versus NULL
    null_blank_change_dates()
    TheLogs.log_headline(f'{updates} snow changes updated in the table',2,"#",LOG)
    return

def change_in_table(change_number):
    sql = f"SELECT TOP 1 count(*) FROM snChangeRecords WHERE snChangeNumber = '{change_number}'"
    ch_exists = select(sql)
    if ch_exists:
        return ch_exists[0][0]
    return None

def write_change_db(change):
    # Get a list of CIs that require SAST scans from the change request CI list
    # check_sast_ci will return a comma separated string of CIs that require SAST scanning
    sast_ci = check_sast_ci(change["u_cmdb_ci"])
    scanning_needed = 0
    if len(sast_ci) > 0:
        scanning_needed = 1
    # Get a comma separated list of app names to write to the DB
    app_names = get_app_names_from_sysid(change["u_cmdb_ci"])
    # Get a comma separated list of app names that require SAST scanning to write to the DB
    sast_app_names = get_app_names_from_sysid(sast_ci)
    # Validate we have boarded all the CIs on the change.  If not, we need to set the flag to review the change
    if all_cis_verified(change["u_cmdb_ci"]):
        review_required = 0
    else:
        review_required = 1
    #Check to see if we have a missing prod date or missing CIs
    if change['u_cmdb_ci'] == '' or change['estimated_production_date'] == '':
        missing_data = 1
    else:
        missing_data = 0
    # This is needed in case the branch listed on the change is not properly set from a case sensitivity perspective for the master branch
    if change['rc_branch'] == 'Master':
        rc_branch = 'master'
    else:
        rc_branch = change['rc_branch']
    # Build the SQL statement to insert this change reqcord into the table
    sql = """INSERT INTO snChangeRecords (snChangeNumber, snSysCreatedOn, snSysUpdatedOn, snSysID, snStatus, StatusText, snShortDescription, snRcEntry, snEstimatedProdDate, origProdDate, snRcBranch,
                        snNewSoftware, snChangeType, OrigChangeType, snDeploymentEnd, snClosedAt, snCI, origCI, SASTCI, AppNames, OrigAppNames, SASTAppNames, ScanRequired, MissingData, CICount, ReviewRequired)
                        VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', '{17}', '{18}', '{19}', '{20}', '{21}', '{22}', {23}, {24}, {25})"""
    sql = sql.format(change['number'], utc_to_local(change['sys_created_on']), utc_to_local(change['sys_updated_on']), change['sys_id'], change['status'], get_change_status_text(change['status']), change['short_description'].replace("'","")
                    , change['rc_entry'], change['estimated_production_date'], change['estimated_production_date'], rc_branch, change['new_software'], change['change_type'], change['change_type'], utc_to_local(change['deployment_end'])
                    , utc_to_local(change['closed_at']), change['u_cmdb_ci'], change['u_cmdb_ci'], sast_ci, app_names, app_names, sast_app_names, scanning_needed, missing_data, count_cis(change['u_cmdb_ci']), review_required)
    insert(sql)
    return

def update_change_db(change):
    # Get a list of CIs that require SAST scans from the change request CI list
    # check_sast_ci will return a comma separated string of CIs that require SAST scanning
    sast_ci = check_sast_ci(change["u_cmdb_ci"])
    scanning_needed = 0
    if len(sast_ci) > 0:
        scanning_needed = 1
    # Get a comma separated list of app names to write to the DB
    app_names = get_app_names_from_sysid(change["u_cmdb_ci"])
    # Validate we have boarded all the CIs on the change.  If not, we need to set the flag to review the change
    if all_cis_verified(change["u_cmdb_ci"]):
        review_required = 0
    else:
        review_required = 1
    # Get a comma separated list of app names that require SAST scanning to write to the DB
    sast_app_names = get_app_names_from_sysid(sast_ci)
    # Check to see if this change has been approved yet
    # If we get a date that the change was approved, we know the change was approved.
    approved_on = check_change_approval(change['number'])
    if len(approved_on) > 0:
        approved = 1
    else:
        approved = 0
    # We need to check to see if the current prod date on the change is the same that is recorded in our DB
    # If it is not, then the date has changed or been rescheduled.  We need to increment the Rescheduled counter by one
    sql = "SELECT snEstimatedProdDate, Rescheduled FROM snChangeRecords WHERE snChangeNumber = '" + change['number'] + "'"
    query_response = select(sql)
    if query_response:
        db_date = query_response[0][0]
        rescheduled_counter = query_response[0][1]
        if change["estimated_production_date"] != "" and db_date.strftime("%Y-%m-%d") != change["estimated_production_date"]:
            rescheduled_counter += 1
        # This is needed in case the branch listed on the change is not properly set from a case sensitivity perspective for the master branch
        if change['rc_branch'] == 'Master':
            rc_branch = 'master'
        else:
            rc_branch = change['rc_branch']
        # Build the SQL statement to update this change in the table
        sql = """UPDATE snChangeRecords set snStatus = '{0}', StatusText = '{1}', snSysUpdatedOn = '{2}', snShortDescription = '{3}', snRcEntry = '{4}', snEstimatedProdDate = '{5}', snRcBranch = '{6}', snNewSoftware = '{7}',
                            snDeploymentEnd = '{8}', snClosedAt = '{9}', snCI = '{10}', SASTCI = '{11}', Approved = {12}, ApprovedOn = '{13}', AppNames = '{14}', SASTAppNames = '{15}', ScanRequired = {16}, Rescheduled = {17},
                            CICount = {18}, ReviewRequired = {19}, snChangeType = '{20} '
                            WHERE snChangeNumber = '{21}'"""
        sql = sql.format(change['status'], get_change_status_text(change['status']), utc_to_local(change['sys_updated_on']), change['short_description'].replace("'", ""), change['rc_entry'], change['estimated_production_date']
                        , rc_branch, change['new_software'], utc_to_local(change['deployment_end']), utc_to_local(change['closed_at']), change['u_cmdb_ci'], sast_ci, approved, utc_to_local(approved_on), app_names, sast_app_names
                        , scanning_needed, rescheduled_counter, count_cis(change['u_cmdb_ci']), review_required, change['change_type'], change['number'])
        update(sql)
    null_blank_change_dates()
    return

def null_blank_change_dates():
    # Now we will get rid of all the '1900-01-01 00:00:00' date values where a date was not set yet in the change request data
    sql = "UPDATE snChangeRecords SET snDeploymentEnd = NULL WHERE snDeploymentEnd = '1900-01-01 00:00:00'"
    update(sql)
    sql = "UPDATE snChangeRecords SET snClosedAt = NULL WHERE snClosedAt = '1900-01-01 00:00:00'"
    update(sql)
    return

# This function will call the functions to get and record any new SNOW changes and tasks
def process_new_records():
    TheLogs.log_headline('Processing New SNOW records Started',1,"#",LOG)
    process_new_changes()
    process_new_tasks()
    TheLogs.log_headline('Processing New SNOW records Complete',1,"#",LOG)
    return

# This function will get a listing of new SNOW changes that have been created since the last one was written to the DB.
# The function will then add the new change request to the DB.
def process_new_tasks():
    sql = "SELECT TOP 1 snTaskNumber as taskNumber, snSysCreatedOn as snSysCreatedOn from snTaskRecords ORDER BY snSysCreatedOn DESC"
    db_task = select(sql)
    if db_task:
        tasks = get_tasks_after_date(db_task[0].snSysCreatedOn)
        snow_task_manager = SNTasksManager()
        for task in tasks:
            write_task_db(task)
            change = get_change_by_query({'sys_id': task['parent']['value']})
            update_change_db(change)
            TheLogs.log_info(f'Task {task["number"]} added to the database',1,"#",LOG)
            required_scans = write_required_scans_db(change['number'])
            if len(required_scans) > 0:
                schedule_scans_for_change(change['number'])
                comment = "Scan(s) of  "
                for scan in required_scans:
                    comment += scan['name'] + " (" + scan['sysid'] + "), "
                comment = comment[0:-2] + " is/are required."
                add_comment_to_task(task['number'], comment)
            else:
                if review_required_on_change(change['number']):
                    comment = "Change request has an issue that needs to be reviewed before task can be approved."
                else:
                    comment = "No apps identified on the change request require scanning at this time."
                add_comment_to_task(task['number'], comment)
                task_number = task['number']
                change_number = change['number']
                snow_task_manager.pass_validation_on_task(task_number, change_number)
    return

def write_required_scans_db(change_number):
    required_scans = []
    sql = "SELECT SASTCI FROM snChangeRecords WHERE snChangeNumber = '" + change_number + "'"
    CIs = select(sql)[0][0]
    if CIs == '':
        return required_scans
    for app_sysid in CIs.split(","):
        sql = "SELECT snName from snAppRecords WHERE snSysID = '" + app_sysid + "'"
        app_name = select(sql)[0][0]
        sql = "INSERT INTO RequiredScans (ChangeNumber, AppSysID, AppName) VALUES ('{0}', '{1}', '{2}')"
        sql = sql.format(change_number, app_sysid, app_name)
        insert(sql)
        TheLogs.log_info(f'Required scan for {app_sysid}: {app_name} on {change_number} '
                             f'has been added to the database',1,"*",LOG)
        required_scans.append({'name': app_name, 'sysid': app_sysid})
    return required_scans

def review_required_on_change(change_number):
    sql = "SELECT ReviewRequired FROM snChangeRecords WHERE snChangeNumber = '" + change_number + "'"
    required = select(sql)[0][0]
    return required

# This function will get a listing of new SNOW changes that have been created since the last one was written to the DB.
# The function will then add the new tasks to the DB.
def process_new_changes():
    sql = "SELECT TOP 1 snChangeNumber as changeNumber, snSysCreatedOn as snSysCreatedOn from snChangeRecords ORDER BY snSysCreatedOn DESC"
    db_change = select(sql)
    if db_change:
        changes = get_changes_after_date(db_change[0].snSysCreatedOn)
        for change in changes:
            write_change_db(change)
            TheLogs.log_info(f'Change {change["number"]} added to the database',1,"*",LOG)
    return

# This function will be used to get a listing of all the CMDB CIs in the service now table and insert new apps or update existing apps in the SQL Database
def process_app_updates():
    TheLogs.log_headline('Processing App updates',2,"#",LOG)
    updates = 0
    inserts = 0
    for app in all_snow_apps():
        if app_in_db(app['sys_id']) is not None:
            update_app_db(app)
            updates += 1
        else:
            write_app_db(app)
            inserts += 1
    TheLogs.log_info(f'{inserts} snow apps inserted into the table',2,"*",LOG)
    TheLogs.log_info(f'{updates} snow apps updated in the table',2,"*",LOG)
    return

# This function returns all SNOW application records with a subcategory of Application and a name that is not null
def all_snow_apps():
    # Set the query so that it will return all changes starting with the system date that we began getting SNOW tasks
    my_query = pysnow.QueryBuilder()
    my_query.field('name').not_equals('').AND().field('used_for').equals('Production')
    return app_table().get(query=my_query).all()

# This function returns a single SNOW application record
def single_snow_app(Repo):
    # Set the query so that it will return all changes starting with the system date that we began getting SNOW tasks
    my_query = pysnow.QueryBuilder()
    my_query.field('name').equals(Repo).AND().field('used_for').equals('Production')
    return cmdb_table().get(query=my_query).all()

def app_in_db(app_id):
    sql = f"SELECT TOP 1 count(*) FROM snAppRecords WHERE snSysID = '{app_id}'"
    in_db = select(sql)
    if in_db:
        return in_db[0][0]
    return None

def update_app_db(app):
    global snJiraProjectKey
    if app['owned_by'] == '':
        owned_by = ''
    else:
        owned_by = app_owned_by(app['owned_by']['value'])
    if app['managed_by'] == '':
        managed_by = ''
    else:
        managed_by = app_managed_by(app['managed_by']['value'])
    if app['u_ci_cd_pipeline'] == 'Yes':
        ci_cd = 1
    else:
        ci_cd = 0
    # Check to see if the Jira Project is set
    if len(app['u_jira_project']) == 2:
        jira_key = getsnJiraProjectKey(app['u_jira_project']['value'])
    else:
        jira_key = ""
    # Build the SQL statement to update this task in the tabl
    sql = """UPDATE snAppRecords set snName = '{0}', snUsedFor = '{1}', snServiceClassification = '{2}', snManagedBy = '{3}', snOwnedBy = '{4}', snCICD = {5}, snRepo = '{6}', snJiraProjectKey = '{7}'
                        WHERE snSysID = '{8}'"""
    sql = sql.format(app['name'], app['used_for'], app['service_classification'], managed_by, owned_by, ci_cd, app['u_repository_name'].replace(" ", "-").lower(), jira_key, app['sys_id'])
    update(sql)
    return

def write_app_db(app):
    global snJiraProjectKey
    if app['owned_by'] == '':
        owned_by = ''
    else:
        owned_by = app_owned_by(app['owned_by']['value'])
    if app['managed_by'] == '':
        managed_by = ''
    else:
        managed_by = app_managed_by(app['managed_by']['value'])
    if app['u_ci_cd_pipeline'] == 'Yes':
        ci_cd = 1
    else:
        ci_cd = 0
    # Check to see if the Jira Project is set
    if len(app['u_jira_project']) == 2:
        jira_key = getsnJiraProjectKey(app['u_jira_project']['value'])
    else:
        jira_key = ""
    # Build the SQL statement to insert this task into the table
    sql = """INSERT INTO snAppRecords (snSysID, snName, snUsedFor, snServiceClassification, snManagedBy, snOwnedBy, snCICD, snRepo, snJiraProjectKey) Values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6}, '{7}', '{8}')"""
    sql = sql.format(app['sys_id'], app['name'], app['used_for'], app['service_classification'], managed_by, owned_by, ci_cd, app['u_repository_name'].replace(" ", "-").lower(), jira_key)
    insert(sql)
    return

# This function will take in a string with comma separated list of values, compare those values against the snSysID on the Applications table
# The function will create a list of SysIDs that have a 1 value in the SASTRequired column in the table and before returning the results, convert that list to a comma
# separated string.
def check_sast_ci(ci_list):
    sast_ci = []
    for ci in ci_list.split(","):
        sql = f"""SELECT TOP 1 SASTRequired FROM Applications WHERE snSysID = '{ci}' AND SASTRequired = 1"""
        sast_required = select(sql)
        if sast_required:
            sast_ci.append(ci)
    # This join statement will convert the list object to a comma separated string
    return ",".join(sast_ci)

def get_app_names_from_sysid(sys_id_list):
    app_names = []
    for sys_id in sys_id_list.split(","):
        sql = "SELECT TOP 1 snName FROM snAppRecords WHERE snSysID = '" + sys_id + "'"
        app_name = select(sql)
        if app_name:
            app_names.append(app_name[0][0])
    # return the app_names list as a comma separated string
    return ",".join(app_names)

def all_cis_verified(sys_id_list):
    sys_ids = ""
    # if there are no CIs in the list, we need to return false
    if len(sys_id_list) == 0:
        return False
    # Validate all the CIs in the list are found in our application table
    for sys_id in sys_id_list.split(","):
        sql = "SELECT TOP 1 * FROM Applications WHERE snSysID = '" + sys_id + "' AND Retired = 0"
        if not select(sql):
            return False
    return True

# This function will check to see if there is an approval record from AppSec on the submitted Change Request number
# The function will return a 0 if there is no approval record, and a 1 if there is an approval record
def check_change_approval(change_number):
    my_query = pysnow.QueryBuilder()
    my_query.field('u_approval_for_string').equals(change_number)\
                    .AND().field('sys_updated_by').equals('chris.parliment')\
                    .OR().field('sys_updated_by').equals('chris.parliment@progleasing.com')\
                    .OR().field('sys_updated_by').equals('sean.mclaughlin')\
                    .OR().field('sys_updated_by').equals('sean.mclaughlin@progleasing.com')\
                    .OR().field('sys_updated_by').equals('john.mccutchen')\
                    .OR().field('sys_updated_by').equals('john.mccutchen@progleasing.com')
    approvals = approval_table().get(query=my_query).all()
    if len(approvals) > 0:
        approval_date =  approvals[0]['sys_updated_on']
    else:
        approval_date = ''
    return approval_date

def update_orig_app_names():
    sql = "SELECT snChangeNumber as snChangeNumber, OrigCI as OrigCI FROM snChangeRecords"
    for row in select(sql):
        if row.OrigCI != None:
            app_names = get_app_names_from_sysid(row.OrigCI)
            sql = "UPDATE snChangeRecords SET OrigAppNames = '{0}' WHERE snChangeNumber = '{1}'"
            sql = sql.format(app_names, row.snChangeNumber)
            update(sql)
    return

def count_cis(change_cis):
    ci_count = 0
    if len(change_cis) > 0:
        ci_count = len(change_cis.split(","))
    return ci_count

# Retuan the text equivalent to the change record status value
# Some of these "values" are actually text already and need to be account for by checking the length of the index passed in
# If the index is > 2 then we have been given a text value and will just pass that right back
def get_change_status_text(index):
    if len(index) > 2:
        return index
    status_text = ['Unused', 'Pipeline', 'Ready for RC', 'Index3', 'Index4', 'Ready for RC Deployment', 'RC Testing', 'CIO Production Sign-Off', 'Scheduled for Deployment', 'Deployed to Produciton', 'Failed/Rolled back', 'Cancelled']
    return status_text[int(index)]

def get_task_state_text(index):
    state_text = ['Unused', 'Open', 'Cancelled', 'Passed Validation', 'Failed Validation']
    if int(index) > 4:
        return "Unknown"
    return state_text[int(index)]

# This function will schedule and then kickoff the scans for any SASTCI that is in the database for the requested change number
def schedule_scans_for_change(change_number):
    sql = "SELECT SASTCI as sast_ids, snRcBranch as branch FROM snChangeRecords WHERE snChangeNumber = '" + change_number + "'"
    change_details = select(sql)[0]
    ci_list = change_details.sast_ids.split(",")
    for ci in ci_list:
        sql = """SELECT snAppRecords.snName as name, snAppRecords.snCICD as cicd, Applications.repo as repo, Applications.cicd_branch_override as branch
                    FROM snAppRecords JOIN Applications ON snAppRecords.snSysID = Applications.snSysID
                    WHERE snAppRecords.snSysID = '{0}'"""
        sql = sql.format(ci)
        app = select(sql)[0]
        # We need to check to see if this application is identified as CICD in SNow
        # If CICD = 1 then it is a CICD app and the branch for CICD is always master regardless of what the change request branch value is
        if app.cicd:
            if app.branch:
                branch = app.branch
            else:
                branch = 'master'
        else:
            branch = change_details.branch
        subject = "Script creation of scan of " + app.name + " for change request " + change_number
        sql = """INSERT INTO QABuilds (Subject, RcvDate, Branch, Repo, AppSysID, Status, ChangeRequestNum)
                    VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"""
        sql = sql.format(subject, datetime.now(pytz.timezone("America/Denver")), branch, app.repo, ci, 'New', change_number)
        insert(sql)
    return

# This function will update the submitted task state to 'Passed Validation' in Service Now
def pass_validation_on_task(task_number, change_number = ""):
    # We need to check the change record associated with this task to verify whether or not a review is required before approving the task
    # If a review is not needed, we will set the status of the task to passed validations
    if change_number == "":
        sql = f"""SELECT snChangeRecords.snChangeNumber, snChangeRecords.snSysID,
        snChangeRecords.ReviewRequired from snChangeRecords JOIN snTaskRecords on
        snTaskRecords.snChangeRequest = snChangeRecords.snChangeNumber WHERE
        snTaskRecords.snTaskNumber ='{task_number}'"""
        change_number = select(sql)[0][0]
    if change_number:
        ch_lnk = Alerts.create_change_ticket_link_by_task(task_number)
        if change_number[0][2] == 1:
            TheLogs.log_info(f'{task_number} cannot be set to passed validation: review required',
                             2,"!",LOG)
            issue = "Incorrect, missing or duplicate snSysID from Applications table for a CI"
            msg = [rf'*Change Ticket:*  {change_number}',rf'*Possible Issue:*  {issue}']
            if ch_lnk is not None:
                msg = [rf'*Change Ticket:*  {ch_lnk}',rf'*Possible Issue:*  {issue}']
            Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 11, SLACK_URL_ALERTS)
        else:
            update = {'state': '3'}
            task_table().update(query = {'number': task_number}, payload = update)
            TheLogs.log_info(f'{task_number} state set to passed validation in Service Now',2,"*",
                             LOG)
            lastFourChange = int(change_number[-4:])
            if lastFourChange < 6500:
                msg = [rf'*Task Updated:*  {task_number}',rf'*Change Ticket:*  {change_number}',
                       '*Status:*  Passed Validation; Ready for approval']
                if ch_lnk is not None:
                    msg = [rf'*Task Updated:*  {task_number}',rf'*Change Ticket:*  {ch_lnk}',
                           '*Status:*  Passed Validation; Ready for approval']
                Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 12, SLACK_URL_ALERTS)
            else:
                TheLogs.log_info(f'Slack message not needed for {change_number[0][1]}, '
                                 'CCSX #s above 6500 do not need manual approval',2,"*",
                                LOG)
    return

# This function will update the specified task and mark it as failed validation
def fail_validation_on_task(task_number, change_number = ""):
    update = {'state': '4'}
    task_table().update(query = {'number': task_number}, payload = update)
    TheLogs.log_info(f'{task_number} state set to failed validation in Service Now',2,"!",LOG)
    ch_lnk = Alerts.create_change_ticket_link(change_number)
    msg = [f'*Task Number:*  {task_number}']
    if ch_lnk is not None:
        msg = [f'*Task Number:*  {task_number}',f'*Change Ticket:*  {ch_lnk}']
    Alerts.manual_alert(rf'{ALERT_SOURCE}', msg, 1, 13, SLACK_URL_ALERTS)

# This function will update the task with the specified comment sent in the function call
def add_comment_to_task(task_number, comment):
    update = {'comments': comment}
    task_table().update(query = {'number': task_number}, payload = update)
    TheLogs.log_info(f'{task_number} updated with comment:{comment}',2,"*",LOG)
    return

# This function provides the ability to add a single change from SNOW to our database if it is needed
def add_change_to_db(change_number):
    change = get_change_by_number(change_number)
    write_change_db(change)
    TheLogs.log_info(f'{change["number"]} added to the database',2,"*",LOG)
    return

# This function will return the task object associated with the specified change number
def get_task_for_change(change_number):
    change = get_change_by_number(change_number)
    my_query = pysnow.QueryBuilder()
    # To find the task, we will query which task has the parent set to the specified change request sys_id
    my_query.field('parent').equals(change['sys_id']).AND().field('short_description').equals('Run Security Scans')
    task = task_table().get(query=my_query).one()
    return task

# This function will extract the Name of the managed_by group from SNow
def app_managed_by(user_id):
    # Query for software change task
    response = user_table().get(query={'sys_id': user_id}, stream=True)
    try:
        return response.one()['name']
    except:
        return ''

# This function will extract the name of the owned_by group from SNow
def app_owned_by(group_id):
    # Query for software change task
    response = group_table().get(query={'sys_id': group_id}, stream=True)
    try:
        return response.one()['name']
    except:
        return ''

if __name__ == '__main__':
    main()
