import pytest
import uuid
from datetime import date, timedelta


def get_auth_token(client, email="user@example.com"):
    payload = {"email": email, "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


# ── HABIT CRUD TESTS (1-6) ───────────────────────────────────────────────────

def test_1_create_habit(client):
    token = get_auth_token(client, "crud1@example.com")
    payload = {
        "title": "Daily Reading",
        "description": "Read 10 pages of a book",
        "category": "reading",
        "frequency_type": "daily",
        "target_value": 10,
        "target_unit": "pages",
    }
    res = client.post("/api/v1/habits", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Daily Reading"
    assert data["category"] == "reading"
    assert data["current_streak"] == 0
    assert data["is_active"] is True


def test_2_get_habits_list(client):
    token = get_auth_token(client, "crud2@example.com")
    client.post(
        "/api/v1/habits",
        json={"title": "Habit 1", "category": "fitness"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/habits",
        json={"title": "Habit 2", "category": "study"},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/api/v1/habits", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


def test_3_get_single_habit(client):
    token = get_auth_token(client, "crud3@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Single Habit", "category": "coding"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    res = client.get(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["title"] == "Single Habit"


def test_4_update_habit(client):
    token = get_auth_token(client, "crud4@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "Original Title", "category": "coding"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    update_res = client.patch(
        f"/api/v1/habits/{habit_id}",
        json={"title": "Updated Title", "target_value": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"
    assert update_res.json()["target_value"] == 5


def test_5_delete_habit(client):
    token = get_auth_token(client, "crud5@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "ToDelete Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 404


def test_6_archive_habit(client):
    token = get_auth_token(client, "crud6@example.com")
    create_res = client.post(
        "/api/v1/habits",
        json={"title": "ToArchive Habit", "category": "other"},
        headers={"Authorization": f"Bearer {token}"},
    )
    habit_id = create_res.json()["id"]

    archive_res = client.patch(
        f"/api/v1/habits/{habit_id}/archive?is_archived=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert archive_res.status_code == 200
    assert archive_res.json()["is_archived"] is True


# ── AUTHORIZATION TESTS (7-10) ───────────────────────────────────────────────

def test_7_unauthenticated_user_cannot_access_habits(client):
    res = client.get("/api/v1/habits")
    assert res.status_code in (401, 403)


def test_8_user_cannot_access_another_users_habit(client):
    token_a = get_auth_token(client, "userA_h@example.com")
    token_b = get_auth_token(client, "userB_h@example.com")

    create_res = client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    habit_id = create_res.json()["id"]

    res = client.get(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


def test_9_user_cannot_modify_another_users_habit(client):
    token_a = get_auth_token(client, "userA_m@example.com")
    token_b = get_auth_token(client, "userB_m@example.com")

    create_res = client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    habit_id = create_res.json()["id"]

    res = client.patch(
        f"/api/v1/habits/{habit_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res.status_code == 403


def test_10_user_cannot_delete_another_users_habit(client):
    token_a = get_auth_token(client, "userA_d@example.com")
    token_b = get_auth_token(client, "userB_d@example.com")

    create_res = client.post(
        "/api/v1/habits",
        json={"title": "User A Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    habit_id = create_res.json()["id"]

    res = client.delete(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


# ── FREE PLAN LIMIT TESTS (23-26) ───────────────────────────────────────────

def test_23_24_free_plan_five_habit_limit(client):
    token = get_auth_token(client, "freeplan@example.com")

    # Create 5 active habits (should succeed)
    for i in range(1, 6):
        res = client.post(
            "/api/v1/habits",
            json={"title": f"Free Habit {i}", "category": "fitness"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201

    # Attempt 6th active habit (should be rejected with 403)
    res_6 = client.post(
        "/api/v1/habits",
        json={"title": "Free Habit 6", "category": "fitness"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_6.status_code == 403
    assert "Free plan allows a maximum of 5 active habits" in res_6.json()["detail"]


def test_25_archived_habit_frees_active_slot(client):
    token = get_auth_token(client, "freeslot@example.com")

    habit_ids = []
    for i in range(1, 6):
        res = client.post(
            "/api/v1/habits",
            json={"title": f"Habit {i}", "category": "study"},
            headers={"Authorization": f"Bearer {token}"},
        )
        habit_ids.append(res.json()["id"])

    # Archive habit 1
    archive_res = client.patch(
        f"/api/v1/habits/{habit_ids[0]}/archive?is_archived=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert archive_res.status_code == 200

    # Now creating a new active habit succeeds
    res_new = client.post(
        "/api/v1/habits",
        json={"title": "Habit New", "category": "study"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_new.status_code == 201


def test_26_pro_user_is_not_limited_to_five(client, db_session):
    from app.repositories.user_repository import UserRepository

    token = get_auth_token(client, "prouser@example.com")

    # Upgrade user to pro directly in database
    user = UserRepository.get_by_email(db_session, "prouser@example.com")
    user.subscription_tier = "pro"
    db_session.commit()

    # Create 6 habits
    for i in range(1, 7):
        res = client.post(
            "/api/v1/habits",
            json={"title": f"Pro Habit {i}", "category": "productivity"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201
