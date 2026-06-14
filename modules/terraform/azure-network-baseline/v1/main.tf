resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-${var.project_name}-${var.environment}-${var.location}"
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = [var.vnet_address_space]
  tags                = var.tags
}

# Subnets
resource "azurerm_subnet" "workloads" {
  name                 = "snet-workloads"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_workloads_prefix]
}

resource "azurerm_subnet" "appgw" {
  name                 = "snet-appgw"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_appgw_prefix]
}

resource "azurerm_subnet" "endpoints" {
  name                 = "snet-endpoints"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_endpoints_prefix]
}

resource "azurerm_subnet" "runners" {
  count                = var.is_enterprise ? 1 : 0
  name                 = "snet-runners"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_runners_prefix]

  # Delegations required for Azure Container Apps
  delegation {
    name = "aca-delegation"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetwork/action"]
    }
  }
}

# Network Security Groups
resource "azurerm_network_security_group" "workloads" {
  name                = "nsg-workloads-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_network_security_group" "appgw" {
  name                = "nsg-appgw-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_network_security_group" "endpoints" {
  name                = "nsg-endpoints-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  security_rule {
    name                       = "AllowWorkloadsToEndpoints"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = var.subnet_workloads_prefix
    destination_address_prefix = var.subnet_endpoints_prefix
  }
}

resource "azurerm_network_security_group" "runners" {
  count               = var.is_enterprise ? 1 : 0
  name                = "nsg-runners-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Network Security Group Associations
resource "azurerm_subnet_network_security_group_association" "workloads" {
  subnet_id                 = azurerm_subnet.workloads.id
  network_security_group_id = azurerm_network_security_group.workloads.id
}

resource "azurerm_subnet_network_security_group_association" "appgw" {
  subnet_id                 = azurerm_subnet.appgw.id
  network_security_group_id = azurerm_network_security_group.appgw.id
}

resource "azurerm_subnet_network_security_group_association" "endpoints" {
  subnet_id                 = azurerm_subnet.endpoints.id
  network_security_group_id = azurerm_network_security_group.endpoints.id
}

resource "azurerm_subnet_network_security_group_association" "runners" {
  count                     = var.is_enterprise ? 1 : 0
  subnet_id                 = azurerm_subnet.runners[0].id
  network_security_group_id = azurerm_network_security_group.runners[0].id
}

# NAT Gateway for Outbound Egress
resource "azurerm_public_ip" "nat_pip" {
  name                = "pip-nat-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_nat_gateway" "nat" {
  name                    = "nat-${var.project_name}-${var.environment}"
  location                = var.location
  resource_group_name     = var.resource_group_name
  sku_name                = "Standard"
  idle_timeout_in_minutes = 4
  tags                    = var.tags
}

resource "azurerm_nat_gateway_public_ip_association" "nat_assoc" {
  nat_gateway_id       = azurerm_nat_gateway.nat.id
  public_ip_address_id = azurerm_public_ip.nat_pip.id
}

# Subnet NAT Associations
resource "azurerm_subnet_nat_gateway_association" "workloads_nat" {
  subnet_id      = azurerm_subnet.workloads.id
  nat_gateway_id = azurerm_nat_gateway.nat.id
}

resource "azurerm_subnet_nat_gateway_association" "runners_nat" {
  count          = var.is_enterprise ? 1 : 0
  subnet_id      = azurerm_subnet.runners[0].id
  nat_gateway_id = azurerm_nat_gateway.nat.id
}

# Application Gateway with WAF v2
resource "azurerm_public_ip" "appgw_pip" {
  name                = "pip-appgw-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

locals {
  backend_address_pool_name      = "${azurerm_virtual_network.vnet.name}-beap"
  frontend_port_name             = "${azurerm_virtual_network.vnet.name}-feport"
  frontend_ip_configuration_name = "${azurerm_virtual_network.vnet.name}-feip"
  http_setting_name              = "${azurerm_virtual_network.vnet.name}-be-htst"
  listener_name                  = "${azurerm_virtual_network.vnet.name}-httplstn"
  request_routing_rule_name      = "${azurerm_virtual_network.vnet.name}-rtrt"
  redirect_configuration_name    = "${azurerm_virtual_network.vnet.name}-rdrcfg"
}

resource "azurerm_application_gateway" "app_gateway" {
  name                = "agw-${var.project_name}-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 1
  }

  gateway_ip_configuration {
    name      = "my-gateway-ip-configuration"
    subnet_id = azurerm_subnet.appgw.id
  }

  frontend_port {
    name = local.frontend_port_name
    port = 80
  }

  dynamic "frontend_port" {
    for_each = var.ssl_certificate_key_vault_secret_id != null ? [1] : []
    content {
      name = "${local.frontend_port_name}-https"
      port = 443
    }
  }

  frontend_ip_configuration {
    name                 = local.frontend_ip_configuration_name
    public_ip_address_id = azurerm_public_ip.appgw_pip.id
  }

  backend_address_pool {
    name = local.backend_address_pool_name
  }

  backend_http_settings {
    name                  = local.http_setting_name
    cookie_based_affinity = "Disabled"
    path                  = "/"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }

  http_listener {
    name                           = local.listener_name
    frontend_ip_configuration_name = local.frontend_ip_configuration_name
    frontend_port_name             = local.frontend_port_name
    protocol                       = "Http"
  }

  dynamic "http_listener" {
    for_each = var.ssl_certificate_key_vault_secret_id != null ? [1] : []
    content {
      name                           = "${local.listener_name}-https"
      frontend_ip_configuration_name = local.frontend_ip_configuration_name
      frontend_port_name             = "${local.frontend_port_name}-https"
      protocol                       = "Https"
      ssl_certificate_name           = "${var.project_name}-ssl"
    }
  }

  dynamic "ssl_certificate" {
    for_each = var.ssl_certificate_key_vault_secret_id != null ? [1] : []
    content {
      name                = "${var.project_name}-ssl"
      key_vault_secret_id = var.ssl_certificate_key_vault_secret_id
    }
  }

  request_routing_rule {
    name                       = local.request_routing_rule_name
    rule_type                  = "Basic"
    http_listener_name         = local.listener_name
    backend_address_pool_name  = local.backend_address_pool_name
    backend_http_settings_name = local.http_setting_name
    priority                   = 100
  }

  dynamic "request_routing_rule" {
    for_each = var.ssl_certificate_key_vault_secret_id != null ? [1] : []
    content {
      name                       = "${local.request_routing_rule_name}-https"
      rule_type                  = "Basic"
      http_listener_name         = "${local.listener_name}-https"
      backend_address_pool_name  = local.backend_address_pool_name
      backend_http_settings_name = local.http_setting_name
      priority                   = 110
    }
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
}
