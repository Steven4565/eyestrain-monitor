from random import random
import sqlite3
import time


class Database:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA foreign_keys = 1")

    def create_tables(self):
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS session(
                session_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                datetime TEXT    
                )
            '''
        )
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS session_entries(
                session_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER, 
                year INTEGER, 
                month INTEGER,
                date INTEGER, 
                hour INTEGER, 
                blink_count INTEGER,
                FOREIGN KEY(session_id) REFERENCES session(session_id)
                )
            '''
        )

    def insert_session(self):
        self.cur.execute(
            'INSERT INTO session (datetime) VALUES (datetime(\'now\'))')
        self.con.commit()
        return self.cur.lastrowid

    def insert_session_entries(self, array):
        session_id = self.insert_session()
        new_array = [(session_id, *entry) for entry in array]
        self.cur.executemany(
            'INSERT INTO session_entries (session_id, year, month, date, hour, blink_count) VALUES (?,?,?,?,?,?)', new_array)
        self.con.commit()

    def get_last_session(self):
        raw_session_data = self.cur.execute(
            'SELECT blink_count FROM session_entries WHERE session_id = (SELECT session_id FROM session ORDER BY session_id DESC LIMIT 1)').fetchall()
        session_data = [blink_count[0] for blink_count in raw_session_data]
        if (len(session_data) > 0):
            return session_data
        else:
            return False

    def get_average(self, year, month, date):
        raw_day_average = self.cur.execute(
            'SELECT hour, AVG(blink_count) FROM session_entries WHERE year=? AND month=? AND date=? GROUP BY hour', (year, month, date,)).fetchall()
        day_average = {}
        for i in range(24):
            day_average[i+1] = 0
        for (hour, average) in raw_day_average:
            day_average[hour] = average
        if (len(day_average) > 0):
            return day_average
        else:
            return False

    def get_session_average(self):
        last_session_data = self.get_last_session()
        if (last_session_data):
            return sum(last_session_data) / len(last_session_data)
        else:
            return False

    def close(self):
        self.con.close()

    # ========== DEBUGGING ==========

    def log_sessions(self):
        res = self.cur.execute('SELECT * FROM session')
        print(res.fetchall())

    def log_session_entries(self):
        res = self.cur.execute('SELECT * FROM session_entries')
        print(res.fetchall())

    def reset(self):
        self.cur.execute('DELETE FROM session_entries')
        self.cur.execute('DELETE FROM session')
        self.con.commit()


database = Database()
database.create_tables()

# ========== DEBUGGING ==========

# database.reset()

# session_id = database.insert_session()
# database.insert_session_entry(session_id, 12, 5, 100)
# year = time.strftime('%Y', time.localtime())
# month = time.strftime('%m', time.localtime())
# date = time.strftime('%d', time.localtime())
# hour = time.strftime('%H', time.localtime())

# mock_entry = []
# for i in range(5):
#     mock_entry.append((date, hour, round(random() * 25 + 25)))
# database.insert_session_entries(mock_entry)

# database.log_sessions()
# database.log_session_entries()

# print(database.get_average(2))
# print(database.get_last_session())
