# Disaster Recovery & State Reconstruction Runbook

This runbook provides step-by-step instructions for recovering from catastrophic failures, state corruption, or accidental resource deletions within your landing zone.

---

## 1. Scenario A: Corrupted or Locked Terraform State

If a deployment pipeline is interrupted, the Terraform remote state file may become locked or corrupted, blocking subsequent deployments.

### Step 1: Identify the Lock ID
If the state is locked, Terraform will output an error containing a **Lock Info ID** (a UUID).
```text
Error: Error acquiring the state lock
Lock Info:
  ID:        a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d
  Path:      sovereign-core-prod.tfstate
  Who:       niels@host
```

### Step 2: Force-Unlock the State
If you have verified that no other pipeline or operator is actively deploying, force-unlock the state using the Lock ID:
```bash
cd terraform/
terraform init -backend-config="path/to/backend.tfvars"
terraform force-unlock a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d
```

### Step 3: Recover from State Corruption
If the state file is corrupted, retrieve the last known good backup from the Azure Blob Storage backend (which has versioning enabled by default):
1.  Log in to the Azure Portal or use the Azure CLI.
2.  Navigate to the Storage Account hosting your Terraform state.
3.  Go to the state container, locate your `.tfstate` file, and view its **Version History**.
4.  Promote the last known good version to be the active blob.

---

## 2. Scenario B: Accidental Key Vault Secret/Key Deletion

Because Key Vaults are deployed with **Purge Protection** and a **90-day Soft-Delete window** enabled by default, deleted secrets are not permanently lost and can be recovered.

### Step 1: List Deleted Secrets
List all soft-deleted secrets in the Key Vault to find the name of the deleted secret:
```bash
az keyvault secret list-deleted \
  --vault-name "kv-sovereign-core-prod" \
  --query "[].{name:name, deletedDate:properties.deletedDate}" \
  --output table
```

### Step 2: Recover the Deleted Secret
Recover the soft-deleted secret to restore its active status:
```bash
az keyvault secret recover \
  --vault-name "kv-sovereign-core-prod" \
  --name "ssl-certificate-secret"
```

### Step 3: Recover Deleted Keys or Certificates
Use the equivalent commands to recover deleted cryptographic keys or SSL certificates:
```bash
# Recover a deleted key
az keyvault key recover --vault-name "kv-sovereign-core-prod" --name "encryption-key"

# Recover a deleted certificate
az keyvault certificate recover --vault-name "kv-sovereign-core-prod" --name "appgw-ssl-cert"
```

---

## 3. Scenario C: Reconstructing the Landing Zone (Cold Disaster)

In a catastrophic "cold disaster" scenario where an entire Azure region or resource group is lost, follow these steps to reconstruct the landing zone from scratch.

### Step 1: Re-deploy the OIDC Bootstrap Module
Before the deployment pipeline can run, you must manually bootstrap the OIDC federated credentials to allow GitHub/Azure DevOps to authenticate:
```bash
cd terraform/azure-oidc-bootstrap/v1/
# OR cd bicep/azure-oidc-bootstrap/v1/

# Initialize and apply the bootstrap module locally
terraform init
terraform apply -var-file="bootstrap.tfvars"
```
*Note: This creates the custom least-privilege deployer role and registers the federated trust with your repository.*

### Step 2: Re-create the Remote State Storage Account
If the storage account hosting your Terraform state was lost, re-create it using the bootstrap outputs:
```bash
# Retrieve the storage account name from bootstrap outputs
terraform output state_storage_account_name
```

### Step 3: Trigger the Deployment Pipeline
Once bootstrapping is complete, trigger the deployment pipeline to reconstruct the entire landing zone:
1.  Go to your GitHub repository ➔ **Actions** (or Azure DevOps ➔ **Pipelines**).
2.  Select the **Deploy Landing Zone** workflow.
3.  Click **Run workflow** and select the `main` branch.
4.  The pipeline will automatically:
    *   Authenticate via passwordless OIDC.
    *   Re-create the Virtual Network, subnets, and NSGs.
    *   Re-create the Application Gateway and NAT Gateway.
    *   Re-create the Key Vault and Private Endpoints.
    *   Re-deploy the scale-to-zero self-hosted runner pools.
