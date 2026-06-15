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
}

variable "subnet_runners_id" {
  type        = string
  description = "The ID of the subnet dedicated for scale-to-zero runners"
}

variable "github_org_name" {
  type        = string
  description = "The GitHub Organization or Username"
  default     = ""

  validation {
    condition     = var.github_org_name == "" || (length(var.github_org_name) >= 1 && length(var.github_org_name) <= 39 && can(regex("^[a-zA-Z0-9-]+$", var.github_org_name)))
    error_message = "The github_org_name must be between 1 and 39 characters long and contain only alphanumeric characters and hyphens, or be empty."
  }
}

variable "github_repo_name" {
  type        = string
  description = "The GitHub Repository"
  default     = ""

  validation {
    condition     = var.github_repo_name == "" || (length(var.github_repo_name) >= 1 && length(var.github_repo_name) <= 100 && can(regex("^[a-zA-Z0-9-._]+$", var.github_repo_name)))
    error_message = "The github_repo_name must be between 1 and 100 characters long, and contain only alphanumeric characters, hyphens, periods, and underscores, or be empty."
  }
}

variable "runner_token" {
  type        = string
  description = "GitHub fine-grained PAT or GitHub App installation token for runner registration. MUST be scoped to a single repository with admin:org (self-hosted runners) permission. MUST have a maximum 7-day expiration. Prefer GitHub App installation tokens for automated rotation and security."
  sensitive   = true
  default     = "placeholder-pat"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags mapping"
  default     = {}
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "The resource ID of the central Log Analytics workspace for diagnostics"
  default     = null
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
