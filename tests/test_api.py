import time

from fastapi.testclient import TestClient
from app.main import app
from app.internal.config import THRESHOLD_SEC

API_KEY = 'EXAMPLE_API_KEY'


miner_data = {
    'miner1': {
        "tag": "miner1",
        "name": "Antminer",
        "model": "S19"
    },
    'miner2': {
        "tag": "miner2",
        "name": "Whatsminer",
        "model": "M30S"
    }
}


def test_get_devices_empty():
    with TestClient(app) as client:
        response = client.get(f'/devices?api_key={API_KEY}')
        assert response.status_code == 202
        assert response.json() == []


def test_register_miner():
    with TestClient(app) as client:
        response = client.post(f"/register?api_key={API_KEY}", json=miner_data['miner1'])
        assert response.status_code == 201
        assert response.json() == {"message": "Registered successfully"}

        response = client.get(f"/devices?api_key={API_KEY}")
        devices = response.json()
        assert len(devices) == 1
        assert devices[0]["tag"] == "miner1"
        assert devices[0]["is_active"] is False


def test_record_metrics_and_active_flag():
    with TestClient(app) as client:
        client.post(f"/register?api_key={API_KEY}", json=miner_data['miner1'])

        metrics_data = {
            "tag": "miner1",
            "hashrate": 95.0,
            "power": 3200,
            "voltage": 220,
            "time": "2025-09-09T12:00:00"
        }
        response = client.post(f"/record?api_key={API_KEY}", json=metrics_data)
        assert response.status_code == 201

        response = client.get(f"/devices?api_key={API_KEY}")
        devices = response.json()
        assert devices[0]["is_active"] is True


def test_get_empty_history():
    param = 'hashrate'

    with TestClient(app) as client:
        client.post(f'/register?api_key={API_KEY}', json=miner_data["miner2"])
        response = client.get(f'/{miner_data["miner2"]["tag"]}/history?api_key={API_KEY}&param={param}')
        assert response.status_code == 202
        assert response.json()['points'] == 0
        assert response.json()['tag'] == miner_data['miner2']['tag']


def test_get_filled_history():
    param = 'hashrate'

    metrics_data_1 = {
        "tag": "miner2",
        "hashrate": 95.0,
        "power": 3200,
        "voltage": 220,
    }

    metrics_data_2 = {
        "tag": "miner2",
        "hashrate": 105.0,
        "power": 3230,
        "voltage": 218,
    }
    with TestClient(app) as client:
        client.post(f'/register?api_key={API_KEY}', json=miner_data["miner2"])
        client.post(f"/record?api_key={API_KEY}", json=metrics_data_1)
        client.post(f"/record?api_key={API_KEY}", json=metrics_data_2)

        response = client.get(f'/miner2/history?api_key={API_KEY}&param={param}')
        assert response.status_code == 202
        assert response.json()['tag'] == miner_data['miner2']['tag']
        assert response.json()['points'] == 2
        assert response.json()['data'][0]['value'] == 95.0
        assert response.json()['data'][1]['value'] == 105.0
        

def test_inactive_after_timeout():
    with TestClient(app) as client:
        client.post(f"/register?api_key={API_KEY}", json=miner_data['miner2'])
        metrics_data = {
            "tag": "miner2",
            "hashrate": 80.0,
            "power": 3000,
            "voltage": 220,
            "time": "2025-09-09T12:00:00"
        }
        client.post(f"/record?api_key={API_KEY}", json=metrics_data)

        response = client.get(f"/devices?api_key={API_KEY}")
        assert response.json()[0]["is_active"] is True

        time.sleep(THRESHOLD_SEC + 1)

        response = client.get(f"/devices?api_key={API_KEY}")
        assert response.json()[0]["is_active"] is False
