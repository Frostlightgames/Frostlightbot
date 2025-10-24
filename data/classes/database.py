import os
import sqlite3

class Database:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.path = os.path.join("data","database.db")

        with sqlite3.connect(self.path) as con:
            database = con.cursor()
            database.execute("""CREATE TABLE IF NOT EXISTS config (
                                key     TEXT PRIMARY KEY,
                                value   TEXT)
                            """)

            database.execute("""CREATE TABLE IF NOT EXISTS member (
                                name    VARCHAR,
                                uid     INTEGER PRIMARY KEY,
                                coins   INTEGER,
                                candy   INTEGER,
                                level   INTEGER,
                                xp      INTEGER)
                            """)

    def query(self, query: str, attributes=[], fetch=True):
        if os.path.exists(self.path):
            with sqlite3.connect(self.path) as con:
                database = con.cursor()
                database.execute(query, attributes)
                if fetch:
                    return database.fetchall()
                else:
                    con.commit()

    def get_allowed_keys(self, table):
        allowed_keys_data = self.query(f"PRAGMA table_info({table})")
        allowed_keys = []
        for allowed_key in allowed_keys_data:
            allowed_keys.append(allowed_key[1])

        return allowed_keys

    def set_config(self,key:str ,value:str):
        data = self.get_config(key)
        if not data:
            self.query("INSERT INTO config (key, value) VALUES (?, ?)", [key, value], fetch=False)
        else:
            self.query("UPDATE config SET value = ? WHERE key = ?",[value, key], fetch=False)

    def get_config(self, key: str, default: str = None) -> str:
        data = self.query("SELECT value FROM config WHERE key = ?", [key])
        return data[0][0] if data else default

    def set_member_value(self, uid:int, key:str, value:int):
        if key not in self.get_allowed_keys("member"):
            raise ValueError("Key not in allowed keys")
        
        data = self.query("SELECT uid FROM member WHERE uid = ?",[uid])
        if not data:
            self.query("INSERT INTO member (uid, coins, candy, level, xp) VALUES (?, 0, 0, 0, 0)", [uid], fetch=False)
            self.query(f"UPDATE member SET {key} = ? WHERE uid = ?", [value, uid], fetch=False)
        else:
            self.query(f"UPDATE member SET {key} = ? WHERE uid = ?",[value, uid], fetch=False)

    def get_member_value(self, uid: int, key: str):
        if key not in self.get_allowed_keys("member"):
            raise ValueError("Key not in allowed keys")
        
        data = self.query(f"SELECT {key} FROM member WHERE uid = ?", [uid])
        return data[0][0] if data else None


DATABASE = Database()