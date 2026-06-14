targetScope = 'subscription'

param projectName string
param environment string = 'dev'
param location string
param githubOrgName string = ''
param githubRepoName string = ''
param tags object = {}

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-oidc-${projectName}-${environment}-${location}'
  location: location
  tags: tags
}

module identityModule 'identity.bicep' = {
  name: 'identity-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
    githubOrgName: githubOrgName
    githubRepoName: githubRepoName
    tags: tags
  }
}

// Sub-level custom deployer role definition and assignment (Executed at subscription scope)
resource pipelineDeployerRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(subscription().id, 'pipelineDeployerRole')
  properties: {
    roleName: 'custom-pipeline-deployer-${projectName}-${environment}'
    description: 'Custom least-privilege role for deployment pipeline'
    assignableScopes: [
      subscription().id
    ]
    permissions: [
      {
        actions: [
          'Microsoft.Resources/subscriptions/resourceGroups/read'
          'Microsoft.Resources/subscriptions/resourceGroups/write'
          'Microsoft.Resources/deployments/*'
          'Microsoft.Network/virtualNetworks/read'
          'Microsoft.Network/virtualNetworks/subnets/read'
          'Microsoft.Network/virtualNetworks/subnets/join/action'
          'Microsoft.Network/networkSecurityGroups/read'
          'Microsoft.Network/networkSecurityGroups/write'
          'Microsoft.Network/networkSecurityGroups/join/action'
          'Microsoft.Network/publicIPAddresses/read'
          'Microsoft.Network/publicIPAddresses/write'
          'Microsoft.Network/natGateways/read'
          'Microsoft.Network/natGateways/write'
          'Microsoft.Network/applicationGateways/read'
          'Microsoft.Network/applicationGateways/write'
          'Microsoft.Network/privateEndpoints/read'
          'Microsoft.Network/privateEndpoints/write'
          'Microsoft.KeyVault/vaults/read'
          'Microsoft.KeyVault/vaults/write'
          'Microsoft.KeyVault/vaults/deploy/action'
          'Microsoft.Storage/storageAccounts/read'
          'Microsoft.Storage/storageAccounts/write'
          'Microsoft.Storage/storageAccounts/listKeys/action'
          'Microsoft.App/managedEnvironments/read'
          'Microsoft.App/managedEnvironments/write'
          'Microsoft.App/managedEnvironments/join/action'
          'Microsoft.App/containerApps/read'
          'Microsoft.App/containerApps/write'
          'Microsoft.Web/sites/read'
          'Microsoft.Web/sites/write'
          'Microsoft.ManagedIdentity/userAssignedIdentities/read'
          'Microsoft.ManagedIdentity/userAssignedIdentities/write'
          'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials/read'
          'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials/write'
          'Microsoft.Insights/diagnosticSettings/read'
          'Microsoft.Insights/diagnosticSettings/write'
          'Microsoft.OperationalInsights/workspaces/read'
          'Microsoft.OperationalInsights/workspaces/write'
          'Microsoft.Authorization/*/read'
        ]
        notActions: []
      }
    ]
  }
}

resource pipelineDeployerAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, 'pipelineDeployerAssignment', identityModule.name)
  properties: {
    roleDefinitionId: pipelineDeployerRole.id
    principalId: identityModule.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

output clientId string = identityModule.outputs.clientId
output principalId string = identityModule.outputs.principalId
output identityId string = identityModule.outputs.identityId
