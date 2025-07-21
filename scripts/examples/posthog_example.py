from dotenv import load_dotenv
import pandas as pd

from metrics.examples.posthog.posthog import ingest


def main():
    """Run the PostHog example ingest function and print results."""
    load_dotenv(override=True)
    pd.set_option("display.max_columns", None)
    df = ingest()
    print(df)


if __name__ == "__main__":
    main()
