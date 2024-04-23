# This module will manage the database connections for our JiraInfo database tables

import os
import pyodbc
from common.constants import DB_SERVER, DB_USER
from dotenv import load_dotenv

load_dotenv()
DB_KEY = str(os.environ.get('DB_KEY'))
JIRA_DB = str(os.environ.get('JIRA_DB'))

class JiraDB():
    """Stuff for the JiraInfo database"""
    jirainfo_connection = None

    @staticmethod
    def database_connection():
        """Establishes the connection"""
        if not JiraDB.jirainfo_connection:
            driver = 'SQL Server Native Client 11.0'
            JiraDB.jirainfo_connection = pyodbc.connect(f'Driver={{{driver}}};'
                                                f'Server={DB_SERVER};'
                                                f'Database={JIRA_DB};'
                                                f'UID={DB_USER};'
                                                f'PWD={DB_KEY}')
        return JiraDB.jirainfo_connection

    @staticmethod
    def select(sql):
        """Returns selected data"""
        connection = JiraDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        results = cursor
        return results.fetchall()

    @staticmethod
    def insert(sql):
        """Inserts data"""
        connection = JiraDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def update(sql):
        """Updates data"""
        connection = JiraDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def delete_row(sql):
        """Deletes data"""
        connection = JiraDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def insert_multiple_into_table(table_name,array):
        """Inserts supplied data into the specified table"""
        i_cnt = 0
        if isinstance(array,dict):
            new_array = []
            if array != {}:
                new_array.append(array)
            array = new_array
        if array != []:
            total = len(array)
            processing = 0
            for item in array:
                processing += 1
                print(f"Processing {processing} of {total}",end="\r")
                sql = f"""
                BEGIN
                IF NOT EXISTS (SELECT * FROM {table_name} WHERE"""
                for key, value in item.items():
                    if value != 'NULL' and value != 'None' and value is not None and value != '':
                        if isinstance(value,str):
                            value = value.replace("'","")
                        sql += f" {key} = '{value}' AND"
                sql = f"{sql[:-4]}"
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
                i_cnt += JiraDB.insert(sql)
            print(f"{total} processed"," "*30)
        return i_cnt

    @staticmethod
    def update_multiple_in_table(table_name,array):
        """Updates supplied data in the specified table"""
        u_cnt = 0
        if isinstance(array,dict):
            new_array = []
            if array != {}:
                new_array.append(array)
            array = new_array
        if array != []:
            for item in array:
                sql = f"""UPDATE {table_name} SET """
                for key, value in item['SET'].items():
                    if value != 'NULL' and value != 'None' and value is not None and value != '':
                        if isinstance(value,str):
                            value = value.replace("'","")
                        sql += f"{key} = '{value}',"
                    else:
                        sql += f"{key} = NULL,"
                sql = f"{sql[:-1]}"
                if 'WHERE_EQUAL' in item or 'WHERE_NOT' in item:
                    sql += " WHERE "
                    if 'WHERE_EQUAL' in item:
                        if item['WHERE_EQUAL'] is not None:
                            for key, value in item['WHERE_EQUAL'].items():
                                if value != 'NULL' and value != 'None' and value is not None:
                                    if isinstance(value,str):
                                        value = value.replace("'","")
                                    sql += f"{key} = '{value}' AND "
                                else:
                                    sql += f"{key} IS NULL AND "
                    if 'WHERE_NOT' in item:
                        if item['WHERE_NOT'] is not None:
                            for key, value in item['WHERE_NOT'].items():
                                if value != 'NULL' and value != 'None' and value is not None:
                                    if isinstance(value,str):
                                        value = value.replace("'","")
                                    sql += f"{key} != '{value}' AND "
                                else:
                                    sql += f"{key} IS NOT NULL AND "
                    sql = f"{sql[:-5]}"
                if 'WHERE_NOT_IN' in item:
                    if item['WHERE_NOT_IN'] is not None:
                        for key, value in item['WHERE_NOT_IN'].items():
                            if (value != 'NULL' and value != 'None' and value is not None and
                                value != ''):
                                not_in = str(value).replace("[","").replace("]","")
                                sql += f" AND {key} NOT IN ({not_in})"
                if 'WHERE_IN' in item:
                    if item['WHERE_IN'] is not None:
                        for key, value in item['WHERE_IN'].items():
                            if (value != 'NULL' and value != 'None' and value is not None and
                                value != ''):
                                is_in = str(value).replace("[","").replace("]","")
                                sql += f" AND {key} IN ({is_in})"
                if 'CUSTOM_AND' in item:
                    if item['CUSTOM_AND'] is not None:
                        sql += " AND ("
                        for statement in item['CUSTOM_AND']:
                            sql += f"({statement}) AND "
                        sql = f"{sql[:-5]}"
                        sql += ")"
                if 'CUSTOM_OR' in item:
                    if item['CUSTOM_OR'] is not None:
                        sql += " AND ("
                        for statement in item['CUSTOM_OR']:
                            sql += f"({statement}) OR "
                        sql = f"{sql[:-4]}"
                        sql += ")"
                sql = sql.replace("WHERE AND ","WHERE ").replace("WHERE OR ","WHERE ")
                u_cnt += JiraDB.update(sql)
        return u_cnt
