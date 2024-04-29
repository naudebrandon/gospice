import sqlite3

conn = sqlite3.connect('gospice.db')
print ("Opened database successfully")

conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, account_type INTEGER NOT NULL, credit_balance NUMERIC NOT NULL DEFAULT 0.00)')

print ("Table created successfully")
conn.close()



