from dagster import Definitions, AssetsDefinition, asset

specs = [
    {"name": "asset1", "upstream": [], "sql": "blah blah"},
    {"name": "asset2", "upstream": ["asset1"], "sql": "blah blah"},
]


def execute_sql(sql: str) -> None:
    print(f'Executing SQL: "{sql}"')


def build_asset(spec) -> AssetsDefinition:
    @asset(name=spec["name"], non_argument_deps=set(spec["upstreams"]))
    def _asset():
        execute_sql(spec["sql"])

    return _asset


defs = Definitions(assets=[build_asset(spec) for spec in specs])
