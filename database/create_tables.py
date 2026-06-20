from connection import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    with open("database/schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    create_tables()
