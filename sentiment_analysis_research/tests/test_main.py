# tests/test_main_real.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthcheck():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "Sentiment Analysis API is up and running!"

def test_feedback_sentiment_positive():
    res = client.post("/feedback", json={"feedback": "I had a great experience with your service"})
    assert res.status_code == 200
    assert res.json()["prediction"] in ["positive"]

def test_feedback_sentiment_negative():
    res = client.post("/feedback", json={"feedback": "This was the worst experience ever."})
    assert res.status_code == 200
    assert res.json()["prediction"] in ["negative"]

def test_feedback_category_claim():
    res = client.post("/category", json={"feedback": "My claim took too long to process."})
    assert res.status_code == 200
    assert res.json()["prediction"] in ["claim"]

def test_feedback_category_service():
    res = client.post("/category", json={"feedback": "Your customer support is excellent!"})
    assert res.status_code == 200
    assert res.json()["prediction"] in ["service"]


def test_feedback_missing_field():
    res = client.post("/feedback", json={"text": "something"})
    assert res.status_code == 422  # Unprocessable Entity (validation error)

def test_feedback_wrong_type():
    res = client.post("/feedback", json={"feedback": 12345})
    assert res.status_code == 422  # FastAPI expects a string, not int

