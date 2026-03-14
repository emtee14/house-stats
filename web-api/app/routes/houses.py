from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.deps import get_current_user_with_api_token
from app.data.houses import HouseDataset
from app.db import get_session
from app.models.auth import User
from app.routes.schemas.houses import (
    HouseDetailResponse,
    HousesByPostcodeResponse,
    HouseSummaryResponse,
    LinkedEpcResponse,
    SaleHistoryResponse,
)

router = APIRouter(tags=["Houses"])


@router.get(
    "/postcode/{postcode}",
    response_model=HousesByPostcodeResponse,
    summary="List houses for a postcode",
)
def get_houses_by_postcode(
    postcode: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user_with_api_token),
) -> HousesByPostcodeResponse:
    dataset = HouseDataset(session)
    houses = dataset.list_by_postcode(postcode)

    return HousesByPostcodeResponse(
        postcode=postcode,
        houses=[
            HouseSummaryResponse(
                houseid=house.houseid,
                paon=house.paon,
                saon=house.saon,
                postcode=house.postcode,
                type=house.type,
            )
            for house in houses
        ],
    )


@router.get(
    "/{houseid}",
    response_model=HouseDetailResponse,
    summary="Get house details",
)
def get_house_details(
    houseid: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user_with_api_token),
) -> HouseDetailResponse:
    dataset = HouseDataset(session)
    house = dataset.get_house(houseid)

    if house is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="House not found",
        )

    return HouseDetailResponse(
        houseid=house.houseid,
        paon=house.paon,
        saon=house.saon,
        street=house.postcode_obj.street,
        postcode=house.postcode,
        type=house.type,
        previous_sales=[
            SaleHistoryResponse(
                tui=sale.tui,
                price=sale.price,
                date=sale.date,
                new=sale.new,
                freehold=sale.freehold,
                ppd_cat=sale.ppd_cat,
            )
            for sale in dataset.get_sales(house.houseid)
        ],
        linked_epcs=[
            LinkedEpcResponse(
                lmk_key=certificate.lmk_key,
                address1=certificate.address1,
                address2=certificate.address2,
                address3=certificate.address3,
                postcode=certificate.postcode,
                current_energy_rating=certificate.current_energy_rating,
                potential_energy_rating=certificate.potential_energy_rating,
                property_type=certificate.property_type,
                lodgement_date=certificate.lodgement_date,
                total_floor_area=certificate.total_floor_area,
                uprn=certificate.uprn,
            )
            for certificate in dataset.get_linked_epcs(house)
        ],
    )
