from fastapi.testclient import TestClient
from settings import settings
from core import create_app
import json

client = TestClient(create_app())


def test_get_user():
    username = settings.API_SUPER_USER[0]
    password = settings.API_SUPER_USER[1]
    payload = {"username": username, "password": password}
    jwt = client.post("/authenticate", data=json.dumps(payload)).json().get("Token")
    headers = {"Authorization": "Bearer {0}".format(jwt)}
    response = client.get("/secure/user", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data.get("username") == username

