"""
Integration tests for plant endpoints.
Covers CRUD, RBAC, validation, error responses, and edge cases.
"""
import pytest

VALID_PLANT = {
    "name": "Test Plant Alpha",
    "location": "Stuttgart, Germany",
    "status": "operational",
    "capacity_kw": 5000.0,
    "uptime_percent": 98.5,
}

BASE_URL = "/api/v1/plants"


def _create(client, headers, body=None) -> dict:
    resp = client.post(BASE_URL, json=body or VALID_PLANT, headers=headers)
    assert resp.status_code == 201, f"Create failed: {resp.text}"
    return resp.json()


# ── Unauthenticated access ─────────────────────────────────────────────────────

class TestUnauthenticated:
    def test_list_without_token_is_401(self, client):
        resp = client.get(BASE_URL)
        assert resp.status_code == 401

    def test_create_without_token_is_401(self, client):
        resp = client.post(BASE_URL, json=VALID_PLANT)
        assert resp.status_code == 401

    def test_get_without_token_is_401(self, client):
        resp = client.get(f"{BASE_URL}/any-id")
        assert resp.status_code == 401

    def test_update_without_token_is_401(self, client):
        resp = client.put(f"{BASE_URL}/any-id", json={"status": "maintenance"})
        assert resp.status_code == 401

    def test_delete_without_token_is_401(self, client):
        resp = client.delete(f"{BASE_URL}/any-id")
        assert resp.status_code == 401


# ── List Plants ────────────────────────────────────────────────────────────────

