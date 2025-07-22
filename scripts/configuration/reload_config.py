#!/usr/bin/env python3
"""
Reload Dagster configuration after making changes to YAML files or environment variables.

This script helps users update configurations on the fly without restarting Docker containers.
"""

import os
import sys
from pathlib import Path

import requests


def get_dagster_graphql_url():
    """Get Dagster GraphQL URL from environment or default."""
    host = os.getenv('DAGSTER_HOST', 'localhost')
    port = os.getenv('DAGSTER_PORT', '3000')
    return f"http://{host}:{port}/graphql"

def reload_code_location(location_name="anomstack_code"):
    """Reload a specific code location in Dagster."""
    url = get_dagster_graphql_url()

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
        print(f"🔄 Attempting to reload code location '{location_name}'...")
        response = requests.post(
            url,
            json={"query": mutation, "variables": variables},
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False

        data = response.json()

        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return False

        result = data["data"]["reloadRepositoryLocation"]

        if result["__typename"] == "WorkspaceLocationEntry":
            print(f"✅ Successfully reloaded code location '{location_name}'")

            # Show loaded repositories
            location_data = result["locationOrLoadError"]
            if location_data["__typename"] == "RepositoryLocation":
                repos = location_data["repositories"]
                print(f"📦 Loaded {len(repos)} repositories:")
                for repo in repos:
                    print(f"   - {repo['name']}")
            else:
                print(f"⚠️  Location loaded but with errors: {location_data}")

            return True

        elif result["__typename"] == "ReloadNotSupported":
            print(f"❌ Reload not supported: {result['message']}")
            return False

        elif result["__typename"] == "RepositoryLocationNotFound":
            print(f"❌ Location not found: {result['message']}")
            return False

        else:
            print(f"❌ Unexpected result type: {result}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Dagster. Is the webserver running on http://localhost:3000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Dagster may be busy.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_dagster_health():
    """Check if Dagster is accessible."""
    url = get_dagster_graphql_url().replace("/graphql", "/server_info")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Dagster webserver is accessible at {url}")
            return True
        else:
            print(f"❌ Dagster webserver returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach Dagster webserver: {e}")
        return False

def validate_config():
    """Validate that configuration files are accessible."""
    metrics_dir = Path("./metrics")

    if not metrics_dir.exists():
        print(f"❌ Metrics directory not found at {metrics_dir.absolute()}")
        return False

    defaults_file = metrics_dir / "defaults" / "defaults.yaml"
    if not defaults_file.exists():
        print(f"❌ Defaults file not found at {defaults_file.absolute()}")
        return False

    print(f"✅ Configuration files accessible at {metrics_dir.absolute()}")
    return True

def main():
    """Main function to reload configuration."""
    print("🔧 Anomstack Configuration Reloader")
    print("=" * 50)

    # Check prerequisites
    if not validate_config():
        print("\n💡 Ensure you're running this script from the anomstack root directory.")
        sys.exit(1)

    if not check_dagster_health():
        print("\n💡 Ensure Docker containers are running:")
        print("   docker compose up -d")
        sys.exit(1)

    # Reload configuration
    print("\n🔄 Reloading configuration...")
    success = reload_code_location("anomstack_code")

    if success:
        print("\n🎉 Configuration reload complete!")
        print("\n📝 Your changes should now be active:")
        print("   • YAML configuration updates")
        print("   • Environment variable changes (if containers restarted)")
        print("   • New metric batches")
        print("   • Modified SQL queries or Python functions")
        print("\n🌐 Check the Dagster UI: http://localhost:3000")
    else:
        print("\n💥 Configuration reload failed!")
        print("\n🔧 Try these troubleshooting steps:")
        print("   1. Check Docker containers: docker compose ps")
        print("   2. Check Dagster logs: docker compose logs anomstack_code")
        print("   3. Restart containers if needed: docker compose restart")

        sys.exit(1)

if __name__ == "__main__":
    main()
