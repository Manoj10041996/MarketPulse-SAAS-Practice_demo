def test_create_api_key_returns_201_with_expected_shape(client):
    response = client.post("/auth/api-keys", json={"owner_label": "acme-co"})

    assert response.status_code == 201
    body = response.json()
    assert body["owner_label"] == "acme-co"
    assert body["api_key"].startswith("mp_")
    assert "id" in body
    assert "created_at" in body


def test_create_api_key_rejects_empty_owner_label(client):
    response = client.post("/auth/api-keys", json={"owner_label": ""})
    assert response.status_code == 422
