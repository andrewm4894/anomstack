import os

import pytest
import yaml

from anomstack.config import get_specs


def test_process_yaml_file():
    specs = get_specs()
    assert len(specs) > 0


# Run the test
pytest.main()
