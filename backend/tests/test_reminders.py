import pytest
from datetime import datetime, time, date, timezone as dt_timezone, timedelta
from app.utils.datetime_utils import get_user_today
from app.services.reminder_service import ReminderService


def get_auth_token(client, email="rem_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


def test_1_unauthenticated_reminders_rejected(client):
    res = client.get("/api/v1/reminders")
    assert res.status_code in (401, 403)

    res_post = client.post(
        "/api/v1/reminders",
        json={"habit_id": "00000000-0000-0000-0000-000000000000", "reminder_time": "08:00"},
    )
    assert res_post.status_code in (401, 403)


def test_2_create_and_get_reminder(client):
    token = get_auth_token(client, "rem2@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Morning Meditation", "category": "sleep", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    res = client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "07:30:00", "days_of_week": [0, 1, 2, 3, 4]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["habit_id"] == h_id
    assert data["habit_title"] == "Morning Meditation"
    assert data["reminder_time"] == "07:30:00"
    assert data["days_of_week"] == [0, 1, 2, 3, 4]
    assert data["is_active"] is True

    # Get by ID
    r_id = data["id"]
    res_get = client.get(f"/api/v1/reminders/{r_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_get.status_code == 200
    assert res_get.json()["id"] == r_id


def test_3_list_and_filter_reminders(client):
    token = get_auth_token(client, "rem3@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Workout Habit", "category": "fitness", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Create active reminder
    client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "06:00:00", "is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Create inactive reminder
    client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "18:00:00", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    res_all = client.get("/api/v1/reminders", headers={"Authorization": f"Bearer {token}"})
    assert len(res_all.json()) == 2

    res_active = client.get("/api/v1/reminders?is_active=true", headers={"Authorization": f"Bearer {token}"})
    assert len(res_active.json()) == 1
    assert res_active.json()[0]["is_active"] is True


def test_4_update_and_delete_reminder(client):
    token = get_auth_token(client, "rem4@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Reading Habit", "category": "reading", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    r_id = client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "21:00:00"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Update time and disable
    res_patch = client.patch(
        f"/api/v1/reminders/{r_id}",
        json={"reminder_time": "22:00:00", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["reminder_time"] == "22:00:00"
    assert res_patch.json()["is_active"] is False

    # Delete
    res_del = client.delete(f"/api/v1/reminders/{r_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_del.status_code == 204

    # Verify 404 after deletion
    res_check = client.get(f"/api/v1/reminders/{r_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_check.status_code == 404


def test_5_6_user_isolation_and_habit_ownership(client):
    token_a = get_auth_token(client, "remA@example.com")
    token_b = get_auth_token(client, "remB@example.com")
    today = get_user_today("UTC")

    # User A creates habit and reminder
    h_a = client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "coding", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]

    r_a = client.post(
        "/api/v1/reminders",
        json={"habit_id": h_a, "reminder_time": "09:00:00"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]

    # User B cannot view User A's reminder
    res_b_get = client.get(f"/api/v1/reminders/{r_a}", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_get.status_code in (403, 404)

    # User B cannot link a reminder to User A's habit
    res_b_create = client.post(
        "/api/v1/reminders",
        json={"habit_id": h_a, "reminder_time": "10:00:00"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_b_create.status_code == 403


def test_7_cannot_create_reminder_for_archived_habit(client):
    token = get_auth_token(client, "rem_arch@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Archived Habit", "category": "study", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Archive the habit
    client.patch(f"/api/v1/habits/{h_id}/archive?is_archived=true", headers={"Authorization": f"Bearer {token}"})

    res = client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "14:00:00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


def test_8_9_10_due_reminders_evaluation_and_completion_prevention(client, db_session):
    # Tokyo user (UTC+9)
    token = get_auth_token(client, "rem_tokyo@example.com", timezone="Asia/Tokyo")
    today_tokyo = get_user_today("Asia/Tokyo")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Tokyo Daily Habit", "category": "fitness", "start_date": today_tokyo.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Reminder set for 08:30 Tokyo time (23:30 UTC previous day)
    client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "08:30:00"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Simulate UTC evaluation where local Tokyo time is today_tokyo at 08:30
    tokyo_dt = datetime(today_tokyo.year, today_tokyo.month, today_tokyo.day, 8, 30)
    eval_utc = (tokyo_dt - timedelta(hours=9)).replace(tzinfo=dt_timezone.utc)
    due_items = ReminderService.get_due_reminders(db_session, eval_utc)
    tokyo_items = [item for item in due_items if item.habit_title == "Tokyo Daily Habit"]
    assert len(tokyo_items) == 1
    assert tokyo_items[0].local_time == "08:30"
    assert tokyo_items[0].local_date == today_tokyo

    # Now complete the habit for today_tokyo
    res_comp = client.post(
        f"/api/v1/habits/{h_id}/complete",
        json={"completed_date": today_tokyo.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_comp.status_code == 200

    db_session.expire_all()
    # Re-evaluate due reminders for the same moment -> must NOT fire since already completed!
    due_items_after = ReminderService.get_due_reminders(db_session, eval_utc)
    tokyo_items_after = [item for item in due_items_after if item.habit_title == "Tokyo Daily Habit"]
    assert len(tokyo_items_after) == 0


def test_11_next_reminder_endpoint(client):
    token = get_auth_token(client, "rem_next@example.com")
    today = get_user_today("UTC")

    h_id = client.post(
        "/api/v1/habits",
        json={"title": "Upcoming Habit", "category": "coding", "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    client.post(
        "/api/v1/reminders",
        json={"habit_id": h_id, "reminder_time": "23:59:00"},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/api/v1/reminders/next", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data is not None
    assert data["habit_title"] == "Upcoming Habit"
    assert "23:59" in data["next_occurrence"]
