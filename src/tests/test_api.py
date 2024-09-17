from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy import select
from app.models.parcels import ParcelType
from tests.conftest import db_helper_test
import pytest


async def test_insert_initial_data():
    async with db_helper_test.session_factory() as session:
        parcel_types_res = ["одежда", "электроника", "разное"]
        query = select(ParcelType)
        result = await session.scalars(query)
        if not result.all():
            for pt in parcel_types_res:
                session.add(ParcelType(name=pt))
            await session.commit()

        query = select(ParcelType)
        result = await session.scalars(query)
        parcel_types_res = result.all()

        assert len(parcel_types_res) == 3
        assert {pt.name for pt in parcel_types_res} == {
            "одежда",
            "электроника",
            "разное",
        }


async def test_get_parcels_type(
    async_client: AsyncClient,
):
    response = await async_client.get("/api/v1/parcels/parcels_types")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {pt["name"] for pt in data} == {
        "одежда",
        "электроника",
        "разное",
    }


async def test_register_parcel_positive(
    async_client: AsyncClient,
):
    with patch("tasks.worker.process_package.send") as mock_send:
        response = await async_client.post(
            "/api/v1/parcels/registration",
            json={
                "name": "some_parcel",
                "weight": 10,
                "cost_content": 100,
                "type_id": 1,
            },
        )
        assert response.status_code == 200
        parcel_id = response.json()
        assert isinstance(parcel_id, int)
        assert parcel_id > 0
        mock_send.assert_called_once_with(parcel_id=parcel_id)

        response = await async_client.get(f"/api/v1/parcels/{parcel_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["name"] == "some_parcel"
        assert data[0]["weight"] == "10"
        assert data[0]["cost_content"] == "100"
        assert data[0]["id"] == parcel_id


@pytest.mark.parametrize(
    ("name", "weight", "cost_content", "type_id"),
    [
        ("parcel_negative", 10, 100, 4),
        (10, "aaa", 100, 3),
        ("parcel_negative", 10, "bbb", 3),
        ("parcel_negative", 10, 100, "ccc"),
    ],
)
async def test_register_parcel_negative(
    async_client: AsyncClient,
    name,
    weight,
    cost_content,
    type_id,
):
    # with patch("tasks.worker.process_package.send"):
    response = await async_client.post(
        "/api/v1/parcels/registration",
        json={
            "name": name,
            "weight": weight,
            "cost_content": cost_content,
            "type_id": type_id,
        },
    )
    assert response.status_code == 422, response.text


async def test_get_parcels_by_session_id_positive(
    async_client: AsyncClient,
):
    response = await async_client.get("/api/v1/parcels/parcels_list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


async def test_get_parcels_by_session_id_negative(
    async_client: AsyncClient,
):
    response = await async_client.get(
        "/api/v1/parcels/parcels_list", cookies={"session_id": "test-session-id"}
    )
    assert response.status_code == 404


async def test_get_parcels_by_parcel_id_negative(
    async_client: AsyncClient,
):
    response = await async_client.get("/api/v1/parcels/parcels_list/100000")
    assert response.status_code == 404, response.text
