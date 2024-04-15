# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import os
import sys
import yaml
import json
import logging
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from utils.sftp_utils import SFTP
from utils.line_utils import send_line_message
from utils.json_utils import combine_configs, read_json

# --------------------------------------------------------------------------- #
#                         Assign Arguments/Variables                          #
# --------------------------------------------------------------------------- #
VM_CONFIG_PATH = os.path.join(ROOT_DIR, "config", "vm_config.json")
VM_PUBLIC_IPS_PATH = os.path.join(ROOT_DIR, "config", "vm_public_ips.json")
vm_details_data = combine_configs(VM_CONFIG_PATH, VM_PUBLIC_IPS_PATH)

logging.basicConfig(
    filename=os.path.join(ROOT_DIR, "logs", "create_delete_logs.log"),
    level=logging.INFO,
    format='%(asctime)s + %(levelname)s + %(message)s'
)
logger = logging.getLogger('create_delete_logger')

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
def trainingFiles(
        sftp_object: SFTP,
        model: str, 
        remote_training_wsp_dir: str) -> list:
    
    if model == "detection":
        remote_subir_training = os.path.join(remote_training_wsp_dir, "train")
        remote_subdir_training_list = [
            os.path.join(remote_subir_training, i) 
            for i in sftp_object.ls(remote_subir_training)
        ]
    else:
        remote_subdir_training_list = []
    
    # list of basenames in training dir
    remote_ckpt_files_list = [
        os.path.join(remote_training_wsp_dir, i) 
        for i in sftp_object.ls(remote_training_wsp_dir) if i != "train"
    ]
    training_download_files = remote_ckpt_files_list \
        + remote_subdir_training_list
    
    return training_download_files


def dir_mb_size(directory: str):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)


def trainedFiles(
        sftp_object: SFTP,
        model: str, 
        remote_trained_wsp_dir: str) -> list:
    
    if model == "detection":
        checkpoint_dir = os.path.join(remote_trained_wsp_dir, "checkpoint")
        saved_model_dir = os.path.join(remote_trained_wsp_dir, "saved_model")
        saved_model_vars_dir = os.path.join(saved_model_dir, "variables")
        saved_model_assets = os.path.join(saved_model_dir, "assets")
        pipeline_config_path = os.path.join(
            remote_trained_wsp_dir, "pipeline.config"
        )
        
        # List files
        checkpoint_files = [
            os.path.join(checkpoint_dir, i) 
            for i in sftp_object.ls(checkpoint_dir)
        ]
        saved_model_files = [
            os.path.join(saved_model_dir, i) 
            for i in sftp_object.ls(saved_model_dir) if i != "variables"
        ]
        saved_model_vars_files = [
            os.path.join(saved_model_vars_dir, i) 
            for i in sftp_object.ls(saved_model_vars_dir)
        ]
        saved_model_assets_files = [
            os.path.join(saved_model_assets, i) 
            for i in sftp_object.ls(saved_model_assets)
        ]
        trained_download_files = checkpoint_files + saved_model_files \
            + saved_model_vars_files + saved_model_assets_files \
            + [pipeline_config_path]
    else:
        # List files
        trained_download_files = [
            os.path.join(remote_trained_wsp_dir, i) 
            for i in sftp_object.ls(remote_trained_wsp_dir)
        ]

    return trained_download_files


