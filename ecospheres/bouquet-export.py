import csv

from collections.abc import Sequence, Mapping
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from minicli import cli, run
from pathlib import Path
from typing import Any, Optional

import requests

from ecospheres.api import DatagouvfrAPI


@dataclass
class Bouquet:
    bouquet_id: str
    bouquet_name: str
    bouquet_description: str | None
    bouquet_author_name: str
    bouquet_author_page: str
    bouquet_last_modified: datetime
    bouquet_spatial_coverage: str | None


@dataclass
class Factor:
    bouquet_id: str
    factor_id: str
    factor_index: int
    factor_group: str | None
    factor_availability: str
    factor_title: str
    factor_purpose: str
    dataset_url: str | None = None
    dataset_id: str | None = None
    dataset_title: str | None = None
    dataset_author_name: str | None = None
    dataset_author_page: str | None = None
    # dataset_responsible_parties: list[str] | None = None
    dataset_last_modified: datetime | None = None
    dataset_license: str | None = None
    # dataset_spatial_coverage:
    # dataset_temporal_coverage:
    # dataset_update_frequency:
    dataset_schema: str | None = None
    dataset_quality_score: float | None = None


@dataclass
class Resource:
    dataset_id: str
    resource_id: str
    resource_available: str | None
    resource_title: str
    resource_type: str
    resource_format: str
    resource_schema: str | None


def fieldnames(class_or_instance) -> list[str]:
    return [field.name for field in fields(class_or_instance)]


def maybe_get(payload: Mapping | Sequence, *path) -> Optional[Any]:
    for p in path:
        if not hasattr(payload, "__getitem__"):
            return None
        try:
            payload = payload[p]
        except (IndexError, KeyError):
            return None
        if not payload:
            return None
    return payload  # type: ignore


def get_author(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["organization"] or payload["owner"] or {}


def get_schema(payload: dict[str, Any]) -> str | None:
    schema = payload.get("schema")
    if not schema:
        return None
    label = schema.get("url") or schema.get("name")
    if not label:
        return None
    version = schema.get("version")
    return f"{label} (version {version})" if version else label


@cli("env", choices=["www", "demo"])
def export(id_or_slug: str, env: str = "www"):
    """Export a bouquet

    Will export the bouquet in directory `bouquet--{id_or_slug}`.

    :id_or_slug: Identifier or slug of the bouquet
    :env: Target data.gouv environment
    """
    api = DatagouvfrAPI(url=f"https://{env}.data.gouv.fr", authenticated=False)
    bouquet_payload = api.get_topic(id_or_slug)

    path = Path(f"bouquet--{id_or_slug}")
    path.mkdir(exist_ok=False)

    with (open(path.joinpath("bouquet.csv"), "w") as bouquet_file,
          open(path.joinpath("factors.csv"), mode="w") as factors_file,
          open(path.joinpath("resources.csv"), mode="w") as resources_file):
        bouquet_csv = csv.DictWriter(bouquet_file, fieldnames=fieldnames(Bouquet))
        factors_csv = csv.DictWriter(factors_file, fieldnames=fieldnames(Factor))
        resources_csv = csv.DictWriter(resources_file, fieldnames=fieldnames(Resource))

        bouquet_csv.writeheader()
        factors_csv.writeheader()
        resources_csv.writeheader()

        bouquet_author = get_author(bouquet_payload)
        bouquet = Bouquet(
            bouquet_id=bouquet_payload["id"],
            bouquet_name=bouquet_payload["name"],
            bouquet_description=bouquet_payload.get("description"),
            bouquet_author_name=bouquet_author["name"],
            bouquet_author_page=bouquet_author["page"],
            bouquet_last_modified=datetime.fromisoformat(bouquet_payload["last_modified"]),
            bouquet_spatial_coverage=maybe_get(bouquet_payload, "spatial", "zones", 0)
        )
        bouquet_csv.writerow(asdict(bouquet))

        elements = []
        elements_url = bouquet_payload["elements"]["href"]
        while elements_url:
            payload = requests.get(elements_url).json()
            elements.extend(payload["data"])
            elements_url = payload["next_page"]

        for factor_index, factor_payload in enumerate(elements, start=1):
            factor = Factor(
                bouquet_id=bouquet_payload["id"],
                factor_id=factor_payload["id"],
                factor_index=factor_index,
                factor_group=factor_payload["extras"]["ecospheres"].get("group"),
                factor_availability=factor_payload["extras"]["ecospheres"]["availability"],
                factor_title=factor_payload["title"],
                factor_purpose=factor_payload["description"],
            )

            if factor.factor_availability == "url available":
                factor.dataset_url = factor_payload["extras"]["ecospheres"]["uri"]

            elif factor.factor_availability == "available":
                dataset_id = factor_payload["element"]["id"]
                dataset_payload = api.get(f"/api/1/datasets/{dataset_id}")
                dataset_author = get_author(dataset_payload)
                factor.dataset_id = dataset_id
                factor.dataset_url = dataset_payload["page"]
                factor.dataset_title = dataset_payload["title"]
                factor.dataset_author_name = dataset_author["name"]
                factor.dataset_author_page = dataset_author["page"]
                # factor.dataset_responsible_parties =
                factor.dataset_last_modified = datetime.fromisoformat(dataset_payload["last_modified"])
                factor.dataset_license = dataset_payload.get("license")
                # factor.dataset_spatial_coverage =
                # factor.dataset_temporal_coverage =
                # factor.dataset_update_frequency =
                factor.dataset_schema = get_schema(dataset_payload)
                factor.dataset_quality_score = maybe_get(dataset_payload, "quality", "score")

                for resource_payload in dataset_payload.get("resources", []):
                    resource = Resource(
                        dataset_id=dataset_id,
                        resource_id=resource_payload["id"],
                        resource_available=maybe_get(resource_payload, "extras", "check:available"),
                        resource_title=resource_payload["title"],
                        resource_type=resource_payload["type"],
                        resource_format=resource_payload.get("format"),
                        resource_schema=get_schema(resource_payload),
                    )
                    resources_csv.writerow(asdict(resource))

            factors_csv.writerow(asdict(factor))


if __name__ == "__main__":
    run()
