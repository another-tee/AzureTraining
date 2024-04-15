#!/bin/bash

# Create workspace folders
init_dirs=("workspace/classification" "workspace/detection" "config")
for dir in "${init_dirs[@]}"; do
    full_path="$(pwd)/$dir"
    if [ ! -d "$full_path" ]; then
        mkdir -p "$full_path"
    fi
done

# Create vm_config.json
vm_config_path="config/vm_config.json"
if [ ! -f "$vm_config_path" ]; then
    touch "$vm_config_path"
fi

# Install azure cli
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install PIP Dependencies
sudo apt install -y python3-pip
python3 -m pip install paramiko tqdm requests jupyter notebook

# Install Terraform
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor | \
    sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
gpg --no-default-keyring \
    --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    --fingerprint
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt-get install terraform

# Create and run automate download services
echo "[Unit]
Description=Start automate finish the training job for bva2-ml-trainer

[Service]
User=$USER
ExecStart=/bin/bash -c 'python3 $PWD/scripts/cron_finish.py'

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/bva2-ml-trainer-automate-finish.service > /dev/null

echo "[Unit]
Description=Run bva2-ml-trainer-automate-finish.service every 5 minutes

[Timer]
OnCalendar=*-*-* *:00/05:00
Persistent=true

[Install]
WantedBy=timers.target" | sudo tee /etc/systemd/system/bva2-ml-trainer-automate-finish.timer > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable --now bva2-ml-trainer-automate-finish.timer