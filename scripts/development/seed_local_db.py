#!/usr/bin/env python3
"""
Seed local DuckDB database with flexible metric batch combinations.

This script generates realistic historical data for any combination of metric batches
to provide comprehensive test data for local dashboard development.

Supports: python_ingest_simple, netdata, posthog, yfinance, currency
"""

import argparse
import os
import sys
import random
import json
import pandas as pd
import duckdb
from datetime import datetime, timedelta


def load_ingest_function(metric_batch: str):
    """Load the ingest function for the specified metric batch."""
    if metric_batch == "python_ingest_simple":
        def ingest():
            import random
            import pandas as pd

            metrics = ["metric1", "metric2", "metric3", "metric4", "metric5"]
            metric_values = []

            # Different anomaly types
            anomaly_types = ["spike", "drop", "plateau"]

            # Generate random metrics and introduce occasional anomalies (1% chance)
            anomaly_chance = random.random()
            anomaly_type = random.choice(anomaly_types) if anomaly_chance <= 0.01 else None

            for _ in metrics:
                if anomaly_type == "spike":
                    metric_value = random.uniform(15, 30)
                elif anomaly_type == "drop":
                    metric_value = random.uniform(-10, -1)
                elif anomaly_type == "plateau":
                    plateau_value = random.uniform(5, 6)
                    metric_values = [plateau_value] * len(metrics)
                    break
                else:
                    metric_value = random.uniform(0, 10)

                metric_values.append(metric_value)

            data = {
                "metric_name": metrics,
                "metric_value": metric_values,
                "metric_timestamp": pd.Timestamp.now(),
            }
            df = pd.DataFrame(data)
            return df
    
    elif metric_batch == "netdata":
        def ingest():
            import random
            import pandas as pd

            # Define hosts and chart types (based on netdata example structure)
            hosts = ["london", "bangalore", "frankfurt"]
            charts = {
                "system_cpu": ["user", "system", "nice", "iowait", "irq", "softirq", "steal", "guest"],
                "system_ram": ["free", "used", "cached", "buffers", "available"],
                "system_io": ["in", "out"],
                "system_net": ["received", "sent"]
            }
            
            data = []
            
            # Generate anomaly pattern for this batch (1% chance)
            anomaly_chance = random.random()
            anomaly_type = random.choice(["spike", "drop"]) if anomaly_chance <= 0.01 else None
            
            for host in hosts:
                for chart, metrics in charts.items():
                    for metric in metrics:
                        # Create metric name following netdata pattern
                        metric_name = f"{host}_{chart}_{metric}"
                        
                        # Generate base values based on metric type
                        if "cpu" in chart:
                            base_range = (0, 100)  # CPU percentages
                        elif "ram" in chart:
                            base_range = (1000000, 16000000000)  # RAM in bytes
                        elif "io" in chart:
                            base_range = (0, 10000)  # I/O operations
                        elif "net" in chart:
                            base_range = (0, 1000000)  # Network bytes
                        else:
                            base_range = (0, 100)
                        
                        # Apply anomalies
                        if anomaly_type == "spike":
                            if "cpu" in chart or "io" in chart or "net" in chart:
                                metric_value = random.uniform(base_range[1] * 2, base_range[1] * 5)
                            else:
                                metric_value = random.uniform(base_range[0], base_range[1])
                        elif anomaly_type == "drop":
                            if "ram" in chart and "free" in metric:
                                metric_value = random.uniform(base_range[0], base_range[0] * 2)  # Very low free RAM
                            elif "cpu" in chart and "iowait" in metric:
                                metric_value = random.uniform(50, 100)  # High iowait is bad
                            else:
                                metric_value = random.uniform(base_range[0], base_range[1])
                        else:
                            # Normal values
                            metric_value = random.uniform(base_range[0], base_range[1])
                        
                        data.append({
                            "metric_name": metric_name,
                            "metric_value": round(metric_value, 2),
                            "metric_timestamp": pd.Timestamp.now()
                        })
            
            df = pd.DataFrame(data)
            return df
    
    elif metric_batch == "posthog":
        def ingest():
            import random
            import pandas as pd

            # PostHog project/domain mapping (based on posthog example)
            project_domain_map = {
                "1016": "andrewm4894.com",
                "140227": "anomstack-demo", 
                "112495": "andys-daily-factoids.com",
                "148051": "andys-daily-riddle.com",
            }
            
            data = []
            ts = pd.Timestamp.now()
            
            # Generate anomaly pattern for this batch (1% chance)
            anomaly_chance = random.random()
            anomaly_type = random.choice(["spike", "drop"]) if anomaly_chance <= 0.01 else None
            
            for project_id, domain in project_domain_map.items():
                metrics = {
                    "events_yday": (50, 5000),      # Daily events range
                    "users_yday": (10, 500),        # Daily unique users  
                    "pageviews_yday": (100, 3000),  # Daily pageviews
                }
                
                for metric_key, base_range in metrics.items():
                    # Apply anomalies
                    if anomaly_type == "spike":
                        metric_value = random.uniform(base_range[1] * 1.5, base_range[1] * 3)
                    elif anomaly_type == "drop":
                        metric_value = random.uniform(base_range[0] * 0.1, base_range[0] * 0.5)
                    else:
                        # Normal values
                        metric_value = random.uniform(base_range[0], base_range[1])
                    
                    data.append({
                        "metric_timestamp": ts,
                        "metric_name": f"ph.{domain}.{metric_key}",
                        "metric_value": round(metric_value, 2),
                    })
            
            df = pd.DataFrame(data)
            return df[["metric_timestamp", "metric_name", "metric_value"]] if not df.empty else df
    
    elif metric_batch == "yfinance":
        def ingest():
            import random
            import pandas as pd

            # Stock symbols (based on yfinance example)
            symbols = [
                "GOOG", "TSLA", "AAPL", "MSFT", "NVDA", "AMZN", "TSM", "META",
                "NFLX", "WMT", "DIS", "JNJ", "BRK-B", "V", "JPM", "UNH", 
                "XOM", "PEP", "COST", "NKE", "BAC", "AMD"
            ]
            
            # Base price ranges for different stock categories
            stock_price_ranges = {
                "GOOG": (2800, 3200), "TSLA": (200, 280), "AAPL": (170, 200),
                "MSFT": (360, 420), "NVDA": (400, 900), "AMZN": (140, 170),
                "TSM": (90, 120), "META": (300, 500), "NFLX": (400, 600),
                "WMT": (150, 170), "DIS": (90, 120), "JNJ": (150, 170),
                "BRK-B": (350, 400), "V": (250, 290), "JPM": (140, 170),
                "UNH": (500, 570), "XOM": (100, 120), "PEP": (160, 180),
                "COST": (700, 900), "NKE": (100, 130), "BAC": (30, 40),
                "AMD": (120, 180)
            }
            
            data = []
            ts = pd.Timestamp.now()
            
            # Generate anomaly pattern for this batch (1% chance)
            anomaly_chance = random.random()
            anomaly_type = random.choice(["spike", "drop"]) if anomaly_chance <= 0.01 else None
            
            for symbol in symbols:
                base_range = stock_price_ranges.get(symbol, (50, 150))
                
                # Apply anomalies
                if anomaly_type == "spike":
                    # Stock price spike (15-30% increase)
                    multiplier = random.uniform(1.15, 1.30)
                    price = random.uniform(base_range[0], base_range[1]) * multiplier
                elif anomaly_type == "drop":
                    # Stock price drop (10-25% decrease)
                    multiplier = random.uniform(0.75, 0.90)
                    price = random.uniform(base_range[0], base_range[1]) * multiplier
                else:
                    # Normal stock price
                    price = random.uniform(base_range[0], base_range[1])
                
                data.append({
                    "metric_timestamp": ts,
                    "metric_name": f"yf_{symbol.lower()}_price",
                    "metric_value": round(price, 2),
                })
            
            df = pd.DataFrame(data)
            return df[["metric_timestamp", "metric_name", "metric_value"]] if not df.empty else df
    
    elif metric_batch == "currency":
        def ingest():
            import random
            import pandas as pd

            # Currency pairs (based on currency example)
            base_currencies = ["eur", "usd", "gbp", "jpy", "chf", "aud", "cad"]
            target_currencies = ["usd", "gbp", "jpy", "chf", "aud", "cad", "rub", "inr", "brl", "zar", "cny", "sek", "nzd"]
            
            # Typical exchange rate ranges (base currency to target currency)
            exchange_rate_ranges = {
                # EUR conversions
                "eur_usd": (1.05, 1.15), "eur_gbp": (0.84, 0.90), "eur_jpy": (140, 165),
                "eur_chf": (0.95, 1.05), "eur_aud": (1.55, 1.75), "eur_cad": (1.45, 1.55),
                "eur_rub": (90, 110), "eur_inr": (85, 95), "eur_brl": (5.5, 6.5),
                "eur_zar": (19, 21), "eur_cny": (7.5, 8.5), "eur_sek": (11, 12), "eur_nzd": (1.7, 1.9),
                
                # USD conversions  
                "usd_gbp": (0.75, 0.85), "usd_jpy": (130, 155), "usd_chf": (0.85, 0.95),
                "usd_aud": (1.4, 1.6), "usd_cad": (1.25, 1.4), "usd_rub": (85, 105),
                "usd_inr": (80, 85), "usd_brl": (5.0, 6.0), "usd_zar": (17, 20),
                "usd_cny": (7.0, 7.5), "usd_sek": (10, 11.5), "usd_nzd": (1.55, 1.75),
                
                # Other base currencies (simplified ranges)
                "gbp_usd": (1.18, 1.35), "gbp_jpy": (165, 190), "jpy_usd": (0.0065, 0.0077),
                "chf_usd": (1.05, 1.18), "aud_usd": (0.62, 0.72), "cad_usd": (0.71, 0.80),
            }
            
            data = []
            ts = pd.Timestamp.now()
            
            # Generate anomaly pattern for this batch (1% chance)
            anomaly_chance = random.random()
            anomaly_type = random.choice(["spike", "drop"]) if anomaly_chance <= 0.01 else None
            
            for base in base_currencies:
                for target in target_currencies:
                    if base != target:  # Don't convert currency to itself
                        pair = f"{base}_{target}"
                        
                        # Get base range or use default
                        base_range = exchange_rate_ranges.get(pair, (0.5, 2.0))
                        
                        # Apply anomalies
                        if anomaly_type == "spike":
                            # Currency spike (5-15% increase)
                            multiplier = random.uniform(1.05, 1.15)
                            rate = random.uniform(base_range[0], base_range[1]) * multiplier
                        elif anomaly_type == "drop":
                            # Currency drop (5-15% decrease)
                            multiplier = random.uniform(0.85, 0.95)
                            rate = random.uniform(base_range[0], base_range[1]) * multiplier
                        else:
                            # Normal exchange rate
                            rate = random.uniform(base_range[0], base_range[1])
                        
                        data.append({
                            "metric_timestamp": ts,
                            "metric_name": pair,
                            "metric_value": round(rate, 6),  # Exchange rates need more precision
                        })
            
            df = pd.DataFrame(data)
            return df[["metric_timestamp", "metric_name", "metric_value"]] if not df.empty else df
    
    else:
        raise ValueError(f"Unsupported metric batch: {metric_batch}")
    
    return ingest


