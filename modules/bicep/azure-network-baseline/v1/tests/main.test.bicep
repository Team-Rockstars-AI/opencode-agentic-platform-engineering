// Bicep module test file
param location string = 'westeurope'

// Default (basic tier) invocation
module testNetworkBasic '../main.bicep' = {
  name: 'test-network-basic-deployment'
  params: {
    projectName: 'testproj'
    location: location
  }
}

// Enterprise tier with central diagnostics
module testNetworkEnterprise '../main.bicep' = {
  name: 'test-network-enterprise-deployment'
  params: {
    projectName: 'testproj'
    location: location
    isEnterprise: true
    logAnalyticsWorkspaceId: '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x'
  }
}
