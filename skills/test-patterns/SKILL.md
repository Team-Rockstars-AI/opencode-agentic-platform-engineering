---
name: test-patterns
description: Guidelines for writing unit and validation tests for infrastructure modules
license: MIT
compatibility: opencode
---

## Infrastructure Testing Guidelines

All infrastructure modules must be tested to ensure syntactical correctness, security compliance, and functional reliability:

### 1. Terraform Testing (`.tftest.hcl`)
Use the modern Terraform 1.6+ testing framework to write unit and integration assertions:
- **Unit Assertions:** Write assertions to verify resource properties, variables, and outputs without deploying actual resources (using `run` blocks with `plan` mode).
- **Integration Tests:** Write tests to deploy resources into a test environment, verify their functionality, and tear them down (using `run` blocks with `apply` mode).
- **Validation Blocks:** Test that variable validation blocks correctly reject invalid inputs (e.g., invalid IP ranges, incorrect naming formats).

*Example:*
```hcl
run "verify_keyvault_properties" {
  command = plan

  assert {
    condition     = azurerm_key_vault.kv.purge_protection_enabled == true
    error_message = "Purge protection must be enabled on Key Vault."
  }

  assert {
    condition     = azurerm_key_vault.kv.public_network_access_enabled == false
    error_message = "Public network access must be disabled on Key Vault."
  }
}
```

### 2. Bicep Testing
Write validation tests for Bicep templates:
- **Bicep Build Validation:** Compile Bicep templates (`bicep build`) to verify syntax and resource schemas.
- **Bicep Linting:** Run Bicep linter to ensure compliance with best practices.
- **What-If Validation:** Run `az deployment sub what-if` to verify the planned changes before deployment.
