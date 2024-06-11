import os

import requests


class DatagouvfrAPI:

    def __init__(self, base_url: str | None = None, es_tag: str | None = None):
        if not (
            base_url := base_url or os.getenv("DATAGOUVFR_URL")
        ) or not (
            api_key := os.getenv("DATAGOUVFR_API_KEY")
        ) or not (
            es_tag := os.getenv("ECOSPHERES_TAG")
        ):
            raise Exception("Missing env var(s).")
        self.base_url: str = base_url
        self.api_key: str = api_key
        self.es_tag: str = es_tag

    @property
    def headers(self):
        return {"x-api-key": self.api_key}

    def url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _get(self, endpoint: str, **kwargs):
        return requests.get(self.url(endpoint), **kwargs)

    def get(self, endpoint: str, **kwargs) -> dict:
        r = self._get(endpoint, **kwargs)
        r.raise_for_status()
        return r.json()

    def put(self, endpoint: str, **kwargs) -> dict:
        r = requests.put(self.url(endpoint), headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.json()

    def post(self, endpoint: str, **kwargs) -> dict:
        r = requests.post(self.url(endpoint), headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.json()

    def get_bouquet(self, bouquet_id_or_slug: str) -> dict:
        return self.get(f"/api/2/topics/{bouquet_id_or_slug}")

    def get_bouquets(self) -> list:
        r = self.get(
            "/api/2/topics",
            params={"include_private": "yes", "tag": self.es_tag, "page_size": 100},
        )
        return r["data"]
