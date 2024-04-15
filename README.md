# BVA2-ML-TRAINER-CLOUD

[![Terraform](https://img.shields.io/badge/Terraform-0090ff?logo=terraform)](https://www.terraform.io/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-3776AB)](https://www.python.org/downloads/release/python-390/)

## Host Machine Installation
1. Clone this repository to the host machine.
2. Execute `setup_host.sh`
   ```bash
   chmod +x ./setup_host.sh && ./setup_host.sh
   ```
3. Login with your azure account
   ```bash
   az login
   ```
4. Copy `id` and `tenantId` and paste them into **terraform/providers.tf** as
   `subscription_id` and `tenant_id` respectively.
5. In **terraform/variables.tf**, You must add your host username. 
   (You can type `whoami` in terminal to see the username)
6. Anyway, You can change the other varibles as you wish, both in 
   `variables.tf` and `main.tf`.

## Usage
1. Copy your training data and pipeline configurations to `workspace/detection`   
   or `workspace/classification`
2. Create virtual machine configuration in `config/vm_config.json`, *for example:*
   
      ```json
      {
         "vm_config": {
            "vm1": {
               "name": "trainer_vm1",
               "size": "your_vm_size",
               "model": "detection",
               "workspace": "detection_training_dataset_1"
            },
            "vm2": {
               "name": "trainer_vm2",
               "size": "your_vm_size",
               "model": "detection",
               "workspace": "detection_training_dataset_2"
            },
            "vm3": {
               "name": "trainer_vm3",
               "size": "your_vm_size",
               "model": "classification",
               "workspace": "classification_training_dataset_1"
            },
            "vm4": {
               "name": "trainer_vm4",
               "size": "your_vm_size",
               "model": "classification",
               "workspace": "classification_training_dataset_2"
            }
         }
      }
      ```
      The pricing table of all vm sizes is provided here: https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/#Linux
   
3. You are all set, Use VMs provisioning through `pipeline.ipynb` via vscode, or terminal:
   ```bash
   python3 -m jupyter notebook pipeline.ipynb
   ```

## Caution
This repository only demonstrates how to use Terraform as a provisioner; some training-image information is classified here.