"""Scraper for BezRealitky.cz
author: Mark Barzali
"""

from abc import ABC as abstract
from pathlib import Path
from posixpath import dirname
from typing import ClassVar

from aiohttp import ClientSession

from config import config
from disposition import Disposition
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer


class ScraperBezrealitky(ScraperBase):
    name = "BezRealitky"
    logo_url = "https://www.bezrealitky.cz/manifest-icon-192.maskable.png"
    color = 0x00CC00
    base_url = "https://www.bezrealitky.cz"

    API: ClassVar[str] = "https://api.bezrealitky.cz/"
    OFFER_TYPE: ClassVar[str] = "PRONAJEM"
    ESTATE_TYPE: ClassVar[str] = "BYT"
    BRNO: ClassVar[str] = "R438171"

    class Routes(abstract):
        GRAPHQL: ClassVar[str] = "graphql/"
        OFFERS: ClassVar[str] = "nemovitosti-byty-domy/"

    disposition_mapping = {
        Disposition.FLAT_1KK: "DISP_1_KK",
        Disposition.FLAT_1: "DISP_1_1",
        Disposition.FLAT_2KK: "DISP_2_KK",
        Disposition.FLAT_2: "DISP_2_1",
        Disposition.FLAT_3KK: "DISP_3_KK",
        Disposition.FLAT_3: "DISP_3_1",
        Disposition.FLAT_4KK: "DISP_4_KK",
        Disposition.FLAT_4: "DISP_4_1",
        Disposition.FLAT_5_UP: None,
        Disposition.FLAT_OTHERS: None,
    }

    def _build_query(self) -> dict:
        file_path = Path(dirname(__file__)) / "../../graphql/bezreality.graphql"
        variables = {
            "limit": 15,
            "offset": 0,
            "order": "TIMEORDER_DESC",
            "locale": "CS",
            "offerType": self.OFFER_TYPE,
            "estateType": self.ESTATE_TYPE,
            "disposition": self.get_dispositions_data(),
            "regionOsmIds": [self.BRNO],
        }

        if config.min_price:
            variables["priceFrom"] = config.min_price
        if config.max_price:
            variables["priceTo"] = config.max_price

        with open(file_path) as query_file:
            return {
                "operationName": "AdvertList",
                "query": query_file.read(),
                "variables": variables,
            }

    @staticmethod
    def _create_link_to_offer(item: dict) -> str:
        return f"{ScraperBezrealitky.base_url}/{ScraperBezrealitky.Routes.OFFERS}{item}"

    async def get_latest_offers(self, session: ClientSession) -> list[RentalOffer]:
        async with session.post(
            f"{ScraperBezrealitky.API}{ScraperBezrealitky.Routes.GRAPHQL}",
            json=self._build_query(),
        ) as response:
            data = await response.json()

        return [  # type: list[RentalOffer]
            RentalOffer(
                scraper=self,
                link=self._create_link_to_offer(item["uri"]),
                title=item["imageAltText"],
                location=item["address"],
                price=f"{item['price']} / {item['charges']}",
                image_url=item["mainImage"]["url"] if item["mainImage"] else "",
            )
            for item in data["data"]["listAdverts"]["list"]
        ]
