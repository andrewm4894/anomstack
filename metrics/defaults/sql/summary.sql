SELECT
  metric_batch,
  metric_name,
  MAX(metric_timestamp) AS metric_timestamp_max,
  SUM(CASE WHEN metric_type = 'metric' THEN 1 ELSE 0 END) AS n_metric,
  SUM(CASE WHEN metric_type = 'score' THEN 1 ELSE 0 END) AS n_score,
  SUM(CASE WHEN metric_type = 'alert' THEN 1 ELSE 0 END) AS n_alert
FROM {{ table_key }}
WHERE
  -- Limit to the last {{ summary_metric_timestamp_max_days_ago }} days
  DATE(metric_timestamp) >= DATE('now', '-{{ summary_metric_timestamp_max_days_ago }} day')
GROUP BY metric_batch, metric_name
ORDER BY n_alert DESC
;
