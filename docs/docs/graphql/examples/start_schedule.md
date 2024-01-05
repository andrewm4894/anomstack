
# Start Schedules (GraphQL)

Below is an example GraphQL query to start multiple job schedules (this avoids having to toggle them all on individually in the UI manually).

You can run this via `/graphql` endpoint in the dagster UI.

```graphql
mutation {

  # BigQuery
  startBigqueryExampleSimpleAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startBigqueryExampleSimpleChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startBigqueryExampleSimpleIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startBigqueryExampleSimplePlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startBigqueryExampleSimpleScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startBigqueryExampleSimpleTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "bigquery_example_simple_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # TomTom
  startTomTomAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startTomTomChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startTomTomIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startTomTomPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startTomTomScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startTomTomTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "tomtom_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # EirGrid
  startEirGridAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startEirGridChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startEirGridIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startEirGridPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startEirGridScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startEirGridTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "eirgrid_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # Netdata
  startNetdataAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # NetdataHTTPCheck
  startNetdataHTTPCheckAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataHTTPCheckChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataHTTPCheckIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataHTTPCheckPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataHTTPCheckScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startNetdataHTTPCheckTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "netdata_httpcheck_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # GSOD
  startGSODAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGSODChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGSODIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGSODPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGSODScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGSODTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gsod_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # Gtrends
  startGtrendsAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGtrendsChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGtrendsIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGtrendsPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGtrendsScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startGtrendsTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "gtrends_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # YFinance
  startYFinanceAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startYFinanceChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startYFinanceIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startYFinancePlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startYFinanceScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startYFinanceTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "yfinance_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # Weather
  startWeatherAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startWeatherChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startWeatherIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startWeatherPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startWeatherScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startWeatherTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "weather_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

  # HNTopStoriesScores
  startHNTopStoriesScoresAlertsSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_alerts_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startHNTopStoriesScoresChangeSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_change_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startHNTopStoriesScoresIngestSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_ingest_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startHNTopStoriesScoresPlotJobSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_plot_job_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startHNTopStoriesScoresScoreSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_score_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }
  startHNTopStoriesScoresTrainSchedule: startSchedule(scheduleSelector: { 
    scheduleName: "hn_top_stories_scores_train_schedule", 
    repositoryName: "__repository__", 
    repositoryLocationName: "anomstack_code" 
  }) {
    __typename
    ... on ScheduleStateResult {
      scheduleState {
        name
        status
      }
    }
  }

}
```
