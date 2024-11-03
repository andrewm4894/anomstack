/*
Template for generating the input data for the change detection job.

Written for SQLite but will be translated to target dialect based on `db` param via sqlglot.
*/

with

metric_value_data as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  avg(metric_value) as metric_value
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'metric'
  and
  -- Filter to the last {{ change_metric_timestamp_max_days_ago }} days
  date(metric_timestamp) >= date('now', '-{{ change_metric_timestamp_max_days_ago }} day')
group by
  metric_timestamp, metric_batch, metric_name
),

metric_change_alert_data as
(
select distinct
  metric_timestamp,
  metric_batch,
  metric_name,
  max(metric_value) as metric_change
from
  {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  metric_type = 'change'
  and
  -- Filter to the last {{ change_metric_timestamp_max_days_ago }} days
  date(metric_timestamp) >= date('now', '-{{ change_metric_timestamp_max_days_ago }} day')
group by
  metric_timestamp, metric_batch, metric_name
),

metric_value_recency_ranked as
(
select distinct
  metric_value_data.metric_timestamp,
  metric_value_data.metric_batch,
  metric_value_data.metric_name,
  metric_value_data.metric_value,
  metric_change_alert_data.metric_change as metric_change,
  -- Rank the metric values by recency, with 1 being the most recent
  row_number() over (partition by metric_value_data.metric_name order by metric_value_data.metric_timestamp desc) as metric_value_recency_rank
from
  metric_value_data
left outer join
  metric_change_alert_data
on
  metric_value_data.metric_batch = metric_change_alert_data.metric_batch
  and
  metric_value_data.metric_name = metric_change_alert_data.metric_name
  and
  metric_value_data.metric_timestamp = metric_change_alert_data.metric_timestamp
),

-- Snooze any metrics with change alerts in the last {{ change_snooze_n }} values
snoozed_metric_names as
(
select distinct
  metric_name
from
  metric_value_recency_ranked
where
  -- Exclude metrics with change alerts in the last {{ change_snooze_n }} values
  metric_change = 1
  and
  metric_value_recency_rank <= {{ change_snooze_n }}
),

data_smoothed as
(
select
  metric_timestamp,
  metric_batch,
  metric_name,
  metric_value,
  metric_change,
  metric_value_recency_rank,
  -- Smooth the metric value over the last {{ change_smooth_n }} values
  (
    select
      avg(mv.metric_value)
    from
      metric_value_recency_ranked mv
    where
      mv.metric_name = mr.metric_name
      and
      mv.metric_value_recency_rank between mr.metric_value_recency_rank - {{ change_smooth_n }} and mr.metric_value_recency_rank
  ) as metric_value_smooth
from
  metric_value_recency_ranked mr
where
  metric_value_recency_rank <= {{ change_max_n }}
  and
  -- Exclude snoozed metrics
  metric_name not in (select metric_name from snoozed_metric_names)
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
