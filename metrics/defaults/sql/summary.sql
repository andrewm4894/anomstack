/*
Template for generating input metric data for summary.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/
select
  metric_batch,
  metric_name,
  max(metric_timestamp) as metric_timestamp_max,
  sum(case when metric_type = 'metric' then 1 else 0 end) as n_metric,
  sum(case when metric_type = 'score' then 1 else 0 end) as n_score,
  sum(case when metric_type = 'alert' then 1 else 0 end) as n_alert
from {{ table_key }}
where
  cast(metric_timestamp as timestamp) >= current_timestamp - interval '{{ summary_metric_timestamp_max_days_ago }} day'
group by metric_batch, metric_name
order by n_alert desc
;

