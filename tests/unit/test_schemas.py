"""
Unit tests for Pydantic v2 schemas — all validation edge cases.
These run with no HTTP or DB involvement.
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest
from app.schemas.plant import PlantCreate, PlantUpdate


# ── LoginRequest ───────────────────────────────────────────────────────────────

class TestLoginRequestSchema:
    def test_valid_login(self):
        req = LoginRequest(username="operator", password="Operator@123")
        assert req.username == "operator"

    def test_username_is_lowercased(self):
        req = LoginRequest(username="ADMIN", password="Admin@123")
        assert req.username == "admin"

    def test_username_too_short_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="ab", password="password123")
        assert "username" in str(exc_info.value).lower() or "min_length" in str(exc_info.value)

    def test_username_too_long_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="a" * 51, password="password123")

    def test_username_special_chars_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="user name!", password="password123")

    def test_username_with_leading_space_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username=" admin", password="password123")

    def test_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin", password="short")

    def test_password_at_max_length_passes(self):
        req = LoginRequest(username="admin", password="P" * 128)
        assert len(req.password) == 128

    def test_password_over_max_length_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin", password="P" * 129)

    def test_missing_username_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin")


# ── PlantCreate ────────────────────────────────────────────────────────────────

class TestPlantCreateSchema:
    def _valid(self, **overrides) -> dict:
        base = {
            "name": "Test Plant",
            "location": "Bangalore, India",
            "status": "operational",
            "capacity_kw": 5000.0,
            "uptime_percent": 98.5,
        }
        return {**base, **overrides}

    def test_valid_plant_passes(self):
        p = PlantCreate(**self._valid())
        assert p.name == "Test Plant"
        assert p.capacity_kw == 5000.0

    def test_name_is_stripped(self):
        p = PlantCreate(**self._valid(name="  My Plant  "))
        assert p.name == "My Plant"

    def test_name_too_short_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(name="A"))

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(name="A" * 101))

    def test_name_with_forbidden_chars_raises(self):
        for bad_char in ['<', '>', '"', '{', '}']:
            with pytest.raises(ValidationError, match="forbidden"):
                PlantCreate(**self._valid(name=f"Plant{bad_char}Name"))

    def test_name_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(name="   "))

    def test_capacity_must_be_positive(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(capacity_kw=0))

    def test_capacity_negative_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(capacity_kw=-100))

    def test_capacity_over_max_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(capacity_kw=1_000_001))

    def test_uptime_above_100_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(uptime_percent=100.1))

    def test_uptime_below_0_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(uptime_percent=-0.1))

    def test_uptime_exactly_100_passes(self):
        p = PlantCreate(**self._valid(uptime_percent=100.0))
        assert p.uptime_percent == 100.0

    def test_offline_with_nonzero_uptime_raises(self):
        with pytest.raises(ValidationError, match="offline"):
            PlantCreate(**self._valid(status="offline", uptime_percent=50.0))

    def test_offline_with_zero_uptime_passes(self):
        p = PlantCreate(**self._valid(status="offline", uptime_percent=0.0))
        assert p.status == "offline"

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            PlantCreate(**self._valid(status="broken"))

    def test_missing_required_fields_raise(self):
        for field in ["name", "location", "capacity_kw"]:
            data = self._valid()
            del data[field]
            with pytest.raises(ValidationError):
                PlantCreate(**data)


# ── PlantUpdate ────────────────────────────────────────────────────────────────

class TestPlantUpdateSchema:
    def test_single_field_update_passes(self):
        u = PlantUpdate(status="maintenance")
        assert u.status == "maintenance"
        assert u.name is None

    def test_all_none_raises(self):
        with pytest.raises(ValidationError, match="least one field"):
            PlantUpdate()

    def test_name_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            PlantUpdate(name="   ")

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            PlantUpdate(status="unknown_status")

    def test_uptime_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            PlantUpdate(uptime_percent=101.0)

    def test_partial_update_preserves_none_fields(self):
        u = PlantUpdate(capacity_kw=9000.0)
        d = u.model_dump(exclude_none=True)
        assert d == {"capacity_kw": 9000.0}
