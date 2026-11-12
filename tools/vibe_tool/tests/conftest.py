"""Keep CLI auto-registration in regression tests out of the user's real index."""
import uuid
import pytest


@pytest.fixture(autouse=True)
def isolate_project_registry(monkeypatch, tmp_path_factory):
    folder = tmp_path_factory.getbasetemp() / 'project-registry-isolation'
    monkeypatch.setenv('VIBE_PROJECTS_FILE', str(folder / (uuid.uuid4().hex + '.json')))
