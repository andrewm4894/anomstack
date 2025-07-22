"""
Tests for LLM agent functionality.
"""

from unittest.mock import Mock, patch

import pandas as pd

from anomstack.llm.agent import detect_anomalies


class TestDetectAnomalies:
    """Test cases for the detect_anomalies function."""

    def create_sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_value': [85.5, 95.2]
        })

    @patch('anomstack.llm.agent.AnomalyAgent')
    def test_detect_anomalies_with_both_prompts(self, mock_anomaly_agent):
        """Test detect_anomalies with both detection and verification prompts."""
        # Setup
        mock_agent_instance = Mock()
        mock_anomaly_agent.return_value = mock_agent_instance

        # Mock the return values
        mock_anomalies = Mock()
        mock_agent_instance.detect_anomalies.return_value = mock_anomalies
        mock_df_result = pd.DataFrame({
            'timestamp': ['2023-01-01'],
            'variable_name': ['var1'],
            'value': [3.279153],
            'description': ['Abrupt spike in value, significantly higher than previous observations.']
        })
        mock_agent_instance.get_anomalies_df.return_value = mock_df_result

        df = self.create_sample_df()
        detection_prompt = "Custom detection prompt"
        verification_prompt = "Custom verification prompt"

        # Call function
        result = detect_anomalies(df, detection_prompt, verification_prompt)

        # Assertions
        mock_anomaly_agent.assert_called_once_with(
            detection_prompt=detection_prompt,
            verification_prompt=verification_prompt
        )
        mock_agent_instance.detect_anomalies.assert_called_once_with(
            df, timestamp_col="metric_timestamp"
        )
        mock_agent_instance.get_anomalies_df.assert_called_once_with(mock_anomalies)
        pd.testing.assert_frame_equal(result, mock_df_result)

    @patch('anomstack.llm.agent.AnomalyAgent')
    def test_detect_anomalies_with_detection_prompt_only(self, mock_anomaly_agent):
        """Test detect_anomalies with only detection prompt."""
        # Setup
        mock_agent_instance = Mock()
        mock_anomaly_agent.return_value = mock_agent_instance

        mock_anomalies = Mock()
        mock_agent_instance.detect_anomalies.return_value = mock_anomalies
        mock_df_result = pd.DataFrame({
            'timestamp': ['2023-01-01'],
            'variable_name': ['var1'],
            'value': [3.279153],
            'description': ['Abrupt spike in value, significantly higher than previous observations.']
        })
        mock_agent_instance.get_anomalies_df.return_value = mock_df_result

        df = self.create_sample_df()
        detection_prompt = "Custom detection prompt"

        # Call function
        detect_anomalies(df, detection_prompt)

        # Assertions
        mock_anomaly_agent.assert_called_once_with(detection_prompt=detection_prompt)
        mock_agent_instance.detect_anomalies.assert_called_once_with(
            df, timestamp_col="metric_timestamp"
        )

    @patch('anomstack.llm.agent.AnomalyAgent')
    def test_detect_anomalies_with_verification_prompt_only(self, mock_anomaly_agent):
        """Test detect_anomalies with only verification prompt."""
        # Setup
        mock_agent_instance = Mock()
        mock_anomaly_agent.return_value = mock_agent_instance

        mock_anomalies = Mock()
        mock_agent_instance.detect_anomalies.return_value = mock_anomalies
        mock_df_result = pd.DataFrame({
            'timestamp': ['2023-01-01'],
            'variable_name': ['var1'],
            'value': [3.279153],
            'description': ['Abrupt spike in value, significantly higher than previous observations.']
        })
        mock_agent_instance.get_anomalies_df.return_value = mock_df_result

        df = self.create_sample_df()
        verification_prompt = "Custom verification prompt"

        # Call function
        detect_anomalies(df, verification_prompt=verification_prompt)

        # Assertions
        mock_anomaly_agent.assert_called_once_with(verification_prompt=verification_prompt)

    @patch('anomstack.llm.agent.AnomalyAgent')
    def test_detect_anomalies_with_no_prompts(self, mock_anomaly_agent):
        """Test detect_anomalies with no custom prompts (uses defaults)."""
        # Setup
        mock_agent_instance = Mock()
        mock_anomaly_agent.return_value = mock_agent_instance

        mock_anomalies = Mock()
        mock_agent_instance.detect_anomalies.return_value = mock_anomalies
        mock_df_result = pd.DataFrame({
            'timestamp': ['2023-01-01'],
            'variable_name': ['var1'],
            'value': [3.279153],
            'description': ['Abrupt spike in value, significantly higher than previous observations.']
        })
        mock_agent_instance.get_anomalies_df.return_value = mock_df_result

        df = self.create_sample_df()

        # Call function with no prompts
        detect_anomalies(df)

        # Assertions - should be called with no arguments (uses defaults)
        mock_anomaly_agent.assert_called_once_with()

    @patch('anomstack.llm.agent.AnomalyAgent')
    def test_detect_anomalies_with_none_prompts(self, mock_anomaly_agent):
        """Test detect_anomalies with explicitly None prompts."""
        # Setup
        mock_agent_instance = Mock()
        mock_anomaly_agent.return_value = mock_agent_instance

        mock_anomalies = Mock()
        mock_agent_instance.detect_anomalies.return_value = mock_anomalies
        mock_df_result = pd.DataFrame({'timestamp': ['2023-01-01'], 'anomaly': [True]})
        mock_agent_instance.get_anomalies_df.return_value = mock_df_result

        df = self.create_sample_df()

        # Call function with explicit None values
        detect_anomalies(df, detection_prompt=None, verification_prompt=None)

        # Assertions - should be called with no arguments (None values filtered out)
        mock_anomaly_agent.assert_called_once_with()


