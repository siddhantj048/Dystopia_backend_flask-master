import sqlite3
conn=sqlite3.connect('dystopiadb.db')
cur=conn.cursor()
print("Opened db successfully")
creationscript=open('creationscripts.sql')
for line in creationscript.readlines():
    cur.execute(line)
print("Table created successfully")
conn.close()