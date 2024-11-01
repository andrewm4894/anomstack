/*
Template for generating the input data for the plot job.
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
    AND DATE(metric_timestamp) >= DATE('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_score_data AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    AVG(metric_value) AS metric_score
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'score'
    AND DATE(metric_timestamp) >= DATE('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_alert_data AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    MAX(metric_value) AS metric_alert
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'alert'
    AND DATE(metric_timestamp) >= DATE('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_change_data AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    MAX(metric_value) AS metric_change
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'change'
    AND DATE(metric_timestamp) >= DATE('now', '-{{ change_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_value_recency_rank
  FROM metric_value_data
),

metric_score_recency_ranked AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_score,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_score_recency_rank
  FROM metric_score_data
),

data_ranked AS (
  SELECT
    m.metric_timestamp,
    m.metric_batch,
    m.metric_name,
    m.metric_value,
    s.metric_score,
    a.metric_alert,
    c.metric_change,
    m.metric_value_recency_rank,
    s.metric_score_recency_rank
  FROM metric_value_recency_ranked m
  LEFT JOIN metric_score_recency_ranked s
    ON m.metric_batch = s.metric_batch
    AND m.metric_name = s.metric_name
    AND m.metric_timestamp = s.metric_timestamp
  LEFT JOIN metric_alert_data a
    ON m.metric_batch = a.metric_batch
    AND m.metric_name = a.metric_name
    AND m.metric_timestamp = a.metric_timestamp
  LEFT JOIN metric_change_data c
    ON m.metric_batch = c.metric_batch
    AND m.metric_name = c.metric_name
    AND m.metric_timestamp = c.metric_timestamp
),

data_smoothed AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    metric_alert,
    metric_change,
    metric_value_recency_rank,
    metric_score_recency_rank,
    -- Use a subquery or custom logic to compute the moving average for smoothing
    (SELECT AVG(metric_score)
     FROM data_ranked ds
     WHERE ds.metric_batch = dr.metric_batch
     AND ds.metric_name = dr.metric_name
     AND ds.metric_score_recency_rank BETWEEN dr.metric_score_recency_rank - {{ alert_smooth_n }} AND dr.metric_score_recency_rank) AS metric_score_smooth
  FROM data_ranked dr
),

data_alerts AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    metric_score_smooth,
    metric_alert,
    metric_change
  FROM data_smoothed
  WHERE metric_value_recency_rank <= {{ alert_max_n }}
)

SELECT
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  metric_alert,
  metric_change
FROM data_alerts
;
