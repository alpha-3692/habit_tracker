import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="streak@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


# ── COMPLETION TESTS (11-14) ──────────────────────────────────────────────────

def test_11_complete_habit(client):
    token = get_auth_token(client, "comp11@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Workout", "category": "fitness", "frequency_type": "daily"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    comp_res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"value": 1, "notes": "Completed session"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert comp_res.status_code == 200
    data = comp_res.json()
    assert data["streak"]["current_streak"] == 1
    assert data["streak"]["total_completions"] == 1


def test_12_duplicate_completion_prevented(client):
    token = get_auth_token(client, "comp12@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Meditate", "category": "personal_growth"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    res1 = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200

    res2 = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 409
    assert "already completed" in res2.json()["detail"]


def test_13_archived_habit_cannot_be_completed(client):
    token = get_auth_token(client, "comp13@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Archived Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    client.patch(
        f"/api/v1/habits/{habit_id}/archive?is_archived=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "inactive or archived" in res.json()["detail"]


def test_14_future_completion_handled_correctly(client):
    token = get_auth_token(client, "comp14@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Future Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    today = get_user_today("UTC")
    future_date = (today + timedelta(days=2)).isoformat()

    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": future_date},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "future date" in res.json()["detail"]


# ── STREAK ENGINE & FREQUENCY TESTS (15-22) ─────────────────────────────────

def test_15_16_first_and_consecutive_completions(client):
    token = get_auth_token(client, "streak15@example.com")
    today = get_user_today("UTC")
    start = today - timedelta(days=3)

    create_res = client.post(
        "/api/v1/habits",
        json={
            "title": "Study DSA",
            "category": "coding",
            "frequency_type": "daily",
            "start_date": start.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    # Complete 3 consecutive past days
    for i in range(3, 0, -1):
        d = (today - timedelta(days=i)).isoformat()
        res = client.post(
            f"/api/v1/habits/{habit_id}/complete",
            json={"completed_date": d},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

    # Today's completion
    res_today = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_today.status_code == 200
    assert res_today.json()["streak"]["current_streak"] == 4
    assert res_today.json()["streak"]["best_streak"] == 4


def test_17_18_19_missed_day_breaks_streak_and_preserves_best_streak(client):
    token = get_auth_token(client, "streak17@example.com")
    today = get_user_today("UTC")
    start = today - timedelta(days=10)

    create_res = client.post(
        "/api/v1/habits",
        json={
            "title": "Running",
            "category": "fitness",
            "frequency_type": "daily",
            "start_date": start.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    # Days -10 to -6 (5-day streak)
    for i in range(10, 5, -1):
        client.post(
            f"/api/v1/habits/{habit_id}/complete",
            json={"completed_date": (today - timedelta(days=i)).isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Day -5 MISSED

    # Days -4 to -1 (4-day streak)
    for i in range(4, 0, -1):
        client.post(
            f"/api/v1/habits/{habit_id}/complete",
            json={"completed_date": (today - timedelta(days=i)).isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Today
    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    streak_data = res.json()["streak"]
    # Current streak after missed day is 5 (days -4, -3, -2, -1, 0)
    assert streak_data["current_streak"] == 5
    # Best streak is preserved as 5
    assert streak_data["best_streak"] == 5


def test_20_weekly_frequency(client):
    token = get_auth_token(client, "weekly@example.com")
    today = get_user_today("UTC")
    start = today - timedelta(days=14)

    create_res = client.post(
        "/api/v1/habits",
        json={
            "title": "Weekly Review",
            "category": "productivity",
            "frequency_type": "weekly",
            "start_date": start.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    habit_id = create_res.json()["id"]

    # Complete 2 weeks ago and 1 week ago
    two_wks_ago = (today - timedelta(days=14)).isoformat()
    one_wk_ago = (today - timedelta(days=7)).isoformat()

    client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": two_wks_ago},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": one_wk_ago},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["streak"]["current_streak"] >= 2


def test_21_irregular_frequency_weekdays(client):
    token = get_auth_token(client, "weekdays@example.com")
    today = get_user_today("UTC")

    create_res = client.post(
        "/api/v1/habits",
        json={
            "title": "Coding Practice",
            "category": "coding",
            "frequency_type": "weekdays",
            "start_date": (today - timedelta(days=14)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    # Complete today
    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        json={"completed_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["streak"]["current_streak"] >= 1


def test_22_timezone_boundary(client):
    # Register user with specific timezone
    token = get_auth_token(client, "tzuser@example.com", timezone="Asia/Tokyo")

    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Tokyo Habit", "category": "reading"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    res = client.post(
        f"/api/v1/habits/{habit_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["streak"]["current_streak"] == 1
