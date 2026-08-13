"""
Unit tests for the plant service layer — pure business logic, no HTTP.
"""
import pytest

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.domain import PLANTS_DB, USERS_DB
from app.schemas.plant import PlantCreate, PlantQueryParams, PlantUpdate
from app.services.plant_service import (
    create_plant,
    delete_plant,
    get_plant,
    list_plants,
    update_plant,
)


def _admin():
    return next(u for u in USERS_DB.values() if u.role == "admin")

def _operator():
    return next(u for u in USERS_DB.values() if u.role == "operator")

def _make_plant(name="Test Plant", **kwargs) -> PlantCreate:
    return PlantCreate(
        name=name,
        location="Bangalore, India",
        status="operational",
        capacity_kw=5000.0,
        uptime_percent=98.5,
        **kwargs,
    )


class TestCreatePlant:
    def test_create_plant_returns_response(self):
        result = create_plant(_make_plant(), _admin())
        assert result.name == "Test Plant"
        assert result.id in PLANTS_DB

    def test_create_plant_sets_owner_id(self):
        admin = _admin()
        result = create_plant(_make_plant(), admin)
        assert result.owner_id == admin.id

    def test_duplicate_name_raises_conflict(self):
        create_plant(_make_plant("Alpha Plant"), _admin())
        with pytest.raises(ConflictError):
            create_plant(_make_plant("alpha plant"), _admin())  # Case-insensitive

    def test_different_names_succeed(self):
        create_plant(_make_plant("Plant A"), _admin())
        result = create_plant(_make_plant("Plant B"), _admin())
        assert result.name == "Plant B"
        assert len(PLANTS_DB) == 2


class TestGetPlant:
    def test_get_existing_plant(self):
        created = create_plant(_make_plant(), _admin())
        fetched = get_plant(created.id)
        assert fetched.id == created.id
        assert fetched.name == created.name

    def test_get_nonexistent_raises_not_found(self):
        with pytest.raises(NotFoundError):
            get_plant("nonexistent-id")


class TestListPlants:
    def _seed(self):
        create_plant(_make_plant("Operational Plant 1", status="operational", uptime_percent=99.0), _admin())
        create_plant(_make_plant("Maintenance Plant", status="maintenance", uptime_percent=0.0), _admin())
        create_plant(_make_plant("Operational Plant 2", status="operational", uptime_percent=75.0), _admin())

    def test_list_returns_all(self):
        self._seed()
        result = list_plants(PlantQueryParams())
        assert result.total == 3
        assert len(result.items) == 3

    def test_filter_by_status(self):
        self._seed()
        result = list_plants(PlantQueryParams(status="operational"))
        assert result.total == 2
        assert all(p.status == "operational" for p in result.items)

    def test_filter_by_min_uptime(self):
        self._seed()
        result = list_plants(PlantQueryParams(min_uptime=90.0))
        assert result.total == 1
        assert result.items[0].uptime_percent >= 90.0

    def test_pagination(self):
        for i in range(5):
            create_plant(_make_plant(f"Plant {i}"), _admin())
        p1 = list_plants(PlantQueryParams(page=1, page_size=2))
        p2 = list_plants(PlantQueryParams(page=2, page_size=2))
        assert len(p1.items) == 2
        assert len(p2.items) == 2
        assert p1.total == 5
        assert p1.items[0].id != p2.items[0].id

    def test_empty_db_returns_empty(self):
        result = list_plants(PlantQueryParams())
        assert result.total == 0
        assert result.items == []


class TestUpdatePlant:
    def test_admin_can_update_any_plant(self):
        operator = _operator()
        created = create_plant(_make_plant(), operator)
        result = update_plant(created.id, PlantUpdate(status="maintenance"), _admin())
        assert result.status == "maintenance"

    def test_operator_can_update_own_plant(self):
        operator = _operator()
        created = create_plant(_make_plant(), operator)
        result = update_plant(created.id, PlantUpdate(capacity_kw=9000.0), operator)
        assert result.capacity_kw == 9000.0

    def test_operator_cannot_update_others_plant(self):
        admin = _admin()
        created = create_plant(_make_plant(), admin)
        operator = _operator()
        with pytest.raises(ForbiddenError):
            update_plant(created.id, PlantUpdate(status="maintenance"), operator)

    def test_update_nonexistent_raises_not_found(self):
        with pytest.raises(NotFoundError):
            update_plant("bad-id", PlantUpdate(status="maintenance"), _admin())

    def test_update_preserves_unmodified_fields(self):
        created = create_plant(_make_plant(), _admin())
        updated = update_plant(created.id, PlantUpdate(capacity_kw=9999.0), _admin())
        assert updated.name == created.name
        assert updated.location == created.location
        assert updated.status == created.status

    def test_offline_uptime_conflict_raises(self):
        created = create_plant(_make_plant(status="operational", uptime_percent=98.5), _admin())
        with pytest.raises(ConflictError, match="offline"):
            update_plant(created.id, PlantUpdate(status="offline"), _admin())

    def test_name_change_to_duplicate_raises_conflict(self):
        create_plant(_make_plant("Existing Plant"), _admin())
        created2 = create_plant(_make_plant("Another Plant"), _admin())
        with pytest.raises(ConflictError):
            update_plant(created2.id, PlantUpdate(name="existing plant"), _admin())


class TestDeletePlant:
    def test_admin_can_delete(self):
        created = create_plant(_make_plant(), _admin())
        delete_plant(created.id, _admin())
        assert created.id not in PLANTS_DB

    def test_delete_nonexistent_raises_not_found(self):
        with pytest.raises(NotFoundError):
            delete_plant("nonexistent-id", _admin())
