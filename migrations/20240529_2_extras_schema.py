"""
Remove legacy extras' schema data prior after migration
Depends on `20240529_1_extras_schema`
"""
import json

from minicli import cli, run

from api import DatagouvfrAPI


api = DatagouvfrAPI()


@cli
def migrate(slug: str = "", dry_run: bool = False):
    bouquets = api.get_bouquets()
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")
        if not all([
            i in bouquet["extras"].get("ecospheres", {})
            for i in ["datasets_properties", "theme", "subtheme"]
        ]):
            raise ValueError("Bouquet not migrated")
        payload = bouquet["extras"]
        payload.pop("ecospheres:datasets_properties")
        payload.pop("ecospheres:informations")
        if not dry_run:
            api.put(f"/api/1/topics/{bouquet['id']}/", data=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
