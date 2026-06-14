param projectName string
param environment string = 'dev'
param location string
param isEnterprise bool = false
param vnetAddressSpace string = '10.0.0.0/16'
param subnetWorkloadsPrefix string = '10.0.1.0/24'
param subnetAppgwPrefix string = '10.0.2.0/24'
param subnetEndpointsPrefix string = '10.0.3.0/24'
param subnetRunnersPrefix string = '10.0.4.0/24'
param tags object = {}

@description('The Key Vault Secret ID of the SSL certificate for HTTPS')
param sslCertificateKeyVaultSecretId string = ''

// Public IP for outbound NAT Gateway
resource natPip 'Microsoft.Network/publicIPAddresses@2021-08-01' = {
  name: 'pip-nat-${projectName}-${environment}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  tags: tags
}

// NAT Gateway
resource natGateway 'Microsoft.Network/natGateways@2021-08-01' = {
  name: 'nat-${projectName}-${environment}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    idleTimeoutInMinutes: 4
    publicIpAddresses: [
      {
        id: natPip.id
      }
    ]
  }
  tags: tags
}

// Network Security Groups
resource workloadsNsg 'Microsoft.Network/networkSecurityGroups@2021-08-01' = {
  name: 'nsg-workloads-${projectName}-${environment}'
  location: location
  properties: {
    securityRules: []
  }
  tags: tags
}

resource appgwNsg 'Microsoft.Network/networkSecurityGroups@2021-08-01' = {
  name: 'nsg-appgw-${projectName}-${environment}'
  location: location
  properties: {
    securityRules: []
  }
  tags: tags
}

resource endpointsNsg 'Microsoft.Network/networkSecurityGroups@2021-08-01' = {
  name: 'nsg-endpoints-${projectName}-${environment}'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowWorkloadsToEndpoints'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: subnetWorkloadsPrefix
          destinationAddressPrefix: subnetEndpointsPrefix
        }
      }
    ]
  }
  tags: tags
}

resource runnersNsg 'Microsoft.Network/networkSecurityGroups@2021-08-01' = if (isEnterprise) {
  name: 'nsg-runners-${projectName}-${environment}'
  location: location
  properties: {
    securityRules: []
  }
  tags: tags
}

// Virtual Network with subnets associated with NAT Gateway and Network Security Groups
resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' = {
  name: 'vnet-${projectName}-${environment}-${location}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressSpace
      ]
    }
    subnets: [
      {
        name: 'snet-workloads'
        properties: {
          addressPrefix: subnetWorkloadsPrefix
          natGateway: {
            id: natGateway.id
          }
          networkSecurityGroup: {
            id: workloadsNsg.id
          }
        }
      }
      {
        name: 'snet-appgw'
        properties: {
          addressPrefix: subnetAppgwPrefix
          networkSecurityGroup: {
            id: appgwNsg.id
          }
        }
      }
      {
        name: 'snet-endpoints'
        properties: {
          addressPrefix: subnetEndpointsPrefix
          networkSecurityGroup: {
            id: endpointsNsg.id
          }
        }
      }
      // Only include runner subnet configuration if enterprise is true.
      // Bicep does not support conditional subnets inside the main subnets block as easily,
      // so we use a subnets array built dynamically.
    ]
  }
  tags: tags
}

// Separate deployment for runners subnet if enterprise to enable delegating properly and associate NSG
resource runnersSubnet 'Microsoft.Network/virtualNetworks/subnets@2021-08-01' = if (isEnterprise) {
  name: 'snet-runners'
  parent: vnet
  properties: {
    addressPrefix: subnetRunnersPrefix
    natGateway: {
      id: natGateway.id
    }
    networkSecurityGroup: {
      id: runnersNsg.id
    }
    delegations: [
      {
        name: 'aca-delegation'
        properties: {
          serviceName: 'Microsoft.App/environments'
        }
      }
    ]
  }
}

// Public IP for Inbound App Gateway
resource appgwPip 'Microsoft.Network/publicIPAddresses@2021-08-01' = {
  name: 'pip-appgw-${projectName}-${environment}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  tags: tags
}

