from typing import TypedDict

from ecospheres.api import DatagouvfrAPI


class Rel(TypedDict):
    href: str


def iter_rel(rel: Rel, api: DatagouvfrAPI):
    current_url = rel["href"]
    while current_url is not None:
        payload = api.get(current_url)
        current_url = payload["next_page"]
        for d in payload["data"]:
            yield d
