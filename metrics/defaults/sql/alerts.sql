with

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
  extract(day from cast(now() as timestamp) - cast(metric_timestamp as timestamp)) <= {{ alert_metric_timestamp_max_days_ago }}
group by 1,2,3
),

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
  extract(day from cast(now() as timestamp) - cast(metric_timestamp as timestamp)) <= {{ alert_metric_timestamp_max_days_ago }}
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
),

data_smoothed as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
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
  metric_score_smooth,
  -- only alert on the most recent {{ alert_max_n }} values
  if(metric_score_recency_rank <= {{ alert_recent_n }} and (metric_score_smooth >= {{ alert_threshold }} or {{ alert_always }}=True ), 1, 0) as metric_alert
from
  data_smoothed
where
  -- only alert on the most recent {{ alert_max_n }} values
  metric_score_recency_rank <= {{ alert_max_n }}
),

metrics_triggered as
(
select
  metric_batch,
  metric_name,
  max(metric_alert) as metric_alert_tmp
from 
  data_alerts
group by 1,2
having max(metric_alert) = 1
)

select
  metric_timestamp,
  data_alerts.metric_batch as metric_batch,
  data_alerts.metric_name as metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  metric_alert
from
  data_alerts
-- only return metrics that have been triggered
join
  metrics_triggered
on
  data_alerts.metric_batch = metrics_triggered.metric_batch
  and
  data_alerts.metric_name = metrics_triggered.metric_name
;