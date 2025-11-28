import pytest
from fastapi.testclient import TestClient
from app.main import app  # adjust if your main application file name differs

client = TestClient(app)


def test_angle_api_crisis_and_blame():
    payload = {
        "text": "This disaster happened because the mayor is to blame."
    }

    resp = client.post("/api/angle", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    assert data["dominant_emotions"] == ["fear"]
    assert "crisis" in data["framing_patterns"]
    assert "blame" in data["framing_patterns"]

    # evidence spans should include matched words
    assert "disaster" in data["evidence_spans"]
    assert "blame" in data["evidence_spans"]

    assert data["confidence"] == 1.0


def test_angle_api_anecdotal():
    payload = {
        "text": "My friend told me what happened, but there were no official numbers."
    }

    resp = client.post("/api/angle", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    assert "anecdotal" in data["framing_patterns"]
    assert any("my friend" in span for span in data["evidence_spans"])


def test_angle_api_no_patterns():
    payload = { "text": "The sky is blue and the grass is green." }

    resp = client.post("/api/angle", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    assert data["framing_patterns"] == []
    assert data["dominant_emotions"] == []
    assert data["evidence_spans"] == []
    assert "does not strongly match" in data["angle_summary"]
