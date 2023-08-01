select
  *
from
  (
    select
      current_timestamp() as metric_timestamp,
      'metric_1' as metric_name,
      rand() as metric_value
    union all
    select
      current_timestamp() as metric_timestamp,
      'metric_2' as metric_name,
      rand() as metric_value
  )
;
