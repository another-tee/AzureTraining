terraform {
  required_version = ">=1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    external = {
      source = "hashicorp/external"
    }
  }
}

provider "azurerm" {
  # subscription_id in CSP
  # tenant_id, use az login in terminal
  subscription_id = "your_az_login_id"
  tenant_id       = "your_az_login_tenant_id"

  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}