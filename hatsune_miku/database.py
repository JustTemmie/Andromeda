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

    def read(self):
        query = f"SELECT * FROM {self.table}"
        data = cursor.execute(query).fetchall()
        return data

    def update(self, id, new_data_key, new_data):
        query = f"UPDATE {self.table} SET {new_data_key} = ? WHERE id = ?"
        cursor.execute(query, (new_data, id))
        database.commit()

class ReminderDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__("reminders")
    
    def write(self, id, timestamp, author_id, message_content):
        query = f"INSERT INTO {self.table} VALUES (?, ?, ?, ?)"
        cursor.execute(query, (id, timestamp, author_id, message_content))
        database.commit()

database = sqlite3.connect("local_only/database.db")
cursor = database.cursor()
# database.execute("CREATE TABLE IF NOT EXISTS messages(id INT, message_content STRING)")
database.execute("CREATE TABLE IF NOT EXISTS reminders(id INT, timestamp INT, author_id INT, message_content STRING)")

reminder_database = ReminderDatabase()

if __name__ == "__main__":
    pass

    # write("messages", 29841294142, "beav")
    # delete("messages", 29841294142)
    # update("messages", 29841294142, "message_content", "beaver!")
    # print(read("messages"))