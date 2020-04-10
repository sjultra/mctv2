from python_terraform import *
from mct_config import Configuration 
import argparse
import os

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

def config_gcp_env(secrets):
    os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = secrets["gcp"]["key-path"]

def get_azure_backend_config(key, secrets):
    return {"storage_account_name": secrets["storage-account-name"], 
            "container_name": secrets["storage-account-container"], 
            "key": key, 
            "sas_token": secrets["storage-account-sas"]}


def deploy_infrastructure(id, secrets, steps, config, workspace):
    config_azure_env(secrets)
    config_gcp_env(secrets)

    tf_controller = Terraform(working_dir=workspace, 
                              variables=config["parameters"])

    backend_config = None
    if "backend" in config.keys():
        backend_config = get_azure_backend_config(config["backend"]["key"], secrets["azurerm-backend"])
    tf_controller.init(capture_output=False, backend_config=backend_config)
    
    workspace_list = tf_controller.cmd('workspace', 'list')[1]
    workspace_list = workspace_list.replace('\n', '').replace('*', '').split()

    if not id in workspace_list:
        tf_controller.create_workspace(id)

    tf_controller.set_workspace(id)

    if "deploy" in steps:
        tf_controller.plan(capture_output=False)
        tf_controller.apply(capture_output=False, skip_plan=True)

    if "destroy" in steps:
        tf_controller.destroy(capture_output=False)
        tf_controller.delete_workspace(id)


if __name__ == "__main__":
    parameters = get_parameters()
    parameters = check_parameters(parameters)
    
    config = Configuration(parameters.config_path, parameters.secrets_path, parameters)

    output = deploy_infrastructure(config.content["deployment_id"],
                                   config.content["secrets"],
                                   config.content["steps"],
                                   config.content["terraform"], 
                                   parameters.terraform_workspace)
