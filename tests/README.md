# Anomstack Test Suite

This directory contains comprehensive tests for the anomstack anomaly detection system. The test suite covers core functionality including ML pipelines, Dagster job orchestration, data validation, SQL operations, alerting, plotting, and configuration management.

## Test Overview

**Total Tests:** 115 tests across 10 test files  
**Runtime:** ~21 seconds for full suite  
**Coverage:** Comprehensive anomstack functionality including ML, jobs, IO, configuration, data validation, SQL operations, alerts, and visualization

## Test Files

### `test_ml.py` (18 tests)
Tests the machine learning pipeline components:

- **Model Training (4 tests):** IForest, KNN, invalid models, empty data handling
- **Data Preprocessing (7 tests):** `make_x` function with various modes, differencing, smoothing, lags
- **Change Detection (4 tests):** MAD-based anomaly detection with different scenarios
- **Integration (3 tests):** End-to-end ML pipeline testing

**Key Features Tested:**
- Real model training with PyOD algorithms
- Data preprocessing transformations
- Change point detection algorithms
- ML pipeline integration with logging

### `test_df.py` (13 tests) ⭐ *NEW*
Tests data wrangling and manipulation functions:

- **Data Wrangling (5 tests):** `wrangle_df` with type conversion, NaN handling, column ordering, rounding
- **Metadata Extraction (8 tests):** `extract_metadata` with JSON parsing, error handling, edge cases

**Key Features Tested:**
- DataFrame structure validation and cleanup
- Robust JSON metadata extraction
- Type conversion and data quality enforcement
- Error handling for malformed data

### `test_validate.py` (9 tests) ⭐ *NEW*
Tests data validation functions:

- **DataFrame Validation (9 tests):** `validate_df` with column validation, data type checking, structure verification

**Key Features Tested:**
- Required column presence validation
- Data type enforcement (numeric, datetime, string)
- DataFrame structure and size validation
- Case-insensitive column name checking
- Comprehensive error reporting

### `test_sql.py` (16 tests) ⭐ *NEW*
Tests SQL operations and database connectivity:

- **Multi-Database Support (12 tests):** BigQuery, Snowflake, DuckDB, SQLite, ClickHouse
- **SQL Translation (3 tests):** `db_translate` functionality
- **Error Handling (1 test):** Unknown database types

**Key Features Tested:**
- Database-specific SQL execution
- Query translation between SQL dialects
- Return vs non-return query modes
- Comprehensive logging and debugging
- Database abstraction layer

### `test_alerts.py` (10 tests) ⭐ *NEW*
Tests alert sending and notification systems:

- **Alert Functions (5 tests):** `send_alert` with multiple notification methods
- **DataFrame Alerts (5 tests):** `send_df` for tabular data notifications

**Key Features Tested:**
- Email and Slack notification routing
- Custom alert parameters and thresholds
- Tag-based alert categorization
- HTML table generation for data alerts
- Flexible alert method configuration

### `test_plots.py` (11 tests) ⭐ *NEW*
Tests visualization and plotting functions:

- **Alert Plotting (5 tests):** `make_alert_plot` for anomaly visualization
- **Batch Plotting (6 tests):** `make_batch_plot` for multi-metric visualization

**Key Features Tested:**
- Matplotlib figure generation
- Multi-subplot layouts with twin axes
- Time series visualization with alerts
- Custom score columns and thresholds
- Empty data and edge case handling

### `test_io.py` (8 tests)
Tests model persistence and storage:

- **Model Saving (3 tests):** Local storage, cloud paths (GCS/S3), error handling
- **Model Loading (4 tests):** Single model loading, missing files, path validation
- **Integration (1 test):** Complete save/load cycle with real models

**Storage Types Covered:**
- Local filesystem (`local://`)
- Google Cloud Storage (`gs://`)
- Amazon S3 (`s3://`)

### `test_jobs.py` (17 tests)
Tests Dagster job creation and configuration:

