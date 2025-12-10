from typing import Any

from aiohttp import ClientSession

from config import config
from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase


class ScraperUlovDomov(ScraperBase):
    name = "UlovDomov"
    logo_url = "https://www.ulovdomov.cz/favicon.png"
    color = 0xFFFFFF
    base_url = (
        "https://ud.api.ulovdomov.cz/v1/offer/find?page=1&perPage=20&sorting=latest"
    )

    disposition_mapping = {
        Disposition.FLAT_1KK: "onePlusKk",
        Disposition.FLAT_1: "onePlusOne",
        Disposition.FLAT_2KK: "twoPlusKk",
        Disposition.FLAT_2: "twoPlusOne",
        Disposition.FLAT_3KK: "threePlusKk",
        Disposition.FLAT_3: "threePlusOne",
        Disposition.FLAT_4KK: "fourPlusKk",
        Disposition.FLAT_4: "fourPlusOne",
        Disposition.FLAT_5_UP: ("fivePlusKk", "fivePlusOne", "sixAndMore"),
        Disposition.FLAT_OTHERS: "atypical",
    }

    def disposition_id_to_string(self, id: str) -> str:
        return {
            "onePlusKk": "1+kk",
            "onePlusOne": "1+1",
            "twoPlusKk": "2+kk",
            "twoPlusOne": "2+1",
            "threePlusKk": "3+kk",
            "threePlusOne": "3+1",
            "fourPlusKk": "4+kk",
            "fourPlusOne": "4+1",
            "fivePlusKk": "5+kk",
            "fivePlusOne": "5+1",
            "sixAndMore": "6+",
            "atypical": "Atypický",
        }.get(id, "")

    def _get_data(self) -> dict[str, Any]:
        price_cfg = {}
        if config.min_price:
            price_cfg["min"] = config.min_price
        if config.max_price:
            price_cfg["max"] = config.max_price

        return {
            "bounds": {
                "northEast": {"lat": 49.294485, "lng": 16.7278532},
                "southWest": {"lat": 49.1096552, "lng": 16.4280678},
            },
            "offerType": "rent",
            "propertyType": "flat",
            "disposition": self.get_dispositions_data(),
            "price": {"min": 10000, "max": 20000},
        }

    async def get_latest_offers(self, session: ClientSession) -> list[RentalOffer]:
        async with session.post(self.base_url, json=self._get_data()) as response:
            data = await response.json()

        items: list[RentalOffer] = []
        for offer in data["data"]["offers"]:
            location = offer["village"]["title"]
            if offer["street"] is not None:
                location = offer["street"]["title"] + ", " + location
            if offer["villagePart"] is not None:  # Městská část
                location += " - " + offer["villagePart"]["title"]

            disposition_str = self.disposition_id_to_string(offer["disposition"])
            items.append(
                RentalOffer(
                    scraper=self,
                    link=offer["absoluteUrl"],
                    # TODO "Pronájem" podle ID?
                    title=f"Pronájem {disposition_str} {offer['area']} m²",
                    location=location,
                    price=offer["rentalPrice"]["value"],
                    image_url=offer["photos"][0]["path"],
                )
            )

        return items
