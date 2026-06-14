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
}

variable "github_repo_name" {
  type        = string
  description = "The GitHub Repository"
  default     = ""
}

variable "runner_token" {
  type        = string
  description = "Personal access token (PAT) for registration"
  sensitive   = true
  default     = "placeholder-pat"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags mapping"
  default     = {}
}
