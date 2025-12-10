import asyncio
from io import BytesIO

from aiohttp import ClientSession
from imagehash import ImageHash, average_hash
from PIL import Image

from config import config
from scrapers.rental_offer import RentalOffer


async def _get_hash(
    session: ClientSession, offer: RentalOffer
) -> tuple[RentalOffer, ImageHash | None]:
    if not offer.image_url:
        return offer, None

    async with session.get(offer.image_url) as response:
        if response.status > 299:
            return offer, None

        data = BytesIO(await response.content.read())
        image = Image.open(data)
        return offer, average_hash(image)


async def deduplicate_offers(offers: list[RentalOffer]) -> list[RentalOffer]:
    hashes: list[tuple[RentalOffer, ImageHash | None]] = []
    deduplicated: list[tuple[RentalOffer, ImageHash | None]] = []

    async with ClientSession() as session:
        hashes = await asyncio.gather(*[_get_hash(session, offer) for offer in offers])

    for offer, photo_hash in hashes:
        matched = False

        for existing_offer, existing_hash in deduplicated:
            if (
                existing_hash
                and photo_hash
                and existing_hash - photo_hash < config.image_deduplication_threshold
            ):
                existing_offer.duplicate_offers.append(offer)
                matched = True

        if not matched:
            deduplicated.append((offer, photo_hash))

    return [o for o, _ in deduplicated]


def _filter_offer(offer: RentalOffer) -> bool:
    if config.min_price and offer.price < config.min_price:
        return False

    if config.max_price and offer.price > config.max_price:
        return False

    return True


def filter_offers(offers: list[RentalOffer]) -> list[RentalOffer]:
    return [offer for offer in offers if _filter_offer(offer)]
