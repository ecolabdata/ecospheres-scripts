import json

from pathlib import Path

import yaml

from minicli import cli, run
from slugify import slugify
from typing import Literal

from ecospheres.api import DatagouvfrAPI

OLD_THEMES = Path("ecospheres/migrations/data/logistique/themes_old.yaml")
NEW_THEMES = Path("ecospheres/migrations/data/logistique/themes_new.yaml")
SITE_PREFIX = "logistique"

FilterTypes = Literal["theme", "subtheme"]


def compute_tag(value: str, prefix: FilterTypes) -> str:
    return slugify(f"{SITE_PREFIX}-{prefix}-{value.lower()}")


def find_slug(
    filter: FilterTypes,
    value: str,
    themes_file: Path = NEW_THEMES
) -> str | None:
    with themes_file.open() as f:
        filters = yaml.safe_load(f)["filters"]["bouquets"]["items"]

    try:
        values = next(f for f in filters if f["id"] == filter)["values"]
        filter_value = next(v for v in values if v["name"] == value)
        return filter_value["id"]
    except StopIteration:
        print(f"No slug found for {filter} / '{value}', skipping.")
        return None


@cli
def migrate_bouquets(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "ecospheres/migrations/data/logistique/env.yaml", clean_tags: bool = False):
    """
    Copies or move themes/subthemes from extras to slugified tags.
    Idempotent when using `move=False`.
    """
    api = DatagouvfrAPI(env)
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")

        original_theme = bouquet["extras"][SITE_PREFIX].get("theme")
        original_subtheme = bouquet["extras"][SITE_PREFIX].get("subtheme")
        if not original_theme or not original_subtheme:
            print("No theme or subtheme to migrate, skipping.")
            continue
        theme_slug = find_slug("theme", original_theme)
        subtheme_slug = find_slug("subtheme", original_subtheme)
        if not theme_slug or not subtheme_slug:
            print(f"Warning: no theme or subtheme found on {bouquet['id']} for {original_theme}/{original_subtheme}, skipping.")
            continue
        theme = compute_tag(theme_slug, "theme")
        subtheme = compute_tag(subtheme_slug, "subtheme")
        if clean_tags:
            tags = [api.es_tag]
        else:
            excludes = [compute_tag("", "theme"), compute_tag("", "subtheme")]
            tags = *[t for t in bouquet["tags"] if not any(t.startswith(e) for e in excludes)],
        tags = [
            *tags,
            theme,
            subtheme,
        ]
        payload = {"tags": tags}
        if move:
            payload["extras"] = bouquet["extras"]
            payload["extras"][SITE_PREFIX].pop("theme", None)
            payload["extras"][SITE_PREFIX].pop("subtheme", None)
        if not dry_run:
            api.put(f"/api/1/topics/{bouquet['id']}/", json=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
