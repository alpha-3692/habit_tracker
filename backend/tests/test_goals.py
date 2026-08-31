import pytest
from datetime import date, timedelta
from app.utils.datetime_utils import get_user_today


def get_auth_token(client, email="goal_user@example.com", timezone="UTC"):
    payload = {"email": email, "password": "Password123!", "timezone": timezone}
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/v1/auth/login", json=payload)
    return res.json()["access_token"]


# ── GOAL CRUD (1-5) ──────────────────────────────────────────────────────────

def test_1_create_goal(client):
    token = get_auth_token(client, "goal1@example.com")
    payload = {
        "title": "Master Full-Stack Engineering",
        "description": "Learn FastAPI and Next.js deeply",
        "category": "coding",
        "target_date": (date.today() + timedelta(days=90)).isoformat(),
    }
    res = client.post("/api/v1/goals", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Master Full-Stack Engineering"
    assert data["status"] == "active"
    assert data["habit_count"] == 0
    assert data["progress_percentage"] == 0.0


def test_2_list_goals(client):
    token = get_auth_token(client, "goal2@example.com")
    client.post("/api/v1/goals", json={"title": "Goal 1", "category": "fitness"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/api/v1/goals", json={"title": "Goal 2", "category": "study"}, headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/goals", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_3_get_single_goal(client):
    token = get_auth_token(client, "goal3@example.com")
    create_res = client.post("/api/v1/goals", json={"title": "Single Goal", "category": "productivity"}, headers={"Authorization": f"Bearer {token}"})
    goal_id = create_res.json()["id"]

    res = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["title"] == "Single Goal"


def test_4_update_goal(client):
    token = get_auth_token(client, "goal4@example.com")
    create_res = client.post("/api/v1/goals", json={"title": "Old Goal Title", "category": "career"}, headers={"Authorization": f"Bearer {token}"})
    goal_id = create_res.json()["id"]

    res = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"title": "New Goal Title", "status": "completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["title"] == "New Goal Title"
    assert res.json()["status"] == "completed"
    assert res.json()["progress_percentage"] == 100.0


def test_5_delete_goal(client):
    token = get_auth_token(client, "goal5@example.com")
    create_res = client.post("/api/v1/goals", json={"title": "To Delete Goal", "category": "other"}, headers={"Authorization": f"Bearer {token}"})
    goal_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 404


# ── AUTHORIZATION (6-9) ──────────────────────────────────────────────────────

def test_6_unauthenticated_goal_rejected(client):
    res = client.get("/api/v1/goals")
    assert res.status_code in (401, 403)


def test_7_user_cannot_read_another_users_goal(client):
    token_a = get_auth_token(client, "g_userA@example.com")
    token_b = get_auth_token(client, "g_userB@example.com")

    create_res = client.post("/api/v1/goals", json={"title": "User A Goal", "category": "fitness"}, headers={"Authorization": f"Bearer {token_a}"})
    goal_id = create_res.json()["id"]

    res = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


def test_8_user_cannot_modify_another_users_goal(client):
    token_a = get_auth_token(client, "g_userA_m@example.com")
    token_b = get_auth_token(client, "g_userB_m@example.com")

    create_res = client.post("/api/v1/goals", json={"title": "User A Goal", "category": "fitness"}, headers={"Authorization": f"Bearer {token_a}"})
    goal_id = create_res.json()["id"]

    res = client.patch(f"/api/v1/goals/{goal_id}", json={"title": "Hacked Goal"}, headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


def test_9_user_cannot_delete_another_users_goal(client):
    token_a = get_auth_token(client, "g_userA_d@example.com")
    token_b = get_auth_token(client, "g_userB_d@example.com")

    create_res = client.post("/api/v1/goals", json={"title": "User A Goal", "category": "fitness"}, headers={"Authorization": f"Bearer {token_a}"})
    goal_id = create_res.json()["id"]

    res = client.delete(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


# ── RELATIONSHIPS (10-14) ────────────────────────────────────────────────────

def test_10_11_12_assign_remove_habit_goal(client):
    token = get_auth_token(client, "g_rel@example.com")

    # Create Goal
    goal_res = client.post("/api/v1/goals", json={"title": "Fitness Goal", "category": "fitness"}, headers={"Authorization": f"Bearer {token}"})
    goal_id = goal_res.json()["id"]

    # Create Habit without goal
    habit_res = client.post("/api/v1/habits", json={"title": "Morning Run", "category": "fitness"}, headers={"Authorization": f"Bearer {token}"})
    habit_id = habit_res.json()["id"]

    # Assign habit to goal
    update_res = client.patch(f"/api/v1/habits/{habit_id}", json={"goal_id": goal_id}, headers={"Authorization": f"Bearer {token}"})
    assert update_res.status_code == 200
    assert update_res.json()["goal_id"] == goal_id

    # Verify goal habit count is 1
    get_goal = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_goal.json()["habit_count"] == 1

    # Remove habit from goal
    remove_res = client.patch(f"/api/v1/habits/{habit_id}", json={"goal_id": None}, headers={"Authorization": f"Bearer {token}"})
    assert remove_res.status_code == 200
    assert remove_res.json()["goal_id"] is None

    # Habit remains valid
    get_h = client.get(f"/api/v1/habits/{habit_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_h.status_code == 200


def test_13_14_cannot_link_to_another_users_goal(client):
    token_a = get_auth_token(client, "crossA@example.com")
    token_b = get_auth_token(client, "crossB@example.com")

    # User A creates Goal
    goal_a = client.post("/api/v1/goals", json={"title": "User A Goal", "category": "fitness"}, headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

    # User B tries to create habit linked to User A's goal
    res = client.post(
        "/api/v1/habits",
        json={"title": "User B Habit", "category": "fitness", "goal_id": goal_a},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res.status_code == 403

    # User B tries to update existing habit with User A's goal_id
    habit_b = client.post(
        "/api/v1/habits",
        json={"title": "User B Standalone Habit", "category": "fitness"},
        headers={"Authorization": f"Bearer {token_b}"},
    ).json()["id"]

    res_patch = client.patch(
        f"/api/v1/habits/{habit_b}",
        json={"goal_id": goal_a},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_patch.status_code == 403


# ── PROGRESS (15-20) ─────────────────────────────────────────────────────────

def test_15_goal_with_no_habits(client):
    token = get_auth_token(client, "prog15@example.com")
    res = client.post("/api/v1/goals", json={"title": "Empty Goal", "category": "study"}, headers={"Authorization": f"Bearer {token}"})
    assert res.json()["progress_percentage"] == 0.0


def test_16_17_18_19_20_progress_calculation(client):
    token = get_auth_token(client, "prog16@example.com")
    today = get_user_today("UTC")

    # Create Goal
    goal_id = client.post("/api/v1/goals", json={"title": "Learn AI", "category": "coding"}, headers={"Authorization": f"Bearer {token}"}).json()["id"]

    # Create 2 habits linked to goal
    h1 = client.post(
        "/api/v1/habits",
        json={"title": "Read Paper", "category": "coding", "goal_id": goal_id, "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    h2 = client.post(
        "/api/v1/habits",
        json={"title": "Implement Model", "category": "coding", "goal_id": goal_id, "start_date": today.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]

    # Initial progress should be 0.0%
    g1 = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert g1.json()["progress_percentage"] == 0.0
    assert g1.json()["habit_count"] == 2

    # Complete h1 today -> h1 is 100%, h2 is 0% -> goal progress = 50.0%
    client.post(f"/api/v1/habits/{h1}/complete", headers={"Authorization": f"Bearer {token}"})

    g2 = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert g2.json()["progress_percentage"] == 50.0

    # Complete h2 today -> both 100% -> goal progress = 100.0%
    client.post(f"/api/v1/habits/{h2}/complete", headers={"Authorization": f"Bearer {token}"})

    g3 = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert g3.json()["progress_percentage"] == 100.0

    # Archiving h2 excludes it from active goal calculations
    client.patch(f"/api/v1/habits/{h2}/archive?is_archived=true", headers={"Authorization": f"Bearer {token}"})
    g4 = client.get(f"/api/v1/goals/{goal_id}", headers={"Authorization": f"Bearer {token}"})
    assert g4.json()["habit_count"] == 1
    assert g4.json()["progress_percentage"] == 100.0


# ── DATES & ISOLATION (21-25) ────────────────────────────────────────────────

def test_21_22_23_target_date_and_completed_status(client):
    token = get_auth_token(client, "date21@example.com")
    past_date = (date.today() - timedelta(days=10)).isoformat()

    # Expired target date goal creates successfully (remains active unless marked completed)
    res = client.post(
        "/api/v1/goals",
        json={"title": "Past Deadline Goal", "category": "study", "target_date": past_date},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    assert res.json()["status"] == "active"

    # Mark completed
    goal_id = res.json()["id"]
    res_comp = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_comp.json()["status"] == "completed"
    assert res_comp.json()["progress_percentage"] == 100.0


def test_24_25_user_isolation(client):
    token_a = get_auth_token(client, "isoA@example.com")
    token_b = get_auth_token(client, "isoB@example.com")

    # User A creates goal with a habit
    goal_a = client.post("/api/v1/goals", json={"title": "Secret Goal A", "category": "career"}, headers={"Authorization": f"Bearer {token_a}"}).json()["id"]
    client.post("/api/v1/habits", json={"title": "Secret Habit A", "category": "career", "goal_id": goal_a}, headers={"Authorization": f"Bearer {token_a}"})

    # User B lists goals
    res_b = client.get("/api/v1/goals", headers={"Authorization": f"Bearer {token_b}"})
    assert len(res_b.json()) == 0

    # User B tries to fetch User A's goal
    get_res = client.get(f"/api/v1/goals/{goal_a}", headers={"Authorization": f"Bearer {token_b}"})
    assert get_res.status_code == 403
