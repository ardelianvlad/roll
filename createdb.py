import sqlite3
conn = sqlite3.connect('database.db')

if __name__ == "__main__":
    c = conn.cursor()

    # Create table
    c.execute('CREATE TABLE person (pid INTEGER PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255))')
    c.execute('CREATE TABLE queue (qid INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) UNIQUE, img VARCHAR(255), range INTEGER)')
    c.execute('CREATE TABLE q_order (id INTEGER PRIMARY KEY, qid INTEGER, pid INTEGER, no INTEGER, UNIQUE(qid, pid) ON CONFLICT IGNORE)')

    conn.commit()
    conn.close()