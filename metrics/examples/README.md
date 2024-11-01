# Examples

Some example metric batch sub folders. For example you might have one per source or subject, or whatever makes most sense to you really.

- [bigquery](bigquery/): Example of a BigQuery metric batch.
- [eirgrid](eirgrid/): Example of a metric batch that uses a custom python `ingest_fn` parameter to just use python to create an `ingest()` function that returns a pandas df.
- [example_jinja](example_jinja/): Example of a metric batch that uses Jinja templating.
- [example_simple](example_simple/): Example of a simple metric batch.
- [example_sql_file](example_sql_file/): Example of a metric batch that uses a SQL file.
- [freq](freq/): Example of a metric batch that uses the `freq` parameter.
- [gsod](gsod/): Example of a metric batch that uses GSOD data from BigQuery.
- [gtrends](gtrends/): Example of a metric batch that uses Google Trends data from BigQuery.
- [hackernews](hackernews/): Example of a metric batch that uses the Hacker News API.
- [netdata](netdata/): Example of a metric batch that uses the Netdata API.
- [netdata_httpcheck](netdata_httpcheck/): Example of a metric batch that uses the Netdata API to check the status of a website.
- [python](python/): Example of a metric batch that uses a custom python `ingest_fn` parameter to just use python to create an `ingest()` function that returns a pandas df.
- [s3](s3/): Example of a metric batch that uses S3.
- [sales](sales/): Example of a metric batch that uses a SQL file.
- [snowflake](snowflake/): Example of a metric batch that uses Snowflake.
- [tomtom](tomtom/): Example of a metric batch that uses the TomTom API.
- [users](users/): Example of a metric batch that uses a SQL file.
- [weather](weather/): Example of a metric batch that uses Open Meteo data.
- [weather_forecast](weather_forecast/): Example of a metric batch that uses weather forecast data from Snowflake.
- [yfinance](yfinance/): Example of a metric batch that uses the Yahoo Finance API.


```
.
├── README.md
├── bigquery
│   ├── README.md
│   └── bigquery_example_simple
│       ├── README.md
│       └── bigquery_example_simple.yaml
├── eirgrid
│   ├── README.md
│   ├── eirgrid.py
│   └── eirgrid.yaml
├── example_jinja
│   ├── README.md
│   └── example_jinja.yaml
├── example_simple
│   ├── README.md
│   └── example_simple.yaml
├── example_sql_file
│   ├── README.md
│   ├── example_sql_file.sql
│   └── example_sql_file.yaml
├── freq
│   ├── README.md
│   └── freq.yaml
├── gsod
│   ├── README.md
│   ├── gsod.sql
│   └── gsod.yaml
├── gtrends
│   ├── README.md
│   ├── gtrends.sql
│   └── gtrends.yaml
├── hackernews
│   ├── README.md
│   ├── hn_top_stories_scores.py
│   └── hn_top_stories_scores.yaml
├── netdata
│   ├── README.md
│   ├── netdata.py
│   └── netdata.yaml
├── netdata_httpcheck
│   ├── netdata_httpcheck.py
│   └── netdata_httpcheck.yaml
├── python
│   ├── README.md
│   └── python_ingest_simple
│       ├── README.md
│       ├── ingest.py
│       └── python_ingest_simple.yaml
├── s3
│   ├── README.md
│   └── s3_example_simple
│       ├── README.md
│       └── s3_example_simple.yaml
├── sales
│   ├── README.md
│   ├── sales.sql
│   └── sales.yaml
├── snowflake
│   ├── README.md
│   └── snowflake_example_simple
│       ├── README.md
│       └── snowflake_example_simple.yaml
├── tomtom
│   ├── README.md
│   ├── tomtom.py
│   └── tomtom.yaml
├── users
│   ├── README.md
│   ├── users.sql
│   └── users.yaml
├── weather
│   ├── README.md
│   ├── ingest_weather.py
│   └── weather.yaml
├── weather_forecast
│   ├── README.md
│   ├── weather_forecast.sql
│   └── weather_forecast.yaml
└── yfinance
    ├── README.md
    ├── yfinance.py
    └── yfinance.yaml

25 directories, 58 files
```
