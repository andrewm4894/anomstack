/*
Template for generating the input data for the delete job.

Written for SQLite but will be translated to target dialect based on `db` param via sqlglot.
*/

delete from {{ table_key }}
where
  metric_batch = '{{ metric_batch }}'
  and
  -- Delete data older than the specified number of days
  date(metric_timestamp) < date('now', '-{{ delete_after_n_days }} day')
;
