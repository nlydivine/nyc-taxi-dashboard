-- ============================================================
-- NYC Taxi Dashboard — Database Schema
-- Dimension table (zones) + Fact table (trips), normalized,
-- with foreign keys and indexes for the dashboard's filter/sort needs.
-- Column names match the raw TLC fields (see data_dictionary PDF)
-- so they stay consistent with data/csv_handler.py's cleaning output.
-- ============================================================

PRAGMA foreign_keys = ON;

-- =========================
-- ZONES TABLE (DIMENSION)
-- =========================
CREATE TABLE IF NOT EXISTS zones (
    LocationID      INTEGER PRIMARY KEY,
    Borough         TEXT NOT NULL,
    Zone            TEXT NOT NULL,
    service_zone    TEXT
);

-- =========================
-- TRIPS TABLE (FACT)
-- =========================
CREATE TABLE IF NOT EXISTS trips (
    trip_id                 INTEGER PRIMARY KEY AUTOINCREMENT,

    -- ---- raw fields (cleaned, from yellow_tripdata) ----
    VendorID                INTEGER,
    tpep_pickup_datetime    DATETIME NOT NULL,
    tpep_dropoff_datetime   DATETIME NOT NULL,
    passenger_count         INTEGER,
    trip_distance           REAL NOT NULL,
    RatecodeID               INTEGER,
    store_and_fwd_flag       TEXT,
    PULocationID              INTEGER NOT NULL,
    DOLocationID              INTEGER NOT NULL,
    payment_type              INTEGER,
    fare_amount               REAL NOT NULL,
    extra                     REAL DEFAULT 0,
    mta_tax                   REAL DEFAULT 0,
    tip_amount                REAL DEFAULT 0,
    tolls_amount               REAL DEFAULT 0,
    improvement_surcharge      REAL DEFAULT 0,
    total_amount                REAL NOT NULL,
    congestion_surcharge         REAL DEFAULT 0,

    -- ---- derived / engineered features (Task 1, item 4) ----
    trip_duration_minutes   REAL,   -- (dropoff - pickup) in minutes
    avg_speed_mph           REAL,   -- trip_distance / (duration in hours)
    tip_percentage          REAL,   -- tip_amount / fare_amount * 100

    FOREIGN KEY (PULocationID) REFERENCES zones (LocationID),
    FOREIGN KEY (DOLocationID) REFERENCES zones (LocationID)
);

-- =========================
-- INDEXES (PERFORMANCE)
-- =========================
CREATE INDEX IF NOT EXISTS idx_pickup_time ON trips (tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_pu          ON trips (PULocationID);
CREATE INDEX IF NOT EXISTS idx_do          ON trips (DOLocationID);
CREATE INDEX IF NOT EXISTS idx_fare        ON trips (fare_amount);
CREATE INDEX IF NOT EXISTS idx_distance    ON trips (trip_distance);
