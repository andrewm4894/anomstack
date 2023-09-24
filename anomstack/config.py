"""
Handle configuration for the jobs.
"""

import os
import yaml
from pathlib import Path

# environment variables that can be used to override the configuration.
env_vars = [
    'ANOMSTACK_GCP_PROJECT_ID',
    'ANOMSTACK_MODEL_PATH',
    'ANOMSTACK_TABLE_KEY'
]

# directories
config_dir = Path('./metrics')
defaults_dir = Path('./metrics/defaults')
examples_dir = Path('./metrics/examples')

specs = {}


def process_yaml_file(yaml_file):
    """
    Process a YAML file and add it to the specs dictionary.
    """
    
    with open(yaml_file, 'r') as file:
        
        metric_specs = yaml.safe_load(file)
        metric_batch = metric_specs['metric_batch']
        merged_specs = {**defaults, **metric_specs}
        
        if merged_specs['disable_batch'] == True:
            return None
        for env_var in env_vars:
            if env_var in os.environ:
                merged_specs[env_var.replace('ANOMSTACK_','').lower()] = os.getenv(env_var)

        specs[metric_batch] = merged_specs


# load defaults
with open(defaults_dir / 'defaults.yaml', 'r') as file:    
    defaults = yaml.safe_load(file)

# load all the YAML files
for root, dirs, files in os.walk(config_dir):
    
    # ignore examples if the environment variable is set
    if os.getenv('ANOMSTACK_IGNORE_EXAMPLES') == 'yes' and examples_dir in Path(root).parents:        
        continue
    
    # process all the YAML files
    for yaml_file in files:
        
        if yaml_file == 'defaults.yaml':
            continue
        
        if yaml_file.endswith('.yaml'):
            yaml_path = Path(root) / yaml_file
            process_yaml_file(yaml_path)
