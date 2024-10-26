import pandas as pd


def ingest(top_n=10) -> pd.DataFrame:
    """ """

    import pandas as pd
    import requests

    # Hacker News API endpoint for top stories
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"

    # Make a request to the API to get the list of top story IDs
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching top stories: ", response.status_code)
        return pd.DataFrame()

    # Get the list of top story IDs
    story_ids = response.json()
    # Limit the number of story IDs to the top N
    story_ids = story_ids[:top_n]

    # Initialize variables for min, max, and avg scores
    min_score = float("inf")
    max_score = 0
    total_score = 0

    # Loop through the top story IDs and fetch each story's details
    for story_id in story_ids:
        # API endpoint for story details
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"

        # Make a request to the API to get the story details
        story_response = requests.get(story_url)
        if story_response.status_code != 200:
            print("Error fetching story details: ", story_response.status_code)
            continue

        # Parse the story details
        story = story_response.json()

        # Get the story's score
        score = story.get("score", 0)

        # Update min, max, and total scores
        min_score = min(min_score, score)
        max_score = max(max_score, score)
        total_score += score

    # Calculate average score
    avg_score = total_score / len(story_ids)

    # Create a Pandas DataFrame with the metrics
    data = [
        [f"hn_top_{top_n}_min_score", min_score],
        [f"hn_top_{top_n}_max_score", max_score],
        [f"hn_top_{top_n}_avg_score", avg_score],
        [f"hn_top_{top_n}_total_score", total_score],
    ]
    df = pd.DataFrame(data, columns=["metric_name", "metric_value"])
    df["metric_timestamp"] = pd.Timestamp.utcnow()

    return df
