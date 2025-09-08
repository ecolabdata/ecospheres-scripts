import json

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI
from ecospheres.config import get_page_config


@cli
def migrate_bouquets(slug: str = "", dry_run: bool = False, move: bool = False, env: str = "demo", site: str = "ecospheres", page: str = "bouquets"):
    """
    Migrate bouquets from legacy extra structure to new elements structure in Topics.
    Should work for all sites, given the correct conf.
    """
    config = get_page_config(site, env, page)
    api = DatagouvfrAPI(config.base_url)
    bouquets = api.get_topics(config.universe_query["tag"])
    bouquets = [b for b in bouquets if b["slug"] == slug] if slug else bouquets
    for bouquet in bouquets:
        print(f"--> Handling {bouquet['slug']}...")

        site_extras = bouquet["extras"].get(site)
        if not site_extras:
            print("No extras for this site, skipping.")
            continue

        elements = []
        for factor in site_extras.get("datasets_properties"):
            element = {
                "title": factor["title"],
                "description": factor["purpose"],
                "tags": [],
                "extras": {
                    site: {
                        "uri": factor.get("uri"),
                        "group": factor.get("group"),
                        "availability": factor["availability"],
                    }
                }
            }
            # reference to data.gouv.fr dataset
            if factor["availability"] == "available":
                element["element"] = {"class": "Dataset", "id": factor["id"]}
            elements.append(element)

        payload = {
            "tags": bouquet["tags"],
            "elements": elements,
        }
        if move:
            payload["extras"] = {k: v for k, v in bouquet["extras"].items() if k != site}

        if not dry_run:
            api.put(f"/api/2/topics/{bouquet['id']}/", json=payload)
        else:
            print("Would have updated with:")
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
