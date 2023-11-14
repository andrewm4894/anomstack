with

forecast_data as
(
SELECT
  CASE
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 77001 AND 77299 THEN 'Houston'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 75201 AND 75398 THEN 'Dallas'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 73301 AND 78799 THEN 'Austin'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 78201 AND 78299 THEN 'San Antonio'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 90001 AND 91609 THEN 'Los Angeles'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 10001 AND 10292 THEN 'New York'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 94101 AND 94188 THEN 'San Francisco'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 33101 AND 33299 THEN 'Miami'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 60601 AND 60699 THEN 'Chicago'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 20001 AND 20020 THEN 'Washington DC'
    WHEN TRY_CAST(postal_code AS INTEGER) BETWEEN 85001 AND 85099 THEN 'Phoenix'
    ELSE 'Other'
  END AS place,
  avg(tot_precipitation_in) as avg_precipitation_in,
  avg(tot_snowfall_in) as avg_snowfall_in,
  avg(probability_of_snow_pct) as prob_of_snow_pct,
  avg(probability_of_precipitation_pct) as prob_of_precip_pct,
  avg(avg_wind_speed_10m_mph) as avg_wind_speed,
  avg(avg_humidity_relative_2m_pct) as avg_humidity,
  avg(avg_cloud_cover_tot_pct) as avg_cloud_cover
FROM
  global_weather__climate_data_for_bi.standard_tile.forecast_day
WHERE
  date_valid_std >= DATEADD(DAY, 0, CURRENT_DATE())
  AND
  date_valid_std <= DATEADD(DAY, 3, CURRENT_DATE())
group by
  1
),

forecast_data_clean as
(
select
  current_timestamp() as metric_timestamp,
  replace(lower(place),'','_') as place_clean,
  *
from
  forecast_data
)

select
  metric_timestamp,
  concat('fcast3d','_',place_clean,'_','avg_precipitation_in') as metric_name,
  avg_precipitation_in as metric_value
from
  forecast_data_clean
union all
select
  metric_timestamp,
  concat('fcast3d','_',place_clean,'_','avg_snowfall_in') as metric_name,
  avg_snowfall_in as metric_value
from
  forecast_data_clean
;
