import os
import psycopg2

class DatabaseClient:
    """Class to integrate with Heroku Postgres DB"""

    def __init__(self):
        """Initializes an object with all necessary items to create a Database Client"""
        self.connection = None
        self.cursor = None
        self.db_url = os.environ['DATABASE_URL']

    def close(self):
        """Close Database connection"""
        self.cursor.close()
        self.connection.close()

    def connect(self):
        """Authentication for Database Client"""
        self.connection = psycopg2.connect(self.db_url, sslmode='require')
        self.cursor = self.connection.cursor()

    def execute(self, query):
        """Executes and returns results from provided query"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

if __name__ == "__main__":
    myDb = DatabaseClient()
    myDb.connect()
    print(myDb.execute('select version();'))
    exit()
    