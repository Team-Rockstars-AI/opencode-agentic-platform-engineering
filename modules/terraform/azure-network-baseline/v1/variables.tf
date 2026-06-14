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

variable "is_enterprise" {
  type        = bool
  description = "Enable Enterprise-level options (e.g. Runner Subnets and KEDA configuration)"
  default     = false
}

variable "vnet_address_space" {
  type        = string
  description = "Address space CIDR block for VNet"
  default     = "10.0.0.0/16"
}

variable "subnet_workloads_prefix" {
  type        = string
  description = "Workloads Subnet IP Prefix"
  default     = "10.0.1.0/24"
}

variable "subnet_appgw_prefix" {
  type        = string
  description = "Application Gateway Subnet IP Prefix"
  default     = "10.0.2.0/24"
}

variable "subnet_endpoints_prefix" {
  type        = string
  description = "Private Endpoints Subnet IP Prefix"
  default     = "10.0.3.0/24"
}

variable "subnet_runners_prefix" {
  type        = string
  description = "Private Runners Subnet IP Prefix"
  default     = "10.0.4.0/24"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags mapping"
  default     = {}
}
