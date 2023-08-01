with

metric_1 as
(
select
  current_timestamp() as metric_timestamp,
  'metric_1' as metric_name,
  rand() as metric_value
),

metric_2 as
(
select
  current_timestamp() as metric_timestamp,
  'metric_2' as metric_name,
  rand() as metric_value
)

select
  metric_timestamp,
  metric_name,
  metric_value,
from
  (
  select * from metric_1
  union all
  select * from metric_2
  )
;
