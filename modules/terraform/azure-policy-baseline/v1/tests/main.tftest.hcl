# Modern Terraform 1.6+ Test File

# Mocked provider so tests run offline (no Azure credentials in CI).
mock_provider "azurerm" {}

variables {
  project_name    = "testproj"
  subscription_id = "00000000-0000-0000-0000-000000000000"
}

run "all_six_assignments_created_by_default" {
  command = plan

  assert {
    condition     = length(azurerm_subscription_policy_assignment.nic_no_public_ip) == 1
    error_message = "NIC public-IP deny assignment expected by default"
  }

  assert {
    condition     = azurerm_subscription_policy_assignment.allowed_locations.enforce == true
    error_message = "Assignments must enforce by default"
  }
}

run "allowed_locations_parameter_propagates" {
  command = plan

  variables {
    allowed_locations = ["westeurope", "northeurope", "germanywestcentral"]
  }

  assert {
    condition     = strcontains(azurerm_subscription_policy_assignment.allowed_locations.parameters, "germanywestcentral")
    error_message = "allowed_locations must propagate into the assignment parameters JSON"
  }
}

run "nic_deny_policy_can_be_disabled" {
  command = plan

  variables {
    enable_deny_public_ip_nics = false
  }

  assert {
    condition     = length(azurerm_subscription_policy_assignment.nic_no_public_ip) == 0
    error_message = "NIC public-IP deny assignment must be absent when disabled"
  }
}

run "do_not_enforce_mode" {
  command = plan

  variables {
    enforcement_mode = false
  }

  assert {
    condition     = azurerm_subscription_policy_assignment.allowed_locations.enforce == false
    error_message = "enforcement_mode = false must set DoNotEnforce on the assignments"
  }

  assert {
    condition     = azurerm_subscription_policy_assignment.keyvault_purge_protection.enforce == false
    error_message = "enforcement_mode = false must set DoNotEnforce on all assignments"
  }
}

run "policy_effect_propagates" {
  command = plan

  variables {
    policy_effect = "Deny"
  }

  assert {
    condition     = strcontains(azurerm_subscription_policy_assignment.storage_secure_transfer.parameters, "Deny")
    error_message = "policy_effect must propagate into the parameterisable assignments"
  }
}
