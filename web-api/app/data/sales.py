from datetime import datetime

from app.data.base import BaseDataset


class SalesDataset(BaseDataset):
    VALID_AREA_TYPES = {"area", "district", "county", "town", "sector", "outcode", "postcode"}

    @staticmethod
    def build_data_id(area_type: str, area: str, start_date: datetime, end_date: datetime) -> str:
        return f"{area_type}_{area}:{start_date}-{end_date}".upper().replace(" ", "")

    def _gen_query(self, area_type: str, area: str,
                   start_date: datetime, end_date: datetime):

        if area_type not in self.VALID_AREA_TYPES:
            raise ValueError(f"Invalid area_type: {area_type}")

        sql = f"""
        SELECT s.price, s.date, h.type, h.paon, h.saon, h.postcode,
               p.street, p.town, h.houseid
        FROM housing_data.postcodes AS p
        JOIN housing_data.houses AS h
            ON p.postcode = h.postcode
           AND p.{area_type} = :area
        JOIN housing_data.sales AS s
            ON h.houseid = s.houseid
           AND h.type != 'O'
        WHERE s.ppd_cat = 'A'
          AND s.date BETWEEN :start_date AND :end_date
        """

        params = {
            "area": area,
            "start_date": start_date,
            "end_date": end_date
        }

        return sql, params

    def query(self, area_type: str, area: str, start_date: datetime, end_date: datetime,):

        sql, params = self._gen_query(area_type, area, start_date, end_date)

        df = self.run_query(sql, params)
        data_id = self.build_data_id(area_type, area, start_date, end_date)

        return df, data_id
