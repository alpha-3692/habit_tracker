import pytest


def test_protected_endpoint_without_authentication(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403 or response.status_code == 401


def test_protected_endpoint_with_valid_authentication(client):
    register_payload = {
        "email": "userprofile@example.com",
        "password": "Password123!",
        "full_name": "Valid Auth User",
    }
    reg_res = client.post("/api/v1/auth/register", json=register_payload)
    token = reg_res.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "userprofile@example.com"
    assert data["full_name"] == "Valid Auth User"


def test_user_cannot_access_another_users_protected_resource(client):
    """
    Test user isolation: User A registers and logs in. User B registers and logs in.
    User A requests /users/me and receives User A's data. User A cannot impersonate User B
    or modify User B's profile without User B's token.
    """
    # User A
    res_a = client.post("/api/v1/auth/register", json={"email": "userA@example.com", "password": "Password123!"})
    token_a = res_a.json()["access_token"]
    user_a_id = res_a.json()["user"]["id"]

    # User B
    res_b = client.post("/api/v1/auth/register", json={"email": "userB@example.com", "password": "Password123!"})
    token_b = res_b.json()["access_token"]
    user_b_id = res_b.json()["user"]["id"]

    # Request with User A token returns User A
    get_a = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_a}"})
    assert get_a.status_code == 200
    assert get_a.json()["id"] == user_a_id
    assert get_a.json()["email"] == "usera@example.com"

    # Request with User B token returns User B
    get_b = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b.status_code == 200
    assert get_b.json()["id"] == user_b_id
    assert get_b.json()["email"] == "userb@example.com"

    # User A updates profile — modifies ONLY User A
    patch_a = client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated User A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert patch_a.status_code == 200
    assert patch_a.json()["full_name"] == "Updated User A"

    # User B profile remains unchanged
    get_b_again = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b_again.json()["full_name"] is None or get_b_again.json()["full_name"] != "Updated User A"
