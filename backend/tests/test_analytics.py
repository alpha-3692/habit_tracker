import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="an_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


def test_1_unauthenticated_trends_rejected(client):
    res = client.get("/api/v1/analytics/trends")
    assert res.status_code in (401, 403)


def test_2_authenticated_trends_succeeds(client):
    token = get_auth_token(client, "an2@example.com")
    res = client.get("/api/v1/analytics/trends", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "overall_consistency" in data
    assert "momentum_score" in data
    assert "weekly_trends" in data
    assert "day_of_week" in data
    assert "category_breakdown" in data
    assert "insights" in data


def test_3_user_isolation(client):
    token_a = get_auth_token(client, "anA@example.com")
    token_b = get_auth_token(client, "anB@example.com")
    today = get_user_today("UTC")

    # User A creates and completes habit
    h_a = client.post(
        "/api/v1/habits",
        json={"title": "Habit A", "category": "coding", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]
    client.post(f"/api/v1/habits/{h_a}/complete", headers={"Authorization": f"Bearer {token_a}"})

    # User B trends should have 0 completions and 0 habits
    res_b = client.get("/api/v1/analytics/trends", headers={"Authorization": f"Bearer {token_b}"})
    data_b = res_b.json()
    assert data_b["total_habits_tracked"] == 0
    assert data_b["total_completions"] == 0


def test_4_empty_user_trends(client):
    token = get_auth_token(client, "an_empty@example.com")
    res = client.get("/api/v1/analytics/trends", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["overall_consistency"] == 0.0
    assert data["momentum_score"] == 0
    assert len(data["day_of_week"]) == 7


def test_5_6_day_of_week_and_category_breakdown(client):
    token = get_auth_token(client, "an_cat@example.com")
    today = get_user_today("UTC")

    # Coding Habit
    h1 = client.post(
        "/api/v1/habits",
        json={"title": "DSA Code", "category": "coding", "start_date": (today - timedelta(days=10)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Fitness Habit
    h2 = client.post(
        "/api/v1/habits",
        json={"title": "Gym Workout", "category": "fitness", "start_date": (today - timedelta(days=10)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete h1 today
    client.post(f"/api/v1/habits/{h1}/complete", headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/analytics/trends?days=14", headers={"Authorization": f"Bearer {token}"})
    data = res.json()

    assert data["total_habits_tracked"] == 2
    assert len(data["category_breakdown"]) == 2

    cat_map = {c["category"]: c for c in data["category_breakdown"]}
    assert "coding" in cat_map
    assert "fitness" in cat_map
    assert cat_map["coding"]["completed"] >= 1


def test_7_momentum_score_calculation(client):
    token = get_auth_token(client, "an_mom@example.com")
    today = get_user_today("UTC")

    # Create daily habit
    h = client.post(
        "/api/v1/habits",
        json={"title": "Momentum Habit", "category": "productivity", "start_date": (today - timedelta(days=6)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete all past 7 days
    for i in range(7):
        past_d = today - timedelta(days=i)
        client.post(f"/api/v1/habits/{h}/complete", json={"completed_date": past_d.isoformat()}, headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/analytics/trends?days=30", headers={"Authorization": f"Bearer {token}"})
    data = res.json()
    assert data["momentum_score"] >= 70


def test_8_invalid_days_param(client):
    token = get_auth_token(client, "an_inv@example.com")

    # Too small (< 7)
    res_small = client.get("/api/v1/analytics/trends?days=3", headers={"Authorization": f"Bearer {token}"})
    assert res_small.status_code == 400

    # Too large (> 365)
    res_large = client.get("/api/v1/analytics/trends?days=400", headers={"Authorization": f"Bearer {token}"})
    assert res_large.status_code == 400
