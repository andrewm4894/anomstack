with

data_ranked as
(
select
  *,
  rank() over (partition by metric_type, metric_batch, metric_name order by metric_timestamp desc) as metric_score_recency_rank
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'score'
),

data_smoothed as
(
select
  metric_batch,
  metric_name,
  avg(ifnull(metric_value,0)) as metric_score,
  min(metric_timestamp) as metric_timestamp_min,
  max(metric_timestamp) as metric_timestamp_max,
from
  data_ranked
where
  metric_score_recency_rank <= {{ alert_recent_n }}
group by 1,2
)

select
  *
from
  data_smoothed
where
  metric_score >= {{ alert_threshold }}
;