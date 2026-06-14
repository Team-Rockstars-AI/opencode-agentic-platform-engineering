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
}

variable "soft_delete_retention_days" {
  type        = number
  description = "Number of days soft-deleted keys are retained"
  default     = 7
}

variable "purge_protection_enabled" {
  type        = bool
  description = "Is purge protection enabled for this Key Vault?"
  default     = false
}
