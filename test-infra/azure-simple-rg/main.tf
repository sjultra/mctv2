variable "azure_subscription_id" {
    type = string
}

variable "azure_client_id" {
    type = string
}

variable "azure_client_secret" {
    type = string
}

variable "azure_tenant_id" {
    type = string
}

provider "azurerm" {
    # The "feature" block is required for AzureRM provider 2.x. 
    # If you're using version 1.x, the "features" block is not allowed.
    version = "~>2.0"
    features {}

    subscription_id = var.azure_subscription_id
    client_id       = var.azure_client_id
    client_secret   = var.azure_client_secret
    tenant_id       = var.azure_tenant_id
}


resource "azurerm_resource_group" "myterraformgroup" {
    name     = "test-rg"
    location = "eastus"

    tags = {
        environment = "Terraform Demo"
    }
}