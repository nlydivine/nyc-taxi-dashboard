import os
import pandas as pd
from connection import get_connection

# ------------------------------------------------------------
# Config
# ------------------------------------------------------------
PARQUET_PATH = os.path.join("data", "yellow_tripdata.parquet")
FAILED_LOG_PATH = os.path.join("test", "failed_records.csv")

# How many rows to process. Set to None to load the full file
# once you've confirmed the pipeline works end-to-end.
SAMPLE_SIZE = 5000

# Columns required in every row — anything missing here is dropped.
REQUIRED_FIELDS = [
    "passenger_count", "RatecodeID", "store_and_fwd_flag", "payment_type",
    "fare_amount", "total_amount", "trip_distance",
    "PULocationID", "DOLocationID",
    "tpep_pickup_datetime", "tpep_dropoff_datetime",
]

VALID_PAYMENT_TYPES = {0, 1, 2, 3, 4, 5, 6}
VALID_RATECODE_IDS = {1, 2, 3, 4, 5, 6, 99}
VALID_VENDOR_IDS = {1, 2, 6, 7}


def load_zone_ids():
    """Pull the set of valid LocationIDs already inserted into zones,
    so we never insert a trip pointing at a zone that doesn't exist."""
    conn = get_connection()
    ids = {row[0] for row in conn.execute("SELECT LocationID FROM zones")}
    conn.close()
    return ids


def clean_and_engineer(df, valid_zone_ids):
    """Vectorized cleaning + feature engineering. Returns (valid_df, failed_df)
    where failed_df has a 'reason' column for transparency, per the
    assignment's logging requirement."""

    df = df.copy()
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

    currency_fields = ["fare_amount", "extra", "mta_tax", "tip_amount",
                        "tolls_amount", "improvement_surcharge", "total_amount"]
    for col in currency_fields:
        if col in df.columns:
            df[col] = df[col].round(2)
        else:
            df[col] = 0.0  # column missing from this TLC month's schema

    if "congestion_surcharge" not in df.columns:
        df["congestion_surcharge"] = 0.0

    # reason is assigned to the FIRST failing check only, in priority order,
    # mirroring data/csv_handler.py's row-by-row logic but vectorized.
    reason = pd.Series([None] * len(df), index=df.index, dtype=object)

    def flag(mask, label):
        target = mask & reason.isna()
        reason.loc[target] = label

    flag(df[REQUIRED_FIELDS].isna().any(axis=1), "null field")
    flag((df["fare_amount"] < 0) | (df["total_amount"] < 0), "negative amount")
    flag(df["tpep_pickup_datetime"].dt.year < 2019, "year of record out of given range")
    flag(df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"], "dropoff time earlier than pickup time")
    flag((df["passenger_count"] <= 0) | (df["passenger_count"] > 8), "negative or excessive passenger count")
    flag(df["trip_distance"] <= 0, "zero or negative trip distance")
    flag(~df["PULocationID"].isin(valid_zone_ids) | ~df["DOLocationID"].isin(valid_zone_ids),
         "location does not appear in lookup dict")
    flag(~df["store_and_fwd_flag"].isin(["Y", "N"]), "invalid flag")
    flag(~df["payment_type"].isin(VALID_PAYMENT_TYPES), "payment type not recognised")
    flag(~df["RatecodeID"].isin(VALID_RATECODE_IDS), "rate code ID type not recognised")
    flag(~df["VendorID"].isin(VALID_VENDOR_IDS), "vendorID not recognised")

    failed_df = df[reason.notna()].copy()
    failed_df["reason"] = reason[reason.notna()]

    valid_df = df[reason.isna()].copy()

    # ---- duplicates (assignment: "Identify and resolve ... duplicates") ----
    dupe_mask = valid_df.duplicated(
        subset=["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
                "PULocationID", "DOLocationID", "trip_distance"],
        keep="first",
    )
    dupes = valid_df[dupe_mask].copy()
    dupes["reason"] = "duplicate record"
    failed_df = pd.concat([failed_df, dupes], ignore_index=True)
    valid_df = valid_df[~dupe_mask]

    # ---- derived / engineered features (assignment: at least 3) ----
    duration_min = (valid_df["tpep_dropoff_datetime"] - valid_df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
    valid_df["trip_duration_minutes"] = duration_min.round(2)

    # drop trips with an implausible duration (<1 min or >180 min) — outliers
    duration_outlier = (valid_df["trip_duration_minutes"] < 1) | (valid_df["trip_duration_minutes"] > 180)
    outliers = valid_df[duration_outlier].copy()
    outliers["reason"] = "implausible trip duration"
    failed_df = pd.concat([failed_df, outliers], ignore_index=True)
    valid_df = valid_df[~duration_outlier]

    valid_df["avg_speed_mph"] = (
        valid_df["trip_distance"] / (valid_df["trip_duration_minutes"] / 60.0)
    ).round(2)
    # unrealistic speed (e.g. GPS/odometer glitches) — physical outlier
    speed_outlier = (valid_df["avg_speed_mph"] <= 0) | (valid_df["avg_speed_mph"] > 80)
    speed_bad = valid_df[speed_outlier].copy()
    speed_bad["reason"] = "implausible average speed"
    failed_df = pd.concat([failed_df, speed_bad], ignore_index=True)
    valid_df = valid_df[~speed_outlier]

    valid_df["tip_percentage"] = (
        (valid_df["tip_amount"] / valid_df["fare_amount"].replace(0, pd.NA)) * 100
    ).round(2).fillna(0)

    return valid_df, failed_df


def insert_trips():
    if not os.path.exists(PARQUET_PATH):
        print(f"❌ Could not find {PARQUET_PATH}. "
              f"Download yellow_tripdata and place it at that path.")
        return

    print("Loading parquet file...")
    df = pd.read_parquet(PARQUET_PATH)
    if SAMPLE_SIZE is not None:
        df = df.head(SAMPLE_SIZE)
    print(f"Loaded {len(df)} raw rows.")

    valid_zone_ids = load_zone_ids()
    if not valid_zone_ids:
        print("❌ zones table is empty — run insert_zones.py first.")
        return

    valid_df, failed_df = clean_and_engineer(df, valid_zone_ids)
    print(f"{len(valid_df)} rows passed cleaning, {len(failed_df)} rows excluded.")

    # ---- transparency log of excluded records ----
    os.makedirs(os.path.dirname(FAILED_LOG_PATH), exist_ok=True)
    failed_df.to_csv(FAILED_LOG_PATH, index=False)
    print(f"Excluded-record log written to {FAILED_LOG_PATH}")

    columns = [
        "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
        "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag",
        "PULocationID", "DOLocationID", "payment_type", "fare_amount",
        "extra", "mta_tax", "tip_amount", "tolls_amount",
        "improvement_surcharge", "total_amount", "congestion_surcharge",
        "trip_duration_minutes", "avg_speed_mph", "tip_percentage",
    ]

    insert_df = valid_df[columns].copy()
    insert_df["tpep_pickup_datetime"] = insert_df["tpep_pickup_datetime"].astype(str)
    insert_df["tpep_dropoff_datetime"] = insert_df["tpep_dropoff_datetime"].astype(str)
    records = list(insert_df.itertuples(index=False, name=None))

    placeholders = ", ".join(["?"] * len(columns))
    insert_sql = f"""
        INSERT INTO trips ({", ".join(columns)})
        VALUES ({placeholders})
    """

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(insert_sql, records)
    conn.commit()
    conn.close()

    print(f"✅ {len(records)} cleaned trips inserted into the database")


if __name__ == "__main__":
    insert_trips()
