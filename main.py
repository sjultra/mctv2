from python_terraform import *
import argparse
import os
import json

def get_parameters():
    parser = argparse.ArgumentParser(description="MCTv2 Alpha")

    parser.add_argument('--config_path')
    parser.add_argument('--terraform_workspace')

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

def get_config(config_path):
    config_file = open(config_path)
    
    json_content = config_file.read()
    content = json.loads(json_content)

    return content

def deploy_infrastructure(config, workspace):
    tf_controller = Terraform(working_dir=workspace, variables=config["parameters"])

    tf_controller.init(capture_output=False)
    tf_controller.plan(capture_output=False)
    tf_controller.apply(capture_output=False, skip_plan=True)
    tf_controller.destroy(capture_output=False, force=IsNotFlagged)


if __name__ == "__main__":
    parameters = get_parameters()
    parameters = check_parameters(parameters)

    config = get_config(parameters.config_path)

    output = deploy_infrastructure(config["terraform"], parameters.terraform_workspace)
