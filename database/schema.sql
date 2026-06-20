-- =========================
-- ZONES TABLE (DIMENSION)
-- =========================
CREATE TABLE IF NOT EXISTS zones (
    LocationID INTEGER PRIMARY KEY,
    Borough TEXT,
    Zone TEXT,
    service_zone TEXT
);

-- =========================
-- TRIPS TABLE (FACT)
-- =========================
CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tpep_pickup_datetime TEXT,
    tpep_dropoff_datetime TEXT,
    passenger_count INTEGER,
    trip_distance REAL,
    PULocationID INTEGER,
    DOLocationID INTEGER,
    fare_amount REAL,
    total_amount REAL,

    FOREIGN KEY (PULocationID) REFERENCES zones(LocationID),
    FOREIGN KEY (DOLocationID) REFERENCES zones(LocationID)
);

-- =========================
-- INDEXES (PERFORMANCE)
-- =========================
CREATE INDEX IF NOT EXISTS idx_pickup_time ON trips(tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_pu ON trips(PULocationID);
CREATE INDEX IF NOT EXISTS idx_do ON trips(DOLocationID);
