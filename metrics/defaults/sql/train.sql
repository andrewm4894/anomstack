/*
Template for generating the input data for the train job.
*/

with

data as
(
select
  metric_timestamp,
  metric_name,
  avg(metric_value) AS metric_value
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'metric'
  {% if train_exclude_metrics is defined %}
  and
  -- Exclude the specified metrics
  metric_name not in ({{ ','.join(train_exclude_metrics) }})
  {% endif %}
group by metric_timestamp, metric_name
),

data_ranked as
(
select
  *,
  row_number() over (partition by metric_name order by metric_timestamp desc) as metric_recency_rank
from
  data
)

select
  *
from
  data_ranked
where
  -- Only include the most recent {{ train_max_n }} records
  metric_recency_rank <= {{ train_max_n }}
  and
  -- Must be at least {{ train_min_n }} records
  metric_recency_rank >= {{ train_min_n }}
;
