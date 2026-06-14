# Backend configuration is populated dynamically by pipelines/scaffolding
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-{{project_name}}-backend"
    storage_account_name = "st{{project_name}}tfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}
