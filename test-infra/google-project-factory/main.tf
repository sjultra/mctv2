terraform {
    backend "azurerm" {}
}


provider "google" {
  version     = "~> 2.18.1"
}

provider "google-beta" {
}

module "project-factory" {
  source                  = "github.com/terraform-google-modules/terraform-google-project-factory"
  random_project_id       = false
  name                    = var.gcp_project_name
  project_id              = var.gcp_project_id
  org_id                  = var.gcp_organization_id
  billing_account         = var.gcp_billing_account
  default_service_account = var.gcp_service_account
  sa_role                 = "roles/viewer"

  activate_apis = [
    "cloudresourcemanager.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudkms.googleapis.com",
    "iam.googleapis.com",
    "container.googleapis.com"
  ]
}
