import os
import yaml
from pathlib import Path

env_vars = {
    'PROJECT_ID': 'project_id',
    'BUCKET_NAME': 'bucket_name',
    'DATASET': 'dataset',
    'TABLE': 'table'
}

config_dir = Path("metrics")
specs = {}

with open(config_dir / 'defaults.yaml', 'r') as file:
    defaults = yaml.safe_load(file)

for yaml_file in config_dir.glob('*.yaml'):
    if yaml_file.name == 'defaults.yaml':
        continue
    with open(yaml_file, 'r') as file:
        metric_specs = yaml.safe_load(file)
        metric_name = metric_specs["name"]
        merged_specs = {**defaults, **metric_specs}
        for env_var, key in env_vars.items():
            if env_var in os.environ:
                merged_specs[key] = os.getenv(env_var)
        specs[metric_name] = merged_specs
