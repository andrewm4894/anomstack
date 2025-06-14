# SQL Utilities

This directory contains utilities for SQL query processing, execution, and database interactions within Anomstack.

## Overview

The `sql` module provides standardized interfaces for working with SQL across different database backends, enabling Anomstack to query metrics from various data platforms consistently.

## Components

### `read.py`
- **Purpose**: SQL query execution and result processing
- **Functions**:
  - Execute SQL queries against configured databases
  - Handle query parameterization and templating
  - Process query results into standardized dataframes
  - Manage database connections and connection pooling
  - Implement query caching for performance

### `utils.py`
- **Purpose**: Common SQL utility functions
- **Functions**:
  - SQL query validation and syntax checking
  - Query optimization and analysis
  - Database schema introspection
  - Common SQL pattern helpers
  - Error handling and logging utilities

### `translate.py`
- **Purpose**: SQL dialect translation and compatibility
- **Functions**:
  - Translate queries between different SQL dialects
  - Handle database-specific syntax differences
  - Provide compatibility layers for various backends
  - Abstract common SQL operations across platforms

## Supported Database Backends

The SQL utilities work with multiple database systems:

- **BigQuery**: Google Cloud's data warehouse
- **Snowflake**: Cloud data platform
- **ClickHouse**: OLAP database for analytics
- **DuckDB**: Analytics database (local and MotherDuck)
- **SQLite**: Lightweight database for development
- **PostgreSQL**: Popular relational database
- **And more...**

## Query Execution Flow

1. **Query Template Loading**: Load SQL from `.sql` files
2. **Parameter Substitution**: Replace template variables
3. **Dialect Translation**: Adapt query for target database
4. **Query Execution**: Execute against the database
5. **Result Processing**: Convert to standardized dataframe
6. **Caching**: Store results for subsequent use

## SQL File Structure

Anomstack expects SQL files to follow this structure:

```sql
-- metrics/your_batch/your_metric.sql
SELECT 
    timestamp_column as ds,
    metric_value as y,
    additional_dimensions
FROM your_table
WHERE timestamp_column >= '{start_date}'
  AND timestamp_column < '{end_date}'
ORDER BY timestamp_column
```

## Query Templating

SQL queries support Jinja2 templating for dynamic content:

```sql
SELECT 
    {{ timestamp_col }} as ds,
    {{ metric_col }} as y
FROM {{ table_name }}
WHERE {{ timestamp_col }} >= '{{ start_date }}'
{% if end_date %}
  AND {{ timestamp_col }} < '{{ end_date }}'
{% endif %}
{% if additional_filters %}
  AND {{ additional_filters }}
{% endif %}
ORDER BY {{ timestamp_col }}
```

## Configuration Parameters

SQL execution can be configured through metric batch YAML files:

```yaml
# Database connection
data_source: bigquery
data_source_params:
  project_id: "your-project"
  dataset_id: "your_dataset"

# Query parameters
sql_params:
  timestamp_col: "created_at"
  metric_col: "revenue"
  table_name: "sales_data"

# Performance settings
query_timeout: 300
max_results: 1000000
enable_cache: true
```

## Error Handling

The SQL utilities implement comprehensive error handling:

- **Connection Errors**: Retry logic for network issues
- **Query Errors**: Detailed error messages with query context
- **Timeout Handling**: Graceful handling of long-running queries
- **Permission Errors**: Clear messages for access issues
- **Data Type Errors**: Automatic type conversion when possible

## Performance Optimization

- **Query Caching**: Cache results to avoid repeated execution
- **Connection Pooling**: Reuse database connections
- **Lazy Loading**: Only execute queries when results are needed
- **Result Streaming**: Handle large result sets efficiently
- **Query Optimization**: Analyze and optimize SQL queries

## Common Usage Patterns

### Basic Query Execution
```python
from anomstack.sql.read import execute_sql

# Execute a SQL query
df = execute_sql(
    sql_file="metrics/sales/daily_revenue.sql",
    params={
        "start_date": "2023-12-01",
        "end_date": "2023-12-31"
    },
    data_source="bigquery"
)
```

### Query Validation
```python
from anomstack.sql.utils import validate_sql

# Validate SQL syntax
is_valid = validate_sql(
    sql_content=sql_query,
    dialect="bigquery"
)
```

### Dialect Translation
```python
from anomstack.sql.translate import translate_query

# Translate query between dialects
postgres_query = translate_query(
    sql_query=bigquery_sql,
    source_dialect="bigquery",
    target_dialect="postgresql"
)
```

## SQL Best Practices

1. **Use Parameterized Queries**: Prevent SQL injection and enable reuse
2. **Include Proper Filtering**: Always filter by timestamp ranges
3. **Order Results**: Sort by timestamp for time series analysis
4. **Handle Nulls**: Explicitly handle null values in queries
5. **Optimize Performance**: Use appropriate indexes and partitioning
6. **Test Queries**: Validate queries against sample data

## Query Requirements

For Anomstack compatibility, SQL queries should:

- Return at least two columns: timestamp (`ds`) and metric value (`y`)
- Include proper date/time filtering parameters
- Sort results by timestamp in ascending order
- Handle missing or null values appropriately
- Use consistent column naming conventions

## Troubleshooting

### Common Issues

1. **Connection failures**: Check database credentials and network
2. **Query timeouts**: Optimize queries or increase timeout settings
3. **Permission denied**: Verify database access permissions
4. **Syntax errors**: Validate SQL syntax for target dialect
5. **Large result sets**: Implement pagination or result limits

### Debugging

Enable SQL debugging:
```python
import logging
logging.getLogger('anomstack.sql').setLevel(logging.DEBUG)
```

This will log all executed queries and their parameters for troubleshooting. 