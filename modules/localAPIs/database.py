import sqlite3


# this is just legacy stuff because i don't want to break existing reminders
# probably should never touch this


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


db = sqlite3.connect("local_only/database.db")

reminder_table = ReminderTable(db=db)