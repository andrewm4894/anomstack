"""
Generate score jobs and schedules.
"""

import os

import pandas as pd
from google.api_core.exceptions import NotFound
from dagster import (
    MAX_RUNTIME_SECONDS_TAG,
    DefaultScheduleStatus,
    JobDefinition,
    ScheduleDefinition,
    get_dagster_logger,
    job,
    op,
)

from anomstack.config import specs
from anomstack.df.save import save_df
from anomstack.df.wrangle import wrangle_df
from anomstack.fn.run import define_fn
from anomstack.io.load import load_model
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql
from anomstack.validate.validate import validate_df

ANOMSTACK_MAX_RUNTIME_SECONDS_TAG = os.getenv("ANOMSTACK_MAX_RUNTIME_SECONDS_TAG", 3600)


def build_score_job(spec) -> JobDefinition:
    """
    Build job definitions for score jobs.

    Args:
        spec (dict): A dictionary containing specifications for the job.

    Returns:
        JobDefinition: A job definition for the score job.
    """

    if spec.get("disable_score"):

        @job(
            name=f'{spec["metric_batch"]}_score_disabled',
            tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
        )
        def _dummy_job():
            @op(name=f'{spec["metric_batch"]}_noop')
            def noop():
                pass

            noop()

        return _dummy_job

    logger = get_dagster_logger()

    metric_batch = spec["metric_batch"]
    model_path = spec["model_path"]
    table_key = spec["table_key"]
    db = spec["db"]
    preprocess_params = spec["preprocess_params"]
    score_metric_rounding = spec.get("score_metric_rounding", 4)

    @job(
        name=f"{metric_batch}_score",
        tags={MAX_RUNTIME_SECONDS_TAG: ANOMSTACK_MAX_RUNTIME_SECONDS_TAG},
    )
    def _job():
        """
        Get data for scoring and score data.
        """

        @op(name=f"{metric_batch}_get_score_data")
        def get_score_data() -> pd.DataFrame:
            """
            Get data for scoring.

            Returns:
                pd.DataFrame: A pandas dataframe containing data for scoring.
            """

            df = read_sql(render("score_sql", spec), db)

            return df

        @op(name=f"{metric_batch}_score_op")
        def score(df) -> pd.DataFrame:
            """
            Score data.

            Args:
                df (pd.DataFrame): A pandas dataframe containing data to be scored.

            Returns:
                pd.DataFrame: A pandas dataframe containing the scored data.
            """

            preprocess = define_fn(
                fn_name="preprocess", fn=render("preprocess_fn", spec)
            )

            df_scores = pd.DataFrame()

            for metric_name in df["metric_name"].unique():
                df_metric = df[df["metric_name"] == metric_name]

                logger.debug(f"preprocess {metric_name} in {metric_batch} score job.")
                logger.debug(f"df_metric:\n{df_metric.head()}")

                # try load model and catch google.api_core.exceptions.NotFound
                try:
                    model = load_model(metric_name, model_path, metric_batch)
                except NotFound as e:
                    logger.warning(e)
                    logger.warning(
                        f"model not found for {metric_name} in {metric_batch} score job."
                    )
                    continue

                X = preprocess(df_metric, **preprocess_params)

                if len(X) == 0:
                    logger.debug(
                        f"X is empty for {metric_name} in {metric_batch} score job."
                    )
                    continue

                logger.debug(f"X:\n{X.head()}")

                scores = model.predict_proba(X)

                # create initial df_score
                df_score = pd.DataFrame(
                    data=scores[:, 1],  # probability of anomaly
                    index=X.index,
                    columns=["metric_value"],
                ).round(3)

                # limit to timestamps where metric_score is null to begin with
                # in df_metric or its not in df_metric
                df_score = df_score[
                    df_score.index.isin(
                        df_metric[df_metric["metric_score"].isnull()].index
                    )
                    | ~df_score.index.isin(df_metric.index)
                ].reset_index()

                # merge some df_metric info onto df_score
                df_score = df_score.merge(
                    df_metric[["metric_timestamp", "metric_name", "metric_batch"]],
                    on=["metric_timestamp"],
                    how="left",
                )
                df_score["metric_type"] = "score"
                df_score = df_score[
                    [
                        "metric_timestamp",
                        "metric_name",
                        "metric_value",
                        "metric_batch",
                        "metric_type",
                    ]
                ]
                df_score["metric_name"] = df_score["metric_name"].fillna(metric_name)
                df_score["metric_batch"] = df_score["metric_batch"].fillna(metric_batch)

                df_scores = pd.concat([df_scores, df_score], ignore_index=True)

            if len(df_scores) == 0:
                logger.debug(f"df_scores is empty for {metric_batch} score job.")
                return df_scores

            df_scores = wrangle_df(df_scores, rounding=score_metric_rounding)
            df_scores = validate_df(df_scores)

            logger.debug(f"df_scores:\n{df_scores.head()}")

            return df_scores

        @op(name=f"{metric_batch}_save_scores")
        def save_scores(df) -> pd.DataFrame:
            """
            Save scores to db.

            Args:
                df (pd.DataFrame): A pandas dataframe containing the scored data.

            Returns:
                pd.DataFrame: A pandas dataframe containing the saved data.
            """

            if len(df) > 0:
                df = save_df(df, db, table_key)
            else:
                logger.debug(
                    f"no scores to save, df is empty for {metric_batch} score job."
                )

            return df

        save_scores(score(get_score_data()))

    return _job


# Build score jobs and schedules.
score_jobs = []
score_schedules = []
for spec_name, spec in specs.items():
    score_job = build_score_job(spec)
    score_jobs.append(score_job)
    if spec["score_default_schedule_status"] == "RUNNING":
        score_default_schedule_status = DefaultScheduleStatus.RUNNING
    else:
        score_default_schedule_status = DefaultScheduleStatus.STOPPED
    score_schedule = ScheduleDefinition(
        job=score_job,
        cron_schedule=spec["score_cron_schedule"],
        default_status=score_default_schedule_status,
    )
    score_schedules.append(score_schedule)
