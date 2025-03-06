/*
Template for generating the input data for the change detection job.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

metric_value_data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(metric_value) as metric_value
  from
    {{ table_key }}
  where
    metric_batch = '{{ metric_batch }}'
    and metric_type = 'metric'
    and metric_timestamp >= current_date - interval '{{ change_metric_timestamp_max_days_ago }} day'
    {% if change_include_metrics is defined %}
      and metric_name in ({{ ','.join(change_include_metrics) }})
    {% endif %}
    {% if change_exclude_metrics is defined %}
      and metric_name not in ({{ ','.join(change_exclude_metrics) }})
    {% endif %}
  group by
    metric_timestamp, metric_batch, metric_name
),

metric_change_alert_data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    max(coalesce(metric_value, 0)) as metric_change
  from
    {{ table_key }}
  where
    metric_batch = '{{ metric_batch }}'
    and metric_type = 'change'
    and metric_timestamp >= current_date - interval '{{ change_metric_timestamp_max_days_ago }} day'
    {% if change_include_metrics is defined %}
      and metric_name in ({{ ','.join(change_include_metrics) }})
    {% endif %}
    {% if change_exclude_metrics is defined %}
      and metric_name not in ({{ ','.join(change_exclude_metrics) }})
    {% endif %}
  group by
    metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked as (
  select
    m.metric_timestamp,
    m.metric_batch,
    m.metric_name,
    m.metric_value,
    coalesce(c.metric_change, 0) as metric_change,
    row_number() over (
      partition by m.metric_name 
      order by m.metric_timestamp desc
    ) as metric_value_recency_rank
  from
    metric_value_data m
  left join
    metric_change_alert_data c
    on m.metric_batch = c.metric_batch
    and m.metric_name = c.metric_name
    and m.metric_timestamp = c.metric_timestamp
),

snoozed_metric_names as (
  select
    metric_name
  from
    metric_value_recency_ranked
  where
    metric_change = 1
    and metric_value_recency_rank <= {{ change_snooze_n }}
),

data_smoothed as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    metric_change,
    metric_value_recency_rank,
    AVG(metric_value) OVER (
      PARTITION BY metric_batch, metric_name
      ORDER BY metric_value_recency_rank
      ROWS BETWEEN {{ change_smooth_n }} PRECEDING AND CURRENT ROW
    ) as metric_value_smooth
  from
    metric_value_recency_ranked
  where
    metric_value_recency_rank <= {{ change_max_n }}
    and metric_name not in (select metric_name from snoozed_metric_names)
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_value_smooth,
  metric_change
from
  data_smoothed
;
