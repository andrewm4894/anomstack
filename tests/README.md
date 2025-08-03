# Anomstack Test Suite

Comprehensive tests for the anomstack anomaly detection system covering ML pipelines, data processing, alerts, and job orchestration.

## Quick Start

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=anomstack --cov-report=term-missing

# Run specific test file
pytest tests/test_ml.py -v
```

## Test Overview

- **Total Tests:** 134 tests across 17 test files
- **Runtime:** ~40 seconds for full suite
- **Coverage:** 56% overall code coverage
- **Scope:** ML, jobs, data validation, SQL, alerts, plotting, and configuration

## Test Files

### Core Functionality
- **`test_ml.py`** (18 tests) - Machine learning pipeline, model training, preprocessing
- **`test_jobs.py`** (17 tests) - Dagster job creation and orchestration
- **`test_df.py`** (13 tests) - Data wrangling and manipulation
- **`test_sql.py`** (16 tests) - SQL operations across multiple databases
- **`test_validate.py`** (9 tests) - Data validation and structure checking

### Alerts & Notifications
- **`test_alerts.py`** (10 tests) - Alert routing and sending
- **`test_email.py`** (4 tests) - Email notifications with plots
- **`test_slack.py`** (15 tests) - Slack notifications
- **`test_asciiart.py`** (11 tests) - ASCII art generation for alerts

### Visualization & IO
- **`test_plots.py`** (11 tests) - Chart generation and visualization
- **`test_io.py`** (8 tests) - Model persistence and storage
- **`test_config.py`** (7 tests) - Configuration management
- **`test_main.py`** (6 tests) - Main module integration

### External Integrations
- **`test_external_duckdb_simple.py`** (4 tests) - DuckDB database operations
- **`test_duckdb.py`** (8 tests) - Extended DuckDB functionality
- **`test_alert_jobs.py`** (6 tests) - Alert job orchestration

## Running Tests

### Basic Commands
```bash
# All tests
pytest tests/

# Verbose output
pytest tests/ -v

# Specific test file
pytest tests/test_ml.py

# Tests matching pattern
pytest tests/ -k "validation"
```

### Coverage Reports
```bash
# Terminal coverage report
pytest tests/ --cov=anomstack --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=anomstack --cov-report=html
open htmlcov/index.html
```

### Test Categories
```bash
# Core ML and data processing
pytest tests/test_ml.py tests/test_df.py tests/test_validate.py

# Database and SQL
pytest tests/test_sql.py tests/test_external_duckdb_simple.py

# Alerts and notifications
pytest tests/test_alerts.py tests/test_email.py tests/test_slack.py

# Jobs and orchestration
pytest tests/test_jobs.py tests/test_alert_jobs.py
```

## Coverage Highlights

### High Coverage (>90%)
- **Email, Alerts, Plotting:** 100% coverage for core notification systems
- **ML Pipeline:** 93-100% coverage for training and preprocessing
- **Data Validation:** 100% coverage for structure checking
- **Configuration:** 97% coverage for config management

### Medium Coverage (50-89%)
- **Job Orchestration:** 58-76% coverage for Dagster jobs
- **ASCII Art Generation:** 62% coverage for alert formatting

### Areas for Improvement (<50%)
- **External Integrations:** Database and cloud service connections
- **LLM Components:** AI-powered alerting features
- **Slack Integration:** External API dependencies

## Test Design

### Key Principles
- **Fast & Reliable:** Tests run quickly with deterministic results
- **Comprehensive:** Cover critical paths and edge cases
- **Maintainable:** Clear naming and focused test scope
- **Realistic:** Use actual data structures and error conditions

### Common Patterns
```python
# Data function testing
def test_data_function():
    df = create_test_dataframe()
    result = function_under_test(df)
    assert isinstance(result, pd.DataFrame)
    assert 'expected_column' in result.columns

# Mocking external dependencies
@patch('module.external_service')
def test_with_mock(mock_service):
    mock_service.return_value = expected_result
    result = function_under_test()
    mock_service.assert_called_once()
```

## Debugging Tips

### Common Issues
- **Import errors:** Check virtual environment and dependencies
- **Mock failures:** Verify patch paths and return value types
- **DataFrame comparisons:** Use `pd.testing.assert_frame_equal()`
- **Plotting issues:** Always call `plt.close(fig)` after tests

### Verbose Output
```bash
# Detailed output with logs
pytest tests/ -v -s --log-cli-level=DEBUG

# Show full stack traces
pytest tests/ --tb=long
```

## Contributing

### Adding New Tests
1. Follow naming: `test_<module>.py`, `test_<functionality>`
2. Keep tests focused on single behaviors
3. Mock external dependencies appropriately
4. Include both success and error cases
5. Clean up resources (close figures, files)

### Test Structure
```python
def test_new_feature():
    """Test description."""
    # Arrange - setup test data
    test_data = create_test_data()

    # Act - call function
    result = function_under_test(test_data)

    # Assert - verify results
    assert result.meets_expectation()
```

The test suite provides comprehensive coverage while maintaining fast execution suitable for development workflows.
