import os
import sys
import inspect
import requests
import urllib.parse
import urllib3
from dotenv import load_dotenv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONJUR_DNS = 'prdappcjr.proginternal.net:443'
CONJUR_HOST = 'host/Prod/MP_IS-APPSEC_A'.encode('ascii')
CONJUR_HOST_ENCODED = urllib.parse.quote_plus(CONJUR_HOST)
POLICY = 'prod'
CALLED_FROM = os.environ.get("CALLED_FROM")

class ScrVar():
    """Script-wide stuff"""
    src = os.path.basename(__file__)

# This class works as a wrapper for secrets within the appsec repo. It facilitates the retrieval
# of authorization tokens from Conjur and setting the Conjur secrets in your environment.
# To use this class, just call instantiate it; the __init__ will take care of everything.
class Conjur:
    def __init__(self, set_env=True, environment='prod'):
        load_dotenv()
        self.CONJUR_API_KEY = os.environ.get("CONJUR_API_KEY")
        self.SLACK_URL_GENERAL = os.environ.get("SLACK_URL_GENERAL")
        self.auth_token = self.get_auth_token()
        self.conjur_secrets = ['BITBUCKET_HEADER', 'BITBUCKET_KEY', 'BITSIGHT_KEY', 'CXDB_KEY',
                               'CX_CLIENT_KEY', 'CX_SERVER_PASS', 'CX_USER_KEY', 'DB_KEY',
                               'JENKINS_PASSWORD', 'JIRA_KEY', 'JIRA_FOUR_KEY', 'KB4_KEY', 'SLACK_ROOT',
                               'SLACK_URL_ALERTS', 'SLACK_URL_CX', 'SLACK_URL_GENERAL',
                               'SLACK_URL_MEND', 'SNOW_KEY', 'WS_KEY_API', 'WS_KEY_USER',
                               'WS_TOKEN']
        if environment == 'prod':
            self.safe_name = 'MP_IS-APPSEC'
        if set_env:
            self.set_conjur_secrets()

    def get_auth_token(self):
        url = f"https://{CONJUR_DNS}/authn/{POLICY}/{CONJUR_HOST_ENCODED}/authenticate"
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'base64'}
        try:
            response = requests.post(url=url,headers=headers,data=self.CONJUR_API_KEY,verify=False)
            response.raise_for_status()
            return response.text
        except Exception as details:
            print(f'{details=}')
            message = f'*Running Function:*\n{inspect.stack()[0][3]}\n\n*Details:*\n{details}'
            source = ScrVar.src
            if CALLED_FROM != 'Unset':
                source = CALLED_FROM
            from common.alerts import Alerts
            Alerts.manual_alert(source,[],1,29,self.SLACK_URL_GENERAL,message,True)
            sys.exit()

    def set_conjur_secrets(self):
        for secret in self.conjur_secrets:
            if not os.getenv(secret):
                secret_id = f"Conjur_Sync/{self.safe_name}/GenericWebApp-stormwind.local-{secret}" \
                            f"/password"
                url = f"https://{CONJUR_DNS}/secrets/prod/variable/vault/{secret_id}"
                data = {}
                headers = {
                    'Authorization': f'Token token="{self.auth_token}"',
                    'Content-Type': 'text/plain'}
                try:
                    response = requests.get(url=url,headers=headers,data=data,verify=False)
                    response.raise_for_status()
                    os.environ[secret] = response.text
                except Exception as details:
                    print(f'{details=}')
                    message = f'*Running Function:*\n{inspect.stack()[0][3]}\n\n*Details:*\n{details}'
                    source = ScrVar.src
                    if CALLED_FROM != 'Unset':
                        source = CALLED_FROM
                    from common.alerts import Alerts
                    Alerts.manual_alert(source,[],1,29,self.SLACK_URL_GENERAL,message,True)
                    sys.exit()

    def retrieve_secret(self, secret, address, platform_id, safe_name):
        secret_id = f"Conjur_Sync/{safe_name}/{platform_id}-{address}-{secret}" \
                    f"/password"
        url = f"https://{CONJUR_DNS}/secrets/prod/variable/vault/{secret_id}"
        data = {}
        headers = {
            'Authorization': f'Token token="{self.auth_token}"',
            'Content-Type': 'text/plain'}
        try:
            response = requests.get(url=url,headers=headers,data=data,verify=False)
            response.raise_for_status()
            os.environ[secret] = response.text
        except Exception as details:
            print(f'{details=}')
            message = f'*Running Function:*\n{inspect.stack()[0][3]}\n\n*Details:*\n{details}'
            source = ScrVar.src
            if CALLED_FROM != 'Unset':
                source = CALLED_FROM
            from common.alerts import Alerts
            Alerts.manual_alert(source,[],1,29,self.SLACK_URL_GENERAL,message,True)
            sys.exit()

conjur = Conjur()
