import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="cal_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


# ── CALENDAR API (16-25) ─────────────────────────────────────────────────────

def test_16_17_18_daily_aggregation_and_mixed_frequencies(client):
    token = get_auth_token(client, "cal16@example.com")
    today = get_user_today("UTC")
    start = today - timedelta(days=2)

    # Habit 1: Daily
    h1 = client.post(
        "/api/v1/habits",
        json={"title": "Daily Habit", "category": "fitness", "start_date": start.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Habit 2: Daily
    h2 = client.post(
        "/api/v1/habits",
        json={"title": "Daily Reading", "category": "reading", "start_date": start.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete h1 today, complete h1 & h2 yesterday
    yesterday = today - timedelta(days=1)
    client.post(f"/api/v1/habits/{h1}/complete", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/v1/habits/{h1}/complete", json={"completed_date": yesterday.isoformat()}, headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/v1/habits/{h2}/complete", json={"completed_date": yesterday.isoformat()}, headers={"Authorization": f"Bearer {token}"})

    res = client.get(
        f"/api/v1/analytics/calendar?start_date={start.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    days = res.json()["days"]
    assert len(days) == 3

    # Check yesterday (100% completion)
    y_day = [d for d in days if d["date"] == yesterday.isoformat()][0]
    assert y_day["expected"] == 2
    assert y_day["completed"] == 2
    assert y_day["percentage"] == 100.0

    # Check today (50% completion)
    t_day = [d for d in days if d["date"] == today.isoformat()][0]
    assert t_day["expected"] == 2
    assert t_day["completed"] == 1
    assert t_day["percentage"] == 50.0


def test_19_zero_expected_habits(client):
    token = get_auth_token(client, "cal19@example.com")
    today = get_user_today("UTC")
    res = client.get(
        f"/api/v1/analytics/calendar?start_date={today.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    days = res.json()["days"]
    assert days[0]["expected"] == 0
    assert days[0]["completed"] == 0
    assert days[0]["percentage"] == 0.0


def test_23_user_isolation(client):
    token_a = get_auth_token(client, "calA@example.com")
    token_b = get_auth_token(client, "calB@example.com")
    today = get_user_today("UTC")

    # User A creates & completes habit
    h_a = client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "fitness", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]
    client.post(f"/api/v1/habits/{h_a}/complete", headers={"Authorization": f"Bearer {token_a}"})

    # User B calendar should be empty (0 expected, 0 completed)
    res_b = client.get(
        f"/api/v1/analytics/calendar?start_date={today.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    day = res_b.json()["days"][0]
    assert day["expected"] == 0
    assert day["completed"] == 0


def test_24_25_date_range_limits(client):
    token = get_auth_token(client, "cal24@example.com")
    today = get_user_today("UTC")

    # Exceeding 365 days
    res = client.get(
        f"/api/v1/analytics/calendar?start_date={(today - timedelta(days=400)).isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400

    # Start date > End date
    res_inv = client.get(
        f"/api/v1/analytics/calendar?start_date={today.isoformat()}&end_date={(today - timedelta(days=5)).isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_inv.status_code == 400
