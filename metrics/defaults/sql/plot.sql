/*
Template for generating the input data for the plot job.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

metric_value_data as 
(
select
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
  cast(metric_timestamp as timestamp) >= current_timestamp - interval '{{ alert_metric_timestamp_max_days_ago }}' day
group by 1,2,3
),

metric_score_data as 
(
select
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
  metric_timestamp >= current_date - interval '{{ alert_metric_timestamp_max_days_ago }}' day
group by 1,2,3
),

metric_alert_data as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  max(metric_value) as metric_alert
from 
  {{ table_key }}
where 
  metric_batch = '{{ metric_batch }}'
  and 
  metric_type = 'alert'
  and 
  metric_timestamp >= current_date - interval '{{ alert_metric_timestamp_max_days_ago }}' day
group by 1,2,3
),

metric_change_data as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  max(metric_value) as metric_change
from 
  {{ table_key }}
where 
  metric_batch = '{{ metric_batch }}'
  and 
  metric_type = 'change'
  and
  metric_timestamp >= current_date - interval '{{ change_metric_timestamp_max_days_ago }}' day 
group by 1,2,3
),

metric_value_recency_ranked as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_value_recency_rank
from 
  metric_value_data
),

metric_score_recency_ranked as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_score,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_score_recency_rank
from 
  metric_score_data
),

data_ranked as 
(
select
  m.metric_timestamp,
  m.metric_batch,
  m.metric_name,
  m.metric_value,
  s.metric_score,
  a.metric_alert,
  c.metric_change,
  m.metric_value_recency_rank,
  s.metric_score_recency_rank
from 
  metric_value_recency_ranked m
left join
  metric_score_recency_ranked s
on 
  m.metric_batch = s.metric_batch
  and 
  m.metric_name = s.metric_name
  and 
  m.metric_timestamp = s.metric_timestamp
left join
  metric_alert_data a
on 
  m.metric_batch = a.metric_batch
  and 
  m.metric_name = a.metric_name
  and 
  m.metric_timestamp = a.metric_timestamp
left join
  metric_change_data c
on 
  m.metric_batch = c.metric_batch
  and 
  m.metric_name = c.metric_name
  and 
  m.metric_timestamp = c.metric_timestamp
),

data_smoothed as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_alert,
  metric_change,
  metric_value_recency_rank,
  metric_score_recency_rank,
  avg(metric_score) over (
        partition by metric_batch, metric_name
        order by metric_score_recency_rank
        rows between {{ alert_smooth_n }} preceding and current row
    ) AS metric_score_smooth
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
  ifnull(metric_alert,0) as metric_alert,
  ifnull(metric_change,0) as metric_change
from 
  data_smoothed
where
  metric_value_recency_rank <= {{ alert_max_n }}
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  metric_alert,
  metric_change
from 
  data_alerts
;
