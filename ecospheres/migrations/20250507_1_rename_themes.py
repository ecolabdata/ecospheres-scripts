import json

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI

TAG_PREFIX = "ecospheres-theme"

THEMES = [
    # old, new
    ("consommer", "mieux-consommer"),
    ("produire", "mieux-produire"),
    ("preserver", "mieux-preserver-valoriser-ecosystemes"),
    ("se-deplacer", "mieux-se-deplacer"),
    ("se-loger", "mieux-se-loger"),
    ("se-nourrir", "mieux-se-nourrir"),
    ("chantiers-transverses", "autre"),
]


def compute_tag(radical: str):
    return f"{TAG_PREFIX}-{radical}"


def migrate_tags(tags: list[str], move: bool = False) -> set[str]:
    tag_mapping = {compute_tag(old): compute_tag(new) for old, new in THEMES}
    new_tags = set()
    for tag in tags:
        if tag in tag_mapping:
            new_tags.add(tag_mapping[tag])
            if not move:
                new_tags.add(tag)
        else:
            new_tags.add(tag)
    return new_tags


@cli
def migrate_bouquets(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "demo"):
    """
    Rename "theme" tags on bouquets.
    """
    api = DatagouvfrAPI(env)
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")
        tags = list(migrate_tags(bouquet["tags"], move=move))
        payload = {"tags": tags}
        if not dry_run:
            api.put(f"/api/1/topics/{bouquet['id']}/", json=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
