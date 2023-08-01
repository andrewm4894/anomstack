"""
Handle configuration for the jobs.
"""

import os
import yaml
from pathlib import Path

env_vars = {
    'PROJECT_ID': 'project_id',
    'BUCKET_NAME': 'bucket_name',
    'DATASET': 'dataset',
    'TABLE': 'table',
}

config_dir = Path('metrics')
defaults_dir = Path('metrics/defaults')
examples_dir = Path('metrics/examples')
specs = {}

def process_yaml_file(yaml_file):
    with open(yaml_file, 'r') as file:
        metric_specs = yaml.safe_load(file)
        metric_batch = metric_specs['metric_batch']
        merged_specs = {**defaults, **metric_specs}
        for env_var, key in env_vars.items():
            if env_var in os.environ:
                merged_specs[key] = os.getenv(env_var)
        specs[metric_batch] = merged_specs

# load defaults.yaml
with open(defaults_dir / 'defaults.yaml', 'r') as file:
    defaults = yaml.safe_load(file)

# process YAML files in all subdirectories
for root, dirs, files in os.walk(config_dir):
    if os.getenv('ANOMSTACK_IGNORE_EXAMPLES') == 'yes' and examples_dir in Path(root).parents:
        continue
    for yaml_file in files:
        if yaml_file == 'defaults.yaml':
            continue
        if yaml_file.endswith('.yaml'):
            yaml_path = Path(root) / yaml_file
            process_yaml_file(yaml_path)
