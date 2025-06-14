# SQL File Pattern Example

This **Anomstack metric batch** demonstrates the best practice of separating SQL queries from YAML configuration files. Perfect for maintaining clean, readable code with proper syntax highlighting and version control benefits.

## Overview

This example shows how to:
- Separate SQL metric definitions from configuration using `.sql` files
- Maintain clean and readable SQL with proper syntax highlighting
- Enable better version control and collaboration on complex queries
- Structure metric batches for maintainability and reusability
- Follow software engineering best practices in data pipeline development

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Loads and executes the SQL file for data ingestion
2. **Train Job**: PyOD models train on the query results
3. **Score Job**: Generate anomaly scores for the metrics
4. **Alert Job**: Send notifications when anomalies are detected

### File Structure Benefits
```
example_sql_file/
├── README.md              # This documentation
├── example_sql_file.yaml  # Configuration only
└── example_sql_file.sql   # SQL query only
```

**vs. Inline SQL approach**:
```yaml
# Everything mixed together in YAML
metric_batch: 'example'
ingest_sql: >
  SELECT very_long_complex_query_here...
```

## Files

- **[`example_sql_file.sql`](example_sql_file.sql)**: Clean SQL query with proper formatting
- **[`example_sql_file.yaml`](example_sql_file.yaml)**: Configuration referencing the SQL file

## Configuration Details

The YAML file demonstrates the clean separation pattern:
```yaml
metric_batch: 'example_sql_file'
# Reference external SQL file instead of inline SQL
ingest_sql_file: 'example_sql_file.sql'
# All other configuration parameters
db: 'duckdb'
alert_threshold: 0.8
```

### Key Benefits

#### Code Organization
- **Separation of Concerns**: SQL logic separate from configuration
- **File Modularity**: Each file has a single, clear responsibility
- **Easier Navigation**: Quickly find SQL vs. configuration

#### Developer Experience  
- **Syntax Highlighting**: Full SQL highlighting in editors
- **Code Completion**: SQL-aware autocomplete and IntelliSense
- **Error Detection**: SQL linting and syntax validation
- **Formatting**: Auto-formatting tools work properly

#### Version Control
- **Cleaner Diffs**: Changes to SQL vs. config clearly separated
- **Better Reviews**: Reviewers can focus on SQL logic independently
- **Branching**: Different SQL versions can be developed in parallel

#### Collaboration
- **Role Separation**: SQL developers vs. configuration managers
- **Reusability**: SQL files can be shared across metric batches
- **Documentation**: Easier to document complex queries

## Setup & Usage

### Prerequisites
- Anomstack environment configured
- Database connection set up
- SQL query that returns required columns (`metric_timestamp`, `metric_name`, `metric_value`)

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/example_sql_file metrics/my_sql_batch
   ```

2. **Edit the SQL file**: Modify `example_sql_file.sql`:
   ```sql
   -- Clean, readable SQL with comments
   SELECT 
     created_at as metric_timestamp,
     'user_signups' as metric_name,
     COUNT(*) as metric_value
   FROM users 
   WHERE created_at >= NOW() - INTERVAL '1 day'
   GROUP BY DATE(created_at)
   ```

3. **Configure the YAML**: Update `example_sql_file.yaml`:
   ```yaml
   metric_batch: 'my_sql_batch'
   ingest_sql_file: 'example_sql_file.sql'  # Points to your SQL file
   db: 'your_database_type'
   ```

4. **Enable in Dagster**: The jobs will load and execute your SQL

## Advanced SQL Patterns

### Complex Business Logic
```sql
-- example_sql_file.sql
-- Sales performance metrics with business rules
WITH daily_sales AS (
  SELECT 
    DATE(order_date) as date,
    SUM(amount) as daily_revenue,
    COUNT(*) as daily_orders,
    COUNT(DISTINCT customer_id) as daily_customers
  FROM orders 
  WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(order_date)
),
sales_metrics AS (
  SELECT 
    date as metric_timestamp,
    'daily_revenue' as metric_name,
    daily_revenue as metric_value
  FROM daily_sales
  
  UNION ALL
  
  SELECT 
    date as metric_timestamp,
    'daily_orders' as metric_name,
    daily_orders as metric_value
  FROM daily_sales
  
  UNION ALL
  
  SELECT 
    date as metric_timestamp,
    'avg_order_value' as metric_name,
    daily_revenue / NULLIF(daily_orders, 0) as metric_value
  FROM daily_sales
)
SELECT * FROM sales_metrics
ORDER BY metric_timestamp DESC;
```

### Multi-Table Joins
```sql
-- Complex joins with proper formatting
SELECT 
  u.created_at as metric_timestamp,
  CASE 
    WHEN u.subscription_tier = 'premium' THEN 'premium_signups'
    WHEN u.subscription_tier = 'basic' THEN 'basic_signups'
    ELSE 'free_signups'
  END as metric_name,
  COUNT(*) as metric_value
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id
LEFT JOIN user_profiles p ON u.id = p.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL '7 days'
  AND u.status = 'active'
  AND p.email_verified = true
