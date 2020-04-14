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
    "deployment_id": "",
    "steps": ["deploy", "destroy"],
    "terraform": {
        "backend": {
            "type": "azurerm",
            "key": "mct-test/"
        },
        "parameters": {
            "test_param": "ZZZZZZZZZZZZZ"
        }
    }
}
```
3. Create json screts file. Example: 
```
{
    "secret_provider": {
        "name": "AzureKeyVault",
        "credentials": {
            "azure_keyvault_url": "",
            "azure_client_id": "",
            "azure_client_secret": "",
            "azure_tenant_id": ""
        }
    },
    "secrets": {
        "azure": {
            "subscription-id": "",
            "client-id": "",
            "client-secret": "",
            "tenant-id": ""
        },
        "gcp": {
            "key-value": ""
        },
        "azurerm-backend": {
            "storage-account-name": "",
            "storage-account-container": "",
            "storage-account-sas": ""
        }
    }
}
```

4. Run MCTv2:
```
python3 src/runner.py \
    # Config created at step 2
    --config_path "./config.json" \
    # Secrets file created at step 3
    --secrets_path "./secrets.json" \
    # Path to the terraform workspace
    --terraform_workspace "./test-infra/google-project-factory/" \
    # Terraform steps to execute (only deploy / destroy supported)
    --steps "deploy,destroy" \
    --id "test" \
    # Key/value string separrated using ';'
    # The runner with replase the value at path 'terraform.parameters.param_from_cli' with value 'value'
    # Will create the key if it doesn't exist
    --custom_fields 'terraform.parameters.param_from_cli=value'
```

## Configuration
ToDo
