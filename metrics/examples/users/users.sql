with

{% set geos = ['ireland', 'usa', 'eu'] %}

{% for geo in geos %}

users_total_{{ geo }} as
(
select
  get_current_timestamp() as metric_timestamp,
  'users_total_{{ geo }}' as metric_name,
  (random()*100)+(random()*100) as metric_value
),

users_active_{{ geo }} as
(
select
  get_current_timestamp() as metric_timestamp,
  'users_active_{{ geo }}' as metric_name,
  (random()*25)+(random()*25) as metric_value
),

users_active_rate_{{ geo }} as
(
select
  get_current_timestamp() as metric_timestamp,
  'users_active_rate_{{ geo }}' as metric_name,
  users_active_{{ geo }}.metric_value / users_total_{{ geo }}.metric_value as metric_value
from
  users_total_{{ geo }}
join
  users_active_{{ geo }}
on
  date_trunc('day', users_total_{{ geo }}.metric_timestamp) = date_trunc('day', users_active_{{ geo }}.metric_timestamp)
)
{% if not loop.last %},{% endif %}
{% endfor %}

select
  metric_timestamp,
  metric_name,
  metric_value,
from
  (
  {% for geo in geos %}
  select * from users_total_{{ geo }}
  union all
  select * from users_active_{{ geo }}
  union all
  select * from users_active_rate_{{ geo }}
  {% if not loop.last %}union all{% endif %}
  {% endfor %}
  )
;
