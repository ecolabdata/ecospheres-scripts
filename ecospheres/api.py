import os

import requests

class DatagouvfrAPI:

    def __init__(self, url: str, authenticated: bool = True):
        self.api_key: str | None = None
        if authenticated:
            if not (api_key := os.getenv("DATAGOUVFR_API_KEY")):
                raise Exception("Missing env var DATAGOUVFR_API_KEY.")
            self.api_key = api_key
        self.base_url: str = url
        print(f"API ready for {self.base_url}")

    @property
    def headers(self):
        return {"x-api-key": self.api_key} if self.api_key else {}

    def url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _get(self, endpoint: str, **kwargs):
        return requests.get(endpoint if "://" in endpoint else self.url(endpoint), **kwargs)

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

    def get_topic(self, topic_id_or_slug: str) -> dict:
        return self.get(f"/api/2/topics/{topic_id_or_slug}")

    def get_topics(self, universe_tag: str, include_private: bool = True) -> list:
        LIMIT = 100
        params = {"tag": universe_tag, "page_size": LIMIT}
        if include_private:
            params["include_private"] = "yes"
        r = self.get(
            "/api/2/topics",
            params=params,
        )
        data = r["data"]
        assert len(data) < LIMIT, "Too many topics"
        return data
