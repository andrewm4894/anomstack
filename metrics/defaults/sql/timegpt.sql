/*
Template for generating the input data for the timegptalert job.
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
  -- limit to the last {{ alert_metric_timestamp_max_days_ago }} days
  cast(metric_timestamp as datetime) >= CURRENT_DATE - INTERVAL '{{ alert_metric_timestamp_max_days_ago }}' DAY
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

data_ranked as 
(
select
  m.metric_timestamp,
  m.metric_batch,
  m.metric_name,
  m.metric_value,
  m.metric_value_recency_rank
from
  metric_value_recency_ranked m
),

data_timegpt as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value
from
  data_ranked
where
  -- only plot most recent {{ timegptalert_max_n }} values
  metric_value_recency_rank <= {{ timegptalert_max_n }}
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value
from
  data_timegpt
;