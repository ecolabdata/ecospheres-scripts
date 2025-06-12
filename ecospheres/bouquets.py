import requests

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI
from ecospheres.config import get_page_config
from ecospheres.rel import iter_rel


@cli
def copy(slug: str, source: str = "prod", destination: str = "demo", site: str = "ecospheres", page: str = "bouquets"):
    """
    Copy a bouquet from one env to another
    """
    print(f"Copying from {source} to {destination}")

    config_source = get_page_config(site, source, page)
    config_destination = get_page_config(site, destination, page)

    api_source = DatagouvfrAPI(config_source.base_url, authenticated=False)
    api_destination = DatagouvfrAPI(config_source.base_url)

    source_data = api_source.get_topic(slug)

    existing_id = None
    try:
        r = api_destination.get_topic(slug)
        confirm = input(f"{slug} already exists on {destination}, y to replace: ")
        if confirm.lower() != "y":
            return
        existing_id = r["id"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            pass
        else:
            raise e

    destination_data = {}
    destination_data["tags"] = [config_destination.universe_query["tag"], *source_data["tags"]]
    destination_data["name"] = source_data["name"]
    destination_data["description"] = source_data["description"]
    destination_data["spatial"] = source_data["spatial"]
    destination_data["private"] = source_data["private"]

    if source_data["owner"]:
        r = api_destination._get(f"/api/1/users/{source_data['owner']['id']}/")
        if r.ok:
            destination_data["owner"] = source_data["owner"]
        else:
            print(f"Owner does not exist on {destination}")
    elif source_data["organization"]:
        r = api_destination._get(f"/api/1/organization/{source_data['organization']['id']}/")
        if r.ok:
            destination_data["organization"] = source_data["organization"]
        else:
            print(f"Organization does not exist on {destination}")

    existing_elements = iter_rel(source_data["elements"], api_source)

    destination_data["elements"] = []
    for element in existing_elements:
        if element_object := element.get("element"):
            r = api_destination._get(f"/api/2/datasets/{element_object['id']}/")
            if not r.ok:
                print(f"{element_object['id']} not on {destination}, transforming to URL")
                element["extras"] = {
                    site: {
                        "uri": f"{config_source.base_url}/datasets/{element_object['id']}/",
                        "group": element["extras"][site].get("group"),
                        "availability": "url available",
                    },
                    **element["extras"],
                }
        destination_data["elements"].append(element)

    if existing_id:
        r = api_destination.put(f"/api/2/topics/{existing_id}/", json=destination_data)
    else:
        r = api_destination.post("/api/2/topics/", json=destination_data)

    print(f"Bouquet copied at {r['slug']}")


if __name__ == "__main__":
    run()
