variable "gcp_organization_id" {
  description = "The organization id for the associated services"
  default = ""
}

variable "gcp_billing_account" {
  description = "The ID of the billing account to associate this project with"
  default = ""
}

variable "gcp_service_account" {
  description = "Project default service account setting: can be one of `delete`, `depriviledge`, `disable`, or `keep`."
  default = ""
}

variable "gcp_project_name" {
  default = "project"
}

variable "gcp_project_id" {
  default = "project"
}
