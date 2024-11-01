/*
Template for generating input metric data for scoring.
*/

WITH

data AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    AVG(CASE WHEN metric_type = 'metric' THEN metric_value ELSE NULL END) AS metric_value,
    AVG(CASE WHEN metric_type = 'score' THEN metric_value ELSE NULL END) AS metric_score
  FROM {{ table_key }}
  WHERE metric_batch = '{{ metric_batch }}'
    AND metric_type IN ('metric', 'score')
  GROUP BY metric_timestamp, metric_batch, metric_name
),

data_ranked AS (
  SELECT
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY metric_timestamp DESC) AS metric_recency_rank
  FROM data
)

SELECT
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score
FROM data_ranked
WHERE
  -- Limit to the most recent {{ score_max_n }} records
  metric_recency_rank <= {{ score_max_n }}
;
