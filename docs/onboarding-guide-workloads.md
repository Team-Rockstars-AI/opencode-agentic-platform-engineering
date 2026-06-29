# Workload Developer Onboarding Guide

This guide describes how application development teams can securely onboard and deploy their workloads onto the provisioned secure-by-design landing zone.

---

## 1. Requesting a Spoke Subnet

To isolate your application workload from other services, you must request a dedicated **Spoke Subnet** inside the Virtual Network.

### Step 1: Define Subnet Parameters
Coordinate with the platform team to allocate a non-overlapping CIDR block for your subnet.
*   *Example Workloads Subnet:* `10.0.1.0/24`
*   *Example App Gateway Subnet:* `10.0.2.0/24`

### Step 2: Update the Network Baseline Configuration
Add your subnet definition to the `terraform/main.tf` (or `bicep/main.bicep`) file:
```hcl
# Add your subnet to the network baseline module call
module "network_baseline" {
  source = "../modules/terraform/azure-network-baseline/v1"

  project_name        = "sovereign-core"
  environment         = "prod"
  location            = "westeurope"
  vnet_address_space  = ["10.0.0.0/16"]
  
  # Define your application subnet prefix
  workloads_subnet_prefix = "10.0.1.0/24"
}
```

---

## 2. Configuring Private Endpoints for Databases

To comply with the security baseline, application databases (such as Azure SQL, Cosmos DB, or PostgreSQL) must have public network access disabled and use **Private Endpoints**.

### Step 1: Disable Public Access
Ensure public network access is disabled in your database configuration:
```hcl
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "db-myapp-prod"
  resource_group_name    = var.resource_group_name
  location               = var.location
  
  # Disable public access
  public_network_access_enabled = false
}
```

### Step 2: Create the Private Endpoint
Deploy a Private Endpoint to map your database to a private IP inside the `endpoints` subnet:
```hcl
resource "azurerm_private_endpoint" "db_endpoint" {
  name                = "pe-db-myapp-prod"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = module.network_baseline.endpoints_subnet_id

  private_service_connection {
    name                           = "psc-db-myapp-prod"
    private_connection_resource_id = azurerm_postgresql_flexible_server.db.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }
}
```

---

## 3. Integrating Application Logging

All application workloads must stream their stdout/stderr logs and metrics to the centralized **Log Analytics Workspace** for auditing and compliance monitoring.

### Step 1: Retrieve the Log Analytics Workspace ID
Retrieve the Workspace ID exported by the network baseline module:
```hcl
# Reference the workspace ID in your application deployment
log_analytics_workspace_id = module.network_baseline.log_analytics_workspace_id
```

### Step 2: Configure Container App Diagnostics
If deploying onto Azure Container Apps, configure the diagnostic settings to stream logs:
```hcl
resource "azurerm_monitor_diagnostic_setting" "app_logs" {
  name                       = "ds-myapp-prod"
  target_resource_id         = azurerm_container_app.app.id
  log_analytics_workspace_id = module.network_baseline.log_analytics_workspace_id

  enabled_log {
    category = "ContainerAppConsoleLogs"
  }

  metric {
    category = "AllMetrics"
  }
}
```

---

## 4. Setting Up OIDC-Federated Pipelines

To deploy your application without using long-lived client secrets, configure your application's deployment pipeline to use **OIDC Federated Credentials**.

### Step 1: Request a Federated Identity
Ask the platform team to register a User-Assigned Managed Identity for your application and configure federated trust with your application's repository:
```hcl
# Platform team registers federated trust for your app repo
resource "azurerm_federated_identity_credential" "app_pipeline" {
  name                = "fic-myapp-prod-deploy"
  resource_group_name = var.resource_group_name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:your-org/myapp-repo:environment:production"
  parent_id           = azurerm_user_assigned_identity.app_deployer.id
}
```

### Step 2: Configure Your GitHub Actions Workflow
In your application's repository, configure the deployment workflow to authenticate using the federated identity:
```yaml
name: Deploy Application

on:
  push:
    branches: [ main ]

permissions:
  id-token: write # Required for requesting the JWT
  contents: read  # Required for actions/checkout

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Checkout Code
      uses: actions/checkout@v4

    - name: Log in to Azure via OIDC
      uses: azure/login@v2
      with:
        client-id: ${{ secrets.AZURE_CLIENT_ID }}
        tenant-id: ${{ secrets.AZURE_TENANT_ID }}
        subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

    - name: Deploy Workload
      run: |
        echo "Deploying application securely..."
```
