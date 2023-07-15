import pandas as pd
from dagster import Definitions, AssetsDefinition, asset, EnvVar
from dagster_gcp_pandas import BigQueryPandasIOManager


specs = {
    'spec1':[
        {"name": "assetA1", "upstream": [], "sql": "select 666", "dataset": "tmp"},
        {"name": "assetA2", "upstream": ["assetA1"], "sql": "select 999", "dataset": "tmp"},
    ],
    'spec2':[
        {"name": "assetB1", "upstream": [], "sql": "select 123", "dataset": "tmp"},
        {"name": "assetB2", "upstream": ["assetB1"], "sql": "select 000", "dataset": "tmp"},
    ],
}


def build_asset(spec) -> AssetsDefinition:
    @asset(
        name=spec["name"], 
        non_argument_deps=set(spec["upstream"]),
        key_prefix=["gcp", "bigquery", spec["dataset"]]
    )
    def _asset() -> pd.DataFrame:
        df = pd.read_gbq(
            query=spec['sql'], 
            project_id=EnvVar("GCP_PROJECT"),
        )
        return df

    return _asset


defs = Definitions(
    assets=[
        build_asset(s) 
        for spec in specs 
        for s in specs[spec]
    ],
    resources={
        "io_manager": BigQueryPandasIOManager(
            project=EnvVar("GCP_PROJECT"),
            dataset=EnvVar("GCP_DATASET"),
            ),
    }
)
