from python_terraform import Terraform
from mct_config import Configuration
from script_exec import execute_script
import argparse
import os
import base64
from pathlib import Path
import requests
import json

def get_parameters():
    parser = argparse.ArgumentParser(description="MCTv2 Alpha")

    parser.add_argument('--config_path')
    parser.add_argument('--secrets_path')
    parser.add_argument('--terraform_workspace')
    parser.add_argument('--steps')
    parser.add_argument('--id')
    parser.add_argument('--custom_fields')

    return parser.parse_args()


def check_parameters(parameters):
    if not parameters.id:
        raise Exception("id parameter is empty")

    if not parameters.config_path:
        raise Exception("config_path parameter is empty")
    parameters.config_path = os.path.abspath(parameters.config_path)

    if not parameters.secrets_path:
        raise Exception("secrets_path parameter is empty")
    parameters.secrets_path = os.path.abspath(parameters.secrets_path)

    if not parameters.terraform_workspace:
        raise Exception("terraform_workspace parameter is empty")
    parameters.terraform_workspace = os.path.abspath(parameters.terraform_workspace)

    if not os.path.isfile(parameters.config_path):
        raise Exception("File {} does not exist".format(parameters.config_path))
    if not os.path.isfile(parameters.secrets_path):
        raise Exception("File {} does not exist".format(parameters.secrets_path))
    if not os.path.isdir(parameters.terraform_workspace):
        raise Exception("File {} does not exist".format(parameters.terraform_workspace))

    return parameters


def config_azure_env(secrets):
    os.environ["ARM_CLIENT_ID"] = secrets["azure"]["client-id"]
    os.environ["ARM_CLIENT_SECRET"] = secrets["azure"]["client-secret"]
    os.environ["ARM_SUBSCRIPTION_ID"] = secrets["azure"]["subscription-id"]
    os.environ["ARM_TENANT_ID"] = secrets["azure"]["tenant-id"]


def config_devops_env(secrets):
    os.environ["AZDO_PERSONAL_ACCESS_TOKEN"] = secrets["azuredevops"]["token"]
    os.environ["AZDO_ORG_SERVICE_URL"] = secrets["azuredevops"]["service-url"]


def config_gcp_env(secrets):
    if secrets["gcp"]["key-path"]:
        os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = secrets["gcp"]["key-path"]
    else:
        with open('/tmp/gcp_credentials.json', 'w') as gcp_secrets:
            gcp_secrets.write(base64.b64decode(secrets["gcp"]["key-value"]).decode('utf-8'))


def get_azure_backend_config(key, secrets):
    return {"storage_account_name": secrets["storage-account-name"],
            "container_name": secrets["storage-account-container"],
            "key": key,
            "sas_token": secrets["storage-account-sas"]}


def configure_terraform_cloud_secrets(secrets):
    secrets_entry = 'credentials "app.terraform.io" {0}'.format('{ token = "' + secrets["token"] + '" }')

    Path("~/.terraform.d").mkdir(parents=True, exist_ok=True)
    with open("~/.terraform.d/credentials.tfrc.json", "a") as terraform_config:
        terraform_config.write(secrets_entry)


def deploy_infrastructure(id, secrets, steps, config, workspace):
    if "azure" in secrets.keys():
        config_azure_env(secrets)
    if "gcp" in secrets.keys():
        config_gcp_env(secrets)
    if "azuredevops" in secrets.keys():
        config_devops_env(secrets)

    tf_controller = Terraform(working_dir=workspace,
                              variables=config["parameters"])

    backend_config = None
    if "backend" in config.keys():
        if config["backend"]["type"] == "azurerm":
            backend_config = get_azure_backend_config(config["backend"]["key"], secrets["azurerm-backend"])
    tf_controller.init(capture_output=False, backend_config=backend_config)

    if config["backend"]["type"] == "azurerm":
        workspace_list = tf_controller.cmd('workspace', 'list')[1]
        workspace_list = workspace_list.replace('\n', '').replace('*', '').split()

        if id not in workspace_list:
            tf_controller.create_workspace(id)
        tf_controller.set_workspace(id)
    elif config["backend"]["type"] == "terraform-cloud":
        url = "https://app.terraform.io/api/v2/organizations/{0}/workspaces/{1}".format(config["backend"]["org"], config["backend"]["workspace"])
        header = {"Authorization": "Bearer {}".format(secrets["terraform-cloud-backend"]["token"]),
                  "Content-Type": "application/vnd.api+json"}
        data = {"data": {"type": "workspaces", "attributes": {"operations": False}}}

        requests.patch(url, data=json.dumps(data), headers=header)

    if "deploy" in steps:
        tf_controller.plan(capture_output=False)
        tf_controller.apply(capture_output=False, skip_plan=True)

    if "destroy" in steps:
        tf_controller.destroy(capture_output=False)

        if config["backend"]["type"] == "azurerm":
            tf_controller.delete_workspace(id)
        elif config["backend"]["type"] == "terraform-cloud":
            url = "https://app.terraform.io/api/v2/organizations/{0}/workspaces/{1}".format(config["backend"]["org"], config["backend"]["workspace"])
            header = {"Authorization": "Bearer {}".format(secrets["terraform-cloud-backend"]["token"]),
                      "Content-Type": "application/vnd.api+json"}

            requests.delete(url, headers=header)


if __name__ == "__main__":
    parameters = get_parameters()
    parameters = check_parameters(parameters)

    config = Configuration(parameters.config_path, parameters.secrets_path, parameters)

    if "prepare" in config.content["steps"] and "prepare" in config.content["script"].keys():
        execute_script(config.content["script"]["prepare"], config.content["script"]["env"])

    deploy_infrastructure(config.content["deployment_id"],
                          config.content["secrets"],
                          config.content["steps"],
                          config.content["terraform"],
                          parameters.terraform_workspace)

    if "cleanup" in config.content["steps"] and "cleanup" in config.content["script"].keys():
        execute_script(config.content["script"]["cleanup"], config.content["script"]["env"])
