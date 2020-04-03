from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential

class SecretProvider():
    def __init__(self, provider_details):
        self._provider_details = provider_details

    def get_secret(key_name):
        pass

    def set_secret(key_name, key_value):
        pass

class AzureKeyVault(SecretProvider):
    def __init__(self, provider_details):
        super().__init__(provider_details) 
        self.__auth_azure()

    def __auth_azure(self):
        provider_credentials = self._provider_details["credentials"]
        credential = ClientSecretCredential(tenant_id=provider_credentials["azure_tenant_id"], 
                                            client_id=provider_credentials["azure_client_id"],
                                            client_secret=provider_credentials["azure_client_secret"])

        self.__provider = SecretClient(vault_url=provider_credentials["azure_keyvault_url"], 
                                       credential=credential)

    def set_secret(self, key_name, key_value):
        self.__provider.set_secret(key_name, key_value)

    def get_secret(self, key_name):
        return self.__provider.get_secret(key_name)