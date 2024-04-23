# This module will manage the database connections for our AppSec database
import pyodbc
import os
from common.constants import CXDB_SERVER, CXDB_USER, DB_SERVER, DB_USER
from dotenv import load_dotenv

load_dotenv()
CXDB_KEY = str(os.environ.get('CXDB_KEY'))
DB_KEY = str(os.environ.get('DB_KEY'))
appsec_connection = None
checkmarx_connection = None

# Need to maintain an open connection to the access DB for all activities while running the maint jobs
def database_connection():
    """Creates connection to AppSec database"""
    global appsec_connection
    if not appsec_connection:
        driver = 'SQL Server Native Client 11.0'
        appsec_connection = pyodbc.connect(f'Driver={{{driver}}};'
                                            f'Server={DB_SERVER};'
                                            'Database=AppSec;'
                                            f'UID={DB_USER};'
                                            f'PWD={DB_KEY}')
    return appsec_connection

# Need to maintain an open connection to the Checkmarx DB while looping through all SAST findings
def cx_connection():
    """Creates connection to CxDB database"""
    global checkmarx_connection
    if not checkmarx_connection:
        driver = 'SQL Server Native Client 11.0'
        checkmarx_connection = pyodbc.connect(f'Driver={{{driver}}};'
                                            f'Server={CXDB_SERVER};'
                                            'Database=CxDB;'
                                            f'UID={CXDB_USER};'
                                            f'PWD={CXDB_KEY}')
    return checkmarx_connection

def cx_select(sql):
    """Select from CxDB database and return results"""
    connection = cx_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor
    return results.fetchall()

def select(sql):
    """Select from AppSec database and return results"""
    connection = database_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def insert(sql):
    """Insert into AppSec database and return count of rows inserted"""
    connection = database_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.commit()
    rows = cursor.rowcount
    return rows

def update(sql):
    """Update AppSec database and return count of rows updated"""
    connection = database_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.commit()
    rows = cursor.rowcount
    return rows

def delete_row(sql):
    """Delete from AppSec database and return count of rows deleted"""
    connection = database_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.commit()
    rows = cursor.rowcount
    return rows

def insert_multiple_into_table(table_name,array,level=1,verify_on=[],custom_filter=None,show_progress=True):
    """Inserts supplied data into the specified table.
    To add filters (i.e. don't insert if Repo exists and the cxBaselineProject is either NULL or
    equal to the update):
    Set verify_on to an array of the columns to use for a comparison stating 'these values must
    be equal' (i.e. verify_on=['Repo','cxBaselineProject'])
    Set custom_filter to any sql snippet that would be included as directly following the
    verify_on data (i.e. custom_filter='OR (Repo = repo_name AND cxBaselineProject IS NULL)')
    Using both examples together would result in verification of whether the item already exists:
    (Repo = 'repo_name' AND cxBaselineProject = '12345') OR (Repo = repo_name AND cxBaselineProject IS NULL)
    You can use either verify_on or custom_filter by itself, but be aware that custom_filter does
    not dynamically pull values from the array items for comparison."""
    i_cnt = 0
    res = 0
    spaces = "     "*level
    if isinstance(array,dict):
        new_array = []
        if array != {}:
            new_array.append(array)
        array = new_array
    if array != []:
        total = len(array)
        processing = 0
        for item in array:
            sql = ""
            processing += 1
            if show_progress is True:
                print(f"{spaces}*  Processing {processing} of {total}",end="\r")
            sql += f"""
            BEGIN
            IF NOT EXISTS (SELECT * FROM {table_name} WHERE """
            if verify_on != []:
                sql += "("
                for key in verify_on:
                    if item[key] is None:
                        sql += f" {key} IS NULL"
                    else:
                        sql += f" {key} = '{item[key]}' AND"
                sql = f"{sql[:-4]})"
            if custom_filter != [] and custom_filter is not None:
                sql += f" {custom_filter}"
            elif verify_on == [] or verify_on is None:
                sql += "("
                for key, value in item.items():
                    if value != 'NULL' and value != 'None' and value is not None and value != '':
                        if isinstance(value,str):
                            value = value.replace("'","")
                        sql += f" {key} = '{value}' AND"
                sql = f"{sql[:-4]})"
            sql += ") "
            sql += f""" BEGIN
            INSERT INTO {table_name} ("""
            sql_values = """) VALUES ("""
            for key, value in item.items():
                if value != 'NULL' and value != 'None' and value is not None and value != '':
                    if isinstance(value,str):
                        value = value.replace("'","")
                    sql += f"{key},"
                    sql_values += f"'{value}',"
            sql = f"{sql[:-1]}{sql_values[:-1]}) "
            sql += """ END
            END """
            try:
                res = insert(sql)
            except:
                print(sql)
            if res != 0:
                i_cnt += res
    return i_cnt

