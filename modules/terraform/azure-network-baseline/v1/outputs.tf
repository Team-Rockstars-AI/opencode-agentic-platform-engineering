output "vnet_id" {
  value       = azurerm_virtual_network.vnet.id
  description = "The ID of the virtual network"
}

output "vnet_name" {
  value       = azurerm_virtual_network.vnet.name
  description = "The Name of the virtual network"
}

output "subnet_workloads_id" {
  value       = azurerm_subnet.workloads.id
  description = "The ID of the workload subnet"
}

output "subnet_appgw_id" {
  value       = azurerm_subnet.appgw.id
  description = "The ID of the App Gateway subnet"
}

output "subnet_endpoints_id" {
  value       = azurerm_subnet.endpoints.id
  description = "The ID of the private endpoints subnet"
}

output "subnet_runners_id" {
  value       = var.is_enterprise ? azurerm_subnet.runners[0].id : null
  description = "The ID of the private runners subnet (if enterprise is enabled)"
}

output "nat_public_ip" {
  value       = azurerm_public_ip.nat_pip.ip_address
  description = "The public IP address used by the outbound NAT gateway"
}

output "appgw_public_ip" {
  value       = azurerm_public_ip.appgw_pip.ip_address
  description = "The public IP address of the App Gateway Inbound"
}
