import sqlite3

class BaseDatabase:
    def __init__(self, table) -> None:
        self.table = table
    
    def write(self, id, content):
        query = f"INSERT INTO {self.table} VALUES (?, ?)"
        cursor.execute(query, (id, content))
        database.commit()

    def delete(self, id):
        query = f"DELETE FROM {self.table} WHERE id = ?"
        cursor.execute(query, (id,))
        database.commit()

    def read_all(self):
        query = f"SELECT * FROM {self.table}"
        data = cursor.execute(query).fetchall()
        return data

    def read_value(self, id):
        query = f"SELECT preferred_language FROM {self.table} where id = ?"
        data = cursor.execute(query, (id,)).fetchone()
        if data:
            return data[0]
        
        return None
        
    def update(self, id, new_data_key, new_data):
        query = f"UPDATE {self.table} SET {new_data_key} = ? WHERE id = ?"
        cursor.execute(query, (new_data, id))
        database.commit()

class ReminderDatabase(BaseDatabase):
    def __init__(self, db) -> None:
        super().__init__("reminders")
        db.execute("CREATE TABLE IF NOT EXISTS reminders(id INT, timestamp INT, author_id INT, message_content STRING)")
        
    
    def write(self, id, timestamp, author_id, message_content):
        query = f"INSERT INTO {self.table} VALUES (?, ?, ?, ?)"
        cursor.execute(query, (id, timestamp, author_id, message_content))
        database.commit()

class LanguageDatabase(BaseDatabase):
    def __init__(self, db) -> None:
        super().__init__("language")
        db.execute("CREATE TABLE IF NOT EXISTS language(id INT, preferred_language STRING)")
        


database = sqlite3.connect("local_only/database.db")
cursor = database.cursor()
# database.execute("CREATE TABLE IF NOT EXISTS messages(id INT, message_content STRING)")

reminder_database = ReminderDatabase(db=database)
language_database = LanguageDatabase(db=database)

if __name__ == "__main__":
    if language_database.read_value(725539745572323409):
        language_database.update(725539745572323409, "preferred_language", "en-US")
    
    else:
        language_database.write(725539745572323409, "en-US")