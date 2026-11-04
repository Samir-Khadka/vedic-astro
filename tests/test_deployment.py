"""Phase 2 deployment: render.yaml and CI workflow stay valid and in sync."""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_render_blueprint():
    doc = yaml.safe_load((ROOT / "render.yaml").read_text())
    svc = doc["services"][0]
    assert svc["type"] == "web" and svc["env"] == "python"
    assert "main:app" in svc["startCommand"] and "$PORT" in svc["startCommand"]
    assert svc["healthCheckPath"] == "/health"
    assert "requirements.txt" in svc["buildCommand"]


def test_ci_workflow_runs_both_suites():
    doc = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    steps = doc["jobs"]["test"]["steps"]
    commands = " ".join(str(s.get("run", "")) for s in steps)
    assert "pytest" in commands
    assert "node --test" in commands
    # PyYAML 1.1 parses the key `on` as boolean True.
    on = doc.get("on", doc.get(True))
    assert on and "pull_request" in on
