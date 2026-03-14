from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


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
