output "runner_identity_principal_id" {
  value       = azurerm_user_assigned_identity.runner.principal_id
  description = "The Principal ID of the runner's user-assigned managed identity"
}

output "runner_app_id" {
  value       = azurerm_container_app.runner_app.id
  description = "The ID of the Container App runner"
}
