# Subscription-scope Azure Policy baseline — runtime enforcement of the
# secure-by-design controls (data residency, PaaS public-access lockdown,
# Key Vault purge protection, NAT-only egress). Assignments default to
# Audit effect; raise policy_effect to "Deny" once the subscription is clean.
module "policy_baseline" {
  count             = var.enable_policy_baseline ? 1 : 0
  source            = "../../modules/terraform/azure-policy-baseline/v1"
  project_name      = var.project_name
  environment       = var.environment
  subscription_id   = var.subscription_id
  allowed_locations = length(var.policy_allowed_locations) > 0 ? var.policy_allowed_locations : [var.location]
  policy_effect     = var.policy_effect
  enforcement_mode  = var.policy_enforcement_mode
}
