import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="hist_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


# ── HABIT HISTORY (1-15) ─────────────────────────────────────────────────────

def test_1_unauthenticated_history_rejected(client):
    res = client.get("/api/v1/habits/00000000-0000-0000-0000-000000000000/history")
    assert res.status_code in (401, 403)


def test_2_authenticated_history_works(client):
    token = get_auth_token(client, "hist2@example.com")
    today = get_user_today("UTC")
    habit_id = client.post(
        "/api/v1/habits",
        json={"title": "Workout", "category": "fitness", "start_date": (today - timedelta(days=5)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    res = client.get(
        f"/api/v1/habits/{habit_id}/history?start_date={(today - timedelta(days=5)).isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["days"]) == 6
    assert data["habit"]["id"] == habit_id


def test_3_user_isolation(client):
    token_a = get_auth_token(client, "histA@example.com")
    token_b = get_auth_token(client, "histB@example.com")

    habit_a = client.post(
        "/api/v1/habits",
        json={"title": "Private Habit", "category": "career"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]

    res = client.get(
        f"/api/v1/habits/{habit_a}/history",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res.status_code == 403


def test_4_invalid_date_range(client):
    token = get_auth_token(client, "hist4@example.com")
    today = get_user_today("UTC")
    habit_id = client.post(
        "/api/v1/habits",
        json={"title": "Habit 4", "category": "study"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # start_date > end_date
    res = client.get(
        f"/api/v1/habits/{habit_id}/history?start_date={today.isoformat()}&end_date={(today - timedelta(days=5)).isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400

    # range > 365 days
    res2 = client.get(
        f"/api/v1/habits/{habit_id}/history?start_date={(today - timedelta(days=400)).isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 400


def test_5_6_7_8_9_day_states(client):
    token = get_auth_token(client, "hist5@example.com")
    today = get_user_today("UTC")
    start = today - timedelta(days=2)

    # Weekdays habit (due Mon-Fri)
    habit_id = client.post(
        "/api/v1/habits",
        json={
            "title": "Weekday Study",
            "category": "study",
            "frequency_type": "weekdays",
            "start_date": start.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete today
    client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"value": 2, "notes": "Great session"},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get(
        f"/api/v1/habits/{habit_id}/history?start_date={start.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    days = res.json()["days"]
    assert len(days) == 3

    today_day = [d for d in days if d["date"] == today.isoformat()][0]
    assert today_day["is_completed"] is True
    assert today_day["value"] == 2.0
    assert today_day["notes"] == "Great session"


def test_10_11_12_13_14_frequencies_due_states(client):
    token = get_auth_token(client, "histfreq@example.com")
    today = get_user_today("UTC")
    # Choose Monday of current or recent week
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    # Weekend habit
    h_weekend = client.post(
        "/api/v1/habits",
        json={"title": "Weekend Rest", "category": "sleep", "frequency_type": "weekends", "start_date": monday.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    res = client.get(
        f"/api/v1/habits/{h_weekend}/history?start_date={monday.isoformat()}&end_date={sunday.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    days = res.json()["days"]
    # Mon-Fri (indices 0..4) should not be due, Sat-Sun (indices 5..6) should be due
    for i in range(5):
        assert days[i]["is_due"] is False
    assert days[5]["is_due"] is True
    assert days[6]["is_due"] is True


def test_15_timezone_boundary(client):
    token = get_auth_token(client, "histtz@example.com", timezone="Asia/Tokyo")
    today_tokyo = get_user_today("Asia/Tokyo")

    habit_id = client.post(
        "/api/v1/habits",
        json={"title": "Tokyo Habit", "category": "coding", "start_date": today_tokyo.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    res = client.get(f"/api/v1/habits/{habit_id}/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["end_date"] == today_tokyo.isoformat()
