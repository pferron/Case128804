"""This file contains functions for BitSight database maintenance"""

import os
import sys
from dotenv import load_dotenv
from common.logging import TheLogs
from common.database_bitsight import BitSightDB

parent = os.path.abspath('.')
sys.path.insert(1, parent)

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\bitsight-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\bitsight-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
BITSIGHT_KEY = os.environ.get('BITSIGHT_KEY')
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')


class ScrVar():
    """Script-wide stuff"""
    fe_cnt = 0
    fe_array = []
    ex_cnt = 0
    ex_array = []

class DBQueries():
    """Has useful functions"""

    @staticmethod
    def ratings_details_available(main_log=LOG):
        """Gets the guid for companies we have access to ratings details for"""
        array = []
        sql = """SELECT DISTINCT guid, name FROM BitSightInventory WHERE subscription_type_key
        IN ('continuous_monitoring','my_subsidiary') ORDER BY name"""
        try:
            items = BitSightDB.select(sql)
        except Exception as details:
            e_code = "BD-RDA-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
        if items:
            for item in items:
                array.append(item[0])
        return array

    @staticmethod
    def get_score_change_list(main_log=LOG):
        """Gets the necessary info for updating BitSightScoreChange"""
        array = []
        sql = """SELECT guid, name, rating, rating_date FROM BitSightInventory ORDER BY name"""
        try:
            items = BitSightDB.select(sql)
        except Exception as details:
            e_code = "BD-GSCL-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
        if items:
            array = []
            for item in items:
                array.append({'guid': item[0],'name': item[1],'current_score': item[2],
                              'current_score_date': item[3]})
        return array

    @staticmethod
    def get_watchlist(main_log=LOG):
        """Gets the guid for companies on the watchlist (ProgOnlyDetailsWatchlist)"""
        array = []
        sql = """SELECT DISTINCT guid, name FROM ProgOnlyDetailsWatchlist ORDER BY name"""
        try:
            items = BitSightDB.select(sql)
        except Exception as details:
            e_code = "BD-GW-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
        if items:
            array = []
            for item in items:
                array.append(item[0])
        return array

    @staticmethod
    def clear_table(table_name,main_log=LOG):
        """Deletes all inventory from the specified table"""
        success = False
        sql = f"""DELETE FROM {table_name}"""
        try:
            BitSightDB.delete_row(sql)
            success = True
        except Exception as details:
            e_code = "BD-CT-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return success
        return success

    @staticmethod
    def insert_into_table(table_name,array,main_log=LOG):
        """Inserts supplied data into the specified table"""
        i_cnt = 0
        if isinstance(array,dict):
            new_array = []
            new_array.append(array)
            array = new_array
        for item in array:
            sql = f"""INSERT INTO {table_name} ("""
            sql_values = """) VALUES ("""
            for key, value in item.items():
                sql += f"{key},"
                sql_values += f"'{value}',"
            sql = f"{sql[:-1]}{sql_values[:-1]})"
            try:
                i_cnt += BitSightDB.insert(sql)
            except Exception as details:
                e_code = "BD-IIT-001"
                TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
                ScrVar.fe_cnt += 1
                ScrVar.fe_array.append(e_code)
                TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
                TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
                continue
        return i_cnt

    @staticmethod
    def update_score_change(main_log=LOG):
        """Sets the score changes in BitSightScoreChange"""
        u_cnt = 0
        sql = """UPDATE BitSightScoreChange SET score_change = current_score - previous_score
        WHERE current_score_date != previous_score_date"""
        try:
            u_cnt += BitSightDB.update(sql)
        except Exception as details:
            e_code = "BD-USC-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return u_cnt
        return u_cnt

    @staticmethod
    def no_score_change(main_log=LOG):
        """Removes previous score data in BitSightScoreChange when the previous and current score
        dates are the same"""
        u_cnt = 0
        sql = """UPDATE BitSightScoreChange SET previous_score = NULL, previous_score_date = NULL
        WHERE current_score_date = previous_score_date"""
        try:
            u_cnt += BitSightDB.update(sql)
        except Exception as details:
            e_code = "BD-NSC-001"
            TheLogs.sql_exception(sql,e_code,details,LOG_EXCEPTION,main_log,EX_LOG_FILE)
            ScrVar.fe_cnt += 1
            ScrVar.fe_array.append(e_code)
            TheLogs.process_exceptions(ScrVar.fe_array,rf'{ALERT_SOURCE}',SLACK_URL,1,main_log)
            TheLogs.process_exceptions(ScrVar.ex_array,rf'{ALERT_SOURCE}',SLACK_URL,2,main_log)
            return u_cnt
        return u_cnt

    # @staticmethod
    # def get_watchlist_guid_and_names(main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Gets the guid for companies on the watchlist (ProgOnlyDetailsWatchlist)"""
    #     array = []
    #     sql = """SELECT DISTINCT guid, name FROM ProgOnlyDetailsWatchlist ORDER BY name"""
    #     try:
    #         items = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-GWGAN-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.fe_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
    #     if items:
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': items}

    # @staticmethod
    # def get_slugs(entity,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Gets the guid for companies on the watchlist (ProgOnlyDetailsWatchlist)"""
    #     array = []
    #     sql = f"""SELECT DISTINCT RiskVector, slug FROM ProgFindingsToJira WHERE ProgEntity =
    #     '{entity}' ORDER BY RiskVector"""
    #     try:
    #         items = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-GS-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.fe_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
    #     if items:
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': items}

    # @staticmethod
    # def findings_to_ticket(entity,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Gets the guid for companies on the watchlist (ProgOnlyDetailsWatchlist)"""
    #     array = []
    #     sql = f"""SELECT DISTINCT FindingTitle, Severity, RiskVector FROM ProgBitSightFindings
    #     WHERE ProgEntity = '{entity}' AND JiraTicket IS NULL ORDER BY Severity, FindingTitle,
    #     RiskVector"""
    #     try:
    #         items = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-FTT-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.fe_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
    #     if items != []:
    #         for item in items:
    #             array.append({'Title':item[0],'Severity':item[1],'Label':item[2]})
    #     return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}

    # @staticmethod
    # def get_lines_for_finding(entity,finding_title,severity,main_log=LOG,ex_log=LOG_EXCEPTION,
    #                           ex_file=EX_LOG_FILE):
    #     '''Retrieves similar findings for ticketing'''
    #     array = []
    #     sql = f"""SELECT Asset, AssetIdentifier, FirstSeen, LastSeen, NextScan, KeyEvidence,
    #     ExampleRecord, ObservedIPs, Findings FROM ProgBitSightFindings WHERE ProgEntity =
    #     '{entity}' AND FindingTitle = '{finding_title}' AND Severity = '{severity}' AND JiraTicket
    #     IS NULL ORDER BY NextScan"""
    #     try:
    #         items = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-GLFF-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.fe_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
    #     if items != []:
    #         for item in items:
    #             array.append({'Asset':item[0],'AssetIdentifier':item[1],'FirstSeen':str(item[2]),
    #                           'LastSeen':str(item[3]),'NextScan':str(item[4]),'Evidence':item[5],
    #                           'Example':item[6],'IPs':item[7],'FindingDetails':item[0]})
    #     return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}

    # @staticmethod
    # def finding_exists(vuln,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Gets the guid for companies on the watchlist (ProgOnlyDetailsWatchlist)"""
    #     exists = False
    #     sql = f"""SELECT JiraTicket FROM ProgBitSightFindings WHERE FindingTitle =
    #     '{vuln['FindingTitle']}' AND Asset = '{vuln['Asset']}' AND RiskCategory =
    #     '{vuln['RiskCategory']}' AND RiskVector = '{vuln['RiskVector']}' AND Severity =
    #     '{vuln['Severity']}'"""
    #     try:
    #         items = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-FE-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.ex_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': exists}
    #     if items != []:
    #         exists = True
    #     return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': exists}

    # @staticmethod
    # def get_jira_for_ticketing(slug,bucket,main_log=LOG,ex_log=LOG_EXCEPTION,ex_file=EX_LOG_FILE):
    #     """Gets the Jira info to use for ticketing"""
    #     array = {}
    #     sql = f"""SELECT JiraProject, JiraEpic FROM ProgFindingsToJira WHERE ProgEntity =
    #     '{bucket}' AND slug = '{slug}' AND JiraProject IS NOT NULL AND JiraEpic IS NOT NULL"""
    #     try:
    #         response = BitSightDB.select(sql)
    #     except Exception as details:
    #         e_code = "BD-GJFT-001"
    #         TheLogs.sql_exception(sql,e_code,details,ex_log,main_log,ex_file)
    #         ScrVar.fe_cnt += 1
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
    #     if response != []:
    #         array['JiraProject'] = response [0][0]
    #         array['JiraEpic'] = response[0][1]
    #         return {'FatalCount': ScrVar.fe_cnt,'ExceptionCount': ScrVar.ex_cnt,'Results': array}
