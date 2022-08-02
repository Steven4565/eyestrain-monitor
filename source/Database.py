import sqlite3
import time


class Database:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA foreign_keys = 1")


    def create_tables(self):
        self.cur.execute(
            '''CREATE TABLE session(
                session_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                datetime TEXT
                )
            '''
        )
        self.cur.execute(
            '''CREATE TABLE session_entries(
                session_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER, 
                date INTEGER, 
                hour INTEGER, 
                blink_count INTEGER,
                FOREIGN KEY(session_id) REFERENCES session(session_id)
                )
            '''
        )

    def insert_session(self):
        print('insert session')
        self.cur.execute('INSERT INTO session (datetime) VALUES (?)', (time.strftime('%x %H:%M', time.localtime()),))
        self.con.commit()

    def insert_session_entry(self):
        print('insert session entry')
        self.cur.execute('INSERT INTO session_entries (session_id, date, hour, blink_count) VALUES (?,?,?,?)', (self.cur.lastrowid, 12, 5, 100))
        self.con.commit()

    def log_sessions(self):
        res = self.cur.execute('SELECT * FROM session')
        print(res.fetchall())
    
    def log_session_entries(self):
        res = self.cur.execute('SELECT * FROM session_entries')
        print(res.fetchall())

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()

database = Database()
# database.create_tables()
# database.insert_session()
# database.insert_session_entry()
database.log_sessions()
database.log_session_entries()
database.close()
