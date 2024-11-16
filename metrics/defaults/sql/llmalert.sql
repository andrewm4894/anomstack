/*
Template for generating the input data for the llmalert job.
*/

with

metric_value_data as 
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(metric_value) AS metric_value
from 
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and 
  metric_type = 'metric'
  and 
  date(metric_timestamp) >= date('now', '-{{ llmalert_metric_timestamp_max_days_ago }} day')
group by metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked as 
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  row_number() over (partition by metric_name order by metric_timestamp desc) as metric_value_recency_rank
from
  metric_value_data
)

select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value
from 
  metric_value_recency_ranked
;
