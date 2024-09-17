from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from decimal import Decimal


class Parcel(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[Decimal]
    type_id: Mapped[int] = mapped_column(ForeignKey("parcel_types.id"), index=True)
    cost_content: Mapped[Decimal]
    cost_delivery: Mapped[Decimal] = mapped_column(nullable=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)

    type: Mapped["ParcelType"] = relationship("ParcelType", back_populates="parcels")
    session: Mapped["Session"] = relationship("Session", back_populates="parcels")


class ParcelType(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255), unique=True)

    parcels: Mapped[list["Parcel"]] = relationship("Parcel", back_populates="type")


class Session(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255), unique=True)

    parcels: Mapped[list["Parcel"]] = relationship("Parcel", back_populates="session")