class TestListPlants:
    def test_viewer_can_list(self, client, viewer_headers):
        resp = client.get(BASE_URL, headers=viewer_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    def test_pagination_defaults(self, client, admin_headers):
        resp = client.get(BASE_URL, headers=admin_headers)
        assert resp.json()["page"] == 1
        assert resp.json()["page_size"] == 10

    def test_pagination_custom(self, client, admin_headers):
        for i in range(5):
            _create(client, admin_headers, {**VALID_PLANT, "name": f"Plant {i}"})
        resp = client.get(f"{BASE_URL}?page=1&page_size=2", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    def test_filter_by_status(self, client, admin_headers, operator_headers):
        _create(client, operator_headers, {**VALID_PLANT, "name": "Op Plant", "status": "operational"})
        _create(client, admin_headers, {**VALID_PLANT, "name": "Maint Plant", "status": "maintenance", "uptime_percent": 0.0})
        resp = client.get(f"{BASE_URL}?status=maintenance", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "maintenance"

    def test_filter_invalid_status_gives_422(self, client, admin_headers):
        resp = client.get(f"{BASE_URL}?status=broken", headers=admin_headers)
        assert resp.status_code == 422

    def test_invalid_page_size_gives_422(self, client, admin_headers):
        resp = client.get(f"{BASE_URL}?page_size=0", headers=admin_headers)
        assert resp.status_code == 422

    def test_page_size_over_100_gives_422(self, client, admin_headers):
        resp = client.get(f"{BASE_URL}?page_size=101", headers=admin_headers)
        assert resp.status_code == 422


# ── Create Plant ───────────────────────────────────────────────────────────────

class TestCreatePlant:
    def test_operator_can_create(self, client, operator_headers):
        resp = client.post(BASE_URL, json=VALID_PLANT, headers=operator_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == VALID_PLANT["name"]
        assert "id" in data
        assert "created_at" in data

    def test_admin_can_create(self, client, admin_headers):
        resp = client.post(BASE_URL, json=VALID_PLANT, headers=admin_headers)
        assert resp.status_code == 201

    def test_viewer_cannot_create(self, client, viewer_headers):
        resp = client.post(BASE_URL, json=VALID_PLANT, headers=viewer_headers)
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_duplicate_name_gives_409(self, client, admin_headers):
        _create(client, admin_headers)
        resp = client.post(BASE_URL, json=VALID_PLANT, headers=admin_headers)
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CONFLICT"

    def test_duplicate_name_case_insensitive(self, client, admin_headers):
        _create(client, admin_headers)
        resp = client.post(BASE_URL, json={**VALID_PLANT, "name": "test plant alpha"}, headers=admin_headers)
        assert resp.status_code == 409

    def test_missing_required_field_gives_422(self, client, admin_headers):
        bad = {k: v for k, v in VALID_PLANT.items() if k != "name"}
        resp = client.post(BASE_URL, json=bad, headers=admin_headers)
        assert resp.status_code == 422
        error = resp.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert any(e["field"] == "name" for e in error["details"])

    def test_negative_capacity_gives_422(self, client, admin_headers):
        resp = client.post(BASE_URL, json={**VALID_PLANT, "capacity_kw": -1}, headers=admin_headers)
        assert resp.status_code == 422

    def test_uptime_over_100_gives_422(self, client, admin_headers):
        resp = client.post(BASE_URL, json={**VALID_PLANT, "uptime_percent": 100.1}, headers=admin_headers)
        assert resp.status_code == 422

    def test_offline_nonzero_uptime_gives_422(self, client, admin_headers):
        resp = client.post(BASE_URL, json={**VALID_PLANT, "status": "offline", "uptime_percent": 50.0}, headers=admin_headers)
        assert resp.status_code == 422

    def test_plant_name_with_html_chars_gives_422(self, client, admin_headers):
        resp = client.post(BASE_URL, json={**VALID_PLANT, "name": "<script>alert(1)</script>"}, headers=admin_headers)
        assert resp.status_code == 422

    def test_empty_body_gives_422(self, client, admin_headers):
        resp = client.post(BASE_URL, json={}, headers=admin_headers)
        assert resp.status_code == 422


# ── Get Plant ──────────────────────────────────────────────────────────────────

class TestGetPlant:
    def test_get_existing_plant(self, client, admin_headers):
        created = _create(client, admin_headers)
        resp = client.get(f"{BASE_URL}/{created['id']}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_nonexistent_gives_404(self, client, viewer_headers):
        resp = client.get(f"{BASE_URL}/does-not-exist", headers=viewer_headers)
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_viewer_can_get(self, client, admin_headers, viewer_headers):
        created = _create(client, admin_headers)
        resp = client.get(f"{BASE_URL}/{created['id']}", headers=viewer_headers)
        assert resp.status_code == 200


# ── Update Plant ───────────────────────────────────────────────────────────────

class TestUpdatePlant:
    def test_admin_can_update_any_plant(self, client, admin_headers, operator_headers):
        created = _create(client, operator_headers)
        resp = client.put(
            f"{BASE_URL}/{created['id']}",
            json={"status": "maintenance"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "maintenance"

    def test_operator_can_update_own_plant(self, client, operator_headers):
        created = _create(client, operator_headers)
        resp = client.put(
            f"{BASE_URL}/{created['id']}",
            json={"capacity_kw": 9000.0},
            headers=operator_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["capacity_kw"] == 9000.0

    def test_operator_cannot_update_others_plant(self, client, admin_headers, operator_headers):
        created = _create(client, admin_headers)  # admin owns it
        resp = client.put(
            f"{BASE_URL}/{created['id']}",
            json={"status": "maintenance"},
            headers=operator_headers,
        )
        assert resp.status_code == 403

    def test_viewer_cannot_update(self, client, admin_headers, viewer_headers):
        created = _create(client, admin_headers)
        resp = client.put(
            f"{BASE_URL}/{created['id']}",
            json={"status": "maintenance"},
            headers=viewer_headers,
        )
        assert resp.status_code == 403

    def test_update_nonexistent_gives_404(self, client, admin_headers):
        resp = client.put(f"{BASE_URL}/no-such-id", json={"status": "maintenance"}, headers=admin_headers)
        assert resp.status_code == 404

    def test_empty_update_body_gives_422(self, client, admin_headers):
        created = _create(client, admin_headers)
        resp = client.put(f"{BASE_URL}/{created['id']}", json={}, headers=admin_headers)
        assert resp.status_code == 422
        assert "least one field" in resp.json()["error"]["details"][0]["message"].lower()

    def test_update_preserves_unset_fields(self, client, admin_headers):
        created = _create(client, admin_headers)
        resp = client.put(
            f"{BASE_URL}/{created['id']}",
            json={"capacity_kw": 7777.0},
            headers=admin_headers,
        )
        assert resp.json()["name"] == created["name"]
        assert resp.json()["location"] == created["location"]


# ── Delete Plant ───────────────────────────────────────────────────────────────

class TestDeletePlant:
    def test_admin_can_delete(self, client, admin_headers):
        created = _create(client, admin_headers)
        resp = client.delete(f"{BASE_URL}/{created['id']}", headers=admin_headers)
        assert resp.status_code == 204
        # Verify it's gone
        get_resp = client.get(f"{BASE_URL}/{created['id']}", headers=admin_headers)
        assert get_resp.status_code == 404

    def test_operator_cannot_delete(self, client, admin_headers, operator_headers):
        created = _create(client, admin_headers)
        resp = client.delete(f"{BASE_URL}/{created['id']}", headers=operator_headers)
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_viewer_cannot_delete(self, client, admin_headers, viewer_headers):
        created = _create(client, admin_headers)
        resp = client.delete(f"{BASE_URL}/{created['id']}", headers=viewer_headers)
        assert resp.status_code == 403

    def test_delete_nonexistent_gives_404(self, client, admin_headers):
        resp = client.delete(f"{BASE_URL}/ghost-id", headers=admin_headers)
        assert resp.status_code == 404


# ── Health endpoint ────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_no_auth_needed(self, client):
        """Health endpoint must not require authentication — Cloud Run probes use it."""
        resp = client.get("/health")
        assert resp.status_code == 200


# ── Error envelope shape ───────────────────────────────────────────────────────

class TestErrorEnvelope:
    """All error responses must follow: {"error": {"code": ..., "message": ...}}"""

    def test_404_has_correct_envelope(self, client, admin_headers):
        resp = client.get(f"{BASE_URL}/missing", headers=admin_headers)
        error = resp.json().get("error")
        assert error is not None
        assert "code" in error
        assert "message" in error

    def test_401_has_correct_envelope(self, client):
        resp = client.get(BASE_URL)
        error = resp.json().get("error")
        assert error is not None

    def test_422_details_are_list(self, client, admin_headers):
        resp = client.post(BASE_URL, json={}, headers=admin_headers)
        error = resp.json()["error"]
        assert isinstance(error["details"], list)
        assert len(error["details"]) > 0
        # Each detail has field, message, type
        detail = error["details"][0]
        assert "field" in detail
        assert "message" in detail

    def test_no_internal_details_leak_on_500(self, client, admin_headers, monkeypatch):
        """500 responses must never expose tracebacks or internal error details."""
        from app.services import plant_service
        def boom(*args, **kwargs):
            raise RuntimeError("db connection failed: host=internal-db:5432")
        monkeypatch.setattr(plant_service, "list_plants", boom)

        resp = client.get(BASE_URL, headers=admin_headers)
        assert resp.status_code == 500
        body = resp.text
        assert "internal-db" not in body
        assert "Traceback" not in body
        assert "RuntimeError" not in body
