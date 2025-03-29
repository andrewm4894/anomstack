"""
Handle configuration for the jobs.
"""

import os
from pathlib import Path

import yaml

# environment variables that can be used to override the configuration.
env_vars = ["ANOMSTACK_GCP_PROJECT_ID", "ANOMSTACK_MODEL_PATH", "ANOMSTACK_TABLE_KEY"]


def get_specs(metrics_dir: str = "./metrics"):
    """
    Process configuration YAML files and return a dictionary of specifications.

    Args:
        metrics_dir (str): Path to the metrics directory. Defaults to "./metrics".
                           When running from a notebook in the repo root, you can pass
                           a relative path like "../metrics".

    Returns:
        dict: Dictionary of processed metric configurations.
    """
    metrics_dir = Path(metrics_dir).resolve()
    defaults_dir = metrics_dir / "defaults"
    examples_dir = metrics_dir / "examples"
    specs = {}

    # Load defaults
    defaults_file = defaults_dir / "defaults.yaml"
    if not defaults_file.exists():
        raise FileNotFoundError(f"Defaults file not found: {defaults_file}")
    with open(defaults_file, "r", encoding="utf-8") as file:
        defaults = yaml.safe_load(file)

    def process_yaml_file(yaml_file: str):
        with open(yaml_file, "r", encoding="utf-8") as f:
            metric_specs = yaml.safe_load(f)
            metric_batch = metric_specs["metric_batch"]
            merged_specs = {**defaults, **metric_specs}
            merged_specs["metrics_dir"] = str(metrics_dir)
            if merged_specs.get("disable_batch"):
                return
            for env_var in env_vars:
                if env_var in os.environ:
                    param_key = env_var.replace("ANOMSTACK_", "").lower()
                    if param_key not in merged_specs:
                        merged_specs[param_key] = os.getenv(env_var)
            specs[metric_batch] = merged_specs

    # Walk through the metrics directory and process YAML files
    for root, dirs, files in os.walk(metrics_dir):
        # Skip the examples directory if the environment variable is set
        if (
            os.getenv("ANOMSTACK_IGNORE_EXAMPLES") == "yes"
            and examples_dir in Path(root).parents
        ):
            continue
        for yaml_file in files:
            if yaml_file == "defaults.yaml":
                continue
            if yaml_file.endswith(".yaml"):
                yaml_path = Path(root) / yaml_file
                process_yaml_file(yaml_path)

    return specs
