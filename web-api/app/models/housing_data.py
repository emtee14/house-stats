from datetime import date, datetime
from typing import List

from sqlalchemy import BigInteger, Column, DateTime
from sqlmodel import Field, SQLModel, Relationship


class Postcode(SQLModel, table=True):
    __tablename__ = "postcodes"
    __table_args__ = {"schema": "housing_data"}

    postcode: str = Field(primary_key=True, max_length=15)
    street: str | None = Field(default=None, max_length=70, index=True)
    town: str | None = Field(default=None, max_length=50, index=True)
    district: str | None = Field(default=None, max_length=50, index=True)
    county: str | None = Field(default=None, max_length=50, index=True)
    outcode: str | None = Field(default=None, max_length=4, index=True)
    area: str | None = Field(default=None, max_length=2, index=True)
    sector: str | None = Field(default=None, max_length=6, index=True)

    houses: List["House"] = Relationship(back_populates="postcode_obj")


class House(SQLModel, table=True):
    __tablename__ = "houses"
    __table_args__ = {"schema": "housing_data"}

    houseid: str = Field(primary_key=True, max_length=150)
    paon: str | None = Field(default=None, max_length=150)
    saon: str | None = Field(default=None, max_length=150)
    postcode: str | None = Field(
        default=None,
        foreign_key="housing_data.postcodes.postcode",
        max_length=15,
        index=True,
    )
    type: str | None = Field(default=None, max_length=1, index=True)

    postcode_obj: Postcode = Relationship(back_populates="houses")
    uprn_lookup: "UPRNLookup" = Relationship(back_populates="house")


class Sale(SQLModel, table=True):
    __tablename__ = "sales"
    __table_args__ = {"schema": "housing_data"}

    tui: str = Field(primary_key=True, max_length=36)
    price: int | None = Field(default=None)
    date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), index=True, nullable=True),
    )
    new: bool | None = Field(default=None)
    freehold: bool | None = Field(default=None, index=True)
    ppd_cat: str | None = Field(default=None, max_length=1, index=True)
    houseid: str | None = Field(
        default=None,
        foreign_key="housing_data.houses.houseid",
        max_length=150,
    )


class EpcCertificate(SQLModel, table=True):
    __tablename__ = "epc_certificates"
    __table_args__ = {"schema": "housing_data"}

    lmk_key: str = Field(primary_key=True, max_length=64)
    address1: str | None = Field(default=None, max_length=150)
    address2: str | None = Field(default=None, max_length=104)
    address3: str | None = Field(default=None, max_length=100)
    postcode: str | None = Field(default=None, max_length=15, index=True)
    current_energy_rating: str | None = Field(default=None, max_length=8, index=True)
    potential_energy_rating: str | None = Field(default=None, max_length=8)
    property_type: str | None = Field(default=None, max_length=76)
    lodgement_date: date | None = Field(default=None, index=True)
    total_floor_area: float | None = Field(default=None)
    uprn: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, index=True, nullable=True),
    )


class UPRNLookup(SQLModel, table=True):
    __tablename__ = "uprn_lookup"
    __table_args__ = {"schema": "housing_data"}

    houseid: str = Field(
        primary_key=True,
        foreign_key="housing_data.houses.houseid",
        max_length=150,
    )
    uprn: int = Field(sa_column=Column(BigInteger, index=True, nullable=False))

    house: House = Relationship(back_populates="uprn_lookup")
