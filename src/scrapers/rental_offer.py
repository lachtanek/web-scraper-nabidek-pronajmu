from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scraper_base import ScraperBase


@dataclass
class RentalOffer:
    """Nabídka pronájmu bytu"""

    link: str
    """URL adresa na nabídku"""

    title: str
    """Popis nabídky (nejčastěji počet pokojů, výměra)"""

    location: str
    """Lokace bytu (městská část, ulice)"""

    price: int | str
    """Cena pronájmu za měsíc bez poplatků a energií"""

    image_url: str
    """Náhledový obrázek nabídky"""

    scraper: "ScraperBase"
    """Odkaz na instanci srapera, ze kterého tato nabídka pochází"""

    duplicate_offers: list["RentalOffer"] = field(default_factory=list)
