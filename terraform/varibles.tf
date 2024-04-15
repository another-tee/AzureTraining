variable "resource_group_location" {
  type        = string
  default     = "southeastasia"
  description = "Location of the resource group."
}

variable "resource_group_name" {
  type        = string
  default     = "your_resource_group_name"
  description = "The resource group name."
}

variable "virtual_network_name" {
  type        = string
  default     = "your_vnet_name"
  description = "The virtual network name of the resource group."
}

variable "subnet_name" {
  type        = string
  default     = "your_subnet_name"
  description = "The subnet name."
}

variable "username" {
  type        = string
  description = "The username for the new VM."
  default     = "your_vm_username"
}

variable "password" {
  type        = string
  description = "The password for the new VM."
  default     = "your_vm_password"
}

variable "repository" {
  type        = string
  description = "The repository path to provision to the new VM."
  default     = "your_repo_dir/your_repo.git"
}