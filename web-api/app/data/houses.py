from sqlmodel import Session, select

from app.models.housing_data import EpcCertificate, House, Sale, UPRNLookup


class HouseDataset:
    def __init__(self, session: Session):
        self.session = session

    def list_by_postcode(self, postcode: str) -> list[House]:
        statement = (
            select(House)
            .where(
                House.postcode
                == postcode
            )
            .order_by(House.paon, House.saon, House.houseid)
        )
        return list(self.session.exec(statement))

    def get_house(self, houseid: str) -> House | None:
        return self.session.get(House, houseid)

    def get_sales(self, houseid: str) -> list[Sale]:
        statement = (
            select(Sale)
            .where(Sale.houseid == houseid)
            .order_by(Sale.date.desc(), Sale.tui)
        )
        return list(self.session.exec(statement))

    def get_linked_epcs(self, house: House) -> list[EpcCertificate]:
        lookup = self.session.exec(
            select(UPRNLookup).where(UPRNLookup.houseid == house.houseid)
        ).first()
        if lookup is None:
            return []

        uprn = lookup.uprn
        statement = select(EpcCertificate).where(EpcCertificate.uprn == uprn)
        return list(self.session.exec(statement))
