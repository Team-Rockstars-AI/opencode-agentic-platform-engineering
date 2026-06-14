variable "project_name" {
  type        = string
  description = "The name of the project"
}

variable "environment" {
  type        = string
  description = "The deployment environment (dev, test, prod)"
  default     = "dev"
}

variable "location" {
  type        = string
  description = "Azure primary region location"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name for OIDC identity"
}

variable "subscription_scope_id" {
  type        = string
  description = "The fully qualified subscription resource id for RBAC permissions"
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
