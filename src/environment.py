import os
import base64
from pathlib import Path
from logger import log
import requests

def config_environment(configuration, terraform_workspace):
    GCPSetup(configuration, terraform_workspace)

def get_dict_value(dictionary, path):
    val = dictionary
    for key in path:
        val = val[key]
    return val

class EnvironmentSetup():
    _parameters = {
        "required": [],
        "optional": []
    }
    _provider_name = None

    def __init__(self, configuration, terraform_workspace):
        self._configuration = configuration
        self._terraform_workspace = terraform_workspace

        if self._provider_name:
            log.info("Configuring environment for: {}".format(self._provider_name))
        else:
            log.warn("Backend type is not supported, backend disabled.")
            return
        if not self._check_required_parameters():
            log.warn("Could not find all required parameters required by {}".format(self._provider_name))
            log.debug("Requred parameters: \n{}".format("\n".join(self._parameters["required"])))
            log.warn("Skipping configuration ...")
            return

        self._configure_environment()

    def _check_required_parameters(self):
        parameters_found = True
        for param_path in self._parameters["required"]:
            value = get_dict_value(self._configuration, param_path.split('.'))
            if value in [None, ""]:
                parameters_found = False
                log.warn("Required parameter is empty: {}".format(param_path))
        return parameters_found

    def _configure_environment(self):
        pass


class GCPSetup(EnvironmentSetup):
    _parameters = {
        "required": ["secrets.env.gcp.service-account-key-url"],
        "optional": ["secrets.env.gcp.project-id"]
    }

    def __init__(self, configuration, terraform_workspace):
        self._provider_name = 'GCP'
        
        super().__init__(configuration, terraform_workspace)

    def _configure_environment(self):
        gcp_params = self._configuration["secrets"]["env"]["gcp"]
        sa_key_url = gcp_params["service-account-key-url"]
        project_id = gcp_params["project-id"]

        service_account = requests.get(sa_key_url, allow_redirects=True)
        with open('/tmp/gcp_credentials.json', 'w') as gcp_secrets:
            gcp_secrets.write(service_account.content.decode('utf-8'))
        os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = '/tmp/gcp_credentials.json'

        if not project_id in ["", None]:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

        #if secrets["gcp"]["service-account-url"]:
        #if secrets["gcp"]["key-path"]:
        #    os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = secrets["gcp"]["key-path"]
        #else:
        #    with open('/tmp/gcp_credentials.json', 'w') as gcp_secrets:
        #        gcp_secrets.write(base64.b64decode(secrets["gcp"]["key-value"]).decode('utf-8'))

