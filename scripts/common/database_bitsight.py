# This module will manage the database connections for our bitsightdb databases

import os
import pyodbc
from common.constants import DB_SERVER, DB_USER, BITSIGHT_DB
from dotenv import load_dotenv

load_dotenv()
DB_KEY = str(os.environ.get('DB_KEY'))

class BitSightDB():
    """Stuff for the BitSight database"""
    bsdb_connected = None

    @staticmethod
    def database_connection():
        """Need to maintain an open connection to the access DB for all activities while running
        the maint jobs"""
        if not BitSightDB.bsdb_connected:
            BitSightDB.bsdb_connected = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                                f'Server={DB_SERVER};'
                                                f'Database={BITSIGHT_DB};'
                                                f'UID={DB_USER};'
                                                f'PWD={DB_KEY}')
        return BitSightDB.bsdb_connected

    @staticmethod
    def select(sql):
        """Select from the database"""
        connection = BitSightDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        results = cursor
        return results.fetchall()

    @staticmethod
    def insert(sql):
        """Insert into the database"""
        connection = BitSightDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def update(sql):
        """Update the database"""
        connection = BitSightDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows

    @staticmethod
    def delete_row(sql):
        """Delete from the database"""
        connection = BitSightDB.database_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.commit()
        rows = cursor.rowcount
        return rows
