import pytest

@pytest.mark.asyncio
async def test_database_connection(client):

    response = await client.get("/db-check")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["result"] == 1