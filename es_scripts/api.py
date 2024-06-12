import os

import requests

from es_scripts.config import get_config


class DatagouvfrAPI:

    def __init__(self, env: str):
        if not (api_key := os.getenv("DATAGOUVFR_API_KEY")):
            raise Exception("Missing env var DATAGOUVFR_API_KEY.")
        self.api_key: str = api_key

        self.config = get_config(env)
        self.base_url: str = self.config["datagouvfr"]["base_url"]
        self.es_tag: str = self.config["universe"]["name"]

        print(f"API ready for {env}")

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
