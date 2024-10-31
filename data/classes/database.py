import os
import sqlite3

from data.functions.log import *

class Database:
    def __init__(self,bot):
        self.bot = bot
        self.path = os.path.join("data","database.db")

        # Creating all database table if they do not exist
        with sqlite3.connect(self.path) as con:
            database = con.cursor()
            database.execute("""CREATE TABLE IF NOT EXISTS config (
                                id     INTEGER PRIMARY KEY,
                                name   TEXT)
                            """)

            database.execute("""CREATE TABLE IF NOT EXISTS member (
                                name    varchar,
                                id      int PRIMARY KEY,
                                coins   int,
                                candy   int,
                                level   int,
                                xp      int)
                            """)
            
            # Adding causal data to database
            self.get_config("guild_id",670321104866377748)
            self.get_config("main_channel_id",970560114115358730)
            self.get_config("log_channel_id",1006678596846354442)
            self.get_config("main_member_role_id",1135178386906562580)

    def query(self,query,attributes=[]):
        if os.path.exists(self.path):
            with sqlite3.connect(self.path) as con:
                database = con.cursor()
                database.execute(query,attributes)
                data = database.fetchall()
                if data != []:
                    return data[0]
                else:
                    return data
                
    def create_member(self,id,name):
        self.query("""INSERT INTO member (name,id,coins,candy,level,xp) VALUES (?,?,?,?,?,?)""",[name,id,0,0,0,0])
        return True
    
    def load_member(self,member):

        # Get data from database
        data = self.query("""SELECT * FROM member WHERE id = ?""",[member.id])
        if data == []:

            # Create blank member data
            self.create_member(member.id,member.name)
            data = ["",0,0,0,0,0]
        return data

    def save_member(self,member):
        data = self.query("""UPDATE member SET name = ?, coins = ?, candy = ?, level = ?, xp = ? WHERE id = ? """,[member.name,member.coins,member.candy,member.level,member.xp,member.id])
        if data != []:
            return data[0]
                
    def get_config(self,key,default_value):
        data = self.query("""SELECT id FROM config WHERE name = ?""",[key])
        if data != []:
            return data[0]
        else:

            # If key does not exist insert default into database
            self.query("""INSERT INTO config (id,name) VALUES (?,?)""",[default_value,key])
        return default_value