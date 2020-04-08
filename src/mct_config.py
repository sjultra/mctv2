import json
import importlib
from secret_provider import *

class Configuration:
    def __init__(self, config_path, parameters):
        self.__config_path = config_path
        self.__parse_config()
        self.__resolve_secrets()
        self.__replace_parameters(parameters)
    
    def __parse_config(self):
        config_file = open(self.__config_path)
    
        json_content = config_file.read()
        self.content = json.loads(json_content)

    def __resolve_secrets(self):
        if not "secret_provider" in self.content:
            print("Warning: Cannot find remote secret provider configuration. Trying to find secrets in config")
            return
        
        remote_secrets = AzureKeyVault(self.content["secret_provider"])
        
        for category in self.content["secrets"].keys():
            for key in self.content["secrets"][category].keys():
                if not self.content["secrets"][category][key]:
                    key_name = category + '-' + key
                    self.content["secrets"][category][key] = remote_secrets.get_secret(key_name).value

    def __replace_parameters(self, parameters):
        if parameters.steps:
            self.content["steps"] = parameters.steps.split(",")

        if parameters.id:
            self.content["deployment_id"] = parameters.id
    
