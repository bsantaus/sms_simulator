import pytest
from fastapi.testclient import TestClient

import json

from monitor.backend.main import app

@pytest.fixture
def client():
    tc = TestClient(app)
    
    # `app` state does not reset between tests
    res = tc.post("/reset")
    assert res.status_code == 200
    return tc


def test_report_message_success(client):

    res = client.post("/message", json={
        "message": "fake message",
        "phone": "1234567890",
        "success": True,
        "delay": 1
    })
    
    assert res.status_code == 200

    # FastAPI by default returns JSON - use json.loads
    # to remove unnecessary quotes
    assert json.loads(res.content) == "OK"

def test_report_message_failure(client):

    # missing field
    res = client.post("/message", json={
        "message": "fake message",
        "phone": "1234567890",
        "success": True,
    })
    
    assert res.status_code == 422

    # invalid value for field
    res = client.post("/message", json={
        "message": "fake message",
        "phone": "1234567890",
        "success": False,
        "delay": None
    })

    assert res.status_code == 422

def test_retrieve_statistics(client):

    res = client.get("/statistics")

    assert res.status_code == 200
    
    initial_stats = json.loads(res.content)

    assert initial_stats["total_messages"] == 0
    assert initial_stats["success_messages"] == 0
    assert initial_stats["average_delay"] == 0

    fake_messages = [(True, 0.5), (True, 1.2), (False, 0.4), (False, 1.1)]

    expected_stats = [
        {
            "success_messages": 1,
            "average_delay": 0.5
        },
        {
            "success_messages": 2,
            "average_delay": 0.85
        },
        {
            "success_messages": 2,
            "average_delay": 0.7
        },
        {
            "success_messages": 2,
            "average_delay": 0.8
        },
    ]

    for idx, (success, delay) in enumerate(fake_messages):

        res = client.post("/message", json={
            "message": "fake message",
            "phone": "1234567890",
            "success": success,
            "delay": delay
        })
    
        assert res.status_code == 200

        stats_res = client.get("/statistics")

        assert stats_res.status_code == 200

        stats = json.loads(stats_res.content)

        assert stats["total_messages"] == idx + 1
        assert stats["success_messages"] == expected_stats[idx]["success_messages"]
        assert round(stats["average_delay"], 5) == round(expected_stats[idx]["average_delay"], 5)


