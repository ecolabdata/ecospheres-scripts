import json

from pathlib import Path

import yaml

from minicli import cli, run
from slugify import slugify
from typing import Literal

from ecospheres.api import DatagouvfrAPI

CATEGORIES = Path("ecospheres/migrations/data/defis/categories.yaml")


@cli
def migrate_defis(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "ecospheres/migrations/data/defis/env.yaml", clean_tags: bool = False):
    api = DatagouvfrAPI(env)

    with CATEGORIES.open() as f:
        categories = yaml.safe_load(f)

    universe_tag = api.es_tag

    for season, topics in categories.items():
        print("Handling season", season)
        for topic_link in topics:
            topic_slug = topic_link.split("/")[-1]
            print("Handling topic", topic_slug)
            topic = api.get_bouquet(topic_slug)
            original_theme = topic["extras"]["defis"].get("theme")
            original_subtheme = topic["extras"]["defis"].get("subtheme")
            if not original_theme or not original_subtheme:
                print("No theme or subtheme to migrate.")
            tags = [universe_tag, f"{universe_tag}-season-{season}", *topic["tags"]]
            payload = {"tags": tags}
            if move:
                payload["extras"] = topic["extras"]
                payload["extras"]["defis"].pop("theme", None)
                payload["extras"]["defis"].pop("subtheme", None)
                # fixup
                payload["extras"].pop("ecospheres", None)
            if not dry_run:
                api.put(f"/api/1/topics/{topic['id']}/", json=payload)
            else:
                print("Would have updated with:")
                print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
