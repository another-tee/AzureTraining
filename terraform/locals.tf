# Read the VMs config
locals {
  json_data = jsondecode(file("../config/vm_config.json"))
  vm_config = { for k, v in local.json_data.vm_config : k => v }
}