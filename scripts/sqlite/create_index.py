from anomstack.external.sqlite import run_sql_sqlite


def add_indexes_to_metrics():
    # Get the list of tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = run_sql_sqlite(tables_query)

    if not tables:
        print("No tables found.")
        return

    for table_row in tables:
        table = table_row[0]  # Extract table name from row tuple

        # Check if the table contains 'metric_timestamp', 'metric_batch', or 'metric_type'
        columns_query = f"PRAGMA table_info({table});"
        columns = run_sql_sqlite(columns_query)

        column_names = [col[1] for col in columns]  # Extract column names

        # Create index on metric_timestamp if it exists
        if "metric_timestamp" in column_names:
            index_query = f"CREATE INDEX IF NOT EXISTS idx_{table}_metric_timestamp ON {table} (metric_timestamp);"
            run_sql_sqlite(index_query)
            print(f"Index created for metric_timestamp in table: {table}")

        # Create index on metric_batch if it exists
        if "metric_batch" in column_names:
            index_query = f"CREATE INDEX IF NOT EXISTS idx_{table}_metric_batch ON {table} (metric_batch);"
            run_sql_sqlite(index_query)
            print(f"Index created for metric_batch in table: {table}")

        # Create index on metric_type if it exists
        if "metric_type" in column_names:
            index_query = f"CREATE INDEX IF NOT EXISTS idx_{table}_metric_type ON {table} (metric_type);"
            run_sql_sqlite(index_query)
            print(f"Index created for metric_type in table: {table}")

# Run the function
add_indexes_to_metrics()
