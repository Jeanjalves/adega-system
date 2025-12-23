import sqlite3

conn = sqlite3.connect("adega.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE vendas ADD COLUMN forma_pagamento TEXT")
    print("Coluna forma_pagamento adicionada com sucesso.")
except Exception as e:
    print("Coluna já existe ou erro:", e)

conn.commit()
conn.close()
