import os
import pytest
from app.services.gemini_adapter import (
    get_gemini_adapter,
    GeminiAdapter,
    MockGeminiAdapter,
)

pytestmark = pytest.mark.asyncio


async def test_mock_adapter_is_loaded_when_no_api_key(monkeypatch):
    # Ensure environment variable is removed
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    adapter = get_gemini_adapter()

    assert isinstance(adapter, MockGeminiAdapter)

    result = await adapter.generate("hello mock")

    assert result["mock"] is True
    assert result["prompt_received"] == "hello mock"


async def test_real_adapter_loaded_when_api_key_present(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "FAKE_KEY")

    adapter = get_gemini_adapter()

    assert isinstance(adapter, GeminiAdapter)
    assert adapter.api_key == "FAKE_KEY"

    # Calling generate should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        await adapter.generate("hello real")
