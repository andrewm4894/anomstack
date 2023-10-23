with

data as
(
select
  metric_timestamp,
  metric_name,
  avg(metric_value) as metric_value
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'metric'
group by 1,2
),

data_ranked as
(
select
  *,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_recency_rank
from
  data
)

select
  *
from
  data_ranked
where
  metric_recency_rank <= {{ train_max_n }}
  and
  metric_recency_rank >= {{ train_min_n }}
;