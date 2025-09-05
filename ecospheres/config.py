from dataclasses import dataclass
from pathlib import Path

import requests
import yaml


def get_config(site: str, env: str) -> dict:
    is_known_env = env in ["demo", "prod"]
    config_path = Path(env) if Path(env).exists() else None
    if not is_known_env and not config_path:
        raise ValueError(f"Unknown env or config file {env}")
    if not config_path:
        gh_base_url = "https://raw.githubusercontent.com/opendatateam/udata-front-kit"
        if site == "ecospheres":
            url = f"{gh_base_url}/ecospheres-{env}/configs/ecospheres/config.yaml"
        else:
            url = f"{gh_base_url}/main/configs/{site}/config.yaml"
        r = requests.get(url)
        r.raise_for_status()
        data = r.text
    else:
        data = config_path.read_text()
    parsed_data = yaml.safe_load(data)

    # sanity check on base_url vs env
    # TODO: only a warning?
    base_url = parsed_data["datagouvfr"]["base_url"]
    if env == "demo" and "demo.data.gouv.fr" not in base_url:
        raise ValueError(f"Invalid base_url for demo env: {base_url}")

    return parsed_data

@dataclass
class PageConfig:
    site: str
    env: str
    base_url: str
    page: str
    universe_query: dict


def get_page_config(site: str, env: str, page: str) -> PageConfig:
    config = get_config(site, env)
    if page not in config["pages"]:
        raise ValueError(f"Unknown page '{page}' for site '{site}'")
    print(f"Loaded config for site '{site}' on env '{env}' and page '{page}'")
    return PageConfig(
        site = site,
        env = env,
        base_url = config["datagouvfr"]["base_url"],
        page = page,
        universe_query = config["pages"][page]["universe_query"],
    )
