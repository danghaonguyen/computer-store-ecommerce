from uuid import uuid4

prefix_register = "/auth/register"
prefix_login = "/auth/login"


# TEST LOGIN SUCCESS
async def test_login_success(client):

    unique_id = uuid4().hex[:10]

    user_data = {
        "username": f"test_{unique_id}",
        "email": f"login_{unique_id}@gmail.com",
        "password": "123456",
        "full_name": "Login Test",
        "phone": "0901234567"
    }

    # Register account
    register_response = await client.post(prefix_register, json=user_data)

    assert register_response.status_code == 201

    # Login
    login_response = await client.post(
        prefix_login,
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "CUSTOMER" in data["roles"]


# TEST LOGIN WITH WRONG PASSWORD
async def test_login_wrong_password(client):

    user_data = {
        "username": "testuser_05e08239eb",
        "email": f"test_05e08239eb@gmail.com",
        "password": "123456",
        "full_name": "Login Test",
        "phone": "0901234567"
    }

    # Login
    login_response = await client.post(
        prefix_login, json={"email": user_data["email"], "password": "wrong password"}
    )

    assert login_response.status_code == 401

    assert login_response.json()["detail"] == "Invalid email or password"


# TEST LOGIN WITH NON-EXISTENT EMAIL
async def test_login_email_not_found(client):

    login_response = await client.post(
        prefix_login, json={"email": f"notfound_{uuid4().hex[:10]}@gmail.com", 
                            "password": "123456"}
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"



# TEST LOGIN WITH DISABLED ACCOUNT
async def test_login_disabled_account(client):

    user_data = {
        "username": "disabled_c3454a577a",
        "email": f"disabled_c3454a577a@gmail.com",
        "password": "123456",
        "full_name": "Disabled User",
        "phone": "0901234567"
    }

    # Login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 403
    assert login_response.json()["detail"] == "Account is disabled"


# TEST GET CURRENT USER
async def test_get_current_user(client):

    user_data = {
        "username": "me_67d9b98f4a",
        "email": "me_67d9b98f4a@gmail.com",
        "password": "123456",
        "full_name": "Current User",
        "phone": "0901234567"
    }

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] is True


# TEST GET CURRENT USER WITHOUT TOKEN
async def test_get_current_user_without_token(client):

    response = await client.get("/auth/me")

    assert response.status_code == 401


# TEST GET CURRENT USER WITH INVALID TOKEN
async def test_get_current_user_invalid_token(client):

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401


# TEST CUSTOMER ACCESS ADMIN API
async def test_customer_access_admin_api(client):

    user_data = {
        "username": "customer_053eaa59da",
        "email": "customer_053eaa59da@gmail.com",
        "password": "123456",
        "full_name": "Customer Test",
        "phone": "0901234567"
    }

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/admin/test",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 403



# TEST ADMIN ACCESS ADMIN API
async def test_admin_access_admin_api(client):

    # Login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "admin_e39d308328@gmail.com",
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "ADMIN" in data["roles"]

    # Access ADMIN API
    response = await client.get(
        "/auth/admin/test",
        headers={
            "Authorization": f"Bearer {data['access_token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome Admin"