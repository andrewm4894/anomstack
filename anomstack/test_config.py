import os
import pytest
import yaml
from .config import process_yaml_file, specs


def test_process_yaml_file():
    # Setup
    test_yaml_file = "test.yaml"
    with open(test_yaml_file, "w") as file:
        yaml.dump({"metric_batch": "test_metric_batch"}, file)

    # Call the function
    process_yaml_file(test_yaml_file)

    # Assert the result
    assert specs["test_metric_batch"]["metric_batch"] == "test_metric_batch"

    # Teardown
    os.remove(test_yaml_file)


# Run the test
pytest.main()
