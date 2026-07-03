// Bicep module test file (subscription scope, matching ../main.bicep)
targetScope = 'subscription'

// Default invocation (Audit effect, enforced)
module testPolicyDefault '../main.bicep' = {
  name: 'test-policy-default-deployment'
  params: {
    projectName: 'testproj'
  }
}

// Report-only invocation with custom locations and NIC deny disabled
module testPolicyReportOnly '../main.bicep' = {
  name: 'test-policy-reportonly-deployment'
  params: {
    projectName: 'testproj'
    environment: 'prod'
    allowedLocations: [
      'westeurope'
      'northeurope'
      'germanywestcentral'
    ]
    policyEffect: 'Deny'
    enforcementMode: false
    enableDenyPublicIpNics: false
  }
}
