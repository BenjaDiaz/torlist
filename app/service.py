import logging
from typing import List

import requests

from app.db import database, whitelisted_ips
from app.models import IPAddress


logger = logging.getLogger(__name__)


class TorIpService:
    def __init__(self, cache) -> None:
        self.cache = cache

    async def get_ips(self) -> List[str]:
        logger.info("Getting Tor ips from dan.me.uk ...")
        res = requests.get("https://www.dan.me.uk/torlist/")
        ips = []
        if res.status_code == 200:
            for line in res.iter_lines():
                ips.append(line.decode().rstrip())
        else:
            if res.status_code == 403:
                logger.info(
                    "Hit the 30min rate limit on dan.me.uk/torlist. Using cache."
                )
            else:
                logger.error(
                    f"Error getting Tor ips from dan.me.uk/torlist\n {res.status_code} - {res.text}. Using cache."
                )
            ips = await self.cache.get("ips", default=[])
        logger.info("Getting Tor ips from torstatus.rueckgr.at ...")
        res = requests.get(
            "https://torstatus.rueckgr.at/ip_list_all.php/Tor_ip_list_ALL.csv"
        )
        if res.status_code == 200:
            for line in res.iter_lines():
                if line.rstrip() not in ips:
                    # Needs .decode() because if we keep it in bytes it generates duplicates in the final response (due to set(ips) considering "1.1.1.1" != b"1.1.1.1")
                    ips.append(line.decode().rstrip())
        else:
            logger.error(
                f"Error getting Tor ips from torstatus.rueckgr.at\n {res.status_code} - {res.text}."
            )
        unique_ips = list(set(ips))
        logger.info(f"Got {len(unique_ips)} unique ips")
        return unique_ips

    async def save_whitelist_ip(self, ip_address: IPAddress):
        query = whitelisted_ips.insert().values(ip=ip_address.ip)
        last_record_id = await database.execute(query)
        return last_record_id

    async def get_whitelisted_ips(self):
        query = whitelisted_ips.select()
        return await database.fetch_all(query)

