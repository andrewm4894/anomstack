/*
Template for generating the input data for the llmalert job.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

metric_value_data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(metric_value) as metric_value
  from {{ table_key }}
  where metric_batch = '{{ metric_batch }}'
    and metric_type = 'metric'
    and metric_timestamp >= current_date - interval '{{ llmalert_metric_timestamp_max_days_ago }} day'
  group by metric_timestamp, metric_batch, metric_name
),

metric_score_data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(metric_value) as metric_score
  from {{ table_key }}
  where metric_batch = '{{ metric_batch }}'
    and metric_type = 'score'
    and metric_timestamp >= current_date - interval '{{ llmalert_metric_timestamp_max_days_ago }} day'
  group by metric_timestamp, metric_batch, metric_name
),

metric_alert_data as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(metric_value) as metric_alert
  from {{ table_key }}
  where metric_batch = '{{ metric_batch }}'
    and metric_type = 'alert'
    and metric_timestamp >= current_date - interval '{{ llmalert_metric_timestamp_max_days_ago }} day'
  group by metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    metric_value,
    row_number() over (partition by metric_name order by metric_timestamp desc) as metric_value_recency_rank
  from metric_value_data
)

select
  m.metric_timestamp,
  m.metric_batch,
  m.metric_name,
  m.metric_value,
  coalesce(s.metric_score, 0) as metric_score,
  coalesce(a.metric_alert, 0) as metric_alert
from metric_value_recency_ranked m
left join metric_score_data s
  on m.metric_timestamp = s.metric_timestamp
  and m.metric_batch = s.metric_batch
  and m.metric_name = s.metric_name
left join metric_alert_data a
  on m.metric_timestamp = a.metric_timestamp
  and m.metric_batch = a.metric_batch
  and m.metric_name = a.metric_name
;
