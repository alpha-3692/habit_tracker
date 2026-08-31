import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today
from app.services.achievement_service import AchievementService


def get_auth_token(client, email="ach_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


def test_1_unauthenticated_requests_rejected(client):
    res = client.get("/api/v1/achievements")
    assert res.status_code in (401, 403)

    res_me = client.get("/api/v1/achievements/me")
    assert res_me.status_code in (401, 403)


def test_2_achievement_catalog(client):
    token = get_auth_token(client, "ach_cat@example.com")
    res = client.get("/api/v1/achievements", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    catalog = res.json()
    assert len(catalog) >= 18
    codes = {a["code"] for a in catalog}
    assert "streak_7" in codes
    assert "streak_30" in codes
    assert "first_completion" in codes
    assert "completions_100" in codes
    assert "first_habit" in codes
    assert "first_goal" in codes


def test_3_first_completion_achievement(client):
    token = get_auth_token(client, "ach_first@example.com")
    today = get_user_today("UTC")

    # Create habit
    h_id = client.post(
        "/api/v1/habits",
        json={"title": "First Habit", "category": "coding", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete habit
    res = client.post(f"/api/v1/habits/{h_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "first_completion" in data["achievements_unlocked"]

    # Check /achievements/me
    res_me = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked_codes = {a["code"] for a in res_me.json() if a["is_unlocked"]}
    assert "first_completion" in unlocked_codes


def test_4_streak_boundary_6_vs_7_days(client):
    token = get_auth_token(client, "ach_strk7@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Streak Habit", "category": "fitness", "start_date": (today - timedelta(days=7)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete for 6 consecutive days (today - 6 to today - 1)
    for i in range(6, 0, -1):
        d = today - timedelta(days=i)
        client.post(
            f"/api/v1/habits/{h_id}/complete",
            json={"completed_date": d.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Verify streak_7 NOT unlocked at 6 days
    res_me = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked = {a["code"]: a for a in res_me.json()}
    assert unlocked["streak_7"]["is_unlocked"] is False
    assert unlocked["streak_7"]["progress"] == 6

    # Complete 7th day (today)
    res_7 = client.post(f"/api/v1/habits/{h_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert "streak_7" in res_7.json()["achievements_unlocked"]

    # Verify streak_7 IS unlocked at 7 days
    res_me_7 = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked_7 = {a["code"]: a for a in res_me_7.json()}
    assert unlocked_7["streak_7"]["is_unlocked"] is True
    assert unlocked_7["streak_7"]["progress_percentage"] == 100.0


def test_5_streak_boundary_29_vs_30_days(client):
    token = get_auth_token(client, "ach_strk30@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "30 Day Habit", "category": "fitness", "start_date": (today - timedelta(days=30)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Complete 29 days
    for i in range(29, 0, -1):
        d = today - timedelta(days=i)
        client.post(
            f"/api/v1/habits/{h_id}/complete",
            json={"completed_date": d.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

    res_me_29 = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked_29 = {a["code"]: a for a in res_me_29.json()}
    assert unlocked_29["streak_30"]["is_unlocked"] is False
    assert unlocked_29["streak_30"]["progress"] == 29

    # Complete 30th day
    res_30 = client.post(f"/api/v1/habits/{h_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert "streak_30" in res_30.json()["achievements_unlocked"]

    res_me_30 = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked_30 = {a["code"]: a for a in res_me_30.json()}
    assert unlocked_30["streak_30"]["is_unlocked"] is True


def test_6_active_habit_achievements(client):
    token = get_auth_token(client, "ach_habs@example.com")
    today = get_user_today("UTC")

    # Create 3 habits
    for i in range(3):
        client.post(
            "/api/v1/habits",
            json={"title": f"Habit {i+1}", "category": "study", "start_date": today.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Complete one habit to trigger evaluation
    habits = client.get("/api/v1/habits", headers={"Authorization": f"Bearer {token}"}).json()
    client.post(f"/api/v1/habits/{habits[0]['id']}/complete", headers={"Authorization": f"Bearer {token}"})

    res_me = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token}"})
    unlocked = {a["code"]: a for a in res_me.json()}
    assert unlocked["first_habit"]["is_unlocked"] is True
    assert unlocked["active_habits_3"]["is_unlocked"] is True
    assert unlocked["active_habits_5"]["is_unlocked"] is False


def test_7_user_isolation(client):
    token_a = get_auth_token(client, "ach_userA@example.com")
    token_b = get_auth_token(client, "ach_userB@example.com")
    today = get_user_today("UTC")

    # User A unlocks first_completion
    h_a = client.post(
        "/api/v1/habits",
        json={"title": "A Habit", "category": "coding", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]
    client.post(f"/api/v1/habits/{h_a}/complete", headers={"Authorization": f"Bearer {token_a}"})

    # User B should have 0 unlocked achievements
    res_b = client.get("/api/v1/achievements/me", headers={"Authorization": f"Bearer {token_b}"})
    unlocked_b = [a for a in res_b.json() if a["is_unlocked"]]
    assert len(unlocked_b) == 0


def test_8_duplicate_unlock_prevention_and_idempotency(client, db_session):
    token = get_auth_token(client, "ach_idem@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Idem Habit", "category": "sleep", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # First completion unlocks first_completion
    res1 = client.post(f"/api/v1/habits/{h_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert "first_completion" in res1.json()["achievements_unlocked"]

    # Re-completing for yesterday should NOT re-report first_completion
    yesterday = today - timedelta(days=1)
    res2 = client.post(
        f"/api/v1/habits/{h_id}/complete",
        json={"completed_date": yesterday.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert "first_completion" not in res2.json()["achievements_unlocked"]

    # Total UserAchievements for user must remain 1 for first_completion
    from app.models.user import User
    from app.models.achievement import UserAchievement, Achievement
    user = db_session.query(User).filter(User.email == "ach_idem@example.com").first()
    ach = db_session.query(Achievement).filter(Achievement.code == "first_completion").first()
    count = db_session.query(UserAchievement).filter(
        UserAchievement.user_id == user.id,
        UserAchievement.achievement_id == ach.id
    ).count()
    assert count == 1
