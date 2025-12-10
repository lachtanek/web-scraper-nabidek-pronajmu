from abc import abstractmethod
from typing import Any

from aiohttp import ClientSession

from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from utils import flatten


class ScraperBase:
    """Hlavní třída pro získávání aktuálních nabídek pronájmu bytů z různých služeb"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def logo_url(self) -> str:
        pass

    @property
    @abstractmethod
    def color(self) -> int:
        pass

    @property
    @abstractmethod
    def disposition_mapping(self) -> dict[Disposition, Any]:
        pass

    def __init__(self, disposition: Disposition) -> None:
        self.disposition = disposition

    def get_dispositions_data(self) -> list:
        return list(flatten([self.disposition_mapping[d] for d in self.disposition]))

    @abstractmethod
    async def get_latest_offers(self, session: ClientSession) -> list[RentalOffer]:
        """Načte a vrátí seznam nejnovějších nabídek bytů k pronájmu z dané služby

        Raises:
            NotImplementedError: Pokud potomek neimplementuje tuto metodu

        Returns:
            list[RentalOffer]: Seznam nabízených bytů k pronájmu
        """
        raise NotImplementedError("Fetching new results is not implemeneted")
