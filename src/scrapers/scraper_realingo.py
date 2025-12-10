from pathlib import Path
from posixpath import dirname
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from config import config
from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase


class ScraperRealingo(ScraperBase):

    name = "realingo"
    logo_url = "https://www.realingo.cz/_next/static/media/images/android-chrome-144x144-cf1233ce.png"
    color = 0x00BC78
    base_url = "https://www.realingo.cz/graphql"

    disposition_mapping = {
        Disposition.FLAT_1KK: "FLAT1_KK",
        Disposition.FLAT_1: "FLAT11",
        Disposition.FLAT_2KK: "FLAT2_KK",
        Disposition.FLAT_2: "FLAT21",
        Disposition.FLAT_3KK: "FLAT3_KK",
        Disposition.FLAT_3: "FLAT31",
        Disposition.FLAT_4KK: "FLAT4_KK",
        Disposition.FLAT_4: "FLAT41",
        Disposition.FLAT_5_UP: ("FLAT5_KK", "FLAT51", "FLAT6_AND_MORE"),
        Disposition.FLAT_OTHERS: "OTHERS_FLAT",
    }

    def _build_query(self) -> dict[str, Any]:
        file_path = Path(dirname(__file__)) / "../../graphql/realingo.graphql"

        with open(file_path) as query_file:
            return {
                "query": query_file.read(),
                "operationName": "SearchOffer",
                "variables": {
                    "purpose": "RENT",
                    "property": "FLAT",
                    "address": "Brno",
                    "saved": False,
                    "categories": self.get_dispositions_data(),
                    "sort": "NEWEST",
                    "first": 300,
                    "skip": 0,
                    "price": {
                        "from": config.min_price,
                        "to": config.max_price,
                    }
                }
            }

    def category_to_string(self, id) -> str:
        return {
            "FLAT1_KK": "Byt 1+kk",
            "FLAT11": "Byt 1+1",
            "FLAT2_KK": "Byt 2+kk",
            "FLAT21": "Byt 2+1",
            "FLAT3_KK": "Byt 3+kk",
            "FLAT31": "Byt 3+1",
            "FLAT4_KK": "Byt 4+kk",
            "FLAT41": "Byt 4+1",
            "FLAT5_KK": "Byt 5+kk",
            "FLAT51": "Byt 5+1",
            "FLAT6_AND_MORE": "Byt 6+kk a v\u011bt\u0161\xed",
            "HOUSE_FAMILY": "Rodinn\xfd dům",
            "HOUSE_APARTMENT": "\u010cin\u017eovn\xed",
            "HOUSE_MANSION": "Vila",
            "LAND_COMMERCIAL": "Komer\u010dn\xed",
            "LAND_HOUSING": "Bydlen\xed",
            "LAND_GARDEN": "Zahrady",
            "LAND_AGRICULTURAL": "Zem\u011bd\u011blsk\xfd",
            "LAND_MEADOW": "Louka",
            "LAND_FOREST": "Les",
            "COMMERCIAL_OFFICE": "Kancel\xe1\u0159",
            "COMMERCIAL_STORAGE": "Sklad",
            "COMMERCIAL_MANUFACTURING": "V\xfdrobn\xed prostor",
            "COMMERCIAL_BUSINESS": "Obchod",
            "COMMERCIAL_ACCOMMODATION": "Ubytov\xe1n\xed",
            "COMMERCIAL_RESTAURANT": "Restaurace",
            "COMMERCIAL_AGRICULTURAL": "Zem\u011bd\u011blsk\xfd objekt",
            "OTHERS_HUT": "Chata",
            "OTHERS_COTTAGE": "Chalupa",
            "OTHERS_GARAGE": "Gar\xe1\u017e",
            "OTHERS_FARMHOUSE": "Zem\u011bd\u011blsk\xe1 usedlost",
            "OTHERS_POND": "Rybn\xedk",
            "OTHERS_FLAT": "Atypick\xfd",
            "OTHERS_OTHERS": "Pam\xe1tka",
            "OTHERS_MONUMENTS": "Ostatn\xed"
        }.get(id, "")


    async def get_latest_offers(self, session: ClientSession) -> list[RentalOffer]:
        async with session.post(self.base_url, json=self._build_query()) as response:
            data = await response.json()

        items: list[RentalOffer] = []

        for offer in data["data"]["searchOffer"]["items"]:
            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.base_url, offer["url"]),
                title = self.category_to_string(offer["category"]) + ", " + str(offer["area"]["main"]) + " m²",
                location = offer["location"]["address"],
                price = offer["price"]["total"],
                image_url = urljoin(self.base_url, "/static/images/" + (offer["photos"]["main"] or ""))
            ))

        return items
