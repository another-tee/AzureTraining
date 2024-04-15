output "vm_public_ips" {
  value = {
    for idx, vm in azurerm_linux_virtual_machine.production : idx => azurerm_linux_virtual_machine.production[idx].public_ip_address
  }
}