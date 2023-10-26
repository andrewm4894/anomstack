with

data as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(if(metric_type='metric',metric_value,null)) as metric_value,
  avg(if(metric_type='score',metric_value,null)) as metric_score,
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type in ('metric','score')
group by 1,2,3
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
  metric_recency_rank <= {{ score_max_n }}
;