# MCTv2 Alpha

Test framework for Terraform infrastructures.

## Steps
1. Setup environment:
```
# Tested only on debian based distros
sudo bash ./utils/setup_env.sh
```
2. Create json config file. Example: 
```
{
    "secret_provider": {
        "name": "AzureKeyVault",
        "credentials": {
            "azure_keyvault_url": "https://test-vault.vault.azure.net/",
            "azure_client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "azure_client_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "azure_tenant_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
    },
    "secrets": {
        "azure": {
            "subscription-id": "",
            "client-id": "",
            "client-secret": "",
            "tenant-id": ""
        }
    },
    "terraform": {
        "parameters": {
            "test_parameter": "XXXXXXXXX"
        }
    }
}
```
3. Run MCTv2:
```
python3 main.py --config_path "./config.json" --terraform_workspace "./test-infra/azure-simple-rg/"
```

## Configuration
ToDo
