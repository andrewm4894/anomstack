/*
Template for generating the input data for the delete job.

Written for DuckDB but will be translated to target dialect based on `db` param via sqlglot.
*/

delete from {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and metric_timestamp < current_date - interval '{{ delete_after_n_days }} day'
;
