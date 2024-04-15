#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker Engine ..."
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # Install the Docker packages.
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Make docker is not require sudo.
    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker
    sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
    sudo chmod g+rwx "$HOME/.docker" -R
    sudo chmod 666 /var/run/docker.sock

    # Start on boot
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
fi

# Make GPUs available on docker if Nvidia GPU is present
if command -v nvidia-smi &> /dev/null; then
    echo "Installing Nvidia Container Toolkit ..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
    && \
        sudo apt-get update

    # Install the Nvidia Container Toolkit
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
fi

# Build docker image
if [[ "$(docker images -q bva2-ml-trainer 2> /dev/null)" == "" ]]; then
    cd /home/your_vm_username/your_repo && docker build -f dockerfiles/tf2/Dockerfile -t your_container_images:your_container_tag .
fi

# Run training container and expose port 8888 (EXPOSE 8888 in my dockerfile) for Jupyter
docker run \
    --name trainer \
    --rm \
    --detach \
    -p 8888:8888 \
    -e JUPYTER_TOKEN='your_jupyter_password_token' \
    -v /home/your_vm_username/your_repo:/your_workspace_in_container \
    your_container_images:your_container_tag \
    jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root