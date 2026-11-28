from uuid import uuid4


prefix = "/auth/register"

# TEST REGISTER
async def test_register_success(client):

    unique_id = uuid4().hex[:10]


    user_data = {

        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@gmail.com",
        "password": "123456",
        "full_name": "Test User",
        "phone": "0901234567"

    }

    response = await client.post(prefix, json=user_data)

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["phone"] == user_data["phone"]
    assert data["is_active"] is True
    assert data["is_verified"] is False

    assert "password" not in data
    assert "password_hash" not in data


# TEST REGISTER WITH EMAIL ALREADY EXIST
async def test_register_duplicate_email(client):

    unique_id = uuid4().hex[:10]

    user_data = {
        "username" : f"testuser_{unique_id}",
        "email": f"existing_{unique_id}@gmail.com",
        "password": "123456",
        "full_name": "Test User",
        "phone": "0901234567"

    }

    # Register first
    first_response = await client.post(prefix, json=user_data)

    assert first_response.status_code == 201

    # Register second
    user_data["username"] = f"another_{unique_id}"

    second_response = await client.post(prefix, json=user_data)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


# TEST REGISTER WITH USERNAME ALREADY EXIST
async def test_register_duplicate_username(client):

    unique_id = uuid4().hex[:10]

    user_data = {

        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@gmail.com",
        "password": "123456",
        "full_name": "Test User",
        "phone": "0901234567"

    }

    first_response = await client.post(prefix, json=user_data)

    assert first_response.status_code == 201

    user_data["email"] = f"another_{unique_id}@gmail.com"

    second_response = await client.post(prefix, json=user_data)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Username already taken"


# TEST REGISTER WITH INVALID USERNAME
async def test_register_invalid_username(client):

    user_data = {

        "username": "ab",
        "email": f"test_{uuid4().hex[:10]}@gmail.com",
        "password": "123456",
        "full_name": "Test User",
        "phone": "0901234567"

    }

    response = await client.post(prefix, json=user_data)

    assert response.status_code == 422


# TEST REGISTER WITH INVALID EMAIL
async def test_register_invalid_email(client):

    user_data = {
        "username": f"testuser_{uuid4().hex[:10]}",
        "email": "invalid-email",
        "password": "123456",
        "full_name": "Test User",
        "phone": "0901234567"
    }

    response = await client.post(prefix, json=user_data)

    assert response.status_code == 422


# TEST REGISTER WITH INVALID PASSWORD
async def test_register_invalid_password(client):

    user_data = {
        "username": f"testuser_{uuid4().hex[:10]}",
        "email": f"test_{uuid4().hex[:10]}@gmail.com",
        "password": "1234",
        "full_name": "Test User",
        "phone": "0901234567"
    }

    response = await client.post(prefix, json=user_data)

    assert response.status_code == 422