def wrangle_df(df: pd.DataFrame, metric_batch: str) -> pd.DataFrame:
    """Process and clean the raw metrics DataFrame."""
    df = df.copy()
    
    # Add metric_batch column
    df["metric_batch"] = metric_batch
    
    # Add metric_type column  
    df["metric_type"] = "metric"
    
    # Add metadata column (None for base metrics)
    df["metadata"] = None
    
    # Ensure correct column order and types
    df = df[["metric_timestamp", "metric_batch", "metric_name", "metric_value", "metric_type", "metadata"]]
    
    # Round metric values
    df["metric_value"] = df["metric_value"].round(4)
    
    return df


def generate_scores_data(metrics_df: pd.DataFrame, target_alert_rate: float = 0.05) -> pd.DataFrame:
    """Generate anomaly scores based on metric values."""
    scores_data = []
    
    # Calculate threshold to achieve target alert rate
    all_values = metrics_df["metric_value"].values
    sorted_values = sorted(all_values, reverse=True)
    threshold_idx = int(len(sorted_values) * target_alert_rate)
    
    if threshold_idx < len(sorted_values):
        alert_threshold = sorted_values[threshold_idx]
    else:
        alert_threshold = max(all_values) + 1  # No alerts if target rate is 0
    
    for _, row in metrics_df.iterrows():
        # Generate score based on metric value (higher values = higher scores)
        metric_value = row["metric_value"]
        
        if metric_value >= alert_threshold:
            # High score for values that should trigger alerts
            score = random.uniform(0.8, 1.0)
        else:
            # Lower scores for normal values
            score = random.uniform(0.0, 0.7)
        
        scores_data.append({
            "metric_timestamp": row["metric_timestamp"],
            "metric_batch": row["metric_batch"],
            "metric_name": row["metric_name"],
            "metric_value": round(score, 4),
            "metric_type": "score",
            "metadata": None
        })
    
    return pd.DataFrame(scores_data)


