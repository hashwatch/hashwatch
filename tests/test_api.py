import pytest
from httpx import AsyncClient
from project.app.main import app


API_KEY = "EXAMPLE_API_KEY"
BASE_URL = "/miners"


@pytest.mark.asyncio
async def test_register_miner():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "tag": "miner1",
            "name": "AlphaMiner",
            "model": "Antminer S19",
            "is_active": True
        }
        response = await ac.post(f"{BASE_URL}/register?api_key={API_KEY}", json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Registered successfully"


@pytest.mark.asyncio
async def test_record_metrics():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "tag": "miner1",
            "hashrate": 100.5,
            "power": 1500.0,
            "voltage": 230.0
        }
        response = await ac.post(f"{BASE_URL}/record?api_key={API_KEY}", json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Recorded successfully"


@pytest.mark.asyncio
async def test_get_devices():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{BASE_URL}/devices?api_key={API_KEY}")
        assert response.status_code == 202
        devices = response.json()
        assert isinstance(devices, list)
        assert any(d["tag"] == "miner1" for d in devices)


@pytest.mark.asyncio
async def test_get_current_metrics():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{BASE_URL}/miner1/metrics?api_key={API_KEY}")
        assert response.status_code == 202
        data = response.json()
        assert data["tag"] == "miner1"
        assert "hashrate" in data


@pytest.mark.asyncio
async def test_get_metric_history():
    async with AsyncClient(app=app, base_url="http://test") as ac:
    