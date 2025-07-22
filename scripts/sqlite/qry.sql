-- read_sql() is about to read this qry:
/*
Template for generating the input data for the alert job.

Written for SQLite but will be translated to target dialect based on `db` param via sqlglot.
*/
WITH "metric_value_data" /* Filter the data to the relevant metric batch for metrics */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    AVG("metric_value") AS "metric_value"
  FROM "metrics_prometheus"
  WHERE
    "metric_batch" = 'prometheus'
    AND "metric_type" = 'metric'
    AND "metric_timestamp" >= DATE('now', '-45 day')
  GROUP BY
    "metric_timestamp",
    "metric_batch",
    "metric_name"
), "metric_score_data" /* Filter the data to the relevant metric batch for scores */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    AVG("metric_value") AS "metric_score"
  FROM "metrics_prometheus"
  WHERE
    "metric_batch" = 'prometheus'
    AND "metric_type" = 'score'
    AND "metric_timestamp" >= DATE('now', '-45 day')
  GROUP BY
    "metric_timestamp",
    "metric_batch",
    "metric_name"
), "metric_alert_data" /* Filter the data to the relevant metric batch for alerts */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    AVG("metric_value") AS "metric_alert_historic"
  FROM "metrics_prometheus"
  WHERE
    "metric_batch" = 'prometheus'
    AND "metric_type" = 'alert'
    AND "metric_timestamp" >= DATE('now', '-45 day')
  GROUP BY
    "metric_timestamp",
    "metric_batch",
    "metric_name"
), "metric_score_recency_ranked" /* Rank the score data by recency */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    "metric_score",
    ROW_NUMBER() OVER (PARTITION BY "metric_name" ORDER BY "metric_timestamp" DESC) AS "metric_score_recency_rank"
  FROM "metric_score_data"
), "metric_value_recency_ranked" /* Rank the value data by recency */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    "metric_value",
    ROW_NUMBER() OVER (PARTITION BY "metric_name" ORDER BY "metric_timestamp" DESC) AS "metric_value_recency_rank"
  FROM "metric_value_data"
), "data_ranked" /* Join the data together */ AS (
  SELECT
    "m"."metric_timestamp",
    "m"."metric_batch",
    "m"."metric_name",
    "m"."metric_value",
    "s"."metric_score",
    COALESCE("a"."metric_alert_historic", 0) AS "metric_alert_historic",
    "m"."metric_value_recency_rank",
    "s"."metric_score_recency_rank"
  FROM "metric_value_recency_ranked" AS "m"
  LEFT JOIN "metric_score_recency_ranked" AS "s"
    ON "m"."metric_name" = "s"."metric_name"
    AND "m"."metric_batch" = "s"."metric_batch"
    AND "m"."metric_timestamp" = "s"."metric_timestamp"
  LEFT JOIN "metric_alert_data" AS "a"
    ON "m"."metric_name" = "a"."metric_name"
    AND "m"."metric_batch" = "a"."metric_batch"
    AND "m"."metric_timestamp" = "a"."metric_timestamp"
), "data_smoothed" /* Smooth the data */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    "metric_value",
    "metric_score",
    "metric_alert_historic",
    "metric_value_recency_rank",
    "metric_score_recency_rank",
    (
      SELECT
        AVG("ds"."metric_score")
      FROM "data_ranked" AS "ds"
      WHERE
        "ds"."metric_name" = "dr"."metric_name"
        AND "ds"."metric_score_recency_rank" BETWEEN "dr"."metric_score_recency_rank" - 3 AND "dr"."metric_score_recency_rank"
    ) AS "metric_score_smooth", /* Smooth the metric score using a custom window */
    (
      SELECT
        MAX("ds"."metric_alert_historic")
      FROM "data_ranked" AS "ds"
      WHERE
        "ds"."metric_name" = "dr"."metric_name"
        AND "ds"."metric_score_recency_rank" BETWEEN "dr"."metric_score_recency_rank" - 3 AND "dr"."metric_score_recency_rank" - 1
    ) AS "metric_has_recent_alert" /* Check for recent alerts */
  FROM "data_ranked" AS "dr"
), "data_alerts" /* Calculate the alerts */ AS (
  SELECT
    "metric_timestamp",
    "metric_batch",
    "metric_name",
    "metric_value",
    "metric_score",
    "metric_score_recency_rank",
    "metric_alert_historic",
    "metric_score_smooth",
    "metric_has_recent_alert",
    CASE
      WHEN "metric_score_recency_rank" <= 1
      AND (
        "metric_score_smooth" >= 0.8 OR FALSE = TRUE
      )
      AND COALESCE("metric_has_recent_alert", 0) = 0
      THEN 1
      ELSE 0
    END AS "metric_alert_calculated"
  FROM "data_smoothed"
  WHERE
    "metric_score_recency_rank" <= 250
    OR FALSE /* flag for always alerting if set */ = TRUE
), "metrics_triggered" /* Filter the data to the metrics with triggered alerts */ AS (
  SELECT
    "metric_batch",
    "metric_name",
    MAX("metric_alert_calculated") AS "metric_alert_calculated_tmp"
  FROM "data_alerts"
  GROUP BY
    "metric_batch",
    "metric_name"
  HAVING
    MAX("metric_alert_calculated") = 1 OR FALSE = TRUE
)
/* Return the data */
SELECT
  "metric_timestamp",
  "data_alerts"."metric_batch" AS "metric_batch",
  "data_alerts"."metric_name" AS "metric_name",
  "metric_value",
  "metric_score",
  "metric_score_smooth",
  IIF("metric_score_recency_rank" = 1, "metric_alert_calculated", "metric_alert_historic") AS "metric_alert"
FROM "data_alerts"
JOIN "metrics_triggered"
  ON "data_alerts"."metric_batch" = "metrics_triggered"."metric_batch"
  AND "data_alerts"."metric_name" = "metrics_triggered"."metric_name"
