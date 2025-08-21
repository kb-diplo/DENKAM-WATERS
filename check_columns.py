from django.db import connection

cursor = connection.cursor()
cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \'main_waterbill\'')
columns = [row[0] for row in cursor.fetchall()]
print('Columns in main_waterbill table:')
for col in columns:
    print(f'  {col}')