def generate_alerts_data(scores_df: pd.DataFrame, threshold: float = 0.75) -> pd.DataFrame:
    """Generate binary alerts based on scores."""
    alerts_data = []
    
    for _, row in scores_df.iterrows():
        score = row["metric_value"]
        
        # Only create alert record if score is above threshold (alert triggered)
        if score >= threshold:
            alerts_data.append({
                "metric_timestamp": row["metric_timestamp"],
                "metric_batch": row["metric_batch"],
                "metric_name": row["metric_name"],
                "metric_value": 1.0,  # Always 1.0 since we only store triggered alerts
                "metric_type": "alert",
                "metadata": None
            })
    
    return pd.DataFrame(alerts_data)


def generate_llmalerts_data(metrics_df: pd.DataFrame, scores_df: pd.DataFrame, llm_alert_rate: float = 0.03) -> pd.DataFrame:
    """Generate LLM alerts with explanatory metadata."""
    llmalerts_data = []
    
    # Calculate threshold for LLM alerts
    all_scores = scores_df["metric_value"].values
    sorted_scores = sorted(all_scores, reverse=True)
    threshold_idx = int(len(sorted_scores) * llm_alert_rate)
    
    if threshold_idx < len(sorted_scores):
        llm_threshold = sorted_scores[threshold_idx]
    else:
        llm_threshold = max(all_scores) + 1  # No LLM alerts if rate is 0
    
    # Create lookup for scores by metric name + timestamp
    scores_lookup = {}
    for _, score_row in scores_df.iterrows():
        key = (score_row["metric_name"], score_row["metric_timestamp"])
        scores_lookup[key] = score_row["metric_value"]
    
    for _, row in metrics_df.iterrows():
        key = (row["metric_name"], row["metric_timestamp"])
        score = scores_lookup.get(key, 0)
        
        # Only create LLM alert if score is above threshold
        if score >= llm_threshold:
            # Generate explanatory metadata
            explanations = [
                f"Unusual spike detected in {row['metric_name']} with value {row['metric_value']:.2f}",
                f"Anomalous pattern observed: {row['metric_name']} shows irregular behavior",
                f"Alert: {row['metric_name']} has exceeded normal operating parameters",
                f"Significant deviation detected in {row['metric_name']} metrics"
            ]
            
            metadata = {
                "explanation": random.choice(explanations),
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "anomaly_type": random.choice(["spike", "trend", "outlier"])
            }
            
            llmalerts_data.append({
                "metric_timestamp": row["metric_timestamp"],
                "metric_batch": row["metric_batch"],
                "metric_name": row["metric_name"],
                "metric_value": 1.0,  # Always 1.0 since we only store triggered alerts
                "metric_type": "llmalert",
                "metadata": json.dumps(metadata)
            })
    
    return pd.DataFrame(llmalerts_data)


