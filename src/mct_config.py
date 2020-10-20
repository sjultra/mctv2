import json
import os
from secret_provider import AzureKeyVault
from logger import log

def add_dict_value(dictionary, path, value):
    if len(path) > 1:
        if path[0] not in dictionary.keys():
            dictionary[path[0]] = {}
        add_dict_value(dictionary[path[0]], path[1:], value)
    else:
        dictionary[path[0]] = value

    return dictionary

def get_dict_value(dictionary, path):
    val = dictionary
    for key in path:
        val = val[key]
    return val


def get_dict_paths(data):
    paths = []

    for key in data.keys():
        if type(data[key]) is dict:
            for next_key in get_dict_paths(data[key]):
                paths.append(key + '.' + next_key)
        else:
            paths.append(key)

    return paths


class Configuration:
    def __init__(self):
        log.info("Starting configuration")
        self.content = dict()

    def new_init(self, parameters):
        self.__resolve_secrets()

        self.__populate_parameters()
        self.__replace_parameters(parameters)

    def parse_config(self, config_path, secrets_path):
        config_file = open(config_path)
        log.info("Using configuration from file: {}".format(config_path))

        json_config = config_file.read()
        self.content.update(json.loads(json_config))

        if secrets_path and os.path.isfile(secrets_path):
            secrets_file = open(secrets_path)
            log.info("Using secrets from file: {}".format(secrets_path))
            json_secrets = secrets_file.read()
            self.content.update(json.loads(json_secrets))
        else:
            log.warn("No secrets file found, trying to import secrets from configuration")
        

    def resolve_custom_fields(self, parameters):
        if not parameters.custom_fields:
            return

        for custom_field in parameters.custom_fields.split(';'):
            path = custom_field.split('=', 1)[0].split('.')
            value = custom_field.split('=', 1)[1]

            log.info("Replacing in configuration: {} = {}".format('.'.join(path), value))
            if path and value:
                self.content = add_dict_value(self.content, path, value)

    def resolve_secrets(self):
        if "secret_provider" not in self.content:
            log.warn("Cannot find secret provider configuration, using default values")
            return

        if self.content["secret_provider"]["type"] == 'azure':
            remote_secrets = AzureKeyVault(self.content["secret_provider"])
        else:
            log.error("Secrets provider of type: {} not supported".format(self.content["secret_provider"]["type"]))

        prefix = ""
        if "prefix" in self.content["secret_provider"].keys() and self.content["secret_provider"]["prefix"]:
            log.info("Looking for secrets with prefix: {}".format(self.content["secret_provider"]["prefix"]))
            prefix = self.content["secret_provider"]["prefix"] + '-'

        secret_vars = get_dict_paths(self.content["secrets"])

        for var in secret_vars:
            value = get_dict_value(self.content["secrets"], var.split('.'))
            if value == "":
                secret_name = prefix + var
                secret = remote_secrets.get_secret(secret_name)
                self.content["secrets"] = add_dict_value(self.content["secrets"], var.split('.'), secret)


    def replace_parameters(self, parameters):
        if parameters.steps:
            self.content["steps"] = parameters.steps.split(",")

        if parameters.id:
            self.content["deployment_id"] = parameters.id
            self.content["terraform"]["parameters"]["id"] = parameters.id

    def __populate_parameters(self):
        if "script" in self.content.keys():
            if "env" not in self.content["script"]:
                self.content["script"]["env"] = dict()
            if "env" in self.content["secrets"].keys():
                self.content["script"]["env"].update(self.content["secrets"]["env"])

        if "parameters" not in self.content["terraform"]:
            self.content["terraform"]["parameters"] = dict()
        if "terraform" in self.content["secrets"].keys():
            self.content["terraform"]["parameters"].update(self.content["secrets"]["terraform"])


