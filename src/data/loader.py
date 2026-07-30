from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ASSETS_CONFIG_PATH = PROJECT_ROOT / "config" / "assets.yaml"
SETTINGS_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_yaml(path: Path) -> dict:
    """
    Load a YAML configuration file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_assets_config() -> dict:
    """
    Load asset metadata from assets.yaml.
    """
    return load_yaml(ASSETS_CONFIG_PATH)


def load_settings_config() -> dict:
    """
    Load application settings from settings.yaml.
    """
    return load_yaml(SETTINGS_CONFIG_PATH)


def get_asset_metadata() -> dict:
    """
    Return the asset metadata dictionary.
    """
    config = load_assets_config()
    return config.get("assets", {})


def get_asset_dataframe():
    """
    Convert asset configuration into a pandas DataFrame.
    """
    import pandas as pd

    assets = get_asset_metadata()

    records = []

    for ticker, metadata in assets.items():
        records.append(
            {
                "ticker": ticker,
                "name": metadata.get("name"),
                "asset_class": metadata.get("asset_class"),
                "sector": metadata.get("sector"),
            }
        )

    return pd.DataFrame(records)