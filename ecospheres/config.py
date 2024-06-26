from pathlib import Path

import requests
import yaml


def get_config(env: str) -> dict:
    is_known_env = env in ["demo", "prod"]
    config_path = Path(env) if not is_known_env and Path(env).exists() else None
    if not is_known_env and not config_path:
        raise ValueError(f"Unknown env or config file {env}")
    if not config_path:
        url = f"https://raw.githubusercontent.com/opendatateam/udata-front-kit/ecospheres-{env}/configs/ecospheres/config.yaml"  # noqa
        r = requests.get(url)
        r.raise_for_status()
        data = r.text
    else:
        data = config_path.read_text()
    return yaml.safe_load(data)
