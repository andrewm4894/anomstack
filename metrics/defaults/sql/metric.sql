with

data_ranked as
(
  select
    *,
    rank() over (partition by metric_type, metric_batch, metric_name order by metric_timestamp desc) as metric_recency_rank
  from
    `{{ table_key }}`
  where
    metric_batch = '{{ metric_batch }}'
    and
    metric_type in ('metric', 'score')
    and
    metric_name = '{{ metric_name }}'
),

data_with_score as
(
  select
    metric_timestamp,
    metric_name,
    avg(if(metric_type='metric',metric_value,null)) as metric_value,
    ifnull(avg(if(metric_type='score',metric_value,null)),0) as metric_score
  from
    data_ranked
  where
    metric_recency_rank <= {{ alert_max_n }}
  group by 1,2
),

data_smoothed as
(
select
  metric_timestamp,
  metric_name,
  metric_value,
  metric_score,
  avg(metric_score) over (
    order by metric_timestamp
    rows between {{ alert_smooth_n }} preceding and current row
  ) as metric_score_smoothed
from
  data_with_score
order by metric_timestamp desc
)

select
  *,
  if(metric_score_smoothed >= {{ alert_threshold }},1,0) as metric_alert
from
  data_smoothed
;