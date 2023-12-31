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
  avg(metric_score) over (partition by metric_name order by metric_score_recency_rank rows between {{ alert_smooth_n }} preceding and current row) as metric_score_smooth,
  -- add a window function to check for previous alerts within the last {{ alert_snooze_n }} values
  max(metric_alert_historic) over (partition by metric_name order by metric_score_recency_rank desc rows between {{ alert_snooze_n }} preceding and 1 preceding) as metric_has_recent_alert
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
  metric_has_recent_alert,
  -- only alert on the most recent {{ alert_recent_n }} values
  -- only alert if the metric score is above the threshold or if the alert is forced
  -- only alert if the metric has not been alerted on in the last {{ alert_snooze_n }} values
  case
    when
      -- only alert on the most recent {{ alert_recent_n }} values
      metric_score_recency_rank <= {{ alert_recent_n }}
      and
      -- only alert if the metric score is above the threshold or if the alert is forced
      (metric_score_smooth >= {{ alert_threshold }} or {{ alert_always }} = True )
      and
      -- only alert if the metric has not been alerted on in the last {{ alert_snooze_n }} values
      metric_has_recent_alert = 0
    then
      1
    else
      0
    end as metric_alert_calculated
from
  data_smoothed
where
  -- limit data to the most recent {{ alert_max_n }} values
  metric_score_recency_rank <= {{ alert_max_n }}
),

metrics_triggered as
(
select
  metric_batch,
  metric_name,
  max(metric_alert_calculated) as metric_alert_calculated_tmp
from
  data_alerts
group by 1,2
having
  -- only return metrics that have been triggered
  max(metric_alert_calculated) = 1
)

select
  metric_timestamp,
  data_alerts.metric_batch as metric_batch,
  data_alerts.metric_name as metric_name,
  metric_value,
  metric_score,
  --metric_alert_historic,
  metric_score_smooth,
  if(metric_score_recency_rank=1,metric_alert_calculated,metric_alert_historic) as metric_alert
from
  data_alerts
-- only return metrics that have been triggered or not snoozed
join
  metrics_triggered
on
  data_alerts.metric_batch = metrics_triggered.metric_batch
  and
  data_alerts.metric_name = metrics_triggered.metric_name
;
