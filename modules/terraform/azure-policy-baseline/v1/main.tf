# Subscription-scope assignments of built-in Azure Policy definitions that
# back the platform's secure-by-design baseline at runtime (post-deployment).
# Definition GUIDs verified against the Microsoft Learn built-in policy index:
# https://learn.microsoft.com/azure/governance/policy/samples/built-in-policies

locals {
  subscription_scope = "/subscriptions/${var.subscription_id}"
  definition_prefix  = "/providers/Microsoft.Authorization/policyDefinitions"
}

# Allowed locations (data residency / geo-compliance). Effect is fixed (deny)
# in the built-in definition; it only takes the location list parameter.
resource "azurerm_subscription_policy_assignment" "allowed_locations" {
  name                 = "pa-locations-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/e56962a6-4747-49cd-b67b-bf8b01975c4c"
  display_name         = "Allowed locations (${var.project_name})"
  description          = "Restrict resource deployment to approved regions for data-residency compliance."
  enforce              = var.enforcement_mode

  parameters = jsonencode({
    listOfAllowedLocations = { value = var.allowed_locations }
  })
}

# Secure transfer (HTTPS-only) to storage accounts.
resource "azurerm_subscription_policy_assignment" "storage_secure_transfer" {
  name                 = "pa-st-https-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/404c3081-a854-4457-ae30-26a93ef643f9"
  display_name         = "Secure transfer to storage accounts (${var.project_name})"
  description          = "Storage accounts must only accept requests over HTTPS (encryption in transit)."
  enforce              = var.enforcement_mode

  parameters = jsonencode({
    effect = { value = var.policy_effect }
  })
}

# Storage accounts should disable public network access (private-endpoint-only posture).
resource "azurerm_subscription_policy_assignment" "storage_no_public_access" {
  name                 = "pa-st-nopub-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/b2982f36-99f2-4db5-8eff-283140c09693"
  display_name         = "Storage accounts should disable public network access (${var.project_name})"
  description          = "Storage accounts must not be exposed to the public internet; access via Private Endpoints only."
  enforce              = var.enforcement_mode

  parameters = jsonencode({
    effect = { value = var.policy_effect }
  })
}

# Azure Key Vault should disable public network access.
resource "azurerm_subscription_policy_assignment" "keyvault_no_public_access" {
  name                 = "pa-kv-nopub-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/405c5871-3e91-4644-8a63-58e19d68ff5b"
  display_name         = "Key Vault should disable public network access (${var.project_name})"
  description          = "Key Vaults must not be reachable over the public internet; access via Private Endpoints only."
  enforce              = var.enforcement_mode

  parameters = jsonencode({
    effect = { value = var.policy_effect }
  })
}

# Key vaults should have deletion (purge) protection enabled.
resource "azurerm_subscription_policy_assignment" "keyvault_purge_protection" {
  name                 = "pa-kv-purge-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/0b60c0b2-2dc2-4e1c-b5c9-abbed971de53"
  display_name         = "Key Vault deletion protection (${var.project_name})"
  description          = "Key Vaults must have purge protection enabled — the platform's non-negotiable recovery baseline."
  enforce              = var.enforcement_mode

  parameters = jsonencode({
    effect = { value = var.policy_effect }
  })
}

# Network interfaces should not have public IPs. Effect is fixed (deny) in the
# built-in definition and it takes no parameters. Enforces the NAT-Gateway-only
# egress design: workloads never attach public IPs directly.
resource "azurerm_subscription_policy_assignment" "nic_no_public_ip" {
  count                = var.enable_deny_public_ip_nics ? 1 : 0
  name                 = "pa-nic-nopip-${var.project_name}-${var.environment}"
  subscription_id      = local.subscription_scope
  policy_definition_id = "${local.definition_prefix}/83a86a26-fd1f-447c-b59d-e51f44264114"
  display_name         = "Network interfaces should not have public IPs (${var.project_name})"
  description          = "Deny public IPs on NICs; all outbound egress flows through the NAT Gateway, inbound through the WAF Application Gateway."
  enforce              = var.enforcement_mode
}
