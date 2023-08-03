with

data_ranked as
(
select
  *,
  rank() over (partition by metric_type, metric_batch, metric_name order by metric_timestamp desc) as metric_recency_rank
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'metric'
)

select
  *
from
  data_ranked
where
  metric_recency_rank <= {{ train_max_n }}
;