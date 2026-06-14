resource "azurerm_user_assigned_identity" "runner" {
  name                = "id-runner-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_container_app_environment" "runner_env" {
  name                           = "cae-runner-${var.project_name}-${var.environment}"
  location                       = var.location
  resource_group_name            = var.resource_group_name
  infrastructure_subnet_id       = var.subnet_runners_id
  internal_load_balancer_enabled = true
  tags                           = var.tags
}

resource "azurerm_container_app" "runner_app" {
  name                         = "ca-runner-${var.project_name}-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.runner_env.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.runner.id]
  }

  template {
    container {
      name   = "ubuntu-runner"
      image  = "mcr.microsoft.com/dotnet/runtime-deps:6.0-jammy" # jammy is highly compatible LTS base
      cpu    = "1.0"
      memory = "2.0Gi"

      env {
        name  = "RUNNER_NAME"
        value = "ca-runner-instance"
      }

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.runner.client_id
      }

      # If GitHub selected
      env {
        name  = "GITHUB_OWNER"
        value = var.github_org_name
      }

      env {
        name  = "GITHUB_REPOSITORY"
        value = var.github_repo_name
      }

      # We can dynamically pass token via secret reference
      env {
        name        = "GITHUB_PAT"
        secret_name = "github-pat"
      }
    }

    # Scale rule KEDA github-runner scaler (Enterprise scale-to-zero)
    min_replicas = 0
    max_replicas = 5

    # Conditional or dummy KEDA rule representing scale-to-zero queue monitoring
    custom_scale_rule {
      name             = "github-queue-scaler"
      custom_rule_type = "github-runner"
      metadata = {
        owner             = var.github_org_name
        repos             = var.github_repo_name
        targetWorkflowId  = "deploy.yml"
      }
    }
  }

  secret {
    name  = "github-pat"
    value = var.runner_token
  }
}

resource "azurerm_monitor_diagnostic_setting" "runner_env" {
  count                      = var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "ds-cae-${var.project_name}-${var.environment}"
  target_resource_id         = azurerm_container_app_environment.runner_env.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "runner_app" {
  count                      = var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "ds-ca-${var.project_name}-${var.environment}"
  target_resource_id         = azurerm_container_app.runner_app.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  metric {
    category = "AllMetrics"
  }
}
