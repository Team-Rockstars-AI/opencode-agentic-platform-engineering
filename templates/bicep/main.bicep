targetScope = 'subscription'

@description('The name of the project')
@minLength(3)
@maxLength(24)
param projectName string = '{{project_name}}'

@description('The primary Azure region to deploy to')
@minLength(1)
param location string = '{{azure_location}}'

@description('The deployment environment')
@allowed([
  'dev'
  'test'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('The Azure active directory tenant ID')
param tenantId string = '{{tenant_id}}'

@description('The governance tier to deploy')
@allowed([
  'basic'
  'enterprise'
  '{{governance_tier}}'
])
param governanceTier string = '{{governance_tier}}'

@description('The GitHub Organization or Username')
param githubOrgName string = '{{github_org_name}}'

@description('The GitHub Repository Name')
param githubRepoName string = '{{github_repo_name}}'
@description('GitHub fine-grained PAT or GitHub App installation token for runner registration. MUST be scoped to a single repository with admin:org (self-hosted runners) permission. MUST have a maximum 7-day expiration. Prefer GitHub App installation tokens for automated rotation and security.')
@secure()
param runnerToken string = 'placeholder-pat'

@description('Assign the subscription-scope Azure Policy baseline (runtime enforcement of the secure-by-design controls)')
param enablePolicyBaseline bool = true

@description('Azure regions resources may be deployed to (data-residency guardrail). Empty array defaults to the platform primary location.')
param policyAllowedLocations array = []

@description('Effect for the parameterisable baseline policies: Audit reports violations, Deny blocks them. Applies to the whole subscription.')
@allowed([
  'Audit'
  'Deny'
  'Disabled'
])
param policyEffect string = 'Audit'

@description('When false, baseline policy assignments are created in DoNotEnforce mode (evaluate and report only)')
param policyEnforcementMode bool = true

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
    logAnalyticsWorkspaceId: logging.outputs.workspaceId
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
    logAnalyticsWorkspaceId: logging.outputs.workspaceId
  }
}

// Subscription-scope Azure Policy baseline — runtime enforcement of the
// secure-by-design controls (data residency, PaaS public-access lockdown,
// Key Vault purge protection, NAT-only egress). Assignments default to
// Audit effect; raise policyEffect to 'Deny' once the subscription is clean.
module policyBaseline '../../modules/bicep/azure-policy-baseline/v1/main.bicep' = if (enablePolicyBaseline) {
  name: 'policy-baseline-deployment'
  params: {
    projectName: projectName
    environment: environment
    allowedLocations: empty(policyAllowedLocations) ? [location] : policyAllowedLocations
    policyEffect: policyEffect
    enforcementMode: policyEnforcementMode
  }
}

output resourceGroupName string = rg.name
output logAnalyticsWorkspaceId string = logging.outputs.workspaceId
output keyVaultUri string = secrets.outputs.vaultUri
output appgwPublicIp string = network.outputs.appgwPublicIp
output natPublicIp string = network.outputs.natPublicIp
