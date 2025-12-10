import asyncio
import logging
import traceback

from aiohttp import ClientSession

from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase
from scrapers.scraper_bravis import ScraperBravis
from scrapers.scraper_euro_bydleni import ScraperEuroBydleni
from scrapers.scraper_idnes_reality import ScraperIdnesReality
from scrapers.scraper_realcity import ScraperRealcity
from scrapers.scraper_realingo import ScraperRealingo
from scrapers.scraper_remax import ScraperRemax
from scrapers.scraper_sreality import ScraperSreality
from scrapers.scraper_ulov_domov import ScraperUlovDomov
from scrapers.scraper_bezrealitky import ScraperBezrealitky
from utils import flatten


def create_scrapers(dispositions: Disposition) -> list[ScraperBase]:
    return [
        ScraperBravis(dispositions),
        ScraperEuroBydleni(dispositions),
        ScraperIdnesReality(dispositions),
        ScraperRealcity(dispositions),
        ScraperRealingo(dispositions),
        ScraperRemax(dispositions),
        ScraperSreality(dispositions),
        ScraperUlovDomov(dispositions),
        ScraperBezrealitky(dispositions),
    ]


async def _fetch_offers(
    session: ClientSession, scraper: ScraperBase
) -> list[RentalOffer]:
    try:
        data = await scraper.get_latest_offers(session)
        logging.info(f"Fetched {len(data)} offers from {scraper.name}")
        return data
    except Exception:
        logging.error(traceback.format_exc())


async def fetch_latest_offers(scrapers: list[ScraperBase]) -> list[RentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Returns:
        list[RentalOffer]: Seznam nabídek
    """

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent}

    async with ClientSession(headers=headers) as session:
        offers = await asyncio.gather(*[_fetch_offers(session, s) for s in scrapers])

    return list(flatten(offers))
