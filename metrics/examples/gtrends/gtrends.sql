with

-- get the latest data
latest_data as 
(
select 
  *
FROM 
  `bigquery-public-data.google_trends.top_terms` 
WHERE
  -- usually the data is updated every 3 days
  refresh_date = date_sub(current_date(), INTERVAL 3 DAY)  
),

-- get the latest week
max_week as
(
SELECT 
  max(week) as week_max 
FROM 
  latest_data
),

-- get the latest data for the latest week
most_recent_week as
(
select 
  latest_data.*
from
  latest_data
join
  max_week
on
  latest_data.week = max_week.week_max
),

-- calculate the metrics
metrics as
(
select
  cast(avg(score) over() as float64) as score_avg,
  cast(sum(score) over() as float64) as score_sum,
  cast(min(score) over() as float64) as score_min,
  cast(max(score) over() as float64) as score_max,
  cast(percentile_disc(score, 0.5) over() as float64) as score_p50,
  cast(percentile_disc(score, 0.9) over() as float64) as score_p90
from
  most_recent_week
limit 1
)

-- unpivot the metrics onto a long format expected by Anomstack
select
  current_timestamp() as metric_timestamp,
  concat('gtrends_',metric_name) as metric_name,
  metric_value,
from
  metrics
  unpivot(metric_value for metric_name IN (
    score_avg,
    score_min,
    score_max,
    score_sum,
    score_p50,
    score_p90
    )
  )
;
