/*
Template for generating the input data for the change detection job.
*/

with

metric_value_data as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(metric_value) as metric_value
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'metric'
  and
  -- limit to the last {{ change_metric_timestamp_max_days_ago }} days
  cast(metric_timestamp as datetime) >= CURRENT_DATE - INTERVAL '{{ change_metric_timestamp_max_days_ago }}' DAY
group by 1,2,3
),

metric_value_recency_ranked as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_value_recency_rank
from
  metric_value_data
),

data_smoothed as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_value_recency_rank,
  -- smooth the metric value over the last {{ change_smooth_n }} values
  avg(metric_value) over (partition by metric_name order by metric_value_recency_rank rows between {{ change_smooth_n }} preceding and current row) as metric_value_smooth
from
  metric_value_recency_ranked
where
  -- only alert on the most recent {{ change_max_n }} values
  metric_value_recency_rank <= {{ change_max_n }}
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_value_smooth,
from
  data_smoothed
;
