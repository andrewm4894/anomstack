# Snowflake

Example of using Snowflake as a data source. See [`examples/snowflake`](/metrics/examples/snowflake/) directory for an example.

## Configuration

1. Set below environment variables in `.env` file.
    - `ANOMSTACK_GOOGLE_APPLICATION_CREDENTIALS`: Path to the Google Cloud Platform service account key file.  
    or
    - `ANOMSTACK_SNOWFLAKE_ACCOUNT`: Snowflake account name.
    - `ANOMSTACK_SNOWFLAKE_USER`: Snowflake user name.
    - `ANOMSTACK_SNOWFLAKE_PASSWORD`: Snowflake password.
    - `ANOMSTACK_SNOWFLAKE_WAREHOUSE`: Snowflake warehouse name.
1. Configure metric batch config yaml file params.
    - `db: snowflake`: Set `db` param to `snowflake`.
1. Ensure `table_key` is like `database.schema.table`.
