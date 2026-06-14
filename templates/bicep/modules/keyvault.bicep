param projectName string
param environment string
param location string
param tenantId string
param subnetEndpointsId string
param workspaceId string

resource kv 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: 'kv-${projectName}-${environment}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    enableRbacAuthorization: true
    enabledForDiskEncryption: true
    softDeleteRetentionInDays: 7
    // Secure-by-design baseline constraints
    enablePurgeProtection: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    accessPolicies: []
  }
}

// Private Endpoint for Key Vault
resource kvPe 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: 'pe-kv-${projectName}-${environment}'
  location: location
  properties: {
    subnet: {
      id: subnetEndpointsId
    }
    privateLinkServiceConnections: [
      {
        name: 'psc-kv-${projectName}-${environment}'
        properties: {
          privateLinkServiceId: kv.id
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
}

// Diagnostics setting streaming audits to central Logs
resource kvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'ds-kv-${projectName}-${environment}'
  scope: kv
  properties: {
    workspaceId: workspaceId
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output vaultUri string = kv.properties.vaultUri
output vaultId string = kv.id
