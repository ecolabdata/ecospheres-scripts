import requests
from urllib.parse import urlparse

from minicli import cli, run

from ecospheres.api import DatagouvfrAPI


@cli
def feed_from_grist(topic_id: str, grist_url: str, table_id: int = 1, url_field_name: str = "URL", env: str = "demo"):
    """
    Feeds a universe from Grist, i.e. adds datasets to the universe topic.

    TODO: create topics from themes/tags and link datasets to them.

    :topic_id:          id of the universe topic
    :grist_url:         https://grist.numerique.gouv.fr/o/fabriquegeocommuns/api/docs/8AxUVpkJACtwE1sVULHn9F
    :table_id:          id of the table in the grist doc
    :url_field_name:    name of the field containing the dataset URL
    :env:               demo or prod
    """
    api = DatagouvfrAPI(env=env)
    grist_api_url = f"{grist_url}/tables/{table_id}/records"
    r = requests.get(grist_api_url)
    r.raise_for_status()
    data = r.json()
    to_add = set()
    for record in data["records"]:
        dataset_url = record["fields"]["URL"]
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
        to_add.add(dataset_id)

    if to_add:
        api.add_datasets_to_topic(topic_id, list(to_add))
        print(f"Added {len(to_add)} datasets to topic {topic_id}.")
    else:
        print("No datasets to add.")


if __name__ == "__main__":
    run()
