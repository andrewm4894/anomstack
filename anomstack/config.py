"""
Handle configuration for the jobs.
"""

import os
from pathlib import Path

import yaml

# environment variables that can be used to override the configuration.
env_vars = ["ANOMSTACK_GCP_PROJECT_ID", "ANOMSTACK_MODEL_PATH", "ANOMSTACK_TABLE_KEY"]

# directories
metrics_dir = Path("./metrics")
defaults_dir = Path(f"{metrics_dir}/defaults")
examples_dir = Path(f"{metrics_dir}/examples")

specs = {}


def process_yaml_file(yaml_file):
    """
    Process a YAML file and add it to the specs dictionary.

    Args:
    yaml_file (str): The path to the YAML file to be processed.

    Returns:
    None
    """

    with open(yaml_file, "r", encoding="utf-8") as f:
        metric_specs = yaml.safe_load(f)
        metric_batch = metric_specs["metric_batch"]
        merged_specs = {**defaults, **metric_specs}

        if merged_specs["disable_batch"] == True:
            return None
        for env_var in env_vars:
            if env_var in os.environ:
                param_key = env_var.replace("ANOMSTACK_", "").lower()
                if param_key not in merged_specs:
                    merged_specs[param_key] = os.getenv(env_var)

        specs[metric_batch] = merged_specs


# load defaults
with open(defaults_dir / "defaults.yaml", "r", encoding="utf-8") as file:
    defaults = yaml.safe_load(file)

# load all the YAML files
for root, dirs, files in os.walk(metrics_dir):
    # ignore examples if the environment variable is set
    if (
        os.getenv("ANOMSTACK_IGNORE_EXAMPLES") == "yes"
        and examples_dir in Path(root).parents
    ):
        continue

    # process all the YAML files
    for yaml_file in files:
        if yaml_file == "defaults.yaml":
            continue

        if yaml_file.endswith(".yaml"):
            yaml_path = Path(root) / yaml_file
            process_yaml_file(yaml_path)
