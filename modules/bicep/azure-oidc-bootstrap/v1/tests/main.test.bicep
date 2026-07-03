// Bicep module test file (subscription scope, matching ../main.bicep)
targetScope = 'subscription'

param location string = 'westeurope'

// Default invocation (no GitHub federation)
module testOidcDefault '../main.bicep' = {
  name: 'test-oidc-default-deployment'
  params: {
    projectName: 'testproj'
    location: location
  }
}

// GitHub-federated invocation
module testOidcGithub '../main.bicep' = {
  name: 'test-oidc-github-deployment'
  params: {
    projectName: 'testproj'
    location: location
    githubOrgName: 'acme'
    githubRepoName: 'infra'
  }
}