GROUP BY 
  DATE(u.created_at),
  u.subscription_tier
ORDER BY u.created_at DESC;
```

### Conditional Metrics
```sql
-- Dynamic metrics based on conditions
SELECT 
  event_timestamp as metric_timestamp,
  event_type || '_' || LOWER(event_category) as metric_name,
  COUNT(*) as metric_value
FROM events 
WHERE event_timestamp >= NOW() - INTERVAL '1 hour'
  AND event_type IN ('click', 'view', 'purchase', 'signup')
GROUP BY 
  DATE_TRUNC('minute', event_timestamp),
  event_type,
  event_category
HAVING COUNT(*) > 0;  -- Only include metrics with activity
```

## SQL File Organization Patterns

### Single Metric Batch
```
my_batch/
├── my_batch.yaml     # Configuration
├── my_batch.sql      # Main query
└── README.md         # Documentation
```

### Multiple Related SQL Files
```
ecommerce_metrics/
├── ecommerce_metrics.yaml       # Main configuration
├── sales_metrics.sql            # Sales-related queries
├── user_metrics.sql             # User behavior queries  
├── inventory_metrics.sql        # Inventory tracking
└── README.md                    # Batch documentation
```

### Shared SQL Components
```
shared/
├── common_filters.sql           # Reusable WHERE clauses
├── date_functions.sql           # Date utility functions
└── business_rules.sql           # Common business logic

my_batch/
├── my_batch.yaml
├── my_batch.sql                 # Imports from shared/
└── README.md
```

## Database-Specific Considerations

### DuckDB (Default)
```sql
-- DuckDB-specific functions
SELECT 
  NOW() as metric_timestamp,
  'random_metric' as metric_name,
  RANDOM() * 100 as metric_value
```

### BigQuery
```sql
-- BigQuery-specific syntax
SELECT 
  CURRENT_TIMESTAMP() as metric_timestamp,
  'bigquery_metric' as metric_name,
  RAND() * 100 as metric_value
```

### Snowflake
```sql
-- Snowflake-specific syntax
SELECT 
  CURRENT_TIMESTAMP() as metric_timestamp,
  'snowflake_metric' as metric_name,
  UNIFORM(1, 100, RANDOM()) as metric_value
```

## Best Practices

### SQL Style Guide
- Use consistent indentation (2 or 4 spaces)
- Put commas at the beginning of lines for easier editing
- Use meaningful aliases
- Add comments explaining business logic
- Capitalize SQL keywords

### Error Handling
```sql
-- Handle potential NULL values and edge cases
SELECT 
  COALESCE(event_timestamp, CURRENT_TIMESTAMP) as metric_timestamp,
  CONCAT('events_', COALESCE(event_type, 'unknown')) as metric_name,
  COALESCE(COUNT(*), 0) as metric_value
FROM events 
WHERE event_timestamp >= NOW() - INTERVAL '1 day'
GROUP BY event_type;
```

### Performance Optimization
```sql
-- Use appropriate indexes and query patterns
SELECT 
  DATE_TRUNC('hour', created_at) as metric_timestamp,
  'hourly_signups' as metric_name,
  COUNT(*) as metric_value
FROM users 
WHERE created_at >= NOW() - INTERVAL '24 hours'  -- Narrow time window
  AND status = 'active'                          -- Use indexed columns
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY metric_timestamp DESC;
```

## Integration with Anomstack Features

- **Dashboard**: SQL results automatically appear in FastHTML dashboard
- **Alerts**: Complex SQL-derived metrics trigger intelligent alerts
- **Change Detection**: Sophisticated queries can detect business rule changes
- **Version Control**: Track SQL changes alongside configuration changes
- **Testing**: Easier to test SQL queries independently of configuration

This pattern provides the foundation for maintainable, professional-grade metric batch development with Anomstack.
