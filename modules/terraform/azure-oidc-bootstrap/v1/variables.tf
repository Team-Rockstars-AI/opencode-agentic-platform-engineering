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
  description = "Resource group name for OIDC identity"

  validation {
    condition     = length(var.resource_group_name) >= 1 && length(var.resource_group_name) <= 90 && can(regex("^[a-zA-Z0-9-_()\\.]*[a-zA-Z0-9-()_]$", var.resource_group_name))
    error_message = "The resource group name must be between 1 and 90 characters, can contain only alphanumeric characters, underscores, hyphens, periods, and parentheses, and cannot end with a period."
  }
}

variable "subscription_scope_id" {
  type        = string
  description = "The fully qualified subscription resource id for RBAC permissions"

  validation {
    condition     = can(regex("^/subscriptions/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.subscription_scope_id))
    error_message = "The subscription_scope_id must be a valid subscription resource ID (e.g., /subscriptions/00000000-0000-0000-0000-000000000000)."
  }
}

variable "github_org_name" {
  type        = string
  description = "The name of the GitHub organization or username"
  default     = ""
}

variable "github_repo_name" {
  type        = string
  description = "The name of the GitHub repository"
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "Resources tags map"
  default     = {}
}
