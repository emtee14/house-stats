from datetime import date, datetime

from pydantic import BaseModel, Field


class HouseSummaryResponse(BaseModel):
    houseid: str
    paon: str | None = None
    saon: str | None = None
    postcode: str | None = None
    type: str | None = None


class HousesByPostcodeResponse(BaseModel):
    postcode: str
    houses: list[HouseSummaryResponse] = Field(default_factory=list)


class SaleHistoryResponse(BaseModel):
    tui: str
    price: int | None = None
    date: datetime | None = None
    new: bool | None = None
    freehold: bool | None = None
    ppd_cat: str | None = None


class LinkedEpcResponse(BaseModel):
    lmk_key: str
    address1: str | None = None
    address2: str | None = None
    address3: str | None = None
    postcode: str | None = None
    current_energy_rating: str | None = None
    potential_energy_rating: str | None = None
    property_type: str | None = None
    lodgement_date: date | None = None
    total_floor_area: float | None = None
    uprn: int | None = None


class HouseDetailResponse(BaseModel):
    houseid: str
    paon: str | None = None
    saon: str | None = None
    street: str | None = None
    postcode: str | None = None
    type: str | None = None
    previous_sales: list[SaleHistoryResponse] = Field(default_factory=list)
    linked_epcs: list[LinkedEpcResponse] = Field(default_factory=list)
