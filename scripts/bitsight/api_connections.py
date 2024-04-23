"""Commonly used BitSight functions"""
import json
import os
import sys
import requests
from common.constants import BITSIGHT_URL
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from common.general import General

parent = os.path.abspath('.')
sys.path.insert(1, parent)

load_dotenv()
SLACK_URL = os.environ.get('SLACK_URL_GENERAL')
BITSIGHT_KEY = os.environ.get('BITSIGHT_KEY')


class BitSightAPI:
    """Provides general functions for interacting with the BitSight API"""

    @staticmethod
    def fetch_companies():
        """Grabs the companies from the BitSightAPI"""
        array = None
        url = f"{BITSIGHT_URL}/companies"
        response = requests.get(url, auth = (BITSIGHT_KEY,''), timeout=60)
        if response.status_code == 200:
            js_data = response.json()
            if 'companies' in js_data:
                js_data = js_data['companies']
                array = []
                for item in js_data:
                    array.append({'guid':item['guid'], 'custom_id':item['custom_id'],
                                  'name':item['name'], 'shortname':item['shortname'],
                                  'network_size_v4':item['network_size_v4'],
                                  'rating':item['rating'], 'rating_date':item['rating_date'],
                                  'date_added':item['date_added'], 'industry':item['industry'],
                                  'sub_industry':item['sub_industry'],
                                  'sub_industry_slug':item['sub_industry_slug'],
                                  'type':item['type'], 'external_id':item['external_id'],
                                  'subscription_type':item['subscription_type'],
                                  'subscription_type_key':item['subscription_type_key'],
                                  'primary_domain':item['primary_domain']})
                array = General.replace_blanks_in_list_of_dicts(array)
        return array

    @staticmethod
    def fetch_current_scores():
        """Gets the current BitSight score information for BitSightScoreChange"""
        array = None
        url = f"{BITSIGHT_URL}/ratings/v1/companies"
        response = requests.get(url, auth = (BITSIGHT_KEY,''), timeout=60)
        if response.status_code == 200:
            array = []
            items = response.json()
            score = None
            score_date = None
            if 'companies' in items:
                for item in items['companies']:
                    score = None
                    score_date = None
                    score = item['rating']
                    score_date = item['rating_date']
                    array.append({'guid':item['guid'],'name':item['name'],
                                    'current_score':score,'current_score_date':score_date})
            array = General.replace_blanks_in_dict(array)
        return array

    @staticmethod
    def fetch_previous_scores():
        """Gets the previous BitSight score information for BitSightScoreChange"""
        start_date = str(date.today() - timedelta(days=30))
        array = None
        url = f"{BITSIGHT_URL}/ratings/v1/companies?rating_date={start_date}"
        response = requests.get(url, auth = (BITSIGHT_KEY,''), timeout=60)
        if response.status_code == 200:
            array = []
            items = response.json()
            if 'companies' in items:
                for item in items['companies']:
                    score = None
                    score_date = None
                    score = item['rating']
                    score_date = item['rating_date']
                    array.append({'guid':item['guid'],'name':item['name'],
                                    'previous_score':score,'previous_score_date':score_date})
            array = General.replace_blanks_in_dict(array)
        return array

    @staticmethod
    def fetch_ratings_details(companies):
        """Grabs the ratings details for companies from the BitSightAPI"""
        array = None
        if companies:
            array = []
            for comp in companies:
                url = f"{BITSIGHT_URL}/ratings/v1/companies/{comp}"
                response = requests.get(url, auth = (BITSIGHT_KEY,''), timeout=60)
                if response.status_code == 200:
                    item = response.json()
                    score = None
                    score_date = None
                    big = None
                    bic = None
                    spg = None
                    spc = None
                    msg = None
                    msc = None
                    ucg = None
                    ucc = None
                    peg = None
                    pec = None
                    spfg = None
                    spfc = None
                    dkimg = None
                    dkimc = None
                    sslcertg = None
                    sslcertc = None
                    sslcong = None
                    sslconc = None
                    opg = None
                    opc = None
                    asg = None
                    asc = None
                    pcg = None
                    pcc = None
                    isg = None
                    isc = None
                    ssg = None
                    ssc = None
                    dsg = None
                    dsc = None
                    mosg = None
                    mosc = None
                    dnsg = None
                    dnsc = None
                    masg = None
                    masc = None
                    fsg = None
                    fsc = None
                    dbg = None
                    dbc = None
                    if 'ratings' in item:
                        score = item['ratings'][0]['rating']
                        score_date = item['ratings'][0]['rating_date']
                    if 'rating_details' in item:
                        if 'botnet_infections' in item['rating_details']:
                            big = item['rating_details']['botnet_infections']['grade']
                            bic = item['rating_details']['botnet_infections']['grade_color']
                        if 'spam_propagation' in item['rating_details']:
                            spg = item['rating_details']['spam_propagation']['grade']
                            spc = item['rating_details']['spam_propagation']['grade_color']
                        if 'malware_servers' in item['rating_details']:
                            msg = item['rating_details']['malware_servers']['grade']
                            msc = item['rating_details']['malware_servers']['grade_color']
                        if 'unsolicited_comm' in item['rating_details']:
                            ucg = item['rating_details']['unsolicited_comm']['grade']
                            ucc = item['rating_details']['unsolicited_comm']['grade_color']
                        if 'potentially_exploited' in item['rating_details']:
                            peg = item['rating_details']['potentially_exploited']['grade']
                            pec = item['rating_details']['potentially_exploited']['grade_color']
                        if 'spf' in item['rating_details']:
                            spfg = item['rating_details']['spf']['grade']
                            spfc = item['rating_details']['spf']['grade_color']
                        if 'dkim' in item['rating_details']:
                            dkimg = item['rating_details']['dkim']['grade']
                            dkimc = item['rating_details']['dkim']['grade_color']
                        if 'ssl_certificates' in item['rating_details']:
                            sslcertg = item['rating_details']['ssl_certificates']['grade']
                            sslcertc = item['rating_details']['ssl_certificates']['grade_color']
                        if 'ssl_configurations' in item['rating_details']:
                            sslcong = item['rating_details']['ssl_configurations']['grade']
                            sslconc = item['rating_details']['ssl_configurations']['grade_color']
                        if 'open_ports' in item['rating_details']:
                            opg = item['rating_details']['open_ports']['grade']
                            opc = item['rating_details']['open_ports']['grade_color']
                        if 'application_security' in item['rating_details']:
                            asg = item['rating_details']['application_security']['grade']
                            asc = item['rating_details']['application_security']['grade_color']
                        if 'patching_cadence' in item['rating_details']:
                            pcg = item['rating_details']['patching_cadence']['grade']
                            pcc = item['rating_details']['patching_cadence']['grade_color']
                        if 'insecure_systems' in item['rating_details']:
                            isg = item['rating_details']['insecure_systems']['grade']
                            isc = item['rating_details']['insecure_systems']['grade_color']
                        if 'server_software' in item['rating_details']:
                            ssg = item['rating_details']['server_software']['grade']
                            ssc = item['rating_details']['server_software']['grade_color']
                        if 'desktop_software' in item['rating_details']:
                            dsg = item['rating_details']['desktop_software']['grade']
                            dsc = item['rating_details']['desktop_software']['grade_color']
                        if 'mobile_software' in item['rating_details']:
                            mosg = item['rating_details']['mobile_software']['grade']
                            mosc = item['rating_details']['mobile_software']['grade_color']
                        if 'dnssec' in item['rating_details']:
                            dnsg = item['rating_details']['dnssec']['grade']
                            dnsc = item['rating_details']['dnssec']['grade_color']
                        if 'mobile_application_security' in item['rating_details']:
                            masg = item['rating_details']['mobile_application_security']['grade']
                            masc = item['rating_details']['mobile_application_security']['grade_color']
                        if 'file_sharing' in item['rating_details']:
                            fsg = item['rating_details']['file_sharing']['grade']
                            fsc = item['rating_details']['file_sharing']['grade_color']
                        if 'data_breaches' in item['rating_details']:
                            dbg = item['rating_details']['data_breaches']['grade']
                            dbc = item['rating_details']['data_breaches']['grade_color']
                        array.append({'guid':item['guid'],'name':item['name'],'bitsight_score':score,
                                    'score_date':score_date,'industry':item['industry'],
                                    'homepage':item['homepage'],
                                    'primary_domain':item['primary_domain'],
                                    'botnet_infections_grade':big,
                                    'botnet_infections_grade_color':bic,
                                    'spam_propagation_grade':spg,
                                    'spam_propagation_grade_color':spc,'malware_servers_grade':msg,
                                    'malware_servers_grade_color':msc,
                                    'unsolicited_comm_grade':ucg,
                                    'unsolicited_comm_grade_color':ucc,
                                    'potentially_exploited_grade':peg,
                                    'potentially_exploited_grade_color':pec,'spf_grade':spfg,
                                    'spf_grade_color':spfc,'dkim_grade':dkimg,
                                    'dkim_grade_color':dkimc,'ssl_certificates_grade':sslcertg,
                                    'ssl_certificates_grade_color':sslcertc,
                                    'ssl_configurations_grade':sslcong,
                                    'ssl_configurations_grade_color':sslconc,
                                    'open_ports_grade':opg,'open_ports_grade_color':opc,
                                    'application_security_grade':asg,
                                    'application_security_grade_color':asc,
                                    'patching_cadence_grade':pcg,
                                    'patching_cadence_grade_color':pcc,
                                    'insecure_systems_grade':isg,
                                    'insecure_systems_grade_color':isc,'server_software_grade':ssg,
                                    'server_software_grade_color':ssc,'desktop_software_grade':dsg,
                                    'desktop_software_grade_color':dsc,
                                    'mobile_software_grade':mosg,
                                    'mobile_software_grade_color':mosc,'dnssec_grade':dnsg,
                                    'dnssec_grade_color':dnsc,
                                    'mobile_application_security_grade':masg,
                                    'mobile_application_security_grade_color':masc,
                                    'file_sharing_grade':fsg,'file_sharing_grade_color':fsc,
                                    'data_breaches_grade':dbg,'data_breaches_grade_color':dbc})
            array = General.replace_blanks_in_list_of_dicts(array)
        return array

    @staticmethod
    def fetch_prog_holdings(companies):
        """Grabs the ratings details for watchlist companies from the BitSightAPI"""
        array = None
        if companies:
            array = []
            for comp in companies:
                url = f"{BITSIGHT_URL}/ratings/v1/companies/{comp}"
                response = requests.get(url, auth = (BITSIGHT_KEY,''), timeout=60)
                if response.status_code == 200:
                    item = response.json()
                    score = None
                    score_date = None
                    big = None
                    spg = None
                    msg = None
                    ucg = None
                    peg = None
                    spfg = None
                    dkimg = None
                    sslcertg = None
                    sslcong = None
                    opg = None
                    asg = None
                    pcg = None
                    isg = None
                    ssg = None
                    dsg = None
                    mosg = None
                    dnsg = None
                    masg = None
                    fsg = None
                    dbg = None
                    if 'ratings' in item:
                        score = item['ratings'][0]['rating']
                        score_date = item['ratings'][0]['rating_date']
                    if 'rating_details' in item:
                        if 'botnet_infections' in item['rating_details']:
                            big = item['rating_details']['botnet_infections']['grade']
                        if 'spam_propagation' in item['rating_details']:
                            spg = item['rating_details']['spam_propagation']['grade']
                        if 'malware_servers' in item['rating_details']:
                            msg = item['rating_details']['malware_servers']['grade']
                        if 'unsolicited_comm' in item['rating_details']:
                            ucg = item['rating_details']['unsolicited_comm']['grade']
                        if 'potentially_exploited' in item['rating_details']:
                            peg = item['rating_details']['potentially_exploited']['grade']
                        if 'spf' in item['rating_details']:
                            spfg = item['rating_details']['spf']['grade']
                        if 'dkim' in item['rating_details']:
                            dkimg = item['rating_details']['dkim']['grade']
                        if 'ssl_certificates' in item['rating_details']:
                            sslcertg = item['rating_details']['ssl_certificates']['grade']
                        if 'ssl_configurations' in item['rating_details']:
                            sslcong = item['rating_details']['ssl_configurations']['grade']
                        if 'open_ports' in item['rating_details']:
                            opg = item['rating_details']['open_ports']['grade']
                        if 'application_security' in item['rating_details']:
                            asg = item['rating_details']['application_security']['grade']
                        if 'patching_cadence' in item['rating_details']:
                            pcg = item['rating_details']['patching_cadence']['grade']
                        if 'insecure_systems' in item['rating_details']:
                            isg = item['rating_details']['insecure_systems']['grade']
                        if 'server_software' in item['rating_details']:
                            ssg = item['rating_details']['server_software']['grade']
                        if 'desktop_software' in item['rating_details']:
                            dsg = item['rating_details']['desktop_software']['grade']
                        if 'mobile_software' in item['rating_details']:
                            mosg = item['rating_details']['mobile_software']['grade']
                        if 'dnssec' in item['rating_details']:
                            dnsg = item['rating_details']['dnssec']['grade']
                        if 'mobile_application_security' in item['rating_details']:
                            masg = item['rating_details']['mobile_application_security']['grade']
                        if 'file_sharing' in item['rating_details']:
                            fsg = item['rating_details']['file_sharing']['grade']
                        if 'data_breaches' in item['rating_details']:
                            dbg = item['rating_details']['data_breaches']['grade']
                        array.append({'guid':item['guid'],'name':item['name'],
                                    'bitsight_score':score,'score_updated':score_date,
                                    'botnet_infections':big,'spam_propagation':spg,
                                    'malware_servers':msg,'unsolicited_communications':ucg,
                                    'potentially_exploited':peg,'spf':spfg,'dkim':dkimg,
                                    'ssl_certificates':sslcertg,'ssl_configurations':sslcong,
                                    'open_ports':opg,'web_application_headers':asg,
                                    'patching_cadence':pcg,'insecure_systems':isg,
                                    'server_software':ssg,'desktop_software':dsg,
                                    'mobile_software':mosg,'dnssec':dnsg,
                                    'mobile_application_security':masg,'file_sharing':fsg,
                                    'security_incidents':dbg})
            array = General.replace_blanks_in_list_of_dicts(array)
        return array

