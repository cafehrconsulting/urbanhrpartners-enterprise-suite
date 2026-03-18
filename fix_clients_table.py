import sqlite3

DB_PATH = "urbanhrpartners.db"

columns_to_add = [
    ("company_name", "TEXT"),
    ("contact_person", "TEXT"),
    ("country", "TEXT"),
    ("language", "TEXT"),
    ("region", "TEXT"),
    ("tax_id_type", "TEXT"),
    ("tax_id_number", "TEXT"),
    ("risk_level", "TEXT"),
    ("needs", "TEXT"),
    ("notes", "TEXT"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(clients)")
existing_columns = {row[1] for row in cur.fetchall()}

for column_name, column_type in columns_to_add:
    if column_name not in existing_columns:
        sql = f"ALTER TABLE clients ADD COLUMN {column_name} {column_type}"
        cur.execute(sql)
        print(f"Added column: {column_name}")
    else:
        print(f"Already exists: {column_name}")

conn.commit()
conn.close()

print("Done.")