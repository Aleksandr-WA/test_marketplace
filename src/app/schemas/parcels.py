from decimal import Decimal
from pydantic import BaseModel, Field


class ParcelType(BaseModel):
    id: int = Field(ge=1, le=3)
    name: str = Field(max_length=255)


class ParcelBase(BaseModel):
    name: str = Field(max_length=255)
    weight: Decimal = Field(gt=0)
    cost_content: Decimal = Field(gt=0)


class ParcelCreate(ParcelBase):
    type_id: int = Field(ge=1, le=3)


class ParcelReadBase(BaseModel):
    id: int
    cost_delivery: Decimal | None


class ParcelReadParcelId(ParcelReadBase, ParcelCreate):
    pass


class ParcelReadSessionId(ParcelReadBase, ParcelBase):
    type: ParcelType