- **Ingest Jobs (4 tests):** SQL-based, Python-based, disabled jobs, missing config
- **Train Jobs (3 tests):** Basic creation, disabled jobs, multiple model configs
- **Score Jobs (3 tests):** Basic creation, disabled jobs, model combination methods
- **Alert Jobs (4 tests):** Basic creation, disabled jobs, different methods/thresholds
- **Integration (3 tests):** Workflow integration, disabled jobs, error handling

**Job Types Covered:**
- Data ingestion jobs
- Model training jobs  
- Scoring/inference jobs
- Alerting jobs

### `test_config.py` (7 tests)
Tests configuration management:

- YAML file processing
- Configuration structure validation
- Default value handling
- Environment variable overrides
- Disabled batch handling
- Metrics directory validation

### `test_main.py` (6 tests)
Tests main module integration:

- Job and schedule counting
- Import validation
- Module structure verification

## Running Tests

### Run All Tests
```bash
# Run full test suite
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=anomstack

# Run with coverage report
pytest tests/ --cov=anomstack --cov-report=html
```

### Run Specific Test Files
```bash
# Data and validation tests
pytest tests/test_df.py tests/test_validate.py

# SQL and database tests
pytest tests/test_sql.py

# Alert and plotting tests
pytest tests/test_alerts.py tests/test_plots.py

# Core ML and job tests
pytest tests/test_ml.py tests/test_jobs.py

# IO and configuration tests
pytest tests/test_io.py tests/test_config.py
```

### Run Specific Test Classes or Functions
```bash
# Run specific test class
pytest tests/test_df.py::TestWrangleDF

# Run specific test function
pytest tests/test_validate.py::TestValidateDF::test_validate_df_valid_data

# Run SQL tests for specific database
pytest tests/test_sql.py -k "duckdb"
```

### Run Tests with Filters
```bash
# Run tests matching pattern
pytest tests/ -k "validation"

# Run tests for data processing
pytest tests/ -k "wrangle or validate"

# Run tests excluding plotting (to avoid matplotlib warnings)
pytest tests/ -k "not plot"
```

## Test Design Principles

### 1. **Fast and Reliable**
- Tests run in ~21 seconds total
- Comprehensive mocking for external dependencies
- Deterministic results with controlled random seeds

### 2. **Comprehensive Coverage**
- Tests cover critical code paths and edge cases
- Integration tests verify component interactions
- Real functionality testing with minimal mocking where possible

### 3. **Maintainable**
- Clear test names describing what's being tested
- Focused tests that verify specific functionality
- Proper use of mocking to isolate components

### 4. **Realistic Scenarios**
- Uses real data structures and configurations
- Tests actual error conditions and edge cases
- Validates integration between components

## Test Data and Fixtures

### Synthetic Data Generation
Tests use `pandas` and `numpy` to generate realistic time series data:
```python
# Example test data pattern for ML tests
df = pd.DataFrame({
    'metric_timestamp': pd.date_range('2023-01-01', periods=100, freq='h'),
    'metric_name': ['test_metric'] * 100,
    'metric_value': np.random.randn(100) + 50
})

# Example test data for validation tests
df = pd.DataFrame({
    'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
    'metric_batch': ['batch1'],
    'metric_name': ['cpu_usage'],
    'metric_type': ['gauge'],
    'metric_value': [85.5],
    'metadata': ['{"host": "server1"}']
})
```

### Mock Configurations
Tests use proper mocking for external services:
```python
# Example mocking pattern for SQL tests
@patch('anomstack.sql.read.get_dagster_logger')
@patch('anomstack.sql.read.read_sql_duckdb')
def test_read_sql_duckdb(mock_read_duckdb, mock_logger):
    mock_logger.return_value = MagicMock()
    test_df = pd.DataFrame({'col1': [1, 2]})
    mock_read_duckdb.return_value = test_df
    
    result = read_sql("SELECT * FROM table", "duckdb")
    
    assert_frame_equal(result, test_df)
```

## Common Test Patterns

