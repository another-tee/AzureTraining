# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import json

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
def read_json(jsonfilepath: str) -> dict:
    """
    Reads a JSON file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: Contents of the JSON file as a dictionary.
        None: If an error occurs during file reading.
    """
    try:
        with open(jsonfilepath, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{jsonfilepath}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file '{jsonfilepath}': {e}")
    except Exception as e:
        print(f"An error occurred while reading file '{jsonfilepath}': {e}")
    return {}


def combine_configs(vm_config_path: str, vm_public_ips_path: str) -> dict:
    """Combine VM configurations with public IP addresses.

    Args:
        vm_config_path (str): Path to the JSON file containing VM config.
        vm_public_ips_path (str): Path to the JSON file containing 
            public IP addresses for the VMs.

    Returns:
        dict: Combined VM configurations with public IP addresses.
    """
    vm_config_data = read_json(vm_config_path).get("vm_config", {})
    vm_public_ip_data = read_json(vm_public_ips_path)\
        .get("vm_public_ips", {}).get("value", {})
    for vm_key, public_ip in vm_public_ip_data.items():
        try:
            vm_config_data[vm_key]["public_ip"] = public_ip
        except KeyError:
            print(f"VM config has no key: '{vm_key}'.")
            continue
    return vm_config_data


if __name__ == '__main__':
    pass