def generate_change_data(metrics_df: pd.DataFrame, target_change_rate: float = 0.02) -> pd.DataFrame:
    """Generate change detection data."""
    change_data = []
    
    # Calculate how many changes to generate
    total_metrics = len(metrics_df)
    num_changes = max(1, int(total_metrics * target_change_rate))
    
    # Randomly select metrics for change detection
    if num_changes > 0 and total_metrics > 0:
        sample_rows = metrics_df.sample(n=min(num_changes, total_metrics))
        
        for _, row in sample_rows.iterrows():
            change_data.append({
                "metric_timestamp": row["metric_timestamp"],
                "metric_batch": row["metric_batch"],
                "metric_name": row["metric_name"],
                "metric_value": 1.0,  # Always 1.0 since we only store detected changes
                "metric_type": "change",
                "metadata": None
            })
    
    return pd.DataFrame(change_data)


def generate_tholdalerts_data(metrics_df: pd.DataFrame, target_tholdalert_rate: float = 0.03) -> pd.DataFrame:
    """Generate threshold alerts with breach metadata."""
    tholdalerts_data = []
    
    # Calculate how many threshold alerts to generate
    total_metrics = len(metrics_df)
    num_alerts = max(1, int(total_metrics * target_tholdalert_rate))
    
    # Randomly select metrics for threshold alerts
    if num_alerts > 0 and total_metrics > 0:
        sample_rows = metrics_df.sample(n=min(num_alerts, total_metrics))
        
        for _, row in sample_rows.iterrows():
            metric_value = row["metric_value"]
            
            # Determine threshold type and value
            if random.random() < 0.5:
                # Upper threshold breach
                threshold_type = "upper"
                threshold_value = metric_value * random.uniform(0.7, 0.9)
                breach_explanation = f"Value {metric_value:.2f} exceeded upper threshold {threshold_value:.2f}"
            else:
                # Lower threshold breach  
                threshold_type = "lower"
                threshold_value = metric_value * random.uniform(1.1, 1.3)
                breach_explanation = f"Value {metric_value:.2f} fell below lower threshold {threshold_value:.2f}"
            
            metadata = {
                "threshold_type": threshold_type,
                "threshold_value": round(threshold_value, 4),
                "breach_explanation": breach_explanation,
                "severity": random.choice(["warning", "critical", "info"])
            }
            
            tholdalerts_data.append({
                "metric_timestamp": row["metric_timestamp"],
                "metric_batch": row["metric_batch"],
                "metric_name": row["metric_name"],
                "metric_value": 1.0,  # Always 1.0 since we only store triggered alerts
                "metric_type": "tholdalert",
                "metadata": json.dumps(metadata)
            })
    
    return pd.DataFrame(tholdalerts_data)


