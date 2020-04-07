from python_terraform import *
from mct_config import Configuration 
import argparse
import os

def get_parameters():
    parser = argparse.ArgumentParser(description="MCTv2 Alpha")

    parser.add_argument('--config_path')
    parser.add_argument('--terraform_workspace')
    parser.add_argument('--steps')

    return parser.parse_args()

def check_parameters(parameters):
    if not parameters.config_path:
        raise Exception("config_path parameter is empty")
    parameters.config_path = os.path.abspath(parameters.config_path)
    if not parameters.terraform_workspace:
        raise Exception("terraform_workspace parameter is empty")
    parameters.terraform_workspace = os.path.abspath(parameters.terraform_workspace)

    if not os.path.isfile(parameters.config_path):
        raise Exception("File {} does not exist".format(parameters.config_path))
    if not os.path.isdir(parameters.terraform_workspace):
        raise Exception("File {} does not exist".format(parameters.terraform_workspace))

    return parameters

def config_azure_env(secrets):
    os.environ["ARM_CLIENT_ID"] = secrets["azure"]["client-id"]
    os.environ["ARM_CLIENT_SECRET"] = secrets["azure"]["client-secret"]
    os.environ["ARM_SUBSCRIPTION_ID"] = secrets["azure"]["subscription-id"]
    os.environ["ARM_TENANT_ID"] = secrets["azure"]["tenant-id"]


def deploy_infrastructure(secrets, steps, config, workspace):
    config_azure_env(secrets)

    tf_controller = Terraform(working_dir=workspace, 
                              variables=config["parameters"])

    if "deploy" in steps:
        tf_controller.init(capture_output=False)
        tf_controller.plan(capture_output=False)
        tf_controller.apply(capture_output=False, skip_plan=True)

    if "destroy" in steps:
        tf_controller.destroy(capture_output=False)


if __name__ == "__main__":
    parameters = get_parameters()
    parameters = check_parameters(parameters)
    
    config = Configuration(parameters.config_path, parameters)

    output = deploy_infrastructure(config.content["secrets"],
                                   config.content["steps"],
                                   config.content["terraform"], 
                                   parameters.terraform_workspace)
