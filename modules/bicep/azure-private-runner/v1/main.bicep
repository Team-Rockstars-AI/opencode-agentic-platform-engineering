@minLength(3)
@maxLength(24)
param projectName string

@allowed([
  'dev'
  'test'
  'staging'
  'prod'
])
param environment string = 'dev'

@minLength(1)
@maxLength(50)
param location string

param subnetRunnersId string

@minLength(1)
@maxLength(39)
param githubOrgName string

@minLength(1)
@maxLength(100)
param githubRepoName string

@description('GitHub fine-grained PAT for runner registration. MUST be scoped to a single repository with admin:org (self-hosted runners) permission. MUST have a maximum 7-day expiration. Prefer GitHub App installation tokens.')
@secure()
param runnerToken string = 'placeholder-pat'
param tags object = {}

@description('The resource ID of the central Log Analytics workspace for diagnostics')
param logAnalyticsWorkspaceId string = ''

// Runner Identity
resource runnerIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-runner-${projectName}-${environment}'
  location: location
  tags: tags
}

// Managed Environment for Container Apps
resource runnerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-runner-${projectName}-${environment}'
  location: location
  properties: {
    infrastructureSubnetId: subnetRunnersId
    vnetConfiguration: {
      internal: true
    }
  }
  tags: tags
}

// Container App Runner with KEDA github-runner scaling
resource runnerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ca-runner-${projectName}-${environment}'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${runnerIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: runnerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: [
        {
          name: 'github-pat'
          value: runnerToken
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'ubuntu-runner'
          image: 'mcr.microsoft.com/dotnet/runtime-deps:6.0-jammy'
          resources: {
            cpu: any('1.0')
            memory: '2.0Gi'
          }
          env: [
            {
              name: 'RUNNER_NAME'
              value: 'ca-runner-instance'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: runnerIdentity.properties.clientId
            }
            {
              name: 'GITHUB_OWNER'
              value: githubOrgName
            }
            {
              name: 'GITHUB_REPOSITORY'
              value: githubRepoName
            }
            {
              name: 'GITHUB_PAT'
              secretRef: 'github-pat'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 5
        rules: [
          {
            name: 'github-queue-scaler'
            custom: {
              type: 'github-runner'
              metadata: {
                owner: githubOrgName
                repos: githubRepoName
                targetWorkflowId: 'deploy.yml'
              }
            }
          }
        ]
      }
    }
  }
  tags: tags
}

// Diagnostic settings for Container App Environment
resource runnerEnvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'ds-cae-${projectName}-${environment}'
  scope: runnerEnv
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
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

// Diagnostic settings for Container App
resource runnerAppDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'ds-ca-${projectName}-${environment}'
  scope: runnerApp
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
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

output runnerIdentityPrincipalId string = runnerIdentity.properties.principalId
output runnerAppId string = runnerApp.id
