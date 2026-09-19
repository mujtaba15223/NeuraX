from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_unified_analysis_contract_has_process_and_production_data(monkeypatch):
    monkeypatch.setattr(
        "backend.main.predict_image",
        lambda path: {
            "status": "defective",
            "anomaly_score": 0.42,
            "threshold": 0.05,
            "is_defective": True,
            "model": "test-anomaly-model",
        },
    )

    inspection = client.post(
        "/inspection",
        files={
            "file": (
                "contract-test.png",
                b"test-image",
                "image/png",
            )
        },
    )

    assert inspection.status_code == 200
    assert inspection.json()["defect_type"] == "visual anomaly"

    response = client.get("/analysis")
    assert response.status_code == 200

    payload = response.json()

    assert "production_impact" in payload
    assert payload["production_impact"]["total_estimated_impact"] > 0
    assert payload["vision"]["filename"] == "contract-test.png"
    assert payload["root_cause"]["defect"] == "visual anomaly"
    assert payload["production_impact"]["status"] == "inspection_context_applied"
    assert isinstance(payload.get("process", {}).get("analysis"), list)
    assert len(payload["process"]["analysis"]) >= 3
    assert payload["process"]["top_process_candidate"]["station"] in {
        "Drilling",
        "Milling",
        "Assembly",
    }
    assert "production" in payload
    assert "economics" in payload
    assert payload["production"]["total_parts"] > 0
    assert isinstance(payload.get("root_cause", {}).get("process_features"), list)
    assert payload["root_cause"]["likely_contributing_factor"] in {
        "Drilling",
        "Milling",
        "Assembly",
    }
