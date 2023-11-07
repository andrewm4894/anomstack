with

data as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(case when metric_type='metric' then metric_value else null end) as metric_value,
  avg(case when metric_type='score' then metric_value else null end) as metric_score
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
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  rank() over (partition by metric_name order by metric_timestamp desc) as metric_recency_rank
from
  data
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score
from
  data_ranked
where
  metric_recency_rank <= {{ score_max_n }}
;
