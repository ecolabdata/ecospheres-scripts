import json

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI
from ecospheres.config import get_page_config
from ecospheres.rel import iter_rel


@cli
def fix_group_migration(slug: str = "", dry_run: bool = False, env: str = "demo", site: str = "ecospheres", page: str = "bouquets"):
    """
    Fix group values in Topic elements after migration:
    - Convert group: null -> remove the property (undefined)
    - Convert group: "Sans regroupement" -> remove the property (undefined)
    - Keep valid group names as-is

    Should work for all sites, given the correct conf.
    """
    config = get_page_config(site, env, page)
    api = DatagouvfrAPI(config.base_url)
    topics = api.get_topics(config.universe_query["tag"])
    topics = [t for t in topics if t["slug"] == slug] if slug else topics

    fixed_count = 0
    total_topics = len(topics)

    for topic in topics:
        print(f"--> Handling {topic['slug']}...")

        elements = list(iter_rel(topic["elements"], api))
        elements_fixed = False
        updated_elements = []

        for element in elements:
            site_extras = element.get("extras", {}).get(site, {})
            if not site_extras:
                continue

            group_value = site_extras.get("group", False)

            # Check if group needs fixing
            if group_value is None or group_value == "Sans regroupement":
                print(f"  Fixing element '{element.get('title', 'Untitled')}': group={repr(group_value)} -> undefined")
                elements_fixed = True
                # Remove the group property entirely (equivalent to undefined in JS)
                if "group" in element["extras"][site]:
                    del element["extras"][site]["group"]
            updated_elements.append(element)

        if elements_fixed:
            fixed_count += 1
            payload = {
                "tags": topic["tags"],
                "elements": updated_elements,
            }

            if not dry_run:
                api.put(f"/api/2/topics/{topic['id']}/", json=payload)
            else:
                print("Would have updated with:")
                print(json.dumps(payload, indent=2))
        else:
            print(f"No fixes needed for {topic['id']}")

    print(f"Fixed {fixed_count}/{total_topics} topics")


if __name__ == "__main__":
    run()
