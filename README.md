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
    "terraform": {
        "parameters": {
            "azure_subscription_id": "XXXXXXXXXXXXXXXXXXXXXXX",
            "azure_client_id": "XXXXXXXXXXXXXXXXXXXXXXX",
            "azure_client_secret": "XXXXXXXXXXXXXXXXXXXXXXX",
            "azure_tenant_id": "XXXXXXXXXXXXXXXXXXXXXXX"
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
