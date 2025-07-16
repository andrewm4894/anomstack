
from anomstack.sensors.timeout import get_kill_after_minutes


def test_get_kill_after_minutes_env(monkeypatch):
    monkeypatch.setenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES", "30")
    assert get_kill_after_minutes() == 30
    monkeypatch.delenv("ANOMSTACK_KILL_RUN_AFTER_MINUTES")


def test_get_kill_after_minutes_yaml(tmp_path, monkeypatch):
    yaml_file = tmp_path / "dagster.yaml"
    yaml_file.write_text("kill_sensor:\n  kill_after_minutes: 45\n")
    monkeypatch.setenv("DAGSTER_HOME", str(tmp_path))
    assert get_kill_after_minutes() == 45
    monkeypatch.delenv("DAGSTER_HOME")


def test_get_kill_after_minutes_default(tmp_path, monkeypatch):
    monkeypatch.setenv("DAGSTER_HOME", str(tmp_path))
    assert get_kill_after_minutes() == 60
    monkeypatch.delenv("DAGSTER_HOME")