class TestLLMAlertPromptExtraction:
    """Test cases for prompt extraction logic in llmalert job."""

    def test_detection_prompt_extraction_new_param(self):
        """Test extraction of detection prompt using new parameter name."""
        spec = {
            "llmalert_anomaly_agent_detection_prompt": "Custom detection prompt"
        }

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt == "Custom detection prompt"
        assert verification_prompt is None

    def test_detection_prompt_extraction_legacy_param(self):
        """Test extraction of detection prompt using legacy parameter name."""
        spec = {
            "llmalert_anomaly_agent_system_prompt": "Legacy system prompt"
        }

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt == "Legacy system prompt"
        assert verification_prompt is None

    def test_detection_prompt_extraction_priority(self):
        """Test that new parameter takes priority over legacy parameter."""
        spec = {
            "llmalert_anomaly_agent_detection_prompt": "New detection prompt",
            "llmalert_anomaly_agent_system_prompt": "Legacy system prompt"
        }

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt == "New detection prompt"
        assert verification_prompt is None

    def test_verification_prompt_extraction(self):
        """Test extraction of verification prompt."""
        spec = {
            "llmalert_anomaly_agent_verification_prompt": "Custom verification prompt"
        }

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt is None
        assert verification_prompt == "Custom verification prompt"

    def test_both_prompts_extraction(self):
        """Test extraction of both prompts."""
        spec = {
            "llmalert_anomaly_agent_detection_prompt": "Custom detection prompt",
            "llmalert_anomaly_agent_verification_prompt": "Custom verification prompt"
        }

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt == "Custom detection prompt"
        assert verification_prompt == "Custom verification prompt"

    def test_no_prompts_extraction(self):
        """Test extraction when no prompts are configured."""
        spec = {}

        # Simulate the extraction logic from llmalert.py
        detection_prompt = (
            spec.get("llmalert_anomaly_agent_detection_prompt") or
            spec.get("llmalert_anomaly_agent_system_prompt")
        )
        verification_prompt = spec.get("llmalert_anomaly_agent_verification_prompt")

        assert detection_prompt is None
        assert verification_prompt is None
