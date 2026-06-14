variable "name" {
  type        = string
  description = "The name of the Key Vault"

  validation {
    condition     = length(var.name) >= 3 && length(var.name) <= 24 && can(regex("^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$", var.name))
    error_message = "The Key Vault name must be between 3 and 24 characters, start with a letter, end with a letter or digit, and contain only alphanumeric characters and hyphens."
  }
}

variable "resource_group_name" {
  type        = string
  description = "The name of the resource group"

  validation {
    condition     = length(var.resource_group_name) >= 1 && length(var.resource_group_name) <= 90 && can(regex("^[a-zA-Z0-9-_()\\.]*[a-zA-Z0-9-()_]$", var.resource_group_name))
    error_message = "The resource group name must be between 1 and 90 characters, can contain only alphanumeric characters, underscores, hyphens, periods, and parentheses, and cannot end with a period."
  }
}

variable "location" {
  type        = string
  description = "The Azure region for the Key Vault"

  validation {
    condition     = length(var.location) >= 3
    error_message = "The location must be a valid Azure region name (minimum 3 characters)."
  }
}

variable "tenant_id" {
  type        = string
  description = "The Active Directory tenant ID"

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.tenant_id))
    error_message = "The tenant_id must be a valid UUID."
  }
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the vault: standard or premium"
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "The sku_name variable must be 'standard' or 'premium'."
  }
}

variable "soft_delete_retention_days" {
  type        = number
  description = "Number of days soft-deleted keys are retained"
  default     = 90

  validation {
    condition     = var.soft_delete_retention_days >= 7 && var.soft_delete_retention_days <= 90
    error_message = "The soft_delete_retention_days variable must be between 7 and 90."
  }
}

variable "purge_protection_enabled" {
  type        = bool
  description = "Is purge protection enabled for this Key Vault?"
  default     = true
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Is public network access enabled for this Key Vault?"
  default     = false
}
