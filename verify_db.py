import sqlite3

conn = sqlite3.connect('backend/database.db')
cursor = conn.cursor()

# Contar personajes
cursor.execute('SELECT COUNT(*) FROM characters')
total = cursor.fetchone()[0]
print(f'Total personajes: {total}')

# Últimos 10 personajes
cursor.execute('SELECT name FROM characters ORDER BY id DESC LIMIT 10')
print('\nÚltimos 10 personajes:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

conn.close()