def isFinishedTraining(
        username: str,
        password: str,
        port: int,
        vm_data: dict):
    
    model = vm_data.get("model", "")
    vm_name = vm_data.get("name", "")
    workspace = vm_data.get("workspace", "")
    public_ip = vm_data.get("public_ip", None)
    sftp_obj = SFTP(public_ip, port, username, password)
    print(f"Checking training checkpoints on on: {vm_name} ...")

    remote_workspace_dir =  os.path.join(
        f"/home/{username}/your_repo", model, "workspace", workspace
    )
    remote_training_dir = os.path.join(
        f"/home/{username}/your_repo", model, "training"
    )
    
    # Path initialize
    if model == "detection":
        local_pipeline_config_path = os.path.join(
            ROOT_DIR, "workspace", model, workspace, "pipeline.yml"
        )
        with open(local_pipeline_config_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        num_steps = config.get('training', None).get("num_steps", None)
        pretrained_model = config.get('pretrained_model', None).get("name", "")
        pretrained_model_prefix = "_".join(pretrained_model.split("_")[:2])
        
        # Training
        remote_training_wsp_dir = os.path.join(
            remote_training_dir, f"{workspace}_{pretrained_model_prefix}"
        )
        # Trained
        remote_trained_dir = os.path.join(
            f"/home/{username}/your_repo",
            model, "trained-inference-graphs"
        )
        remote_trained_wsp_dir = os.path.join(
            remote_trained_dir, f"{workspace}_{pretrained_model_prefix}"
        )
    else:
        # Training
        remote_training_wsp_dir = os.path.join(remote_training_dir, workspace)

        # Trained
        remote_trained_dir = os.path.join(
            f"/home/{username}/your_repo", model, "trained-models"
        )
        remote_trained_wsp_dir = os.path.join(remote_trained_dir, workspace)
    
    training_download_files = trainingFiles(
        sftp_object=sftp_obj,
        model=model,
        remote_training_wsp_dir=remote_training_wsp_dir
    )
    remote_ckpt_num_list = [
        os.path.basename(i).replace(".index", "")
        for i in training_download_files 
        if os.path.basename(i).endswith(".index")
    ]

    # Checking the checkpoints
    print("Checking checkpoint in the training directory ...")
    isFinished = False
    for ckpt in remote_ckpt_num_list:
        finished_ckpt = int(1 + (num_steps / 1000))
        if ckpt.replace("ckpt-", "") == str(finished_ckpt):
            print(f"Finished at checkpoint {finished_ckpt}.")
            print(f"Deleting '{vm_name}' due to reached the checkpoint.")
            isFinished = True


    # Checking files trained-model
    print("Checking saved_model/.pb in the trained directory ...")
    trained_files_list = sftp_obj.ls(remote_trained_wsp_dir)
    if ("saved_model" in trained_files_list) or \
        any(file.endswith('.pb') for file in trained_files_list):
        print(f"Finished at model converting.")
        print(f"Deleting '{vm_name}' due to the existance of saved_model.")
        isFinished = True

    # Download if isDownload == True
    if isFinished:
        try:
            download_files_list = trainedFiles(
                sftp_object=sftp_obj, 
                model=model, 
                remote_trained_wsp_dir=remote_trained_wsp_dir
            )
            start_relpath = remote_trained_wsp_dir
        except:
            download_files_list = training_download_files
            start_relpath = remote_training_wsp_dir
        
        for remote_filepath in download_files_list:
            remote_rel_path = os.path.relpath(
                remote_filepath, 
                start_relpath
            )
            local_downloaded_dir = os.path.join(
                ROOT_DIR, "workspace", model, workspace ,"downloaded_model",
            )
            remote_dirname = os.path.dirname(remote_rel_path)
            if remote_dirname:
                local_train_subdir = os.path.join(
                    local_downloaded_dir, remote_dirname
                )
                os.makedirs(local_train_subdir, exist_ok=True)
            else:
                os.makedirs(local_downloaded_dir, exist_ok=True)
            
            local_filepath = os.path.join(
                local_downloaded_dir, remote_rel_path
            )
            sftp_obj.getfile(remote_filepath, local_filepath)

    sftp_obj.close()

    return isFinished


if __name__ == '__main__':

    PORT = 22
    USERNAME = "your_username_in_tf_file"
    PASSWORD = "your_password_in_tf_file"
    data = read_json(VM_CONFIG_PATH)

    for vm_key, vm_data in vm_details_data.items():
        model = vm_data.get("model", "")
        vm_name = vm_data.get("name", "")
        workspace = vm_data.get("workspace", "")
        public_ip = vm_data.get("public_ip", None)
        
        if isFinishedTraining(USERNAME, PASSWORD, PORT, vm_data):
            send_line_message(f"{str(model).capitalize()} training job on VM is done:\n - VM key: {vm_key}\n - VM name: {vm_name}\n - Workspace: {workspace}\n\n\We will delete this cloud VM.")

            # Double-check the downloaded folder
            local_workspace_dir = os.path.join(
                ROOT_DIR, "workspace", model, workspace
            )
            downloaded_model_dir = os.path.join(
                local_workspace_dir, "downloaded_model"
            )
            isCreated = True if os.path.exists(downloaded_model_dir) else False
            isDownloaded = True if dir_mb_size(downloaded_model_dir) > 10 \
                else False

            if isCreated and isDownloaded:
                print(f"Deleting {vm_key} ...")
                send_line_message(f"Deleting {vm_key} ...")
            
                del data['vm_config'][vm_key]

                with open(VM_CONFIG_PATH, 'w') as json_file:
                    json.dump(data, json_file, indent=3)

                # Terraform
                plan_command = f"terraform -chdir={ROOT_DIR}/terraform/ plan"
                apply_command = f"""
                    terraform -chdir={ROOT_DIR}/terraform/ apply -auto-approve
                """
                
                subprocess.run(
                    f"{plan_command} && {apply_command}", 
                    shell=True, capture_output=False, text=True
                )

                logger.info(f"Deleted VM: {vm_key}")