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

ranked as (
  select
    *,
    row_number() over (partition by metric_name order by metric_timestamp desc) as recency_rank
  from 
    aggregated
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
  metadata
from 
  ranked
{% if cutoff_time is not defined %}
where 
  recency_rank <= {{ last_n }}
{% endif %}
order by 1,2,3
