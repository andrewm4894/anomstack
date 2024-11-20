/*
Template for generating the input data for the alert job.

Written for SQLite but will be translated to target dialect based on `db` param via sqlglot.
*/

with

-- Filter the data to the relevant metric batch for metrics
metric_value_data as (
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
  date(metric_timestamp) >= date('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
group by metric_timestamp, metric_batch, metric_name
),

-- Filter the data to the relevant metric batch for scores
metric_score_data as (
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
  date(metric_timestamp) >= date('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
group by metric_timestamp, metric_batch, metric_name
),

-- Filter the data to the relevant metric batch for alerts
metric_alert_data as (
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
  date(metric_timestamp) >= date('now', '-{{ alert_metric_timestamp_max_days_ago }} day')
group by metric_timestamp, metric_batch, metric_name
),

-- Rank the score data by recency
metric_score_recency_ranked as (
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_score,
  row_number() over (partition by metric_name order by metric_timestamp desc) as metric_score_recency_rank
from 
  metric_score_data
),

-- Rank the value data by recency
metric_value_recency_ranked as (
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  row_number() over (partition by metric_name order by metric_timestamp desc) as metric_value_recency_rank
from 
  metric_value_data
),

-- Join the data together
data_ranked as (
select
  m.metric_timestamp,
  m.metric_batch,
  m.metric_name,
  m.metric_value,
  s.metric_score,
  ifnull(a.metric_alert_historic, 0) as metric_alert_historic,
  m.metric_value_recency_rank,
  s.metric_score_recency_rank
from 
  metric_value_recency_ranked m
left join 
  metric_score_recency_ranked s
on 
  m.metric_name = s.metric_name
  and 
  m.metric_batch = s.metric_batch
  and 
  m.metric_timestamp = s.metric_timestamp
left join 
  metric_alert_data a
on 
  m.metric_name = a.metric_name
  and 
  m.metric_batch = a.metric_batch
  and 
  m.metric_timestamp = a.metric_timestamp
),

-- Smooth the data
data_smoothed as (
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_alert_historic,
  metric_value_recency_rank,
  metric_score_recency_rank,
  -- Smooth the metric score using a custom window
  (select avg(ds.metric_score)
    from data_ranked ds
    where ds.metric_name = dr.metric_name
    and ds.metric_score_recency_rank between dr.metric_score_recency_rank - {{ alert_smooth_n }} and dr.metric_score_recency_rank
  ) as metric_score_smooth,
  -- Check for recent alerts
  (select max(ds.metric_alert_historic)
    from data_ranked ds
    where ds.metric_name = dr.metric_name
    and ds.metric_score_recency_rank between dr.metric_score_recency_rank - {{ alert_snooze_n }} and dr.metric_score_recency_rank - 1
  ) as metric_has_recent_alert
from 
  data_ranked dr
),

-- Calculate the alerts
data_alerts as (
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
  case
    when 
      metric_score_recency_rank <= {{ alert_recent_n }}
      and 
      (metric_score_smooth >= {{ alert_threshold }} OR {{ alert_always }} = True)
      and 
      ifnull(metric_has_recent_alert,0) = 0
    then 1
    else 0
  end as metric_alert_calculated
from 
  data_smoothed
where 
  metric_score_recency_rank <= {{ alert_max_n }} 
  or 
  -- flag for always alerting if set
  {{ alert_always }} = True
),

-- Filter the data to the metrics with triggered alerts
metrics_triggered as (
select
  metric_batch,
  metric_name,
  max(metric_alert_calculated) as metric_alert_calculated_tmp
from 
  data_alerts
group by metric_batch, metric_name
having max(metric_alert_calculated) = 1 or {{ alert_always }} = True
)

-- Return the data
select
  metric_timestamp,
  data_alerts.metric_batch as metric_batch,
  data_alerts.metric_name as metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  if(metric_score_recency_rank = 1, metric_alert_calculated, metric_alert_historic) as metric_alert
from 
  data_alerts
join 
  metrics_triggered
on 
  data_alerts.metric_batch = metrics_triggered.metric_batch
  and
  data_alerts.metric_name = metrics_triggered.metric_name
;
