from dotenv import load_dotenv

from metrics.examples.posthog.posthog import ingest


def main():
    """Run the PostHog example ingest function and print results."""
    load_dotenv(override=True)
    df = ingest()
    print(df)


if __name__ == "__main__":
    main()
