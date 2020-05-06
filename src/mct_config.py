import json
from secret_provider import AzureKeyVault


def add_dict_value(dictionary, path, value):
    if len(path) > 1:
        if path[0] not in dictionary.keys():
            dictionary[path[0]] = {}
        add_dict_value(dictionary[path[0]], path[1:], value)
    else:
        dictionary[path[0]] = value

    return dictionary


class Configuration:
    def __init__(self, config_path, secrets_path, parameters):
        self.content = dict()

        self.__config_path = config_path
        self.__secrets_path = secrets_path
        self.__parse_config()

        self.__resolve_custom_fields(parameters)
        self.__resolve_secrets()

        self.__populate_parameters()
        self.__replace_parameters(parameters)

    def __parse_config(self):
        config_file = open(self.__config_path)
        secrets_file = open(self.__secrets_path)

        json_config = config_file.read()
        json_secrets = secrets_file.read()

        self.content.update(json.loads(json_secrets))
        self.content.update(json.loads(json_config))

    def __resolve_custom_fields(self, parameters):
        if not parameters.custom_fields:
            return

        for custom_field in parameters.custom_fields.split(';'):
            path = custom_field.split('=', 1)[0].split('.')
            value = custom_field.split('=', 1)[1]

            if path and value:
                self.content = add_dict_value(self.content, path, value)

    def __resolve_secrets(self):
        if "secret_provider" not in self.content:
            print("Warning: Cannot find remote secret provider configuration. Trying to find secrets in config")
            return

        remote_secrets = AzureKeyVault(self.content["secret_provider"])

        for category in self.content["secrets"].keys():
            for key in self.content["secrets"][category].keys():
                if not self.content["secrets"][category][key]:
                    key_name = category + '-' + key
                    self.content["secrets"][category][key] = remote_secrets.get_secret(key_name).value

    def __populate_parameters(self):
        if not self.content["script"]["env"]:
            self.content["script"]["env"] = dict()
        if not self.content["terraform"]["parameters"]:
            self.content["terraform"]["parameters"] = dict()

        if "env" in self.content["secrets"].keys():
            self.content["script"]["env"].update(self.content["secrets"]["env"])
        if "terraform" in self.content["secrets"].keys():
            self.content["terraform"]["parameters"].update(self.content["secrets"]["terraform"])

    def __replace_parameters(self, parameters):
        if parameters.steps:
            self.content["steps"] = parameters.steps.split(",")

        if parameters.id:
            self.content["deployment_id"] = parameters.id
