/*
Template for generating the input data for the change detection job.
*/

WITH

metric_value_data AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    AVG(metric_value) AS metric_value
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'metric'
    AND DATE(metric_timestamp) >= DATE('now', '-{{ change_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_value_recency_rank
  FROM metric_value_data
),

data_smoothed AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_value_recency_rank,
    -- Smooth the metric value over the last {{ change_smooth_n }} values
    (SELECT AVG(mv.metric_value)
     FROM metric_value_recency_ranked mv
     WHERE mv.metric_name = mr.metric_name
     AND mv.metric_value_recency_rank BETWEEN mr.metric_value_recency_rank - {{ change_smooth_n }} AND mr.metric_value_recency_rank) AS metric_value_smooth
  FROM metric_value_recency_ranked mr
  WHERE metric_value_recency_rank <= {{ change_max_n }}
)

SELECT
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_value_smooth
FROM data_smoothed
;
