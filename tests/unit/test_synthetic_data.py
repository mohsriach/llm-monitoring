from monitoring.log_store import fetch_recent_logs
from monitoring.synthetic_data import seed_synthetic_drift_data


def test_seed_synthetic_drift_data_inserts_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "requests.db"
    monkeypatch.setenv("MONITORING_DB_PATH", str(db_path))

    summary = seed_synthetic_drift_data(baseline_size=20, current_size=10)

    logs = fetch_recent_logs(limit=100, db_path=str(db_path))
    assert summary["inserted"] == 30
    assert len(logs) == 30
