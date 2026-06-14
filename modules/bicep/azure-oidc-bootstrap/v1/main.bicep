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

// Sub-level assignments (Executed at subscription scope)
resource contributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, 'Contributor', identityModule.name)
  scope: subscription()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c') // Contributor
    principalId: identityModule.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

resource userAccessAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, 'UserAccessAdmin', identityModule.name)
  scope: subscription()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9') // User Access Administrator
    principalId: identityModule.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

output clientId string = identityModule.outputs.clientId
output principalId string = identityModule.outputs.principalId
output identityId string = identityModule.outputs.identityId