// Application Gateway with WAF v2
resource appGateway 'Microsoft.Network/applicationGateways@2021-08-01' = {
  name: 'agw-${projectName}-${environment}'
  location: location
  properties: {
    sku: {
      name: 'WAF_v2'
      tier: 'WAF_v2'
      capacity: 1
    }
    gatewayIPConfigurations: [
      {
        name: 'appgw-ip-config'
        properties: {
          subnet: {
            id: '${vnet.id}/subnets/snet-appgw'
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appgw-frontend-ip'
        properties: {
          publicIPAddress: {
            id: appgwPip.id
          }
        }
      }
    ]
    frontendPorts: concat([
      {
        name: 'port_80'
        properties: {
          port: 80
        }
      }
    ], !empty(sslCertificateKeyVaultSecretId) ? [
      {
        name: 'port_443'
        properties: {
          port: 443
        }
      }
    ] : [])
    sslCertificates: !empty(sslCertificateKeyVaultSecretId) ? [
      {
        name: '${projectName}-ssl'
        properties: {
          keyVaultSecretId: sslCertificateKeyVaultSecretId
        }
      }
    ] : []
    backendAddressPools: [
      {
        name: 'appgw-backend-pool'
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'appgw-http-settings'
        properties: {
          port: 80
          protocol: 'Http'
          cookieBasedAffinity: 'Disabled'
          requestTimeout: 60
        }
      }
    ]
    httpListeners: concat([
      {
        name: 'appgw-listener'
        properties: {
          frontendIPConfiguration: {
            id: '${vnet.id}/frontendIPConfigurations/appgw-frontend-ip'
          }
          frontendPort: {
            id: '${vnet.id}/frontendPorts/port_80'
          }
          protocol: 'Http'
        }
      }
    ], !empty(sslCertificateKeyVaultSecretId) ? [
      {
        name: 'appgw-listener-https'
        properties: {
          frontendIPConfiguration: {
            id: '${vnet.id}/frontendIPConfigurations/appgw-frontend-ip'
          }
          frontendPort: {
            id: '${vnet.id}/frontendPorts/port_443'
          }
          protocol: 'Https'
          sslCertificate: {
            id: '${vnet.id}/sslCertificates/${projectName}-ssl'
          }
        }
      }
    ] : [])
    requestRoutingRules: concat([
      {
        name: 'appgw-routing-rule'
        properties: {
          ruleType: 'Basic'
          httpListener: {
            id: '${vnet.id}/httpListeners/appgw-listener'
          }
          backendAddressPool: {
            id: '${vnet.id}/backendAddressPools/appgw-backend-pool'
          }
          backendHttpSettings: {
            id: '${vnet.id}/backendHttpSettingsCollection/appgw-http-settings'
          }
          priority: 100
        }
      }
    ], !empty(sslCertificateKeyVaultSecretId) ? [
      {
        name: 'appgw-routing-rule-https'
        properties: {
          ruleType: 'Basic'
          httpListener: {
            id: '${vnet.id}/httpListeners/appgw-listener-https'
          }
          backendAddressPool: {
            id: '${vnet.id}/backendAddressPools/appgw-backend-pool'
          }
          backendHttpSettings: {
            id: '${vnet.id}/backendHttpSettingsCollection/appgw-http-settings'
          }
          priority: 110
        }
      }
    ] : [])
    webApplicationFirewallConfiguration: {
      enabled: true
      firewallMode: 'Prevention'
      ruleSetType: 'OWASP'
      ruleSetVersion: '3.2'
    }
  }
  tags: tags
}

output vnetId string = vnet.id
output vnetName string = vnet.name
output subnetWorkloadsId string = '${vnet.id}/subnets/snet-workloads'
output subnetAppgwId string = '${vnet.id}/subnets/snet-appgw'
output subnetEndpointsId string = '${vnet.id}/subnets/snet-endpoints'
output subnetRunnersId string = isEnterprise ? runnersSubnet.id : ''
output natPublicIp string = natPip.properties.ipAddress
output appgwPublicIp string = appgwPip.properties.ipAddress
