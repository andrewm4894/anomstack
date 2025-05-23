/*
Template for generating input metric data for scoring.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(case when metric_type = 'metric' then metric_value else null end) as metric_value,
    avg(case when metric_type = 'score' then metric_value else null end) as metric_score
  from {{ table_key }}
  where metric_batch = '{{ metric_batch }}'
    and metric_type in ('metric', 'score')
    and cast(metric_timestamp as timestamp) >= current_timestamp - interval '{{ score_metric_timestamp_max_days_ago }} day'
    {% if score_exclude_metrics is defined %}
    and metric_name not in ({{ ','.join(score_exclude_metrics) }})
    {% endif %}
  group by metric_timestamp, metric_batch, metric_name
),

data_ranked as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_score,
    row_number() over (partition by metric_name order by metric_timestamp desc) as metric_recency_rank
  from data
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score
from data_ranked
where metric_recency_rank <= {{ score_max_n }}
;
