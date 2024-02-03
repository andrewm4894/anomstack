select
  metric_batch,
  metric_name,
  max(metric_timestamp) as metric_timestamp_max,
  sum(if(metric_type='metric',1,0)) as n_metric,
  sum(if(metric_type='score',1,0)) as n_score,
  sum(if(metric_type='alert',1,0)) as n_alert,
from
  {{ table_key }}
where
  -- limit to the last {{ summary_metric_timestamp_max_days_ago }} days
  cast(metric_timestamp as datetime) >= CURRENT_DATE - INTERVAL '{{ summary_metric_timestamp_max_days_ago }}' DAY
group by 1,2
order by 6 desc
