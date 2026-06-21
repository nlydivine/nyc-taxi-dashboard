#!/bin/bash
set -e

DB_FILE="nyc_taxi.db"
DUMP_FILE="deliverables/nyc_taxi_dump.sql"

if [ -f "$DB_FILE" ]; then
    echo "✅ $DB_FILE already exists — nothing to do."
    echo "   (Run 'rm $DB_FILE' first if you want to rebuild from scratch.)"
    exit 0
fi

if [ -f "$DUMP_FILE" ]; then
    echo "Restoring database from $DUMP_FILE ..."
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$DB_FILE" < "$DUMP_FILE"
    else
        python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_FILE')
with open('$DUMP_FILE') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
"
    fi
    echo "✅ Database restored from dump."
else
    echo "No dump found at $DUMP_FILE — running the full cleaning pipeline instead."
    if [ ! -f "data/yellow_tripdata.parquet" ]; then
        echo "❌ data/yellow_tripdata.parquet not found."
        echo "   Download it first, e.g.:"
        echo "   curl -o data/yellow_tripdata.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-01.parquet"
        exit 1
    fi
    python3 database/create_tables.py
    python3 database/insert_zones.py
    python3 database/insert_trips.py
fi
