# This module will manage the database connections all databases

import os
import pyodbc
from common.constants import DB_SERVER, DB_USER
from dotenv import load_dotenv

load_dotenv()
DB_KEY = str(os.environ.get('DB_KEY'))

class DBQueries():
    """Stuff for connecting to the database"""
    db_connection = None
    connected_to = ''

    @staticmethod
    def database_connection(database='AppSec'):
        """Need to maintain an open connection to the access DB for all activities while running
        the maint jobs"""
        if database != DBQueries.connected_to:
            DBQueries.db_connection = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                            f'Server={DB_SERVER};'
                                            f'Database={database};'
                                            f'UID={DB_USER};'
                                            f'PWD={DB_KEY}')
            DBQueries.connected_to = database
        return DBQueries.db_connection

    @staticmethod
    def select(sql,database='AppSec'):
        """Select from the database"""
        connection = DBQueries.database_connection(database)
        cursor = connection.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    @staticmethod
    def insert(sql,database='AppSec'):
        """Insert into the database"""
        connection = DBQueries.database_connection(database)
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def update(sql,database='AppSec'):
        """Update the database"""
        connection = DBQueries.database_connection(database)
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def delete_row(sql,database='AppSec'):
        """Delete from the database"""
        connection = DBQueries.database_connection(database)
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def clear_table(table_name,database='AppSec'):
        """Clears all lines in a table"""
        sql = f"""DELETE FROM {table_name}"""
        DBQueries.delete_row(sql,database)

    @staticmethod
    def insert_multiple(table_name,array,database='AppSec',level=1,verify_on=[],custom_filter=None,
                        show_progress=True):
        """Inserts supplied data into the specified table"""
        i_cnt = 0
        count = 0
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
                            sql += f" {key} IS NULL AND"
                        else:
                            key_value = item[key]
                            if isinstance(key_value,str):
                                key_value = key_value.replace("'","")
                            sql += f" {key} = '{key_value}' AND"
                    if sql.endswith(" AND") or sql.endswith("AND "):
                        sql = f"{sql[:-4]})"
                    if sql.endswith(" AND)") or sql.endswith("AND )"):
                        sql = f"{sql[:-5]})"
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
                count = DBQueries.insert(sql,database)
                if count > 0:
                    i_cnt += count
            if show_progress is True:
                print(f"{total} processed"," "*30,end="\r")
        return i_cnt

    @staticmethod
    def update_multiple(table_name,array,database='AppSec',level=1,show_progress=True,
                        update_to_null=True):
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
                    elif update_to_null is True:
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
                if sql.endswith(" AND") or sql.endswith("AND "):
                    sql = sql[:-4]
                if sql.endswith(" AND)") or sql.endswith("AND )"):
                    sql = sql[:-5]
                if sql.endswith(" OR)") or sql.endswith("OR )"):
                    sql = sql[:-4]
                sql = sql.replace('WHERE AND','WHERE ').replace("( ","(").replace(" )",")").replace("  "," ")
                u_cnt += DBQueries.update(sql,database)
            if show_progress is True:
                print(f"{total} processed"," "*30,end="\r")
        return u_cnt
