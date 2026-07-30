from pathlib import Path

from app.retrieval import retrieve


def test_retrieve_finds_fabric_guidance(tmp_path: Path):
    (tmp_path / "runbook.md").write_text(
        "Model weights should be mounted from a persistent volume on Fabric.",
        encoding="utf-8",
    )
    results = retrieve("Where should model weights be mounted on Fabric?", tmp_path)
    assert results
    assert "persistent volume" in results[0].text
