from anomstack.sensors.timeout import get_kill_after_minutes


def test_get_kill_after_minutes_env(monkeypatch):
    monkeypatch.setenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES", "30")
    assert get_kill_after_minutes() == 30


def test_get_kill_after_minutes_yaml(tmp_path, monkeypatch):
    # Clear any existing environment variable first
    monkeypatch.delenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES", raising=False)
    yaml_file = tmp_path / "dagster.yaml"
    yaml_file.write_text("kill_sensor:\n  kill_after_minutes: 45\n")
    monkeypatch.setenv("DAGSTER_HOME", str(tmp_path))
    assert get_kill_after_minutes() == 45


def test_get_kill_after_minutes_default(tmp_path, monkeypatch):
    # Clear any existing environment variable first
    monkeypatch.delenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES", raising=False)
    monkeypatch.setenv("DAGSTER_HOME", str(tmp_path))
    assert get_kill_after_minutes() == 15
