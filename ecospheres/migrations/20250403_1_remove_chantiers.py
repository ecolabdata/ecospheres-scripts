import json

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI

TAG_PREFIX = "ecospheres-subtheme"


@cli
def migrate_bouquets(slug: str = "", dry_run: bool = False, env: str = "demo"):
    """
    Remove "chantier" tags from bouquets.
    """
    api = DatagouvfrAPI(env)
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")
        if not any(t.startswith(TAG_PREFIX) for t in bouquet["tags"]):
            print("No chantier tag to remove, skipping.")
            continue
        tags = [t for t in bouquet["tags"] if not t.startswith(TAG_PREFIX)]

        payload = {"tags": tags}
        if not dry_run:
            api.put(f"/api/1/topics/{bouquet['id']}/", json=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
