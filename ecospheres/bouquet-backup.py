import json
import os
from pathlib import Path
from minicli import cli, run

from ecospheres.api import DatagouvfrAPI
from ecospheres.config import get_page_config
from ecospheres.rel import iter_rel


@cli
def backup(env: str, site: str = "ecospheres", page: str = "bouquets"):
    """
    Backup bouquets for a given environment and site

    Creates backup/{site}/{env}/ directory and saves each bouquet payload as JSON
    with filename being the bouquet ID and its elements in a separate file.

    :env: Target environment (demo, prod, or config file path)
    :site: Site name (default: ecospheres)
    :page: Page name (default: bouquets)
    """
    config = get_page_config(site, env, page)
    api = DatagouvfrAPI(config.base_url, authenticated=True)

    # Create backup directory
    backup_dir = Path("backup") / site / env
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get all bouquets including private ones
    universe_tag = config.universe_query["tag"]
    bouquets = api.get_topics(universe_tag, include_private=True)

    print(f"Found {len(bouquets)} bouquets for {site} on {env}")

    # Backup each bouquet
    for bouquet in bouquets:
        bouquet_id = bouquet["id"]

        # Get full bouquet payload
        full_bouquet = api.get_topic(bouquet_id)

        # Save bouquet to main file
        filename = backup_dir / f"{bouquet_id}.json"
        with open(filename, "w") as f:
            json.dump(full_bouquet, f, indent=2, ensure_ascii=False)

        # Get and save related elements
        elements = list(iter_rel(full_bouquet["elements"], api))
        elements_filename = backup_dir / f"{bouquet_id}-elements.json"
        with open(elements_filename, "w") as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)

        print(f"Backed up: {bouquet['name']} ({len(elements)} elements) -> {filename} + {elements_filename}")

    print(f"Backup completed in {backup_dir}")


if __name__ == "__main__":
    run()