def main():
    parser = argparse.ArgumentParser(
        description="Flexible seed script for local DuckDB database with multiple metric batches"
    )
    
    parser.add_argument(
        "--metric-batches", 
        type=str, 
        default="python_ingest_simple",
        help="Comma-separated list of metric batches to seed (e.g., 'python_ingest_simple,netdata,posthog')"
    )
    parser.add_argument(
        "--db-path", 
        type=str, 
        default="tmpdata/anomstack-flexible.db",
        help="Path to the DuckDB database file (default: tmpdata/anomstack-flexible.db)"
    )
    parser.add_argument(
        "--hours", 
        type=int, 
        default=72,
        help="Hours of historical data to generate (default: 72)"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=10,
        help="Interval between data points in minutes (default: 10)"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Remove existing database if it exists"
    )
    parser.add_argument(
        "--alert-rate", 
        type=float, 
        default=0.05,
        help="Target rate for regular alerts (0.0-1.0, default: 0.05 = 5%%)"
    )
    parser.add_argument(
        "--llm-alert-rate", 
        type=float, 
        default=0.03,
        help="Target rate for LLM alerts (0.0-1.0, default: 0.03 = 3%%)"
    )
    parser.add_argument(
        "--threshold-alert-rate", 
        type=float, 
        default=0.03,
        help="Target rate for threshold alerts (0.0-1.0, default: 0.03 = 3%%)"
    )
    parser.add_argument(
        "--change-rate", 
        type=float, 
        default=0.02,
        help="Target rate for change detection (0.0-1.0, default: 0.02 = 2%%)"
    )
    
    args = parser.parse_args()
    
    # Parse metric batches
    metric_batches = [batch.strip() for batch in args.metric_batches.split(",")]
    
    # Validate metric batches
    supported_batches = ["python_ingest_simple", "netdata", "posthog", "yfinance", "currency"]
    for batch in metric_batches:
        if batch not in supported_batches:
            print(f"❌ Unsupported metric batch: {batch}")
            print(f"   Supported batches: {', '.join(supported_batches)}")
            sys.exit(1)
    
    # Check if database exists and handle force flag
    if os.path.exists(args.db_path):
        if args.force:
            os.remove(args.db_path)
            print(f"🗑️  Removed existing database at {args.db_path}")
        else:
            print(f"❌ Database already exists at {args.db_path}")
            print("   Use --force to overwrite, or specify a different --db-path")
            sys.exit(1)
    
    print(f"🌱 Seeding database with metric batches: {', '.join(metric_batches)}")
    print(f"   Database path: {args.db_path}")
    print(f"   Historical data: {args.hours} hours")
    print(f"   Data interval: {args.interval} minutes")
    print(f"   Alert rates: {args.alert_rate*100:.1f}% alerts, {args.llm_alert_rate*100:.1f}% LLM, {args.threshold_alert_rate*100:.1f}% threshold, {args.change_rate*100:.1f}% changes")
    print()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Connect to DuckDB
    conn = duckdb.connect(args.db_path)
    
    # Process each metric batch
    total_rows = 0
    
    for metric_batch in metric_batches:
        print(f"🔄 Processing metric batch: {metric_batch}")
        
        # Load the appropriate ingest function  
        ingest_fn = load_ingest_function(metric_batch)
        
        # Generate historical data for this batch
        dataframes = []
        total_intervals = (args.hours * 60) // args.interval
        
        print(f"   Generating {total_intervals} data points...")
        
        for i in range(total_intervals):
            # Calculate timestamp for this interval
            minutes_ago = i * args.interval
            timestamp = datetime.now() - timedelta(minutes=minutes_ago)
            
            try:
                # Generate data for this timestamp
                df = ingest_fn()
                df["metric_timestamp"] = timestamp
                
                # Process the base metrics dataframe
                metrics_df = wrangle_df(df, metric_batch)
                
                # Generate additional data types
                scores_df = generate_scores_data(metrics_df, args.alert_rate)
                alerts_df = generate_alerts_data(scores_df)
                llmalerts_df = generate_llmalerts_data(metrics_df, scores_df, args.llm_alert_rate)
                change_df = generate_change_data(metrics_df, args.change_rate)
                tholdalerts_df = generate_tholdalerts_data(metrics_df, args.threshold_alert_rate)
                
                # Combine all data types
                all_data = [metrics_df, scores_df, alerts_df, llmalerts_df, change_df, tholdalerts_df]
                combined_df = pd.concat([df for df in all_data if not df.empty], ignore_index=True)
                
                dataframes.append(combined_df)
                
                if (i + 1) % 50 == 0:
                    print(f"   Generated {i + 1}/{total_intervals} data points...")
                    
            except Exception as e:
                print(f"   Error generating data at timestamp {timestamp}: {e}")
                continue
        
        # Create table for this batch
        if dataframes:
            table_name = f"metrics_{metric_batch}"
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            print(f"   Inserting {len(combined_df)} rows into {table_name}")
            
            try:
                # Create table with explicit schema to ensure proper column types
                conn.execute(f"""
                CREATE TABLE {table_name} (
                    metric_timestamp TIMESTAMP,
                    metric_batch VARCHAR,
                    metric_name VARCHAR,
                    metric_value DOUBLE,
                    metric_type VARCHAR,  -- Explicitly set as VARCHAR to accept thumbsup/thumbsdown
                    metadata VARCHAR
                )
                """)
                
                # Insert data into the table
                conn.execute(f"INSERT INTO {table_name} SELECT * FROM combined_df")
                total_rows += len(combined_df)
                
                # Add indexes
                conn.execute(f"CREATE INDEX idx_{table_name}_timestamp ON {table_name}(metric_timestamp)")
                conn.execute(f"CREATE INDEX idx_{table_name}_batch_name ON {table_name}(metric_batch, metric_name)")
                conn.execute(f"CREATE INDEX idx_{table_name}_type ON {table_name}(metric_type)")
                
                print(f"   ✅ Successfully created {table_name} with {len(combined_df)} rows")
                
                # Show statistics for this batch
                stats_query = f"""
                SELECT 
                    metric_type,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT metric_name) as unique_metrics
                FROM {table_name} 
                GROUP BY metric_type 
                ORDER BY metric_type
                """
                
                stats_df = conn.execute(stats_query).df()
                print(f"   📊 {metric_batch} Statistics:")
                for _, stat_row in stats_df.iterrows():
                    print(f"      {stat_row['metric_type']}: {stat_row['total_rows']} rows, {stat_row['unique_metrics']} unique metrics")
                
            except Exception as e:
                print(f"   ❌ Error creating table {table_name}: {e}")
        else:
            print(f"   ⚠️  No data generated for {metric_batch}")
    
    conn.close()
    
    print(f"\n🎉 Flexible local development database is ready!")
    print(f"   Total rows across all tables: {total_rows}")
    print(f"   Tables created: {', '.join([f'metrics_{batch}' for batch in metric_batches])}")
    print(f"💡 To use this database with the dashboard:")
    print(f"   ANOMSTACK_DUCKDB_PATH={args.db_path} make dashboard-uvicorn")
    print(f"   # You'll see: {', '.join(metric_batches)} batches!")


if __name__ == "__main__":
    main() 