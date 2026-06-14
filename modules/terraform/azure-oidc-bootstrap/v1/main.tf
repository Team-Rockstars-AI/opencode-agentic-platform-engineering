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

# Sub-level custom deployer role definition and assignment
resource "azurerm_role_definition" "pipeline_deployer" {
  name        = "custom-pipeline-deployer-${var.project_name}-${var.environment}"
  scope       = var.subscription_scope_id
  description = "Custom least-privilege role for deployment pipeline"

  permissions {
    actions = [
      "Microsoft.Resources/subscriptions/resourceGroups/read",
      "Microsoft.Resources/subscriptions/resourceGroups/write",
      "Microsoft.Resources/deployments/*",
      "Microsoft.Network/virtualNetworks/read",
      "Microsoft.Network/virtualNetworks/subnets/read",
      "Microsoft.Network/virtualNetworks/subnets/join/action",
      "Microsoft.Network/networkSecurityGroups/read",
      "Microsoft.Network/networkSecurityGroups/write",
      "Microsoft.Network/networkSecurityGroups/join/action",
      "Microsoft.Network/publicIPAddresses/read",
      "Microsoft.Network/publicIPAddresses/write",
      "Microsoft.Network/natGateways/read",
      "Microsoft.Network/natGateways/write",
      "Microsoft.Network/applicationGateways/read",
      "Microsoft.Network/applicationGateways/write",
      "Microsoft.Network/privateEndpoints/read",
      "Microsoft.Network/privateEndpoints/write",
      "Microsoft.KeyVault/vaults/read",
      "Microsoft.KeyVault/vaults/write",
      "Microsoft.KeyVault/vaults/deploy/action",
      "Microsoft.Storage/storageAccounts/read",
      "Microsoft.Storage/storageAccounts/write",
      "Microsoft.App/managedEnvironments/read",
      "Microsoft.App/managedEnvironments/write",
      "Microsoft.App/managedEnvironments/join/action",
      "Microsoft.App/containerApps/read",
      "Microsoft.App/containerApps/write",
      "Microsoft.Web/sites/read",
      "Microsoft.Web/sites/write",
      "Microsoft.ManagedIdentity/userAssignedIdentities/read",
      "Microsoft.ManagedIdentity/userAssignedIdentities/write",
      "Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials/read",
      "Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials/write",
      "Microsoft.Insights/diagnosticSettings/read",
      "Microsoft.Insights/diagnosticSettings/write",
      "Microsoft.OperationalInsights/workspaces/read",
      "Microsoft.OperationalInsights/workspaces/write",
      "Microsoft.Authorization/*/read",
    ]
    not_actions = []
  }

  assignable_scopes = [
    var.subscription_scope_id
  ]
}

resource "azurerm_role_assignment" "pipeline_deployer" {
  scope              = var.subscription_scope_id
  role_definition_id = azurerm_role_definition.pipeline_deployer.role_definition_resource_id
  principal_id       = azurerm_user_assigned_identity.pipeline.principal_id
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
