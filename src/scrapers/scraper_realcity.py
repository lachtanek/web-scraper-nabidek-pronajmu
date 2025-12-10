import json
import re
from urllib.parse import quote_plus

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase


class ScraperRealcity(ScraperBase):
    name = "REALCITY"
    logo_url = "https://files.janchaloupka.cz/realcity.png"
    color = 0xB60D1C

    disposition_mapping = {
        Disposition.FLAT_1KK: "1+kk",
        Disposition.FLAT_1: "1+1",
        Disposition.FLAT_2KK: "2+kk",
        Disposition.FLAT_2: "2+1",
        Disposition.FLAT_3KK: "3+kk",
        Disposition.FLAT_3: "3+1",
        Disposition.FLAT_4KK: "4+kk",
        Disposition.FLAT_4: ("4+1", "4+2"),
        Disposition.FLAT_5_UP: ("5+kk", "5+1", "5+2", "6+kk", "6+1", "disp_more"),
        Disposition.FLAT_OTHERS: ("atyp", "disp_nospec"),
    }

    def _get_filters(self) -> str:
        filters = {
            "locality": [68],
            "transactionTypes": ["rent"],
            "propertyTypes": [
                {
                    "propertyType": "flat",
                    "options": {"disposition": self.get_dispositions_data()},
                },
            ],
        }
        return quote_plus(json.dumps(filters))

    async def get_latest_offers(self, session: ClientSession) -> list[RentalOffer]:
        url = f"https://www.realcity.cz/pronajem-bytu/brno-mesto-68/?sp={self._get_filters()}"

        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")

        items: list[RentalOffer] = []

        for item in soup.select("#rc-advertise-result .media.advertise.item"):
            image = item.find("div", "pull-left image")
            body = item.find("div", "media-body")

            items.append(
                RentalOffer(
                    scraper=self,
                    link="https://www.realcity.cz"
                    + body.find("div", "title").a.get("href"),
                    title=body.find("div", "title").a.get_text() or "Chybí titulek",
                    location=body.find("div", "address").get_text().strip()
                    or "Chybí adresa",
                    price=re.sub(
                        r"\D+", "", body.find("div", "price").get_text() or "0"
                    ),
                    image_url="https:" + image.img.get("src"),
                )
            )

        return items
