import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="dash@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


def test_1_unauthenticated_dashboard_rejected(client):
    res = client.get("/api/v1/dashboard")
    assert res.status_code in (401, 403)


def test_2_authenticated_dashboard_succeeds(client):
    token = get_auth_token(client, "dash2@example.com")
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "user" in data
    assert "today" in data
    assert "consistency_summary" in data


def test_3_15_user_isolation(client):
    token_a = get_auth_token(client, "d_userA@example.com")
    token_b = get_auth_token(client, "d_userB@example.com")

    # User A creates a habit
    client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B requests dashboard
    res_b = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    b_habits = res_b.json()["today"]["habits"]
    assert len(b_habits) == 0  # Does not see User A's habit


def test_4_daily_habits_appear(client):
    token = get_auth_token(client, "dash4@example.com")
    client.post(
        "/api/v1/habits",
        json={"title": "Daily Workout", "category": "fitness", "frequency_type": "daily"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    habits = res.json()["today"]["habits"]
    assert len(habits) == 1
    assert habits[0]["title"] == "Daily Workout"


def test_5_weekday_habits_appear_only_when_due(client):
    token = get_auth_token(client, "dash5@example.com")
    today = get_user_today("UTC")
    is_weekday = today.weekday() in (0, 1, 2, 3, 4)

    client.post(
        "/api/v1/habits",
        json={"title": "Weekday Coding", "category": "coding", "frequency_type": "weekdays"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    habits = res.json()["today"]["habits"]
    if is_weekday:
        assert len(habits) == 1
    else:
        assert len(habits) == 0


def test_6_weekend_habits_behave_correctly(client):
    token = get_auth_token(client, "dash6@example.com")
    today = get_user_today("UTC")
    is_weekend = today.weekday() in (5, 6)

    client.post(
        "/api/v1/habits",
        json={"title": "Weekend Hike", "category": "fitness", "frequency_type": "weekends"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    habits = res.json()["today"]["habits"]
    if is_weekend:
        assert len(habits) == 1
    else:
        assert len(habits) == 0


def test_7_weekly_habits_behave_correctly(client):
    token = get_auth_token(client, "dash7@example.com")
    client.post(
        "/api/v1/habits",
        json={"title": "Weekly Planning", "category": "productivity", "frequency_type": "weekly"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    habits = res.json()["today"]["habits"]
    assert len(habits) == 1


def test_8_9_completed_and_incomplete_habits_marked(client):
    token = get_auth_token(client, "dash8@example.com")

    h1 = client.post(
        "/api/v1/habits",
        json={"title": "Habit Completed", "category": "fitness"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    client.post(
        "/api/v1/habits",
        json={"title": "Habit Pending", "category": "study"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Complete habit 1 today
    client.post(
        f"/api/v1/habits/{h1}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    data = res.json()["today"]
    assert data["total_expected_habits"] == 2
    assert data["completed_habits"] == 1
    assert data["completion_percentage"] == 50.0

    completed_list = [h for h in data["habits"] if h["completed_today"]]
    pending_list = [h for h in data["habits"] if not h["completed_today"]]
    assert len(completed_list) == 1
    assert len(pending_list) == 1
    assert completed_list[0]["title"] == "Habit Completed"


def test_10_11_zero_expected_habits(client):
    token = get_auth_token(client, "dash10@example.com")
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    data = res.json()["today"]
    assert data["total_expected_habits"] == 0
    assert data["completed_habits"] == 0
    assert data["completion_percentage"] == 0.0


def test_12_timezone_affects_date(client):
    token = get_auth_token(client, "dashtz@example.com", timezone="Asia/Tokyo")
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["user"]["timezone"] == "Asia/Tokyo"


def test_13_archived_habits_excluded(client):
    token = get_auth_token(client, "dasharch@example.com")
    h = client.post(
        "/api/v1/habits",
        json={"title": "Archived Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    client.patch(
        f"/api/v1/habits/{h}/archive?is_archived=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    habits = res.json()["today"]["habits"]
    assert len(habits) == 0


def test_14_deleted_habits_excluded(client):
    token = get_auth_token(client, "dashdel@example.com")
    h = client.post(
        "/api/v1/habits",
        json={"title": "Deleted Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    client.delete(f"/api/v1/habits/{h}", headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    habits = res.json()["today"]["habits"]
    assert len(habits) == 0


def test_mixed_habit_schedule_dashboard(client):
    token = get_auth_token(client, "mixed@example.com")

    # Create 3 habits
    h1 = client.post(
        "/api/v1/habits",
        json={"title": "Daily Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    h2 = client.post(
        "/api/v1/habits",
        json={"title": "Weekly Habit", "category": "productivity", "frequency_type": "weekly"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete h1 today
    client.post(
        f"/api/v1/habits/{h1}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    today_data = res.json()["today"]
    assert today_data["total_expected_habits"] >= 2
    assert today_data["completed_habits"] == 1
