/*
Template for generating the input data for the dashboard charts.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

with

aggregated as (
  select
    metric_timestamp,
    metric_batch,
    metric_name,
    avg(case when metric_type = 'metric' then metric_value end) as metric_value,
    avg(case when metric_type = 'score' then metric_value end) as metric_score,
    max(case when metric_type = 'alert' then metric_value end) as metric_alert,
    max(case when metric_type = 'llmalert' then metric_value end) as metric_llmalert,
    max(case when metric_type = 'change' then metric_value end) as metric_change,
    sum(case when metric_type = 'thumbsup' then metric_value end) as thumbsup_sum,
    sum(case when metric_type = 'thumbsdown' then metric_value end) as thumbsdown_sum,
    array_agg(distinct metadata) as metadata
  from
    {{ table_key }}
  where
    metric_batch = '{{ metric_batch }}'
    {% if cutoff_time is defined %}
    and metric_timestamp >= '{{ cutoff_time }}'
    {% endif %}
  group by 1,2,3
),

max_metric_timestamp_filter as (
select
  metric_name,
  metric_batch
from
  (
  select
    metric_name,
    metric_batch,
    max(metric_timestamp) as metric_timestamp_max
  from
    aggregated
  group by 1,2
)
where
  -- remove stale metrics
  cast(metric_timestamp_max as timestamp) >= current_timestamp - interval '{{ dashboard_stale_metric_max_days_ago }} day'
),

ranked as (
  select
    aggregated.*,
    row_number() over (partition by aggregated.metric_name order by aggregated.metric_timestamp desc) as recency_rank
  from
    aggregated
  inner join
    max_metric_timestamp_filter
  on
    aggregated.metric_name = max_metric_timestamp_filter.metric_name
    and
    aggregated.metric_batch = max_metric_timestamp_filter.metric_batch
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_score,
  metric_alert,
  metric_llmalert,
  metric_change,
  thumbsup_sum,
  thumbsdown_sum,
  metadata
from
  ranked
{% if cutoff_time is not defined %}
where
  recency_rank <= {{ last_n }}
{% endif %}
order by 1,2,3
