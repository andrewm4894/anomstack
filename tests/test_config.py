import os

import pytest

from anomstack.config import env_vars, get_specs


def test_process_yaml_file():
    specs = get_specs()
    assert len(specs) > 0


def test_specs_structure():
    specs = get_specs()
    for batch_name, spec in specs.items():
        # Test required fields
        assert "metric_batch" in spec
        assert "db" in spec
        assert "table_key" in spec
        assert "model_path" in spec
        assert "model_configs" in spec
        assert "alert_methods" in spec
        assert "ingest_cron_schedule" in spec
        assert "train_cron_schedule" in spec
        assert "score_cron_schedule" in spec
        assert "alert_cron_schedule" in spec

        # Test field types
        assert isinstance(spec["metric_batch"], str)
        assert isinstance(spec["db"], str)
        assert isinstance(spec["table_key"], str)
        assert isinstance(spec["model_path"], str)
        assert isinstance(spec["model_configs"], list)
        assert isinstance(spec["alert_methods"], str)
        assert isinstance(spec["ingest_cron_schedule"], str)
        assert isinstance(spec["train_cron_schedule"], str)
        assert isinstance(spec["score_cron_schedule"], str)
        assert isinstance(spec["alert_cron_schedule"], str)


def test_default_values():
    specs = get_specs()
    for batch_name, spec in specs.items():
        # Test default values from defaults.yaml
        assert spec["model_combination_method"] == "mean"
        assert spec["train_max_n"] == 2500
        assert spec["train_min_n"] == 14
        assert spec["score_max_n"] == 25
        assert spec["alert_threshold"] == 0.8
        assert spec["change_threshold"] == 3.5
        assert spec["llmalert_recent_n"] == 5
        assert spec["delete_after_n_days"] == 365


def test_environment_variable_override():
    # Save original environment variables
    original_env = {}
    for var in env_vars:
        original_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    try:
        # Set test environment variables
        test_project_id = "test-project"
        test_model_path = "test-model-path"
        test_table_key = "test-table"

        os.environ["ANOMSTACK_GCP_PROJECT_ID"] = test_project_id
        os.environ["ANOMSTACK_MODEL_PATH"] = test_model_path
        os.environ["ANOMSTACK_TABLE_KEY"] = test_table_key

        specs = get_specs()

        # Test that environment variables override defaults only when not specified in YAML
        for batch_name, spec in specs.items():
            # gcp_project_id should be overridden since it's not in defaults.yaml
            assert spec["gcp_project_id"] == test_project_id
            # model_path should keep its YAML value (either default or batch-specific)
            assert "model_path" in spec
            if batch_name in ["freq_example", "snowflake_example_simple", "bigquery_example_simple",
                            "gtrends", "weather_forecast", "gsod"]:
                assert spec["model_path"] == "gs://andrewm4894-tmp/models"
            elif batch_name == "s3_example_simple":
                assert spec["model_path"] == "s3://andrewm4894-tmp/models"
            else:
                assert spec["model_path"] == "local://./models"
            # table_key should keep its YAML value (either default or batch-specific)
            assert "table_key" in spec
            if batch_name in ["gsod", "gtrends", "bigquery_example_simple", "freq_example"]:
                assert spec["table_key"] == "andrewm4894.metrics.metrics"
            elif batch_name in ["weather_forecast", "snowflake_example_simple"]:
                assert spec["table_key"] == "ANDREWM4894.METRICS.METRICS"
            elif batch_name == "hn_top_stories_scores":
                assert spec["table_key"] == "metrics_hackernews"
            else:
                # table_key should either be "metrics" or "metrics_<batch_name>"
                assert spec["table_key"] in ["metrics", f"metrics_{batch_name}"]
    finally:
        # Restore original environment variables
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]


def test_disabled_batches():
    specs = get_specs()
    for batch_name, spec in specs.items():
        # Test that disabled flags are boolean
        assert isinstance(spec.get("disable_batch", False), bool)
        assert isinstance(spec.get("disable_ingest", False), bool)
        assert isinstance(spec.get("disable_train", False), bool)
        assert isinstance(spec.get("disable_score", False), bool)
        assert isinstance(spec.get("disable_alert", False), bool)
        assert isinstance(spec.get("disable_change", False), bool)
        assert isinstance(spec.get("disable_llmalert", True), bool)
        assert isinstance(spec.get("disable_plot", False), bool)
        assert isinstance(spec.get("disable_summary", False), bool)
        assert isinstance(spec.get("disable_delete", False), bool)


def test_metrics_dir_parameter():
    # Test with default metrics directory
    specs_default = get_specs()
    assert len(specs_default) > 0

    # Test with custom metrics directory
    custom_metrics_dir = "./metrics"
    specs_custom = get_specs(metrics_dir=custom_metrics_dir)
    assert len(specs_custom) > 0

    # Test that specs are the same regardless of metrics_dir parameter
    assert specs_default == specs_custom


def test_invalid_metrics_dir():
    with pytest.raises(FileNotFoundError):
        get_specs(metrics_dir="./nonexistent_directory")


# Run the test
if __name__ == "__main__":
    pytest.main()
