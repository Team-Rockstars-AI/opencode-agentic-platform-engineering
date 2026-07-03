// Bicep module test file
param location string = 'westeurope'

// Default invocation
module testRunnerDefault '../main.bicep' = {
  name: 'test-runner-default-deployment'
  params: {
    projectName: 'testproj'
    location: location
    subnetRunnersId: '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.Network/virtualNetworks/vnet-x/subnets/snet-runners'
    githubOrgName: 'acme'
    githubRepoName: 'infra'
  }
}

// Central diagnostics invocation
module testRunnerDiagnostics '../main.bicep' = {
  name: 'test-runner-diagnostics-deployment'
  params: {
    projectName: 'testproj'
    location: location
    subnetRunnersId: '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.Network/virtualNetworks/vnet-x/subnets/snet-runners'
    githubOrgName: 'acme'
    githubRepoName: 'infra'
    maxReplicas: 2
    logAnalyticsWorkspaceId: '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x'
  }
}
