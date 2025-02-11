import json

from pathlib import Path

import yaml

from minicli import cli, run
from slugify import slugify
from typing import Literal

from ecospheres.api import DatagouvfrAPI


FilterTypes = Literal["theme", "chantier"]


def compute_tag(value: str, prefix: FilterTypes) -> str:
    return slugify(f"ecospheres-{prefix}-{value.lower()}")


def find_slug(
    filter: FilterTypes,
    value: str,
    themes_files: Path = Path("ecospheres/migrations/data/themes_new.yaml")
) -> str | None:
    with themes_files.open() as f:
        filters = yaml.safe_load(f)["topics"]["filters"]

    try:
        values = next(f for f in filters if f["id"] == filter)["values"]
        filter_value = next(v for v in values if v["name"] == value)
        return filter_value["id"]
    except StopIteration:
        print(f"No slug found for {filter} / '{value}', skipping.")
        return None


@cli
def migrate_bouquets(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "demo"):
    """
    Copies or move themes/subthemes from extras to slugified tags.
    Idempotent when using `move=False`.
    """
    api = DatagouvfrAPI(env)
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")
        original_theme = bouquet["extras"]["ecospheres"].get("theme")
        original_subtheme = bouquet["extras"]["ecospheres"].get("subtheme")
        if not original_theme or not original_subtheme:
            print("No theme or subtheme to migrate, skipping.")
            continue
        theme_slug = find_slug("theme", original_theme)
        subtheme_slug = find_slug("chantier", original_subtheme)
        if not theme_slug or not subtheme_slug:
            continue
        theme = compute_tag(theme_slug, "theme")
        subtheme = compute_tag(subtheme_slug, "chantier")
        tags = [
            *[t for t in bouquet["tags"] if compute_tag("", "theme") not in t and compute_tag("", "chantier") not in t],
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


@cli
def migrate_conf(
    input_file: Path = Path("ecospheres/migrations/data/themes_old.yaml"),
    output_file: Path = Path("ecospheres/migrations/data/themes_new.yaml"),
):
    with input_file.open() as f:
        data = yaml.safe_load(f)

    new_data = {
        "topics": {
            "global_tag_prefix": "ecospheres",
            "filters": [
                {
                    "name": "Thématique",
                    "id": "theme",
                    "child": "chantier",
                    "color": "noop",
                    "values": [],
                },
                {
                    "name": "Chantier",
                    "id": "chantier",
                    "color": "green-archipel",
                    "values": [],
                },
            ]
        }
    }

    for theme in data["themes"]:
        theme_slug = slugify(theme["name"]).lower()
        new_data["topics"]["filters"][0]["values"].append({
            "id": theme_slug,
            "name": theme["name"]
        })
        for subtheme in theme["subthemes"]:
            subtheme_slug = slugify(subtheme["name"]).lower()
            new_data["topics"]["filters"][1]["values"].append({
                "id": subtheme_slug,
                "name": subtheme["name"],
                "parent": theme_slug,
            })

    if output_file.exists():
        response = input(f"{output_file} already exists. Overwrite (y/n)? ")
        if response != "y":
            print("Aborting.")
            return

    with output_file.open("w") as f:
        yaml.safe_dump(new_data, f, allow_unicode=True, sort_keys=False)

    print(f"Done in {output_file}.")


if __name__ == "__main__":
    run()
