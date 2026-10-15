from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CURATED_DATA_DIR = PROJECT_ROOT / "data" / "curated"
CURATED_FILE = CURATED_DATA_DIR / "weather_history.parquet"


def load_curated_history():
    """Load existing curated forecast history, or return an empty DataFrame."""

    if not CURATED_FILE.exists():
        return pd.DataFrame()

    return pd.read_parquet(CURATED_FILE)

def identify_new_forecast_versions(incoming_df, history_df):
    """Return incoming forecast versions not already present in history."""

    if incoming_df.empty:
        return incoming_df.copy()

    if history_df.empty:
        return incoming_df.copy()

    required_columns = {"location_id", "time", "payload_hash"}

    for name, dataframe in (
        ("incoming_df", incoming_df),
        ("history_df", history_df),
    ):
        missing_columns = required_columns - set(dataframe.columns)

        if missing_columns:
            raise ValueError(
                f"{name} is missing required columns: "
                f"{sorted(missing_columns)}"
            )

    history_versions = history_df[
        ["location_id", "time", "payload_hash"]
    ].drop_duplicates()

    comparison = incoming_df.merge(
        history_versions,
        on=["location_id", "time", "payload_hash"],
        how="left",
        indicator=True,
    )

    new_versions = comparison.loc[
        comparison["_merge"] == "left_only",
        incoming_df.columns,
    ]

    return new_versions.reset_index(drop=True)

def save_curated_history(history_df):
    """Persist curated forecast history to a Parquet file."""

    if history_df.empty:
        return

    CURATED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    history_df.to_parquet(
        CURATED_FILE,
        index=False,
    )
def update_curated_history(incoming_df):
    """Add new forecast versions to the existing curated history."""
    history_df = load_curated_history()

    new_versions = identify_new_forecast_versions(
        incoming_df,
        history_df,
    )

    if new_versions.empty:
        return new_versions

    updated_history = pd.concat(
        [history_df, new_versions],
        ignore_index=True,
    )

    save_curated_history(updated_history)

    return new_versions