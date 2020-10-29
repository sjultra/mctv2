import os
import base64
from pathlib import Path
from logger import log
import requests
import json

def get_backend_provider(configuration, terraform_workspace):
    backend_config = configuration["terraform"].get("backend", None)

    backend_type = None
    if backend_config:
        backend_type = backend_config.get("type", None)

    if backend_type == "terraform-cloud":
        return TerraformCloudBackend(configuration, terraform_workspace)
    else:
        return BackendProvider(configuration, terraform_workspace)


def get_dict_value(dictionary, path):
    val = dictionary
    for key in path:
        val = val[key]
    return val

class BackendProvider:
    _parameters = {
        "required": [],
        "optional": []
    }
    _provider_name = None

    def __init__(self, configuration, terraform_workspace):
        self._configuration = configuration
        self._terraform_workspace = terraform_workspace

        if self._provider_name:
            log.info("Configuring backend for: {}".format(self._provider_name))
        else:
            log.warn("Backend type is not supported, backend disabled.")
            return
        if not self._check_required_parameters():
            log.warn("Could not find all required parameters required by backend: {}".format(self._provider_name))
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

    def init_remote_backend(self):
        pass

    def remove_remote_backend(self):
        pass


class TerraformCloudBackend(BackendProvider):
    _parameters = {
        "required": ["secrets.terraform.backend.token",
                     "terraform.backend.config.workspace",
                     "terraform.backend.config.org"],
        "optional": []
    }

    def __init__(self, configuration, terraform_workspace):
        self._provider_name = 'Terraform Cloud'
        
        super().__init__(configuration, terraform_workspace)

    def _configure_environment(self):
        backend = self._configuration["terraform"]["backend"]["config"]
        token = self._configuration["secrets"]["terraform"]["backend"]["token"]

        backend_config = "\n".join([
                          "terraform {{",
                          "    backend \"remote\" {{",
                          "        hostname = \"app.terraform.io\"",
                          "        organization = \"{0}\"",
                          "        workspaces {{",
                          "             name = \"{1}\"",
                          "        }}",
                          "     }}",
                          "}}",
        ]).format(backend["org"], backend["workspace"])
        secrets_config = 'credentials "app.terraform.io" {{ token = \"{0}\" }} '.format(token)

        backend_config_path = os.path.join(self._terraform_workspace, "backend_config.tf")
        log.info("Creating backend config file at: {}".format(backend_config_path))
        with open(backend_config_path, "w") as config_file:
            config_file.write(backend_config)

        #secrets_path = os.path.join(os.environ["HOME"], ".terraform.d")
        #Path(secrets_path).mkdir(parents=True, exist_ok=True)

        secrets_file = os.path.join(self._terraform_workspace, "credentials.tfrc.json")
        os.environ['TF_CLI_CONFIG_FILE'] = secrets_file
        log.info("Creating backend secrets file at: {}".format(secrets_file))
        with open(secrets_file, "w") as terraform_config:
            terraform_config.write(secrets_config)

    def init_remote_backend(self):
        backend = self._configuration["terraform"]["backend"]["config"]
        token = self._configuration["secrets"]["terraform"]["backend"]["token"]

        url = "https://app.terraform.io/api/v2/organizations/{0}/workspaces/{1}".format(backend["org"], backend["workspace"])
        header = {"Authorization": "Bearer {}".format(token), "Content-Type": "application/vnd.api+json"}
        data = {"data": {"type": "workspaces", "attributes": {"operations": False}}}

        log.info("Changing remote workspace \"{}\" execution to local".format(backend["workspace"]))
        response = requests.patch(url, data=json.dumps(data), headers=header)
        if response.status_code != 200:
            log.error("Patch operation failed. Response code: {}".format(response.status_code))
            raise Exception("Patch operation failed. Response code: {}".format(response.status_code))

    def remove_remote_backend(self):
        backend = self._configuration["terraform"]["backend"]["config"]
        token = self._configuration["secrets"]["terraform"]["backend"]["token"]

        url = "https://app.terraform.io/api/v2/organizations/{0}/workspaces/{1}".format(backend["org"], backend["workspace"])
        header = {"Authorization": "Bearer {}".format(token), "Content-Type": "application/vnd.api+json"}

        log.info("Removing remote workspace \"{}\"".format(backend["workspace"]))
        response = requests.delete(url, headers=header)
        if response.status_code != 200:
            log.error("Delete operation failed. Response code: {}".format(response.status_code))
            raise Exception("Delete operation failed. Response code: {}".format(response.status_code))
        