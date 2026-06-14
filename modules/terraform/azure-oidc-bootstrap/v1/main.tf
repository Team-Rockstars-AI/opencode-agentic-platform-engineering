resource "azurerm_resource_group" "oidc" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_user_assigned_identity" "pipeline" {
  name                = "id-pipeline-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.oidc.location
  resource_group_name = azurerm_resource_group.oidc.name
  tags                = var.tags
}

# Sub-level contributor assignment
resource "azurerm_role_assignment" "pipeline_contributor" {
  scope                = var.subscription_scope_id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.pipeline.principal_id
}

# Sub-level User Access Administrator (required for role assignments or pipeline creations)
resource "azurerm_role_assignment" "pipeline_user_access" {
  scope                = var.subscription_scope_id
  role_definition_name = "User Access Administrator"
  principal_id         = azurerm_user_assigned_identity.pipeline.principal_id
}

# Federated identities for GitHub pull requests and main pushes
resource "azurerm_federated_identity_credential" "github_main" {
  count               = var.github_org_name != "" ? 1 : 0
  name                = "fed-github-main"
  resource_group_name = azurerm_resource_group.oidc.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.pipeline.id
  subject             = "repo:${var.github_org_name}/${var.github_repo_name}:ref:refs/heads/main"
}

resource "azurerm_federated_identity_credential" "github_pr" {
  count               = var.github_org_name != "" ? 1 : 0
  name                = "fed-github-pr"
  resource_group_name = azurerm_resource_group.oidc.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.pipeline.id
  subject             = "repo:${var.github_org_name}/${var.github_repo_name}:pull_request"
}
