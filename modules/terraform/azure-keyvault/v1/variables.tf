variable "name" {
  type        = string
  description = "The name of the Key Vault"
}

variable "resource_group_name" {
  type        = string
  description = "The name of the resource group"
}

variable "location" {
  type        = string
  description = "The Azure region for the Key Vault"
}

variable "tenant_id" {
  type        = string
  description = "The Active Directory tenant ID"
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
  default     = 7

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
