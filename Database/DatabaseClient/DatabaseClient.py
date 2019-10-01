import os
import psycopg2
import re

class DatabaseClient:
    """Class to integrate with Heroku Postgres DB"""
    partition_map = {'playlist_track_count': r'playlist_track_count_y\d{4}m\d{1,2}'}

    def __init__(self):
        """Initializes an object with all necessary items to create a Database Client"""
        self.connection = None
        self.cursor = None
        self.filename = None
        self.db_url = os.environ['DATABASE_URL']

    def close(self):
        """Close Database connection"""
        self.cursor.close()
        self.connection.close()

    def connect(self):
        """Authentication for Database Client"""
        self.connection = psycopg2.connect(self.db_url, sslmode='require')
        self.cursor = self.connection.cursor()

    def create_partition(self, partition_name, table, start_val, end_val):
        """Create a new partition for given table """
        if re.match(self.partition_map[table], partition_name):
            query = f"CREATE TABLE {partition_name} PARTITION OF {table} FOR VALUES FROM ({start_val}) TO ({end_val}); COMMIT;"
            self.execute(query)
        else:
            print(f"Partition name {partition_name} does not match pattern {self.partition_map[table]}")
            exit()

    def execute(self, query):
        """Executes and returns results from provided query"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def file_write(self, data, filename=None):
        """Writes data provided to either specified filename or instance filename"""
        if not os.path.exists("data"):
            os.mkdir("data")
        if filename:
            self.filename = f"data/{filename}.txt"
        with open(self.filename, "a+") as file:
            file.write(str(data) + "\n")

    def update_schema(self, schema):
        """Set database schema"""
        self.execute(f"set search_path to {schema}")

if __name__ == "__main__":
    myDb = DatabaseClient()
    myDb.connect()
    print(myDb.execute('select version();'))
    myDb.create_partition('playlist_track_count_1', 'playlist_track_count', '2019-10-01', '2019-11-01')
    exit()
    