variable "azure_rg_name" {
    type = string
}

terraform {
    backend "azurerm" {}
}

provider "azurerm" {
    # The "feature" block is required for AzureRM provider 2.x. 
    # If you're using version 1.x, the "features" block is not allowed.
    version = "~>2.0"
    features {}
}


resource "azurerm_resource_group" "myterraformgroup" {
    name     = var.azure_rg_name
    location = "eastus"

    tags = {
        environment = "Terraform Demo"
    }
}