# class BSVulns:
#     '''For retrieving vulnerabilities from BitSight'''

#     @staticmethod
#     def get_findings_by_type(bucket_guid,bucket_name,slug):
#         """Gets findings from BitSight for the specified bucket"""
#         alerts = []
#         url = f"{BITSIGHT_URL}/ratings/v1/companies/{bucket_guid}/findings?risk_vector="
#         url += f"{slug}&limit=5000&format=json&affects_rating=True"
#         response = requests.get(url,auth=(BITSIGHT_KEY,''),timeout=60)
#         if response.status_code == 200:
#             alerts = []
#             array = response.json()
#             if 'results' in array:
#                 array = array['results']
#                 new_array = []
#                 for item in array:
#                     add_item = {}
#                     if 'details' in item:
#                         details = item['details']
#                         example = None
#                         title = f"{item['risk_category']}: {item['risk_vector_label']}"
#                         fall_off = datetime.now() + timedelta(days=item['remaining_decay'])
#                         fall_off = fall_off.strftime('%Y-%m-%d')
#                         dil = {}
#                         if 'diligence_annotations' in details:
#                             dil = details['diligence_annotations']
#                         remediate = ''
#                         if 'record' in dil:
#                             example = f"```{dil['record']}```"
#                         elif ('operating_system_rule' in dil and 'user_agent_rule' in dil and
#                               'sample_user_agent_strings' in dil):
#                             example = "\n*Example User Agent Strings:*\n"
#                             for string in dil['sample_user_agent_strings']:
#                                 example += f"{string}\n"
#                             example += "\n*Operating System Rule:*\n"
#                             example += f"{dil['operating_system_rule']}\n"
#                             example += "\n*User Agent Rule:*\n"
#                             example += f"{dil['user_agent_rule']}\n"
#                         if 'required' in dil:
#                             for rem in dil['required']:
#                                 if rem['is_missing'] is True:
#                                     remediate += f"\nh3. *{rem['name']}:*\n"
#                                     for ann in rem['annotations']:
#                                         remediate += f"\n*{ann['message']}:* {ann['help_text']}\n"
#                                         remediate += f"{ann['remediation_tip']}"
#                         elif 'answer' in dil:
#                             for ans in dil['answer']:
#                                 remediate += "\n "
#                                 if 'algorithm' in ans:
#                                     remediate += f"\n*Algorithm:*\n{ans['algorithm']}\n"
#                                 if 'keylen' in ans:
#                                     remediate += f"\n*Key Length:*\n{ans['keylen']}\n"
#                                 if 'record' in ans:
#                                     remediate += f"\n*Record:*\n{ans['record']}\n"
#                         elif 'remediations' in details:
#                             for rem in details['remediations']:
#                                 remediate += f"\n*{rem['message']}:* {rem['help_text']}\n"
#                                 remediate += f"{rem['remediation_tip']}"
#                         else:
#                             remediate += json.dumps(dil,indent=5)
#                         ips = ''
#                         if 'observed_ips' in details:
#                             for ip in details['observed_ips']:
#                                 ips += f"{ip}\n"
#                         elif 'sample_ips' in dil:
#                             for ip in dil['sample_ips']:
#                                 ips += f"{ip}\n"
#                         if ips == '':
#                             ips = None
#                         if item['severity_category'].lower() == 'minor':
#                             continue
#                         severity = ''
#                         if item['severity_category'].lower() == 'severe':
#                             severity = 'Critical'
#                         elif item['severity_category'].lower() == 'material':
#                             severity = 'High'
#                         elif item['severity_category'].lower() == 'moderate':
#                             severity = 'Medium'
#                         if 'assets' in item:
#                             for asset in item['assets']:
#                                 add_item['Asset'] = asset['asset']
#                                 add_item['AssetIdentifier'] = asset['identifier']
#                                 add_item['FindingTitle'] = title
#                                 add_item['RiskCategory'] = item['risk_category']
#                                 add_item['RiskVector'] = item['risk_vector']
#                                 add_item['Severity'] = severity
#                                 add_item['FirstSeen'] = item['first_seen']
#                                 add_item['LastSeen'] = item['last_seen']
#                                 add_item['NextScan'] = fall_off
#                                 add_item['KeyEvidence'] = item['evidence_key']
#                                 add_item['Findings'] = remediate
#                                 add_item['ExampleRecord'] = example
#                                 add_item['ObservedIPs'] = ips
#                                 add_item['ProgEntity'] = bucket_name
#                     if add_item != {}:
#                         alerts.append(add_item)
#         return alerts
