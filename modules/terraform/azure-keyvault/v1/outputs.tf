output "id" {
  value       = azurerm_key_vault.kv.id
  description = "The resource ID of the Key Vault"
}

output "vault_uri" {
  value       = azurerm_key_vault.kv.vault_uri
  description = "The URI of the Key Vault"
}
