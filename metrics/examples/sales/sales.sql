with

sales_pipeline_deals_created as
(
select
  get_current_timestamp() as metric_timestamp,
  'sales_pipeline_deals_created' as metric_name,
  random()*2 as metric_value
),

sales_pipeline_deals_sold as
(
select
  get_current_timestamp() as metric_timestamp,
  'sales_pipeline_deals_sold' as metric_name,
  random() as metric_value
),

sales_pipeline_success_rate as
(
select  
  get_current_timestamp() as metric_timestamp,
  'sales_pipeline_success_rate' as metric_name,
  sales_pipeline_deals_sold.metric_value / sales_pipeline_deals_created.metric_value as metric_value
from
  sales_pipeline_deals_created
join 
  sales_pipeline_deals_sold
on 
  date_trunc('day', sales_pipeline_deals_created.metric_timestamp) = date_trunc('day', sales_pipeline_deals_sold.metric_timestamp)
)   

select
  metric_timestamp,
  metric_name,
  metric_value,
from
  (
  select * from sales_pipeline_deals_created
  union all
  select * from sales_pipeline_deals_sold
  union all
  select * from sales_pipeline_success_rate
  )
;
