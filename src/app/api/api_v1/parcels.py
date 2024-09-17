import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, Query, Path
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_helper import db_helper
from app.crud.parcels import (
    create_parcel,
    get_all_parcel_types,
    get_all_parcel_list,
    get_parcel_by_id,
    set_session_id,
    get_session_id,
)
from app.schemas.parcels import (
    ParcelCreate,
    ParcelType,
    ParcelReadParcelId,
    ParcelReadSessionId,
)

router = APIRouter()


@router.post("/registration")
async def register_parcel(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    parcel_create: ParcelCreate,
    request: Request,
    response: Response,
) -> int:
    session_id = await get_session_id(
        session=session,
        request=request,
    )
    if not session_id:
        session_value = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_value,
        )
        session_id = await set_session_id(
            session=session,
            session_value=session_value,
        )
    parcel = await create_parcel(
        session=session,
        parcel_create=parcel_create,
        session_id=session_id,
    )
    return parcel.id


@router.get("/parcels_types", response_model=list[ParcelType])
async def get_parcels_type(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    parcels_types = await get_all_parcel_types(session=session)
    return parcels_types


@router.get("/parcels_list", response_model=list[ParcelReadSessionId])
async def get_parcels_by_session_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=100)] = 10,
    type_id: Annotated[int | None, Query(ge=1, le=3)] = None,
    cost_delivery: Annotated[bool, Query()] = None,
):
    parcels_list = await get_all_parcel_list(
        session=session,
        request=request,
        skip=skip,
        limit=limit,
        type_id=type_id,
        cost_delivery=cost_delivery,
    )
    return parcels_list


@router.get("/{parcel_id}", response_model=list[ParcelReadParcelId])
async def get_parcels_by_parcel_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    parcel_id: Annotated[int, Path(title="This is the parcel id", gt=0)],
    request: Request,
):
    parcels_list_id = await get_parcel_by_id(
        session=session, parcel_id=parcel_id, request=request
    )
    if not parcels_list_id:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcels_list_id
