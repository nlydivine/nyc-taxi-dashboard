import csv
from connection import get_connection

def insert_zones():
    conn = get_connection()
    cursor = conn.cursor()

    with open("data/taxi_zone_lookup.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT OR IGNORE INTO zones
                VALUES (?, ?, ?, ?)
            """, (
                int(row["LocationID"]),
                row["Borough"],
                row["Zone"],
                row["service_zone"]
            ))

    conn.commit()
    conn.close()
    print("Zones inserted successfully")

if __name__ == "__main__":
    insert_zones()
