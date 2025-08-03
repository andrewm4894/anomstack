#!/usr/bin/env python3
"""
Minimal script to run Anomstack examples using existing infrastructure.

This script uses Anomstack's built-in configuration loading and ingest function
execution, just like the actual Dagster jobs do.
"""

import argparse
import sys

# Try to load dotenv for environment variables (optional)
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except ImportError:
    pass

from anomstack.config import get_specs
from anomstack.fn.run import run_df_fn
from anomstack.jinja.render import render


def run_example(example_name: str) -> int:
    """Run an Anomstack example using the existing infrastructure."""

    # Map common example names to their actual metric_batch names
    example_mapping = {
        "hackernews": "hackernews",
        "posthog": "posthog",
    }

    if example_name in example_mapping:
        metric_batch = example_mapping[example_name]
    else:
        metric_batch = example_name  # Use as-is for other examples

    try:
        print(f"📊 Running {example_name} example...")
        print("=" * 50)

        # Load specs using Anomstack's existing config system
        # Load all specs from metrics directory
        specs = get_specs("./metrics")

        if metric_batch not in specs:
            print(f"❌ Example '{metric_batch}' not found.")
            print("💡 Available examples:")
            for spec_name in specs.keys():
                print(f"   • {spec_name}")
            return 1

        spec = specs[metric_batch]

        # Check if it has an ingest function
        if not spec.get("ingest_fn"):
            print(f"❌ Example '{metric_batch}' has no ingest_fn defined.")
            print("This example might use SQL instead of Python.")
            return 1

        # Run the ingest function using Anomstack's existing infrastructure
        # This is exactly what anomstack/jobs/ingest.py does on line 94
        rendered_fn = render("ingest_fn", spec)
        df = run_df_fn("ingest", rendered_fn)

        if df.empty:
            print("❌ No data returned from ingest function.")
            return 1

        print("✅ Example completed successfully!")
        print(f"\n📊 Results from {metric_batch}:")
        print("-" * 30)

        # Format output nicely
        for _, row in df.iterrows():
            metric_name = row["metric_name"]
            metric_value = row["metric_value"]
            print(f"🔸 {metric_name}: {metric_value}")

        print(f"\n⏱️  Timestamp: {df.iloc[0]['metric_timestamp']}")
        print(f"📈 Total metrics collected: {len(df)}")

        print("\n" + "=" * 50)
        print("Raw DataFrame:")
        print(df.to_string(index=False))

        return 0

    except Exception as e:
        print(f"❌ Error running {example_name} example: {e}")
        print("💡 Make sure:")
        print("   • Example exists in metrics/examples/")
        print("   • Required environment variables are set")
        print("   • Dependencies are installed")
        return 1


def list_examples() -> int:
    """List all available examples."""
    try:
        print("📋 Available Examples:")
        print("=" * 50)

        # Load all specs from metrics directory
        specs = get_specs("./metrics")

        # Categorize examples
        python_examples = []
        sql_examples = []

        for name, spec in specs.items():
            if spec.get("ingest_fn"):
                python_examples.append(name)
            else:
                sql_examples.append(name)

        if python_examples:
            print("🐍 Python Examples (ingest_fn):")
            for name in sorted(python_examples):
                print(f"   • {name}")

        if sql_examples:
            print("\n🗄️  SQL Examples (ingest_sql):")
            for name in sorted(sql_examples):
                print(f"   • {name}")

        print(f"\n📊 Total examples: {len(specs)}")
        print("\nUsage:")
        print("  python run_example.py <example_name>")
        print("  make run-example EXAMPLE=<example_name>")

        return 0

    except Exception as e:
        print(f"❌ Error listing examples: {e}")
        return 1


def main():
    """Main function to parse arguments and run examples."""
    parser = argparse.ArgumentParser(
        description="Run Anomstack examples using existing infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_example.py hackernews
  python run_example.py posthog
  python run_example.py --list
        """,
    )

    parser.add_argument(
        "example", nargs="?", help="Example to run (use --list to see available examples)"
    )

    parser.add_argument("--list", "-l", action="store_true", help="List all available examples")

    args = parser.parse_args()

    if args.list:
        return list_examples()

    if not args.example:
        print("❌ No example specified.")
        print("Use --list to see available examples or --help for usage.")
        return 1

    return run_example(args.example.lower())


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
