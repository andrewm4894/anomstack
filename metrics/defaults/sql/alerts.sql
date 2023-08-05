with

metric_score_recency_ranked as
(
select
  metric_timestamp,
  metric_name,
  metric_value as metric_score,
  rank() over (partition by metric_type, metric_batch, metric_name order by metric_timestamp desc) as metric_score_recency_rank
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'score'
),

metric_value_recency_ranked as
(
select
  metric_timestamp,
  metric_name,
  metric_value,
  rank() over (partition by metric_type, metric_batch, metric_name order by metric_timestamp desc) as metric_value_recency_rank
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'value'
),

data_ranked as 
(
select
  m.metric_timestamp,
  m.metric_name,
  m.metric_value,
  s.metric_score,
  m.metric_value_recency_rank,
  s.metric_score_recency_rank,
from
  metric_value_recency_ranked m
left outer join
  metric_score_recency_ranked s
on 
  m.metric_name = s.metric_name
  and
  m.metric_timestamp = s.metric_timestamp
),

data_smoothed as
(
select
  metric_timestamp,
  metric_name,
  metric_value,
  metric_score,
  metric_value_recency_rank,
  metric_score_recency_rank,
  avg(metric_score) over (partition by metric_name order by metric_score_recency_rank rows between {{ alert_smooth_n }} preceding and current row) as metric_score_smooth
from 
  data_ranked
),

data_alerts as
(
select
  metric_timestamp,
  metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  if(metric_score_recency_rank <= {{ alert_recent_n }} and metric_score_smooth >= {{ alert_threshold }}, 1, 0) as alert
from
  data_smoothed
where
  metric_score_recency_rank <= {{ alert_max_n }}
),

metrics_triggered as
(
select
  metric_name,
  max(alert) as alert
from 
  data_alerts
group by 1
having max(alert) = 1
)

select
  metric_timestamp,
  a.metric_name,
  metric_value,
  metric_score,
  metric_score_smooth,
  a.alert
from
  data_alerts a
join
  metrics_triggered t
on
  a.metric_name = t.metric_name
;