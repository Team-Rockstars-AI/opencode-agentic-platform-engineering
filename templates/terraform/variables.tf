variable "project_name" {
  type        = string
  description = "The name of the project"
  default     = "{{project_name}}"

  validation {
    condition     = can(regex("^[a-zA-Z0-9-_]+$", var.project_name)) || var.project_name == "{{project_name}}"
    error_message = "The project_name must be alphanumeric and may contain hyphens or underscores."
  }
}

variable "location" {
  type        = string
  description = "The primary Azure region to deploy to"
  default     = "{{azure_location}}"
}

variable "subscription_id" {
  type        = string
  description = "The Azure subscription ID"
  default     = "{{subscription_id}}"

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.subscription_id)) || var.subscription_id == "{{subscription_id}}"
    error_message = "The subscription_id must be a valid UUID."
  }
}

variable "tenant_id" {
  type        = string
  description = "The Azure active directory tenant ID"
  default     = "{{tenant_id}}"

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.tenant_id)) || var.tenant_id == "{{tenant_id}}"
    error_message = "The tenant_id must be a valid UUID."
  }
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment variable must be one of: dev, staging, prod."
  }
}

variable "governance_tier" {
  type        = string
  description = "Governance tier (basic, enterprise)"
  default     = "{{governance_tier}}"

  validation {
    condition     = contains(["basic", "enterprise"], var.governance_tier) || var.governance_tier == "{{governance_tier}}"
    error_message = "The governance_tier variable must be one of: basic, enterprise."
  }
}

variable "github_org_name" {
  type        = string
  description = "The GitHub Organization or Username"
  default     = "{{github_org_name}}"
}

variable "github_repo_name" {
  type        = string
  description = "The GitHub Repository Name"
  default     = "{{github_repo_name}}"
}

variable "runner_token" {
  type        = string
  description = "GitHub fine-grained PAT or GitHub App installation token for runner registration. MUST be scoped to a single repository with admin:org (self-hosted runners) permission. MUST have a maximum 7-day expiration. Prefer GitHub App installation tokens for automated rotation and security."
  sensitive   = true
  default     = "placeholder-pat"
}
