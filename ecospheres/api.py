import os

import requests

from ecospheres.config import get_config


class DatagouvfrAPI:

    def __init__(self, env: str | None = None, url: str | None = None, authenticated: bool = True):
        self.api_key: str | None = None
        if authenticated:
            if not (api_key := os.getenv("DATAGOUVFR_API_KEY")):
                raise Exception("Missing env var DATAGOUVFR_API_KEY.")
            self.api_key = api_key

        if env:
            self.config = get_config(env)
            self.base_url: str = self.config["datagouvfr"]["base_url"]
            if self.config["pages"]["bouquets"]["universe_query"]:
                self.es_tag: str = self.config["pages"]["bouquets"]["universe_query"]["tag"]
            else:
                # FIXME: legacy format, remove when migrated
                self.es_tag: str = self.config["universe"]["name"]
            self.universe_topic_id = self.config["pages"]["datasets"]["universe_query"]["topic"]
        if url:
            self.base_url = url

        if not self.base_url:
            raise Exception("Missing base_url config.")

        print(f"API ready for {self.base_url}")

    @property
    def headers(self):
        return {"x-api-key": self.api_key} if self.api_key else {}

    def url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _get(self, endpoint: str, **kwargs):
        return requests.get(self.url(endpoint), **kwargs)

    def get(self, endpoint: str, **kwargs) -> dict:
        r = self._get(endpoint, **kwargs, headers=self.headers)
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
        LIMIT = 100
        r = self.get(
            "/api/2/topics",
            params={"include_private": "yes", "tag": self.es_tag, "page_size": LIMIT},
        )
        data = r["data"]
        assert len(data) < LIMIT, "Too many bouquets"
        return [topic for topic in data if topic["id"] != self.universe_topic_id]
