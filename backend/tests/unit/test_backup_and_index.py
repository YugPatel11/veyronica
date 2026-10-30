import os
import tempfile
from pathlib import Path
import pytest
from scripts.backup_restore import perform_backup, verify_restore
from scripts.index_plan import run_explain_plan


def test_backup_and_restore_cycle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        backup_dir = Path(tmp_dir) / "backups"
        res = perform_backup(backup_dir, db_url="sqlite:///:memory:")
        assert "backup_path" in res
        assert "metadata_path" in res
        assert "sha256" in res
        assert Path(res["backup_path"]).exists()

        # Verify restore verification succeeds
        restore_ok = verify_restore(Path(res["backup_path"]), Path(res["metadata_path"]))
        assert restore_ok is True


def test_index_plan_execution():
    plan_results = run_explain_plan(":memory:")
    assert len(plan_results) >= 4
    for q_name, plans in plan_results.items():
        assert len(plans) > 0
        assert any(p["uses_index"] for p in plans)
