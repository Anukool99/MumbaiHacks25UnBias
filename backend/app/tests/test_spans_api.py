import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_spans_basic_structure():
    text = "This is always alarming and intentionally makes it difficult."
    resp = client.post("/api/spans", json={"text": text})

    assert resp.status_code == 200
    data = resp.json()
    assert "spans" in data
    assert isinstance(data["spans"], list)

    for span in data["spans"]:
        assert "label" in span
        assert "span_text" in span
        assert "start" in span
        assert "end" in span
        assert "confidence" in span


def test_offsets_match():
    text = "He always says it's alarming."
    resp = client.post("/api/spans", json={"text": text})
    spans = resp.json()["spans"]

    for span in spans:
        s = span["start"]
        e = span["end"]
        extracted = text[s:e]
        assert extracted.lower() == span["span_text"].lower()


def test_detect_expected_labels():
    text = "She intentionally never does it because it is disastrous."
    resp = client.post("/api/spans", json={"text": text})
    spans = resp.json()["spans"]

    labels = [s["label"] for s in spans]
    assert "Intent Attribution" in labels
    assert "Overgeneralization" in labels
    assert "Loaded Language" in labels
