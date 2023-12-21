/*
Template for generating the input data for the alert job.
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

metric_score_data as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(metric_value) as metric_score
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'score'
  and
  -- limit to the last {{ alert_metric_timestamp_max_days_ago }} days
  cast(metric_timestamp as datetime) >= CURRENT_DATE - INTERVAL '{{ alert_metric_timestamp_max_days_ago }}' DAY
group by 1,2,3
),

metric_alert_data as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(metric_value) as metric_alert_historic
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'alert'
  and
  -- limit to the last {{ alert_metric_timestamp_max_days_ago }} days
  cast(metric_timestamp as datetime) >= CURRENT_DATE - INTERVAL '{{ alert_metric_timestamp_max_days_ago }}' DAY
group by 1,2,3
),

metric_score_recency_ranked as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_score,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_score_recency_rank
from
  metric_score_data
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
  s.metric_score,
  ifnull(a.metric_alert_historic,0) as metric_alert_historic,
  m.metric_value_recency_rank,
  s.metric_score_recency_rank
from
  metric_value_recency_ranked m
left outer join
  metric_score_recency_ranked s
on
  m.metric_name = s.metric_name
  and
  m.metric_batch = s.metric_batch
  and
  m.metric_timestamp = s.metric_timestamp
left outer join
  metric_alert_data a
on
  m.metric_name = a.metric_name
  and
  m.metric_batch = a.metric_batch
  and
  m.metric_timestamp = a.metric_timestamp
),

data_smoothed as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_alert_historic,
  metric_value_recency_rank,
  metric_score_recency_rank,
  -- smooth the metric score over the last {{ alert_smooth_n }} values
  avg(metric_score) over (partition by metric_name order by metric_score_recency_rank rows between {{ alert_smooth_n }} preceding and current row) as metric_score_smooth
from
  data_ranked
),

data_alerts as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_score_recency_rank,
  metric_alert_historic,
  metric_score_smooth,
  -- only alert on the most recent {{ alert_max_n }} values
  case when metric_score_recency_rank <= {{ alert_recent_n }} and (metric_score_smooth >= {{ alert_threshold }} or {{ alert_always }}=True ) then 1 else 0 end as metric_alert_calculated
from
  data_smoothed
where
  -- only alert on the most recent {{ alert_max_n }} values
  metric_score_recency_rank <= {{ alert_max_n }}
)

select
  metric_timestamp,
  data_alerts.metric_batch as metric_batch,
  data_alerts.metric_name as metric_name,
  metric_value,
  metric_score,
  metric_score_recency_rank,
  metric_alert_historic,
  metric_score_smooth,
  metric_alert_calculated,
  if(metric_score_recency_rank=1,metric_alert_calculated,metric_alert_historic) as metric_alert
from
  data_alerts
;
