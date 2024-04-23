import jenkins
import os
import sys
import time
parent = os.path.abspath('.')
sys.path.insert(1,parent)
from common.constants import JENKINS_URL, JENKINS_USERNAME
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Union, Dict, Any
from common.logging import TheLogs

ALERT_SOURCE = os.path.basename(__file__)
LOG_BASE_NAME = ALERT_SOURCE.split(".",1)[0]
LOG_FILE = rf"C:\AppSec\logs\jenkins_files-{LOG_BASE_NAME}.log"
EX_LOG_FILE = rf"C:\AppSec\logs\jenkins_files-{LOG_BASE_NAME}_exceptions.log"
LOG = TheLogs.setup_logging(LOG_FILE)
LOG_EXCEPTION = TheLogs.setup_logging(EX_LOG_FILE)

load_dotenv()
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD')

@dataclass
class JenkinsManager:
    jenkins_server: jenkins.Jenkins = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USERNAME,
                                                      password=JENKINS_PASSWORD)

    def build_job(self, job_name: str, parameters: Union[Dict[str, Any], None], token: str) -> None:
        self.jenkins_server.build_job(job_name, parameters=parameters, token=token)
        TheLogs.log_info(f"Build for project {job_name} has been started",2,"*",LOG)
        time.sleep(10)

    def get_build_info(self, job_name: str, build_number: int) -> Dict[str, Any]:
        TheLogs.log_info(f"Checking status of Jenkins job # {build_number} for {job_name}",2,"*",
                         LOG)
        return self.jenkins_server.get_build_info(job_name, build_number)

    def get_job_info(self, job_name: str) -> Dict[str, Any]:
        return self.jenkins_server.get_job_info(job_name)

    def get_build_console_output(self, job_name: str, job_id: int) -> str:
        return self.jenkins_server.get_build_console_output(job_name, job_id)
