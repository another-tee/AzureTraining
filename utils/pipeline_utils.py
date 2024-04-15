# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import os

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
def remote_tensorboard_logdir(workspace: str, model: str) -> str:
    
    if model == "detection":
        import yaml
        local_pipeline_config_path = os.path.join(
            "workspace", model, workspace, "pipeline.yml"
        )
        with open(local_pipeline_config_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        pretrained_model = config.get('pretrained_model', None).get("name", "")
        pretrained_model_prefix = "_".join(pretrained_model.split("_")[:2])
        workspace_name = f"{workspace}_{pretrained_model_prefix}"
        remote_logdir = os.path.join(
            model, "training", workspace_name, "train"
        )
    else:
        workspace_name = workspace
        remote_logdir = os.path.join(
            model, "trained-models", workspace_name, 
            "tboard_logs_feature_extractor"
        )
    
    return remote_logdir


if __name__ == '__main__':
    pass
    