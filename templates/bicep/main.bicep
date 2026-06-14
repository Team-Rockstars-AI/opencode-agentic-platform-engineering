targetScope = 'subscription'

param projectName string = '{{project_name}}'
param location string = '{{azure_location}}'
param environment string = 'dev'
param tenantId string = '{{tenant_id}}'
param governanceTier string = '{{governance_tier}}'
param githubOrgName string = '{{github_org_name}}'
param githubRepoName string = '{{github_repo_name}}'
@secure()
param runnerToken string = 'placeholder-pat'

// Core resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${projectName}-${environment}-${location}'
  location: location
  tags: {
    Environment: environment
    ManagedBy: 'OpenCode-Platform-Engineer'
    Project: projectName
    GovernanceTier: governanceTier
  }
}

// Network Baseline Deployment
module network '../../modules/bicep/azure-network-baseline/v1/main.bicep' = {
  name: 'network-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
    isEnterprise: (governanceTier == 'enterprise')
    tags: rg.tags
  }
}

// Subdeployments
module logging 'modules/logging.bicep' = {
  name: 'logging-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
  }
}

module secrets 'modules/keyvault.bicep' = {
  name: 'secrets-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
    tenantId: tenantId
    subnetEndpointsId: network.outputs.subnetEndpointsId
    workspaceId: logging.outputs.workspaceId
  }
}

// Private Scale-To-Zero Runner (Enterprise Tier Only)
module runners '../../modules/bicep/azure-private-runner/v1/main.bicep' = if (governanceTier == 'enterprise') {
  name: 'runners-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
    subnetRunnersId: network.outputs.subnetRunnersId
    githubOrgName: githubOrgName
    githubRepoName: githubRepoName
    runnerToken: runnerToken
    tags: rg.tags
  }
}

output resourceGroupName string = rg.name
output logAnalyticsWorkspaceId string = logging.outputs.workspaceId
output keyVaultUri string = secrets.outputs.vaultUri
output appgwPublicIp string = network.outputs.appgwPublicIp
output natPublicIp string = network.outputs.natPublicIp
