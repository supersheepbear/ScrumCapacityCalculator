"""User-facing calculation cases through the HTTP endpoint."""

import json

from app import app


def sample_config():
    return {
        "sprint": {"sprint_name": "Sprint 1", "start_date": "2024-01-08", "end_date": "2024-01-19"},
        "locations": [{"name": "Beijing", "country_code": "CN", "manual_holidays": ["2024-01-10"]}],
        "team_members": [
            {"name": "Alice", "jira_name": "alice", "group": "A", "location": "Beijing", "daily_hours": 8},
            {"name": "Bob", "jira_name": "bob", "group": "B", "location": "Beijing", "daily_hours": 6},
        ],
        "group_holidays": [{"group": "A", "location": "Beijing", "dates": ["2024-01-11"]}],
        "ptos": [
            {"name": "Alice", "date": "2024-01-10", "hours": 4},
            {"name": "Alice", "date": "2024-01-13", "hours": 8},
            {"name": "Alice", "date": "2024-01-12", "hours": 3},
            {"name": "Alice", "date": "2024-01-12", "hours": 7},
        ],
    }


def post(config=None, csv=None, unit="hours"):
    return app.test_client().post("/calculate", data={
        "config_json": json.dumps(config or sample_config()),
        "jira_csv": csv or "Issue Key,Summary,Assignee,Sprint,Estimate\nA-1,Task,alice,Sprint 1,60\nB-1,Task,bob,Sprint 1,20\n",
        "estimate_unit": unit,
    })


def test_capacity_respects_location_group_and_overlapping_pto():
    response = post()
    assert response.status_code == 200
    data = response.get_json()
    alice, bob = data["results"]
    assert alice["member_name"] == "Alice"
    assert alice["capacity_hours"] == 56
    assert alice["planned_hours"] == 60
    assert alice["remaining_hours"] == -4
    assert alice["status"] == "overload"
    assert bob["capacity_hours"] == 54
    assert bob["status"] == "normal"
    assert data["summary"]["total_capacity"] == 110


def test_estimate_unit_must_be_confirmed():
    response = post(unit="points")
    assert response.status_code == 400
    assert "hours" in response.get_json()["error"]


def test_wrong_sprint_is_reported_instead_of_zero_planned_work():
    response = post(csv="Issue Key,Assignee,Sprint,Estimate\nA-1,alice,Other,10\n")
    assert response.status_code == 400
    assert "No Jira tasks match" in response.get_json()["error"]


def test_zero_capacity_and_planned_work_is_overload_without_invalid_json():
    config = sample_config()
    config["locations"][0]["manual_holidays"] = [
        f"2024-01-{day:02d}" for day in range(8, 20)
    ]
    response = post(config=config)
    assert response.status_code == 200
    alice = response.get_json()["results"][0]
    assert alice["capacity_hours"] == 0
    assert alice["load_rate"] is None
    assert alice["status"] == "overload"
