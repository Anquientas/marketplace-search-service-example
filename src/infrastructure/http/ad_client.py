import logging

import httpx

from src.application.ports.ad_source import AdSnapshot, AdSource

logger = logging.getLogger(__name__)


class AdServiceAdSource(AdSource):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        if "://" not in base_url:
            base_url = "http://" + base_url
        self._base_url = base_url.rstrip("/")

    async def get(self, ad_id: int) -> AdSnapshot | None:
        url = f"{self._base_url}/internal/ads/{ad_id}"
        try:
            resp = await self._client.get(url)
        except httpx.HTTPError as exc:
            logger.warning("failed to fetch ad %s: %s", ad_id, exc)
            return None
        if resp.status_code != 200:
            return None
        data = resp.json()
        return AdSnapshot(
            ad_id=data["id"],
            title=data["title"],
            description=data["description"],
            price=data["price"],
            category=data["category"],
            city=data["city"],
            status=data["status"],
        )
