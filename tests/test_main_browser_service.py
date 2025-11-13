"""Integration tests for main_browser_service execute workflow"""
import pytest
from unittest.mock import AsyncMock
from aiohttp import web

from main_browser_service import create_app


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")


@pytest.mark.asyncio
async def test_execute_workflow_cache_hit(aiohttp_client, monkeypatch, setup_env):
    """Ensure repeated requests hit cache and skip browser agent execution"""
    # Patch browser agent to track calls
    mock_execute = AsyncMock(return_value={
        "success": True,
        "result": "Đã xử lý thành công"
    })
    monkeypatch.setattr("main_browser_service.browser_agent.execute_freeform", mock_execute)

    app: web.Application = create_app()
    client = await aiohttp_client(app)

    payload = {
        "user_message": "Tạo đơn vay cho khách hàng Nguyễn Văn A",
        "session_id": "session-cache-test"
    }

    # First request - should call browser agent and populate cache
    resp1 = await client.post("/api/execute", json=payload)
    assert resp1.status == 200
    data1 = await resp1.json()
    assert data1["success"] is True
    assert data1.get("cached") is False

    # Second request - should be served from cache (no additional execute call)
    resp2 = await client.post("/api/execute", json=payload)
    assert resp2.status == 200
    data2 = await resp2.json()
    assert data2["success"] is True
    assert data2.get("cached") is True

    # Browser agent should have been called only once
    assert mock_execute.call_count == 1


@pytest.mark.asyncio
async def test_execute_workflow_cache_miss(aiohttp_client, monkeypatch, setup_env):
    """Ensure cache miss triggers browser agent execution"""
    mock_execute = AsyncMock(return_value={
        "success": True,
        "result": "Đã điền thành công"
    })
    monkeypatch.setattr("main_browser_service.browser_agent.execute_freeform", mock_execute)

    app: web.Application = create_app()
    client = await aiohttp_client(app)

    payload = {
        "user_message": "Cập nhật CRM khách hàng Trần Văn B",
        "session_id": "session-cache-miss"
    }

    resp = await client.post("/api/execute", json=payload)
    assert resp.status == 200
    data = await resp.json()
    assert data["success"] is True
    assert data.get("cached") is False
    assert mock_execute.call_count == 1
