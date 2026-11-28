

prefix_login = "/auth/login"
prefix_admin = "/admin/users"


# TEST GET USERS
async def test_get_users(client):

    login_response = await client.post(prefix_login, 
                                       json={
                                            "email": "admin_e39d308328@gmail.com", 
                                            "password": "123456"
                                       })

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = await client.get(prefix_admin, 
                                headers={
                                    "Authorization" : f"Bearer {access_token}"
                                })

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0



# TEST GET USER BY ID
async def test_get_user_id(client):

    login_response = await client.post(prefix_login, 
                                       json={ 
                                           "email": "admin_e39d308328@gmail.com", 
                                           "password": "123456"
                                           })
                                        


    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Get user list
    users_response = await client.get(prefix_admin, 
                                      headers={
                                          "Authorization" : f"Bearer {access_token}"
                                      })

    assert users_response.status_code == 200

    users = users_response.json()
    user_id = users[0]["id"]

    # Get user id
    response = await client.get(f"{prefix_admin}/{user_id}", 
                                headers={
                                    "Authorization" : f"Bearer {access_token}"
                                })

    print(users)
    print(user_id)
    print(response.json())

    assert response.status_code == 200
    assert response.json()["id"] == user_id



# TEST UPDATE USER
async def test_update_user(client):

    login_response = await client.post(prefix_login, 
                                       json={ 
                                           "email": "admin_e39d308328@gmail.com", 
                                           "password": "123456"
                                           })


    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Get user list
    users_response = await client.get(prefix_admin, 
                                      headers={
                                          "Authorization" : f"Bearer {access_token}"
                                      })

    assert users_response.status_code == 200

    # Get user id
    users = users_response.json()
    user_id = users[0]["id"]

    # Update user
    response = await client.patch(f"{prefix_admin}/{user_id}", 
                                  headers={
                                      "Authorization" : f"Bearer {access_token}"
                                  },

                                  json={
                                      "full_name": "Update user test",
                                      "phone": "0789123456"
                                  })

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["full_name"] == "Update user test"
    assert response.json()["phone"] == "0789123456"


# TEST UPDATE STATUS USER
async def test_update_status_user(client):

    login_response = await client.post(prefix_login, 
                                       json={ 
                                           "email": "admin_e39d308328@gmail.com", 
                                           "password": "123456"
                                           })


    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Get user list
    users_response = await client.get(prefix_admin, 
                                      headers={
                                          "Authorization" : f"Bearer {access_token}"
                                      })

    assert users_response.status_code == 200

    # Get user id
    users = users_response.json()
    user_id = users[4]["id"]

    # Update user
    response = await client.patch(f"{prefix_admin}/{user_id}/status", 
                                  headers={
                                      "Authorization" : f"Bearer {access_token}"
                                  },

                                  json={
                                      "is_active" : False
                                  })

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["is_active"] is False


# TEST UPDATE USER ROLES
async def test_update_user_roles(client):

    login_response = await client.post(prefix_login, 
                                       json={
                                           "email": "admin_e39d308328@gmail.com", 
                                           "password": "123456"
                                           })

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    users_response = await client.get(prefix_admin, 
                                      headers={
                                          "Authorization" : f"Bearer {access_token}"
                                      })

    assert users_response.status_code == 200

    users = users_response.json()
    user_id = users[16]["id"]


    # Update user roles
    response = await client.patch(f"{prefix_admin}/{user_id}/roles", 
                                  headers={
                                      "Authorization" : f"Bearer {access_token}"
                                  }, 
                                  json={
                                      "roles" : ["CUSTOMER"]
                                  })

    assert response.status_code == 200
    assert response.json()["id"] == user_id