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
            
            # Apply global environment variable overrides
            for env_var in env_vars:
                if env_var in os.environ:
                    param_key = env_var.replace("ANOMSTACK_", "").lower()
                    # Check if the parameter exists in either YAML file
                    yaml_value = metric_specs.get(param_key) or defaults.get(param_key)
                    # Always override with the environment variable value
                    merged_specs[param_key] = os.getenv(env_var)
            
            # Apply metric batch-specific environment variable overrides
            # Pattern: ANOMSTACK__<METRIC_BATCH>__<PARAM>
            # These should override both defaults and metric-specific YAML values
            metric_batch_upper = metric_batch.upper().replace("-", "_")
            for env_var, value in os.environ.items():
                if env_var.startswith(f"ANOMSTACK__{metric_batch_upper}__"):
                    # Extract the parameter name from the environment variable
                    param_key = env_var.replace(f"ANOMSTACK__{metric_batch_upper}__", "").lower()
                    # Do NOT convert underscores to hyphens; keep as is to match YAML keys
                    merged_specs[param_key] = value
            
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
