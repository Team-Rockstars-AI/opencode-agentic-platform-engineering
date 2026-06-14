@description('The name of the project')
@minLength(3)
@maxLength(24)
param projectName string

@description('The deployment environment')
@allowed([
  'dev'
  'test'
  'staging'
  'prod'
])
param environment string

@description('The primary Azure region to deploy to')
@minLength(1)
param location string

resource workspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: 'law-${projectName}-${environment}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output workspaceId string = workspace.id
