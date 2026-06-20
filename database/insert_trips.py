from connection import get_connection

def insert_trips():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ VERY SMALL SAFE SAMPLE DATA (ONLY 5 ROWS)
    sample_data = [
        ("2025-01-01 10:00:00", "2025-01-01 10:20:00", 1, 2.5, 1, 2, 10.0, 15.0),
        ("2025-01-01 11:00:00", "2025-01-01 11:30:00", 2, 5.0, 3, 4, 20.0, 25.0),
        ("2025-01-01 12:00:00", "2025-01-01 12:10:00", 1, 1.2, 2, 5, 8.0, 12.0),
        ("2025-01-01 13:00:00", "2025-01-01 13:45:00", 3, 7.8, 4, 6, 30.0, 40.0),
        ("2025-01-01 14:00:00", "2025-01-01 14:25:00", 1, 3.3, 5, 7, 15.0, 22.0),
    ]

    for row in sample_data:
        cursor.execute("""
            INSERT INTO trips (
                tpep_pickup_datetime,
                tpep_dropoff_datetime,
                passenger_count,
                trip_distance,
                PULocationID,
                DOLocationID,
                fare_amount,
                total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    conn.commit()
    conn.close()

    print("SAFE MODE: 5 sample trips inserted")

if __name__ == "__main__":
    insert_trips()
