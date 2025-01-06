"""
Copies or move themes/subthemes from extras to slugified tags
Idempotent when using move=False
"""
import json

from minicli import cli, run
from slugify import slugify
from typing import Literal

from ecospheres.api import DatagouvfrAPI


def compute_slug(value: str, prefix: Literal["theme", "subtheme"]) -> str:
    return slugify(f"ecospheres-{prefix}-{value.lower()}")


@cli
def migrate(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "demo"):
    api = DatagouvfrAPI(env)
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")
        original_theme = bouquet["extras"]["ecospheres"]["theme"]
        original_subtheme = bouquet["extras"]["ecospheres"]["subtheme"]
        if not original_theme or not original_subtheme:
            print("No theme or subtheme to migrate, skipping.")
            continue
        theme = compute_slug(original_theme, "theme")
        subtheme = compute_slug(original_subtheme, "subtheme")
        tags = [
            *[t for t in bouquet["tags"] if compute_slug("", "theme") not in t and compute_slug("", "subtheme") not in t],
            theme,
            subtheme,
        ]
        payload = {"tags": tags}
        if move:
            payload["extras"] = bouquet["extras"]
            payload["extras"]["ecospheres"].pop("theme", None)
            payload["extras"]["ecospheres"].pop("subtheme", None)
        if not dry_run:
            api.put(f"/api/1/topics/{bouquet['id']}/", json=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
