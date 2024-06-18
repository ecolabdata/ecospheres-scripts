import requests

from minicli import cli, run

from es_scripts.api import DatagouvfrAPI


@cli
def copy(slug: str, source: str = "prod", destination: str = "demo"):
    """
    Copy a bouquet from one env to another
    """
    print(f"Copying from {source} to {destination}")

    api_source = DatagouvfrAPI(source)
    api_destination = DatagouvfrAPI(destination)

    config_source = api_source.config
    config_destination = api_destination.config

    source_data = api_source.get_bouquet(slug)

    existing_id = None
    try:
        r = api_destination.get_bouquet(slug)
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
    destination_data["tags"] = [config_destination["universe"]["name"]]
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
    elif source_data["owner"]:
        r = api_destination._get(f"/api/1/organization/{source_data['organization']['id']}/")
        if r.ok:
            destination_data["organization"] = source_data["organization"]
        else:
            print(f"Organization does not exist on {destination}")

    destination_data["datasets"] = []
    destination_data["extras"] = {}
    destination_data["extras"]["ecospheres:informations"] = source_data["extras"][
        "ecospheres:informations"
    ]
    destination_data["extras"]["ecospheres:datasets_properties"] = []
    for d in source_data["extras"]["ecospheres:datasets_properties"]:
        if d["id"]:
            r = api_destination._get(f"/api/1/datasets/{d['id']}/")
            if not r.ok:
                print(f"{d['id']} not on {destination}, transforming to URL")
                d["id"] = None
                d["availability"] = "url available"
                d["uri"] = f"{config_source['datagouvfr']['base_url']}{d['uri']}"
            else:
                destination_data["datasets"].append(d["id"])
        destination_data["extras"]["ecospheres:datasets_properties"].append(d)

    if existing_id:
        r = api_destination.put(f"/api/1/topics/{existing_id}/", json=destination_data)
    else:
        r = api_destination.post("/api/1/topics/", json=destination_data)

    print(f"Bouquet copied at {r['slug']}")


if __name__ == "__main__":
    run()
