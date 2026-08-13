"""
Integration tests for auth endpoints.
Uses TestClient — full HTTP request/response cycle, no mocking.
"""
import pytest


class TestLoginEndpoint:
    URL = "/api/v1/auth/login"

    def test_login_valid_admin(self, client):
        resp = client.post(self.URL, json={"username": "admin", "password": "Admin@123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_case_insensitive_username(self, client):
        resp = client.post(self.URL, json={"username": "ADMIN", "password": "Admin@123"})
        assert resp.status_code == 200

    def test_login_wrong_password(self, client):
        resp = client.post(self.URL, json={"username": "admin", "password": "WrongPass@123"})
        assert resp.status_code == 401
        error = resp.json()["error"]
        assert error["code"] == "INVALID_CREDENTIALS"
        # Must NOT reveal whether username exists
        assert "admin" not in resp.text.lower() or "not found" not in resp.text.lower()

    def test_login_nonexistent_user(self, client):
        resp = client.post(self.URL, json={"username": "nobody", "password": "SomePass@123"})
        assert resp.status_code == 401

    def test_login_missing_username_gives_422(self, client):
        resp = client.post(self.URL, json={"password": "Admin@123"})
        assert resp.status_code == 422
        error = resp.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert any(e["field"] == "username" for e in error["details"])

    def test_login_missing_password_gives_422(self, client):
        resp = client.post(self.URL, json={"username": "admin"})
        assert resp.status_code == 422

    def test_login_short_password_gives_422(self, client):
        resp = client.post(self.URL, json={"username": "admin", "password": "short"})
        assert resp.status_code == 422

    def test_login_invalid_username_pattern_gives_422(self, client):
        resp = client.post(self.URL, json={"username": "admin@hacker", "password": "Admin@123"})
        assert resp.status_code == 422

    def test_login_returns_x_request_id_header(self, client):
        resp = client.post(self.URL, json={"username": "admin", "password": "Admin@123"})
        assert "x-request-id" in resp.headers

    def test_login_empty_body_gives_422(self, client):
        resp = client.post(self.URL, json={})
        assert resp.status_code == 422

    def test_login_all_three_roles(self, client):
        users = [
            ("admin", "Admin@123"),
            ("operator", "Operator@123"),
            ("viewer", "Viewer@123"),
        ]
        for username, password in users:
            resp = client.post(self.URL, json={"username": username, "password": password})
            assert resp.status_code == 200, f"Login failed for {username}"


class TestRefreshEndpoint:
    LOGIN_URL = "/api/v1/auth/login"
    URL = "/api/v1/auth/refresh"

    def _get_refresh_token(self, client) -> str:
        resp = client.post(self.LOGIN_URL, json={"username": "admin", "password": "Admin@123"})
        return resp.json()["refresh_token"]

    def _get_access_token(self, client) -> str:
        resp = client.post(self.LOGIN_URL, json={"username": "admin", "password": "Admin@123"})
        return resp.json()["access_token"]

    def test_refresh_with_valid_token(self, client):
        refresh_token = self._get_refresh_token(client)
        resp = client.post(self.URL, json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_refresh_with_access_token_rejected(self, client):
        """Access tokens must NOT work as refresh tokens."""
        access_token = self._get_access_token(client)
        resp = client.post(self.URL, json={"refresh_token": access_token})
        assert resp.status_code == 401
        assert "access" in resp.json()["error"]["message"].lower() or \
               "refresh" in resp.json()["error"]["message"].lower()

    def test_refresh_with_invalid_token_gives_401(self, client):
        resp = client.post(self.URL, json={"refresh_token": "not.a.real.token"})
        assert resp.status_code == 401

    def test_refresh_missing_token_gives_422(self, client):
        resp = client.post(self.URL, json={})
        assert resp.status_code == 422


class TestMeEndpoint:
    URL = "/api/v1/auth/me"
    LOGIN_URL = "/api/v1/auth/login"

    def test_me_returns_current_user(self, client, admin_headers):
        resp = client.get(self.URL, headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "hashed_password" not in data

    def test_me_without_token_gives_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401

    def test_me_with_bad_token_gives_401(self, client):
        resp = client.get(self.URL, headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_me_viewer_has_correct_role(self, client, viewer_headers):
        resp = client.get(self.URL, headers=viewer_headers)
        assert resp.status_code == 200
        assert resp.json()["role"] == "viewer"

    def test_me_operator_has_correct_role(self, client, operator_headers):
        resp = client.get(self.URL, headers=operator_headers)
        assert resp.status_code == 200
        assert resp.json()["role"] == "operator"

    def test_me_response_has_no_sensitive_fields(self, client, admin_headers):
        resp = client.get(self.URL, headers=admin_headers)
        data = resp.json()
        forbidden_fields = {"hashed_password", "password", "secret", "token"}
        assert not forbidden_fields.intersection(data.keys())