def update_multiple_in_table(table_name,array,level=1,show_progress=True):
    """Updates supplied data in the specified table"""
    u_cnt = 0
    p_cnt = 0
    spaces = "     "*level
    if isinstance(array,dict):
        new_array = []
        if array != {}:
            new_array.append(array)
        array = new_array
    if array != []:
        total = len(array)
        for item in array:
            sql = ""
            p_cnt += 1
            if show_progress is True:
                print(f"{spaces}*  Processing {p_cnt} of {total}",end="\r")
            sql += f""" UPDATE {table_name} SET """
            for key, value in item['SET'].items():
                if value != 'NULL' and value != 'None' and value is not None and value != '':
                    if isinstance(value,str):
                        value = value.replace("'","")
                    sql += f"{key} = '{value}',"
                else:
                    sql += f"{key} = NULL,"
            sql = f"{sql[:-1]}"
            if ('WHERE_EQUAL' in item or 'WHERE_NOT' in item or 'WHERE_LIKE' in item or
                'WHERE_NOT_IN' in item or 'WHERE_IN' in item or 'CUSTOM_AND' in item or
                'CUSTOM_OR' in item):
                sql += " WHERE "
                if 'WHERE_EQUAL' in item:
                    if item['WHERE_EQUAL'] is not None:
                        sql += " ("
                        for key, value in item['WHERE_EQUAL'].items():
                            if value != 'NULL' and value != 'None' and value is not None:
                                if isinstance(value,str):
                                    value = value.replace("'","")
                                sql += f"{key} = '{value}' AND "
                            else:
                                sql += f"{key} IS NULL AND "
                        sql = f"{sql[:-5]}"
                        sql += ") "
                if 'WHERE_NOT' in item:
                    if item['WHERE_NOT'] is not None:
                        sql += " AND ("
                        for key, value in item['WHERE_NOT'].items():
                            if value != 'NULL' and value != 'None' and value is not None:
                                if isinstance(value,str):
                                    value = value.replace("'","")
                                sql += f"{key} != '{value}' AND "
                            else:
                                sql += f"{key} IS NOT NULL AND "
                        sql = f"{sql[:-5]}"
                        sql += ")"
                if 'WHERE_LIKE' in item:
                    if item['WHERE_LIKE'] is not None:
                        sql += " AND ("
                        for key, value in item['WHERE_LIKE'].items():
                            if value != 'NULL' and value != 'None' and value is not None:
                                if isinstance(value,str):
                                    value = value.replace("'","")
                                sql += f"{key} LIKE '{value}' AND "
                        sql = f"{sql[:-5]}"
                        sql += " )"
                if 'WHERE_NOT_LIKE' in item:
                    if item['WHERE_NOT_LIKE'] is not None:
                        sql += " AND ("
                        for key, value in item['WHERE_NOT_LIKE'].items():
                            if value != 'NULL' and value != 'None' and value is not None:
                                if isinstance(value,str):
                                    value = value.replace("'","")
                                sql += f"{key} NOT LIKE '{value}' AND "
                        sql = f"{sql[:-5]}"
                        sql += " )"
                if 'WHERE_NOT_IN' in item:
                    if item['WHERE_NOT_IN'] is not None:
                        sql += " AND ("
                        for key, value in item['WHERE_NOT_IN'].items():
                            if (value != 'NULL' and value != 'None' and value is not None and
                                value != ''):
                                not_in = str(value).replace("[","").replace("]","")
                                sql += f"{key} NOT IN ({not_in}) AND "
                        sql = f"{sql[:-5]}"
                        sql += " )"
                if 'WHERE_IN' in item:
                    if item['WHERE_IN'] is not None:
                        sql += " AND ("
                        for key, value in item['WHERE_IN'].items():
                            if (value != 'NULL' and value != 'None' and value is not None and
                                value != ''):
                                is_in = str(value).replace("[","").replace("]","")
                                sql += f"{key} IN ({is_in}) AND "
                        sql = f"{sql[:-5]}"
                        sql += " )"
                if 'CUSTOM_AND' in item:
                    if item['CUSTOM_AND'] is not None:
                        sql += " AND ("
                        for statement in item['CUSTOM_AND']:
                            sql += f"({statement}) AND "
                        sql = f"{sql[:-5]}"
                        sql += ") "
                if 'CUSTOM_OR' in item:
                    if item['CUSTOM_OR'] is not None:
                        sql += " AND ("
                        for statement in item['CUSTOM_OR']:
                            sql += f"({statement}) OR "
                        sql = f"{sql[:-4]}"
                        sql += ") "
                if 'WHERE_OR_VALUES_AND' in item:
                    if item['WHERE_OR_VALUES_AND'] is not None:
                        sql += " OR ("
                        for key, value in item['WHERE_OR_VALUES_AND'].items():
                            if value != 'NULL' and value != 'None' and value is not None:
                                if isinstance(value,str):
                                    value = value.replace("'","")
                                sql += f"{key} = '{value}' AND "
                            else:
                                sql += f"{key} IS NULL AND "
                        sql = f"{sql[:-5]}"
                        sql += ") "
            sql = sql.replace("  "," ").replace("WHERE AND ","WHERE ").replace("WHERE OR ","WHERE ")
            if sql.endswith("AND") or sql.endswith("AND "):
                sql = sql[:-4]
            if sql.endswith("AND)") or sql.endswith("AND )"):
                sql = sql[:-5]
            if sql.endswith("OR)") or sql.endswith("OR )"):
                sql = sql[:-4]
            sql = sql.replace('WHERE AND','WHERE ').replace("( ","(").replace(" )",")").replace("  "," ")
            res = update(sql)
            if res != 0:
                u_cnt += res
    return u_cnt
