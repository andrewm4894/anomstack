/*
Template for generating the input data for the alert job.
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
    AVG(metric_value) AS metric_alert_historic
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type = 'alert'
    AND DATE(metric_timestamp) >= DATE('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

metric_score_recency_ranked AS (
  SELECT DISTINCT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_score,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_score_recency_rank
  FROM metric_score_data
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

data_ranked AS (
  SELECT
    m.metric_timestamp,
    m.metric_batch,
    m.metric_name,
    m.metric_value,
    s.metric_score,
    IFNULL(a.metric_alert_historic, 0) AS metric_alert_historic,
    m.metric_value_recency_rank,
    s.metric_score_recency_rank
  FROM metric_value_recency_ranked m
  LEFT JOIN metric_score_recency_ranked s
    ON m.metric_name = s.metric_name
    AND m.metric_batch = s.metric_batch
    AND m.metric_timestamp = s.metric_timestamp
  LEFT JOIN metric_alert_data a
    ON m.metric_name = a.metric_name
    AND m.metric_batch = a.metric_batch
    AND m.metric_timestamp = a.metric_timestamp
),

data_smoothed AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    metric_alert_historic,
    metric_value_recency_rank,
    metric_score_recency_rank,
    -- Smooth the metric score using a custom window
    (SELECT AVG(ds.metric_score)
     FROM data_ranked ds
     WHERE ds.metric_name = dr.metric_name
     AND ds.metric_score_recency_rank BETWEEN dr.metric_score_recency_rank - {{ alert_smooth_n }} AND dr.metric_score_recency_rank) AS metric_score_smooth,
    -- Check for recent alerts
    (SELECT MAX(ds.metric_alert_historic)
     FROM data_ranked ds
     WHERE ds.metric_name = dr.metric_name
     AND ds.metric_score_recency_rank BETWEEN dr.metric_score_recency_rank - {{ alert_snooze_n }} AND dr.metric_score_recency_rank - 1) AS metric_has_recent_alert
  FROM data_ranked dr
),

data_alerts AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    metric_score_recency_rank,
    metric_alert_historic,
    metric_score_smooth,
    metric_has_recent_alert,
    CASE
      WHEN metric_score_recency_rank <= {{ alert_recent_n }}
        AND (metric_score_smooth >= {{ alert_threshold }} OR {{ alert_always }} = 1)
        AND metric_has_recent_alert = 0
      THEN 1
      ELSE 0
    END AS metric_alert_calculated
  FROM data_smoothed
  WHERE metric_score_recency_rank <= {{ alert_max_n }}
),

metrics_triggered AS (
  SELECT
    metric_batch,
    metric_name,
    MAX(metric_alert_calculated) AS metric_alert_calculated_tmp
  FROM data_alerts
  GROUP BY metric_batch, metric_name
  HAVING MAX(metric_alert_calculated) = 1
)

SELECT
  metric_timestamp,
  data_alerts.metric_batch AS metric_batch,
  data_alerts.metric_name AS metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  IF(metric_score_recency_rank = 1, metric_alert_calculated, metric_alert_historic) AS metric_alert
FROM data_alerts
JOIN metrics_triggered
  ON data_alerts.metric_batch = metrics_triggered.metric_batch
  AND data_alerts.metric_name = metrics_triggered.metric_name
;
