with

stations_selected as
(
select
  usaf,
  wban,
  country,
  name,
from
  `bigquery-public-data.noaa_gsod.stations`
where
  country in ('US','UK')
),

data_filtered as
(
select
  gsod.*,
  stations.country
from
  `bigquery-public-data.noaa_gsod.gsod2023` gsod
join
  stations_selected stations
on
  gsod.stn = stations.usaf
  and
  gsod.wban = stations.wban
where
  date(date) = date_add(current_date(), interval -4 day)
),

-- US

us_temp_avg as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_us_temp_avg' as metric_name,
  avg(temp) as metric_value
from
  data_filtered
where
  country = 'US'
group by 1,2
),

us_temp_min as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_us_temp_min' as metric_name,
  min(temp) as metric_value
from
  data_filtered
where
  country = 'US'
group by 1,2
),

us_temp_max as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_us_temp_max' as metric_name,
  max(temp) as metric_value
from
  data_filtered
where
  country = 'US'
group by 1,2
),

-- UK

uk_temp_avg as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_uk_temp_avg' as metric_name,
  avg(temp) as metric_value
from
  data_filtered
where
  country = 'UK'
group by 1,2
),

uk_temp_min as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_uk_temp_min' as metric_name,
  min(temp) as metric_value
from
  data_filtered
where
  country = 'UK'
group by 1,2
),

uk_temp_max as
(
select
  timestamp(date) as metric_timestamp,
  'gsod_uk_temp_max' as metric_name,
  max(temp) as metric_value
from
  data_filtered
where
  country = 'UK'
group by 1,2
)

-- union all metrics together
select * from us_temp_avg
union all
select * from us_temp_min
union all
select * from us_temp_max
union all
select * from uk_temp_avg
union all
select * from uk_temp_min
union all
select * from uk_temp_max
;
