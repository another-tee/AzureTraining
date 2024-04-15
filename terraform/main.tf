# Define resource group
resource "azurerm_resource_group" "production" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

# Create virtual network
resource "azurerm_virtual_network" "production" {
  name                = var.virtual_network_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.production.location
  resource_group_name = azurerm_resource_group.production.name
}

# Create subnet
resource "azurerm_subnet" "production" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.production.name
  virtual_network_name = azurerm_virtual_network.production.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Create public_ip for all vms
resource "azurerm_public_ip" "production" {
  for_each = local.vm_config
  name                = "${each.value.name}-public-ip"
  location            = azurerm_resource_group.production.location
  resource_group_name = azurerm_resource_group.production.name
  allocation_method   = "Dynamic"
}

# Create network interface for all vms
resource "azurerm_network_interface" "production" {
  for_each = local.vm_config
  name                = "${each.value.name}-nic"
  location            = azurerm_resource_group.production.location
  resource_group_name = azurerm_resource_group.production.name

  ip_configuration {
    name                          = "internal_nic_configuration"
    subnet_id                     = azurerm_subnet.production.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.production[each.key].id
  }
}

# Create linux VM(s)
resource "azurerm_linux_virtual_machine" "production" {
  for_each = local.vm_config
  name                  = each.value.name
  location              = azurerm_resource_group.production.location
  resource_group_name   = azurerm_resource_group.production.name
  network_interface_ids = [azurerm_network_interface.production[each.key].id]
  size                  = each.value.size
  computer_name         = var.username
  admin_username        = var.username
  admin_password        = var.password

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_disk {
    name                 = "${each.value.name}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }
  
  disable_password_authentication = false
  
  connection {
      host      = self.public_ip_address
      user      = var.username
      password  = var.password
      type      = "ssh"
      agent     = false
    }
  
  provisioner "file" {
    source      = "/home/${data.external.get_username.result["user"]}/.ssh/id_rsa"
    destination = "/home/${var.username}/.ssh/id_rsa"
  }
  provisioner "file" {
    source      = "/home/${data.external.get_username.result["user"]}/.ssh/known_hosts"
    destination = "/home/${var.username}/.ssh/known_hosts"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod 600 /home/${var.username}/.ssh/id_rsa",
      "chmod 644 /home/${var.username}/.ssh/known_hosts",
      "git clone git@bitbucket.org:${var.repository}"
    ]
  }
}

# Provisioner to execute the shell script on the instances
resource "azurerm_virtual_machine_extension" "production" {
  for_each = local.vm_config
  name                 = var.username
  virtual_machine_id   = azurerm_linux_virtual_machine.production[each.key].id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"
  protected_settings =  <<PROT
    {
        "script": "${base64encode(file("../setup/ubuntu_setup.sh"))}"
    }
    PROT
  timeouts {
    create = "1h30m"
    delete = "1h30m"
    update = "1h30m"
  }
}