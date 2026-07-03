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

variable "runner_cpu" {
  type        = string
  description = "CPU cores allocated to the runner container (e.g., \"0.5\", \"1.0\", \"2.0\")"
  default     = "1.0"

  validation {
    condition     = contains(["0.25", "0.5", "0.75", "1.0", "1.25", "1.5", "1.75", "2.0"], var.runner_cpu)
    error_message = "The runner_cpu must be one of: 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0."
  }
}

variable "runner_memory" {
  type        = string
  description = "Memory allocated to the runner container (e.g., \"0.5Gi\", \"1.0Gi\", \"2.0Gi\")"
  default     = "2.0Gi"

  validation {
    condition     = contains(["0.5Gi", "1.0Gi", "1.5Gi", "2.0Gi", "3.0Gi", "4.0Gi"], var.runner_memory)
    error_message = "The runner_memory must be one of: 0.5Gi, 1.0Gi, 1.5Gi, 2.0Gi, 3.0Gi, 4.0Gi."
  }
}

variable "enable_policy_baseline" {
  type        = bool
  description = "Assign the subscription-scope Azure Policy baseline (runtime enforcement of the secure-by-design controls)"
  default     = true
}

variable "policy_allowed_locations" {
  type        = list(string)
  description = "Azure regions resources may be deployed to (data-residency guardrail). Empty list defaults to the platform's primary location."
  default     = []
}

variable "policy_effect" {
  type        = string
  description = "Effect for the parameterisable baseline policies: Audit reports violations, Deny blocks them. Applies to the whole subscription — raise to Deny once the subscription is clean."
  default     = "Audit"

  validation {
    condition     = contains(["Audit", "Deny", "Disabled"], var.policy_effect)
    error_message = "The policy_effect must be one of: Audit, Deny, Disabled."
  }
}

variable "policy_enforcement_mode" {
  type        = bool
  description = "When false, baseline policy assignments are created in DoNotEnforce mode (evaluate and report only)"
  default     = true
}
