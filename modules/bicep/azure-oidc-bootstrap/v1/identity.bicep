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
param githubOrgName string
param githubRepoName string
param tags object

resource pipelineIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-pipeline-${projectName}-${environment}'
  location: location
  tags: tags
}

resource githubMainFed 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = if (!empty(githubOrgName)) {
  name: 'fed-github-main'
  parent: pipelineIdentity
  properties: {
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubOrgName}/${githubRepoName}:ref:refs/heads/main'
  }
}

resource githubPrFed 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = if (!empty(githubOrgName)) {
  name: 'fed-github-pr'
  parent: pipelineIdentity
  properties: {
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubOrgName}/${githubRepoName}:pull_request'
  }
}

output clientId string = pipelineIdentity.properties.clientId
output principalId string = pipelineIdentity.properties.principalId
output identityId string = pipelineIdentity.id
