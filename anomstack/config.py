"""
Handle configuration for the jobs.
"""

import os
from pathlib import Path

import yaml
from dagster import get_dagster_logger

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
    logger = get_dagster_logger()
    logger.info("get_specs called")
    metrics_dir_path = Path(metrics_dir).resolve()
    defaults_dir = metrics_dir_path / "defaults"
    examples_dir = metrics_dir_path / "examples"
    specs = {}

    # Load defaults
    defaults_file = str(defaults_dir / "defaults.yaml")
    if not Path(defaults_file).exists():
        raise FileNotFoundError(f"Defaults file not found: {defaults_file}")
    with open(defaults_file, "r", encoding="utf-8") as file:
        defaults = yaml.safe_load(file)

    def process_yaml_file(yaml_file: str):
        logger.info(f"process_yaml_file called for {yaml_file}")
        with open(yaml_file, "r", encoding="utf-8") as f:
            metric_specs = yaml.safe_load(f)
            metric_batch = metric_specs["metric_batch"]
            merged_specs = {**defaults, **metric_specs}
            merged_specs["metrics_dir"] = str(metrics_dir_path)
            if merged_specs.get("disable_batch"):
                return
            
            # Apply global environment variable overrides
            # Only override if the parameter is NOT specified in either defaults or specific YAML file
            for env_var in env_vars:
                if env_var in os.environ:
                    param_key = env_var.replace("ANOMSTACK_", "").lower()
                    # Only override if the parameter is NOT specified in either defaults or specific YAML file
                    if param_key not in metric_specs and param_key not in defaults:
                        yaml_value = merged_specs.get(param_key)
                        merged_specs[param_key] = os.getenv(env_var)
                        logger.info(f"ENV OVERRIDE: {env_var} replaces {param_key} (was: {yaml_value}, now: {merged_specs[param_key]})")
            
            # Apply metric batch-specific environment variable overrides
            # Pattern: ANOMSTACK__<METRIC_BATCH>__<PARAM>
            # These should override both defaults and metric-specific YAML values
            metric_batch_upper = metric_batch.upper().replace("-", "_")
            for env_var, value in os.environ.items():
                if env_var.startswith(f"ANOMSTACK__{metric_batch_upper}__"):
                    # Extract the parameter name from the environment variable
                    param_key = env_var.replace(f"ANOMSTACK__{metric_batch_upper}__", "").lower()
                    old_value = merged_specs.get(param_key, None)
                    merged_specs[param_key] = value
                    logger.info(f"ENV BATCH OVERRIDE: {env_var} replaces {param_key} (was: {old_value}, now: {value})")
            
            specs[metric_batch] = merged_specs

    # Walk through the metrics directory and process YAML files
    for root, dirs, files in os.walk(str(metrics_dir_path)):
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
                yaml_path = str(Path(root) / yaml_file)
                process_yaml_file(yaml_path)

    return specs


# Hot configuration reload functionality
def reload_code_location(location_name="anomstack_code"):
    """Reload a specific code location in Dagster."""
    import requests
    
    logger = get_dagster_logger()
    host = os.getenv('DAGSTER_HOST', 'localhost')
    port = os.getenv('DAGSTER_PORT', '3000')
    url = f"http://{host}:{port}/graphql"
    
    # GraphQL mutation to reload code location
    mutation = """
    mutation ReloadRepositoryLocation($locationName: String!) {
      reloadRepositoryLocation(repositoryLocationName: $locationName) {
        __typename
        ... on WorkspaceLocationEntry {
          name
          locationOrLoadError {
            __typename
            ... on RepositoryLocation {
              name
              repositories {
                name
              }
            }
            ... on PythonError {
              message
              stack
            }
          }
        }
        ... on ReloadNotSupported {
          message
        }
        ... on RepositoryLocationNotFound {
          message
        }
      }
    }
    """
    
    variables = {"locationName": location_name}
    
    try:
        logger.info(f"🔄 Attempting to reload code location '{location_name}'...")
        response = requests.post(
            url,
            json={"query": mutation, "variables": variables},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
        data = response.json()
        
        if "errors" in data:
            logger.error(f"❌ GraphQL Errors: {data['errors']}")
            return False
            
        result = data["data"]["reloadRepositoryLocation"]
        
        if result["__typename"] == "WorkspaceLocationEntry":
            logger.info(f"✅ Successfully reloaded code location '{location_name}'")
            
            # Show loaded repositories
            location_data = result["locationOrLoadError"]
            if location_data["__typename"] == "RepositoryLocation":
                repos = location_data["repositories"]
                logger.info(f"📦 Loaded {len(repos)} repositories:")
                for repo in repos:
                    logger.info(f"   - {repo['name']}")
            else:
                logger.warning(f"⚠️  Location loaded but with errors: {location_data}")
            
            return True
            
        elif result["__typename"] == "ReloadNotSupported":
            logger.error(f"❌ Reload not supported: {result['message']}")
            return False
            
        elif result["__typename"] == "RepositoryLocationNotFound":
            logger.error(f"❌ Location not found: {result['message']}")
            return False
            
        else:
            logger.error(f"❌ Unexpected result type: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during configuration reload: {str(e)}")
        return False


def execute_config_reload():
    """
    Execute configuration reload with validation.
    
    Returns:
        bool: True if reload was successful, False otherwise
    """
    import requests
    
    logger = get_dagster_logger()
    
    try:
        # Check if Dagster is accessible
        host = os.getenv('DAGSTER_HOST', 'localhost')
        port = os.getenv('DAGSTER_PORT', '3000')
        url = f"http://{host}:{port}/server_info"
        
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            logger.error(f"❌ Dagster webserver returned {response.status_code}")
            return False
        
        logger.info("✅ Dagster webserver is accessible")
        
        # Check if metrics directory is accessible
        metrics_dir = Path("./metrics")
        if not metrics_dir.exists():
            logger.error(f"❌ Metrics directory not found at {metrics_dir.absolute()}")
            return False
            
        defaults_file = metrics_dir / "defaults" / "defaults.yaml"
        if not defaults_file.exists():
            logger.error(f"❌ Defaults file not found at {defaults_file.absolute()}")
            return False
            
        logger.info(f"✅ Configuration files accessible at {metrics_dir.absolute()}")
        
        # Execute reload
        logger.info("🔄 Starting configuration reload...")
        success = reload_code_location("anomstack_code")
        
        if success:
            logger.info("🎉 Configuration reload complete!")
            return True
        else:
            logger.error("💥 Configuration reload failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Configuration reload error: {str(e)}")
        return False
