from fastapi.testclient import TestClient
from settings import settings
from core import create_app
import json

client = TestClient(create_app())


def test_authenticate():
    username = settings.API_SUPER_USER[0]
    password = settings.API_SUPER_USER[1]
    payload = {"username": username, "password": password}
    response = client.post("/authenticate", data=json.dumps(payload))
    assert response.status_code == 200
    assert "Token" in response.json()

