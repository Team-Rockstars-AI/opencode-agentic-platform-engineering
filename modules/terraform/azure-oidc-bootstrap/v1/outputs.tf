output "client_id" {
  value       = azurerm_user_assigned_identity.pipeline.client_id
  description = "The application client ID associated with the pipeline OIDC identity"
}

output "principal_id" {
  value       = azurerm_user_assigned_identity.pipeline.principal_id
  description = "The principal ID of the pipeline identity"
}

output "identity_id" {
  value       = azurerm_user_assigned_identity.pipeline.id
  description = "The resource ID of the OIDC User Assigned Identity"
}
