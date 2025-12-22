import sqlite3
from datetime import datetime

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Sites migrations als applied markieren
cursor.execute("""
    INSERT OR IGNORE INTO django_migrations (app, name, applied) 
    VALUES ('sites', '0001_initial', ?)
""", (datetime.now(),))

cursor.execute("""
    INSERT OR IGNORE INTO django_migrations (app, name, applied) 
    VALUES ('sites', '0002_alter_domain_unique', ?)
""", (datetime.now(),))

# Site mit ID 1 erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS django_site (
        id INTEGER PRIMARY KEY,
        domain VARCHAR(100) NOT NULL UNIQUE,
        name VARCHAR(50) NOT NULL
    )
""")

cursor.execute("""
    INSERT OR IGNORE INTO django_site (id, domain, name) 
    VALUES (1, 'localhost:8000', 'Auth Service Local')
""")

conn.commit()
conn.close()

print("✅ Sites migrations markiert und Site erstellt!")
