variable "project_name" {
  type        = string
  description = "The name of the project"
  default     = "{{project_name}}"
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
}

variable "tenant_id" {
  type        = string
  description = "The Azure active directory tenant ID"
  default     = "{{tenant_id}}"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  default     = "dev"
}

variable "governance_tier" {
  type        = string
  description = "Governance tier (basic, enterprise)"
  default     = "{{governance_tier}}"
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
  description = "Personal access token (PAT) for registration of self-hosted runner"
  sensitive   = true
  default     = "placeholder-pat"
}