### Testing Data Functions
```python
def test_data_function():
    # Arrange - create test dataframe
    df = pd.DataFrame({
        'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
        'metric_value': [85.5],
        'metadata': ['{"key": "value"}']
    })
    
    # Act - call function
    result = data_function(df)
    
    # Assert - verify structure and content
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert 'expected_column' in result.columns
```

### Testing with Mocks
```python
@patch('module.external_dependency')
def test_with_mocking(mock_dependency):
    # Setup mock behavior
    mock_dependency.return_value = expected_result
    
    # Test function
    result = function_under_test(params)
    
    # Verify mock was called correctly
    mock_dependency.assert_called_once_with(expected_params)
    assert result == expected_result
```

### Testing Error Conditions
```python
def test_error_handling():
    invalid_data = create_invalid_test_data()
    
    with pytest.raises(ExpectedError, match="expected error message"):
        function_under_test(invalid_data)
```

### Testing Plotting Functions
```python
def test_plotting_function():
    df = create_test_dataframe()
    
    fig = plotting_function(df, params)
    
    assert fig is not None
    assert len(fig.axes) == expected_subplot_count
    
    # Clean up to prevent memory issues
    plt.close(fig)
```

## Debugging Failed Tests

### Common Issues and Solutions

1. **Import Errors**
   - Ensure you're in the project root directory
   - Check that the virtual environment is activated
   - Verify all dependencies are installed

2. **Mock-Related Errors**
   - Check that mock patch paths are correct
   - Verify mock return values match expected types
   - Ensure mocks are configured before function calls

3. **DataFrame Comparison Issues**
   - Use `pd.testing.assert_frame_equal()` for DataFrame comparisons
   - Check for column order differences
   - Verify data types match between expected and actual

4. **Plotting Test Issues**
   - Always call `plt.close(fig)` after plotting tests
   - Use `pytest.importorskip("matplotlib")` if optional dependency
   - Handle matplotlib backend issues in CI environments

### Verbose Test Output
```bash
# Get detailed test output
pytest tests/ -v -s

# Show print statements and logs
pytest tests/ -s --log-cli-level=DEBUG

# Show warnings and stack traces
pytest tests/ --tb=long -W ignore::DeprecationWarning
```

## Performance Considerations

- **ML Tests:** 3-4 seconds each (real model training)
- **Plotting Tests:** 2-3 seconds each (matplotlib figure generation)
- **SQL Tests:** <1 second each (mocked database calls)
- **Data/Validation Tests:** <1 second each (pandas operations)
- **Job Tests:** <1 second each (job creation only)
- **Config Tests:** <100ms each (file operations)

## Contributing New Tests

### Guidelines for New Tests

1. **Follow Naming Conventions**
   - Test files: `test_<module>.py`
   - Test classes: `Test<Component>`
   - Test functions: `test_<functionality>`

2. **Keep Tests Focused**
   - One test should verify one specific behavior
   - Use descriptive test names
   - Include docstrings for complex tests

3. **Use Appropriate Mocking**
   - Mock external dependencies (databases, APIs, file systems)
   - Don't mock the code under test
   - Use realistic mock return values

4. **Handle Resources Properly**
   - Close matplotlib figures: `plt.close(fig)`
   - Clean up temporary files
   - Reset global state if modified

### Example New Test
```python
def test_new_functionality(self):
    """Test description of what this verifies."""
    # Arrange - set up test data and mocks
    test_data = create_test_data()
    
    with patch('module.dependency') as mock_dep:
        mock_dep.return_value = expected_response
        
        # Act - call the function being tested
        result = function_under_test(test_data, param=value)
        
        # Assert - verify the results
        assert result.meets_expectation()
        mock_dep.assert_called_once()
```

### Adding Tests for New Modules

When adding tests for new modules:

1. Create new test file: `tests/test_<module>.py`
2. Update this README with module description
3. Follow existing patterns for test structure
4. Add appropriate mocking for external dependencies
5. Include both positive and negative test cases

The test suite is designed to provide comprehensive coverage while maintaining fast execution times suitable for development workflows. With 115 tests covering all major components, the suite provides confidence in code quality and helps prevent regressions. 