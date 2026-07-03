# Modern Terraform 1.6+ Test File

# Mocked provider so tests run offline (no Azure credentials in CI).
mock_provider "azurerm" {}

variables {
  project_name          = "testproj"
  location              = "westeurope"
  resource_group_name   = "rg-test-oidc"
  subscription_scope_id = "/subscriptions/00000000-0000-0000-0000-000000000000"
}

run "pipeline_identity_name_derived_from_project" {
  command = plan

  assert {
    condition     = azurerm_user_assigned_identity.pipeline.name == "id-pipeline-testproj-dev"
    error_message = "Pipeline identity name must derive from project name and environment"
  }
}

run "no_federated_credentials_without_github_org" {
  command = plan

  assert {
    condition     = length(azurerm_federated_identity_credential.github_main) == 0
    error_message = "No main-branch federated credential expected without a GitHub org"
  }

  assert {
    condition     = length(azurerm_federated_identity_credential.github_pr) == 0
    error_message = "No PR federated credential expected without a GitHub org"
  }
}

run "federated_credentials_scoped_to_repo_and_branch" {
  command = plan

  variables {
    github_org_name  = "acme"
    github_repo_name = "infra"
  }

  assert {
    condition     = azurerm_federated_identity_credential.github_main[0].subject == "repo:acme/infra:ref:refs/heads/main"
    error_message = "Main federated credential must be scoped to the exact repo and main branch (zero-secrets OIDC)"
  }

  assert {
    condition     = azurerm_federated_identity_credential.github_pr[0].subject == "repo:acme/infra:pull_request"
    error_message = "PR federated credential must be scoped to the exact repo pull_request subject"
  }

  assert {
    condition     = azurerm_federated_identity_credential.github_main[0].issuer == "https://token.actions.githubusercontent.com"
    error_message = "Federated credential issuer must be the GitHub Actions token endpoint"
  }
}
