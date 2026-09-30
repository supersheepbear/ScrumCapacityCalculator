#!/usr/bin/env python
"""Quick test script to verify the Scrum Capacity Calculator is working."""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint."""
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200 and response.json()["status"] == "healthy":
        print("   ✓ Health check passed")
        return True
    else:
        print("   ✗ Health check failed")
        return False

def test_main_page():
    """Test main page loads."""
    print("2. Testing main page...")
    response = requests.get(BASE_URL)
    if response.status_code == 200 and "Scrum Capacity Calculator" in response.text:
        print("   ✓ Main page loads")
        return True
    else:
        print("   ✗ Main page failed to load")
        return False

def test_config_editor():
    """Test config editor page loads."""
    print("3. Testing config editor page...")
    response = requests.get(f"{BASE_URL}/config-editor")
    if response.status_code == 200 and "Configuration Editor" in response.text:
        print("   ✓ Config editor loads")
        return True
    else:
        print("   ✗ Config editor failed to load")
        return False

def test_calculate():
    """Test capacity calculation."""
    print("4. Testing capacity calculation...")

    config = {
        "sprint": {
            "sprint_name": "2024-Q1-Sprint-1",
            "start_date": "2024-01-08",
            "end_date": "2024-01-19"
        },
        "team_members": [
            {
                "name": "张三",
                "jira_name": "john.doe",
                "daily_hours": 8,
                "location": "Beijing"
            }
        ],
        "locations": [
            {
                "name": "Beijing",
                "country_code": "CN",
                "manual_holidays": []
            }
        ],
        "ptos": [
            {
                "name": "张三",
                "date": "2024-01-10",
                "hours": 8
            }
        ]
    }

    jira_csv = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-101,Test Task,john.doe,2024-Q1-Sprint-1,20"""

    response = requests.post(
        f"{BASE_URL}/calculate",
        data={
            "config_json": json.dumps(config),
            "jira_csv": jira_csv
        }
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("   ✓ Calculation succeeded")
            print(f"     - Team members: {data['summary']['total_members']}")
            print(f"     - Total capacity: {data['summary']['total_capacity']}h")
            print(f"     - Total planned: {data['summary']['total_planned']}h")
            print(f"     - Average load: {data['summary']['average_load_rate']:.1f}%")
            return True
        else:
            print(f"   ✗ Calculation failed: {data.get('error')}")
            return False
    else:
        print(f"   ✗ Request failed with status {response.status_code}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Scrum Capacity Calculator - Quick Test")
    print("=" * 60)
    print()

    tests = [
        test_health_check,
        test_main_page,
        test_config_editor,
        test_calculate
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")
            results.append(False)
        print()

    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    if all(results):
        print("✓ All tests passed! System is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running at http://localhost:5000?")
        print("  Start with: python app.py")
        sys.exit(1)
