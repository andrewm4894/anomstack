/*
Template for generating the input data for the train job.
*/

WITH 

data AS (
  SELECT
    metric_timestamp,
    metric_name,
    AVG(metric_value) AS metric_value
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'metric'
  GROUP BY metric_timestamp, metric_name
),

data_ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_recency_rank
  FROM data
)

SELECT
  *
FROM data_ranked
WHERE
  -- Only include the most recent {{ train_max_n }} records
  metric_recency_rank <= {{ train_max_n }}
  AND
  -- Must be at least {{ train_min_n }} records
  metric_recency_rank >= {{ train_min_n }}
;
