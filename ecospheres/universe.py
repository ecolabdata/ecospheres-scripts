import requests
from urllib.parse import urlparse

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI


@cli
def feed_from_grist(
    universe_topic_id: str,
    grist_url: str,
    universe_tag: str = "accessibilite-datagouvfr",
    datasets_table_id: int = 1,
    datasets_url_field: str = "URL",
    datasets_topic_field: str = "Bouquets",
    external_datasets_table_id: int = 2,
    topics_table_id: int = 4,
    topics_name_field: str = "Nom_du_bouquet",
    topics_description_field: str = "Description",
    env: str = "demo"
):
    """
    Feeds a universe from Grist, i.e. adds datasets to the universe topic.

    TODO: create topics from themes/tags and link datasets to them.

    :universe_topic_id: id of the universe topic
    :grist_url:         https://grist.numerique.gouv.fr/o/fabriquegeocommuns/api/docs/8AxUVpkJACtwE1sVULHn9F
    :table_id:          id of the table in the grist doc
    :url_field_name:    name of the field containing the dataset URL
    :topic_field_name:  name of the field containing the topic (bouquet) name
    :env:               demo or prod
    """
    api = DatagouvfrAPI(env=env)
    api.es_tag = universe_tag

    grist_base_api_url = f"{grist_url}/tables"

    # topics records
    r = requests.get(f"{grist_base_api_url}/{topics_table_id}/records")
    r.raise_for_status()
    data = r.json()
    topics = {}
    for record in data["records"]:
        if record["fields"].get("Bouquet_a_publier", None) is False:
            continue
        topics[record["fields"]["Identifiant"]] = {
            "grist_id": record["id"],
            "name": record["fields"][topics_name_field],
            "description": record["fields"][topics_description_field],
            "datasets": []
        }

    # external datasets records
    r = requests.get(f"{grist_base_api_url}/{external_datasets_table_id}/records")
    r.raise_for_status()
    data = r.json()
    for record in data["records"]:
        for topic_id in [r for r in record["fields"]["Bouquet"] or [] if isinstance(r, int)]:
            topic = next((t for t in topics.values() if t["grist_id"] == topic_id), None)
            if topic:
                topic["datasets"].append({
                    "id": None,
                    "title": record["fields"]["Nom_du_dataset"],
                    "purpose": f"Source externe pour '{record['fields']['Nom_du_dataset']}'",
                    "availability": "url available",
                    "uri": record["fields"]["URL"],
                })

    # datasets records
    r = requests.get(f"{grist_base_api_url}/{datasets_table_id}/records")
    r.raise_for_status()
    data = r.json()
    datasets_to_add = set()
    for record in data["records"]:
        dataset_url = record["fields"][datasets_url_field]
        if not dataset_url:
           continue
        parsed_url = urlparse(dataset_url)
        if "data.gouv.fr" not in parsed_url.netloc:
            print(f"Skipping {dataset_url} (not a data.gouv.fr URL).")
            continue
        slug_or_id = parsed_url.path.split("/")[-1] or parsed_url.path.split("/")[-2]
        # try to find the dataset on the target env
        r = requests.get(f"{api.base_url}/api/2/datasets/{slug_or_id}/")
        if r.status_code == 404:
            print(f"Dataset '{slug_or_id}' not found on {env}")
            continue
        dataset = r.json()
        dataset_id = dataset["id"]
        datasets_to_add.add(dataset_id)

        # add the dataset to the topic(s)
        for topic_grist_id in [r for r in record["fields"][datasets_topic_field] or [] if isinstance(r, int)]:
            topic = next((t for t in topics.values() if t["grist_id"] == topic_grist_id), None)
            if topic:
                topic["datasets"].append({
                    "id": dataset["id"],
                    "availability": "available",
                    "purpose": f"Jeu de données '{dataset['title']}' sur data.gouv.fr.",
                    "title": dataset["title"],
                    "uri": f"/datasets/{dataset['id']}",
                })

    # add the datasets to the universe topic
    if datasets_to_add:
        api.add_datasets_to_topic(universe_topic_id, list(datasets_to_add))
        print(f"Added {len(datasets_to_add)} datasets to universe topic {universe_topic_id}.")
    else:
        print("No datasets to add.")

    # create topics (bouquet) and add datasets to them
    existing_topics = api.get_bouquets()
    for topic_id, topic_info in topics.items():
        # FIXME: handle theme
        if existing_topic := next(
            (t for t in existing_topics
                if topic_id == t["extras"].get("accessibilite", {}).get("internal_topic_id")
            ), None
        ):
            api.update_bouquet(
                existing_topic["id"],
                topic_info["name"],
                topic_info["description"],
                topic_info["datasets"],
                tags=existing_topic["tags"],
                extras_key="accessibilite",
                extras={"internal_topic_id": topic_id},
                organization="682c7a7b66325bae33e6ce25",
            )
            print(f"Updated topic '{topic_id}' and added {len(topic_info['datasets'])} datasets.")
        else:
            api.create_bouquet(
                topic_info["name"],
                topic_info["description"],
                topic_info["datasets"],
                tags=[],
                extras_key="accessibilite",
                extras={"internal_topic_id": topic_id},
                organization="682c7a7b66325bae33e6ce25",
            )
            print(f"Created topic '{topic_id}' and added {len(topic_info['datasets'])} datasets.")


if __name__ == "__main__":
    run()
