variable "project_name" {
  type        = string
  description = "The name of the project"

  validation {
    condition     = length(var.project_name) >= 3 && length(var.project_name) <= 24
    error_message = "The project name must be between 3 and 24 characters long."
  }

  validation {
    condition     = can(regex("^[a-zA-Z0-9-]+$", var.project_name))
    error_message = "The project name must only contain alphanumeric characters and hyphens."
  }
}

variable "environment" {
  type        = string
  description = "The deployment environment (dev, test, prod)"
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "The environment variable must be one of: dev, test, prod."
  }
}

variable "location" {
  type        = string
  description = "Azure primary region location"

  validation {
    condition     = length(var.location) >= 3
    error_message = "The location must be a valid Azure region name (minimum 3 characters)."
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

variable "is_enterprise" {
  type        = bool
  description = "Enable Enterprise-level options (e.g. Runner Subnets and KEDA configuration)"
  default     = false
}

variable "vnet_address_space" {
  type        = string
  description = "Address space CIDR block for VNet"
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vnet_address_space))
    error_message = "The vnet_address_space must be a valid CIDR block."
  }
}

variable "subnet_workloads_prefix" {
  type        = string
  description = "Workloads Subnet IP Prefix"
  default     = "10.0.1.0/24"

  validation {
    condition     = can(cidrnetmask(var.subnet_workloads_prefix))
    error_message = "The subnet_workloads_prefix must be a valid CIDR block."
  }
}

variable "subnet_appgw_prefix" {
  type        = string
  description = "Application Gateway Subnet IP Prefix"
  default     = "10.0.2.0/24"

  validation {
    condition     = can(cidrnetmask(var.subnet_appgw_prefix))
    error_message = "The subnet_appgw_prefix must be a valid CIDR block."
  }
}

variable "subnet_endpoints_prefix" {
  type        = string
  description = "Private Endpoints Subnet IP Prefix"
  default     = "10.0.3.0/24"

  validation {
    condition     = can(cidrnetmask(var.subnet_endpoints_prefix))
    error_message = "The subnet_endpoints_prefix must be a valid CIDR block."
  }
}

variable "subnet_runners_prefix" {
  type        = string
  description = "Private Runners Subnet IP Prefix"
  default     = "10.0.4.0/24"

  validation {
    condition     = can(cidrnetmask(var.subnet_runners_prefix))
    error_message = "The subnet_runners_prefix must be a valid CIDR block."
  }
}

variable "tags" {
  type        = map(string)
  description = "Resource tags mapping"
  default     = {}
}

variable "ssl_certificate_key_vault_secret_id" {
  type        = string
  description = "The Key Vault Secret ID of the SSL certificate for HTTPS"
  default     = null
}

variable "disable_http" {
  type        = bool
  description = "Disable the port 80 HTTP listener entirely on the Application Gateway"
  default     = false
}

variable "log_analytics_workspace_id" {
  type        = string
  default     = null
  description = "The resource ID of the central Log Analytics workspace for diagnostics"
}
