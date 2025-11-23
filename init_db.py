import sqlite3, os
DB='jl.db'
if os.path.exists(DB):
    print("DB exists:", DB)
else:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript(open('init_schema.sql').read())
    conn.commit()
    conn.close()
    print("Created DB", DB)
