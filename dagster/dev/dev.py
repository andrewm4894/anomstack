from dagster import Definitions, AssetsDefinition, asset


specs = {
    'spec1':[{"name": "assetA1", "upstream": [], "sql": "blah blah"},{"name": "assetA2", "upstream": ["assetA1"], "sql": "blah blah"},],
    'spec2':[{"name": "assetB1", "upstream": [], "sql": "blah blah"},{"name": "assetB2", "upstream": ["assetB1"], "sql": "blah blah"},],
    }


def execute_sql(sql: str) -> None:
    print(f'Executing SQL: "{sql}"')


def build_asset(spec) -> AssetsDefinition:
    @asset(
        name=spec["name"], 
        non_argument_deps=set(spec["upstream"]))
    def _asset():
        execute_sql(spec["sql"])

    return _asset


defs = Definitions(
    assets=[
        build_asset(s) 
        for spec in specs 
        for s in specs[spec]
    ]
)
