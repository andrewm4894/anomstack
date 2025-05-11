/*
Template for generating the input data for the train job.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

data as (
  select
    metric_timestamp,
    metric_name,
    avg(metric_value) as metric_value
  from {{ table_key }}
  where metric_batch = '{{ metric_batch }}'
    and metric_type = 'metric'
    and cast(metric_timestamp as timestamp) >= current_timestamp - interval '{{ train_metric_timestamp_max_days_ago }} day'
    {% if train_exclude_metrics is defined %}
    and metric_name not in ({{ ','.join(train_exclude_metrics) }})
    {% endif %}
  group by metric_timestamp, metric_name
),

data_ranked as (
  select
    metric_timestamp,
    metric_name,
    metric_value,
    row_number() over (partition by metric_name order by metric_timestamp desc) as metric_recency_rank
  from data
)

select
  metric_timestamp,
  metric_name,
  metric_value,
  metric_recency_rank
from data_ranked
where metric_recency_rank <= {{ train_max_n }}
  and metric_recency_rank >= {{ train_min_n }}
;
