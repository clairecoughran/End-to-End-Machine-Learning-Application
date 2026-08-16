import pytest
import pandas as pd 
import app
import psycopg
from fastapi.testclient import TestClient
client = TestClient(app.app)

# UNIT TEST
def test_import_model():
    model = app.import_model()
    assert model != None

# INTEGRATION TEST
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ex_and_predict():
    response = client.get("/example")
    data = response.json()
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    assert "delay" in response.json() 

