#!/usr/bin/evn python3
import asyncio
import logging
import pdb

from config import config
from transformations import deduplicate_offers, filter_offers
from scrapers_manager import create_scrapers, fetch_latest_offers

scrapers = create_scrapers(config.dispositions)


async def test_fetch_all_offers():
    logging.info("Fetching offers")
    config.min_price = 10000
    config.max_price = 20000

    try:
        all_offers = await fetch_latest_offers(scrapers)
        filtered = filter_offers(all_offers)
        deduplicated = await deduplicate_offers(filtered)
    except Exception:
        pdb.post_mortem()
        raise SystemExit()

    logging.info(
        f"Offers fetched (all: {len(all_offers)}, "
        f"filtered: {len(filtered)}, deduplicated: {len(deduplicated)})"
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=(logging.DEBUG if config.debug else logging.INFO),
        format="%(asctime)s - [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    asyncio.run(test_fetch_all_offers())
