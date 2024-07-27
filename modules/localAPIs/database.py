import sqlite3

class BaseDatabase:
    def __init__(self):
        pass

class BaseTable:
    def __init__(self, table, db) -> None:
        self.table = table
        self.database = db
        self.cursor = db.cursor()
    
    def write(self, id, content):
        query = f"INSERT INTO {self.table} VALUES (?, ?)"
        self.cursor.execute(query, (id, content))
        self.database.commit()

    def delete(self, id):
        query = f"DELETE FROM {self.table} WHERE id = ?"
        self.cursor.execute(query, (id,))
        self.database.commit()

    def read_all(self):
        query = f"SELECT * FROM {self.table}"
        data = self.cursor.execute(query).fetchall()
        return data

    def read_value(self, id):
        query = f"SELECT preferred_language FROM {self.table} where id = ?"
        data = self.cursor.execute(query, (id,)).fetchone()
        if data:
            return data[0]
        
        return None
        
    def update(self, id, new_data_key, new_data):
        query = f"UPDATE {self.table} SET {new_data_key} = ? WHERE id = ?"
        self.cursor.execute(query, (new_data, id))
        self.database.commit()
    
    def add_column(self, column_name, column_type):
        # check if the column already exists
        cursor = self.database.execute(f"PRAGMA table_info({self.table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # if it doesnt, add it
        if column_name not in columns:
            self.database.execute(f"ALTER TABLE {self.table} ADD COLUMN {column_name} {column_type}")

class ReminderTable(BaseTable):
    def __init__(self, db) -> None:
        super().__init__("reminders", db)
        db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (id INTEGER, timestamp INTEGER, author_id INTEGER, message_content STRING)")
        
    
    def write(self, id, timestamp, author_id, message_content):
        query = f"INSERT INTO {self.table} VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (id, timestamp, author_id, message_content))
        self.database.commit()

class LanguageTable(BaseTable):
    def __init__(self, db) -> None:
        super().__init__("language", db)
        db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (id INTEGER, preferred_language STRING)")

class MarriageDatabase(BaseDatabase):
    class MarriageTable(BaseTable):
        def __init__(self, db) -> None:
            super().__init__("marriage", db)
            db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (marriageID INTEGER PRIMARY KEY AUTOINCREMENT, proposerID INTEGER, recipientID INTEGER, time INTEGER, ring TEXT)")

        def write(self, proposerID, recipientID, timestamp, ring) -> int:
            """
                returns thee marriage ID of the newly created entry
            """
            query = f"INSERT INTO {self.table} (proposerID, recipientID, time, ring) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (proposerID, recipientID, timestamp, ring))
            self.database.commit()
            return self.cursor.lastrowid 

        def get_marriage_ID(self, user1, user2):
            query = f"SELECT marriageID FROM {self.table} where proposerID = {user1} AND recipientID = {user2} OR proposerID = {user2} AND recipientID = {user1}"
            data = self.cursor.execute(query).fetchall()
            if data:
                return data[0][0]

            return None
            
    class MarriageReferenceTable(BaseTable):
        def __init__(self, db) -> None:
            super().__init__("marriage_references", db)
            
        def write(self, userID, marriageID):
            self.database.execute(f"CREATE TABLE IF NOT EXISTS table_{userID} (marriageID INTEGER)")
            query = f"INSERT INTO table_{userID} VALUES (?)"
            self.cursor.execute(query, (marriageID,))
            self.database.commit()

        def delete(self, userID, marriageID):
            query = f"DELETE FROM table_{userID} WHERE marriageID = ?"
            self.cursor.execute(query, (marriageID,))
            self.database.commit()

        def read_all(self, userID):
            query = f"SELECT * FROM table_{userID}"
            data = self.cursor.execute(query).fetchall()
            return data
    
    def __init__(self) -> None:
        db = sqlite3.connect("local_only/marriage_database.db")

        self.marriage_table = self.MarriageTable(db)
        self.marriage_reference_table = self.MarriageReferenceTable(db)
    
    def marry(self, proposerID: int, recipientID: int, ring: str):
        marriageID = self.marriage_table.write(proposerID, recipientID, round(time.time()), ring)
        self.marriage_reference_table.write(proposerID, marriageID)
        self.marriage_reference_table.write(recipientID, marriageID)
    
    def divorce(self, user1: int, user2: int):
        marriageID = self.marriage_table.get_marriage_ID(user1, user2)
        self.marriage_reference_table.delete(user1, marriageID)
        self.marriage_reference_table.delete(user2, marriageID)

class EconomyDatabase(BaseDatabase):    
    class CommonEconomyTable(BaseTable):
        def __init__(self, db) -> None:
            super().__init__("economy", db)
            db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (userID INTEGER)")
            self.add_column("balance", "INTEGER") # the user's wallet balance
            self.add_column("daily_streak", "INTEGER") # how many days the user have claimed their daily in a row
            self.add_column("last_daily_day", "INTEGER") # the unix day of the last time the user claimed their daily
    
    def __init__(self) -> None:
        db = sqlite3.connect("local_only/economy_database.db")

        self.common_table = self.CommonEconomyTable(db)
        # self.add_column("lodge", "INT")
        


db = sqlite3.connect("local_only/database.db")
# db.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER, message_content STRING)")

reminder_table = ReminderTable(db=db)
language_table = LanguageTable(db=db)
economy_database = EconomyDatabase() # self managed database
marriage_database = MarriageDatabase() # self managed database

if __name__ == "__main__":
    import time
    # marriage_database.marry(123, 456, "uncommon")
    # marriage_database.divorce(123, 456)