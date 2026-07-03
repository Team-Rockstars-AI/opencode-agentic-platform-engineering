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

variable "subscription_id" {
  type        = string
  description = "The subscription ID (GUID) the policy baseline is assigned to"

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.subscription_id))
    error_message = "The subscription_id must be a valid GUID (e.g., 00000000-0000-0000-0000-000000000000)."
  }
}

variable "allowed_locations" {
  type        = list(string)
  description = "Azure regions resources may be deployed to (data-residency guardrail)"
  default     = ["westeurope", "northeurope"]

  validation {
    condition     = length(var.allowed_locations) >= 1
    error_message = "The allowed_locations list must contain at least one region."
  }
}

variable "policy_effect" {
  type        = string
  description = "Effect for the parameterisable PaaS policies (storage secure transfer / public access, Key Vault public access / purge protection). 'Audit' reports violations; 'Deny' blocks them."
  default     = "Audit"

  validation {
    condition     = contains(["Audit", "Deny", "Disabled"], var.policy_effect)
    error_message = "The policy_effect must be one of: Audit, Deny, Disabled."
  }
}

variable "enforcement_mode" {
  type        = bool
  description = "When false, all assignments are created in DoNotEnforce mode: they evaluate and report compliance but never block deployments"
  default     = true
}

variable "enable_deny_public_ip_nics" {
  type        = bool
  description = "Assign the built-in deny policy blocking public IPs on network interfaces (the platform's NAT Gateway / App Gateway public IPs are standalone resources and unaffected)"
  default     = true
}
