param projectName string
param environment string
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
