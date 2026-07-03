// Subscription-scope assignments of built-in Azure Policy definitions that
// back the platform's secure-by-design baseline at runtime (post-deployment).
// Definition GUIDs verified against the Microsoft Learn built-in policy index:
// https://learn.microsoft.com/azure/governance/policy/samples/built-in-policies
targetScope = 'subscription'

@description('The name of the project')
@minLength(3)
@maxLength(24)
param projectName string

@description('The deployment environment (e.g. dev, test, staging, prod)')
param environment string = 'dev'

@description('Azure regions resources may be deployed to (data-residency guardrail)')
@minLength(1)
param allowedLocations array = [
  'westeurope'
  'northeurope'
]

@description('Effect for the parameterisable PaaS policies (storage secure transfer / public access, Key Vault public access / purge protection)')
@allowed([
  'Audit'
  'Deny'
  'Disabled'
])
param policyEffect string = 'Audit'

@description('When false, all assignments are created in DoNotEnforce mode: they evaluate and report compliance but never block deployments')
param enforcementMode bool = true

@description('Assign the built-in deny policy blocking public IPs on network interfaces (the platform NAT Gateway / App Gateway public IPs are standalone resources and unaffected)')
param enableDenyPublicIpNics bool = true

var definitionPrefix = '/providers/Microsoft.Authorization/policyDefinitions'
var enforcementModeValue = enforcementMode ? 'Default' : 'DoNotEnforce'

// Allowed locations (data residency / geo-compliance). Effect is fixed (deny)
// in the built-in definition; it only takes the location list parameter.
resource allowedLocationsAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'pa-locations-${projectName}-${environment}'
  properties: {
    displayName: 'Allowed locations (${projectName})'
    description: 'Restrict resource deployment to approved regions for data-residency compliance.'
    policyDefinitionId: '${definitionPrefix}/e56962a6-4747-49cd-b67b-bf8b01975c4c'
    enforcementMode: enforcementModeValue
    parameters: {
      listOfAllowedLocations: {
        value: allowedLocations
      }
    }
  }
}

// Secure transfer (HTTPS-only) to storage accounts.
resource storageSecureTransferAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'pa-st-https-${projectName}-${environment}'
  properties: {
    displayName: 'Secure transfer to storage accounts (${projectName})'
    description: 'Storage accounts must only accept requests over HTTPS (encryption in transit).'
    policyDefinitionId: '${definitionPrefix}/404c3081-a854-4457-ae30-26a93ef643f9'
    enforcementMode: enforcementModeValue
    parameters: {
      effect: {
        value: policyEffect
      }
    }
  }
}

// Storage accounts should disable public network access (private-endpoint-only posture).
resource storageNoPublicAccessAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'pa-st-nopub-${projectName}-${environment}'
  properties: {
    displayName: 'Storage accounts should disable public network access (${projectName})'
    description: 'Storage accounts must not be exposed to the public internet; access via Private Endpoints only.'
    policyDefinitionId: '${definitionPrefix}/b2982f36-99f2-4db5-8eff-283140c09693'
    enforcementMode: enforcementModeValue
    parameters: {
      effect: {
        value: policyEffect
      }
    }
  }
}

// Azure Key Vault should disable public network access.
resource keyVaultNoPublicAccessAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'pa-kv-nopub-${projectName}-${environment}'
  properties: {
    displayName: 'Key Vault should disable public network access (${projectName})'
    description: 'Key Vaults must not be reachable over the public internet; access via Private Endpoints only.'
    policyDefinitionId: '${definitionPrefix}/405c5871-3e91-4644-8a63-58e19d68ff5b'
    enforcementMode: enforcementModeValue
    parameters: {
      effect: {
        value: policyEffect
      }
    }
  }
}

// Key vaults should have deletion (purge) protection enabled.
resource keyVaultPurgeProtectionAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'pa-kv-purge-${projectName}-${environment}'
  properties: {
    displayName: 'Key Vault deletion protection (${projectName})'
    description: 'Key Vaults must have purge protection enabled — the platform non-negotiable recovery baseline.'
    policyDefinitionId: '${definitionPrefix}/0b60c0b2-2dc2-4e1c-b5c9-abbed971de53'
    enforcementMode: enforcementModeValue
    parameters: {
      effect: {
        value: policyEffect
      }
    }
  }
}

// Network interfaces should not have public IPs. Effect is fixed (deny) in the
// built-in definition and it takes no parameters. Enforces the NAT-Gateway-only
// egress design: workloads never attach public IPs directly.
resource nicNoPublicIpAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = if (enableDenyPublicIpNics) {
  name: 'pa-nic-nopip-${projectName}-${environment}'
  properties: {
    displayName: 'Network interfaces should not have public IPs (${projectName})'
    description: 'Deny public IPs on NICs; all outbound egress flows through the NAT Gateway, inbound through the WAF Application Gateway.'
    policyDefinitionId: '${definitionPrefix}/83a86a26-fd1f-447c-b59d-e51f44264114'
    enforcementMode: enforcementModeValue
  }
}

output allowedLocationsAssignmentId string = allowedLocationsAssignment.id
output storageSecureTransferAssignmentId string = storageSecureTransferAssignment.id
output storageNoPublicAccessAssignmentId string = storageNoPublicAccessAssignment.id
output keyVaultNoPublicAccessAssignmentId string = keyVaultNoPublicAccessAssignment.id
output keyVaultPurgeProtectionAssignmentId string = keyVaultPurgeProtectionAssignment.id
