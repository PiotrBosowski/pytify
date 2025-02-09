import os
import sqlite3
from datetime import datetime
import pytify.settings as settings
from urllib.parse import urlparse, parse_qs
from contextlib import closing

class Database:
    """
    Singleton-driven database management class.
    """

    database = None

    def __init__(self):
        """Initialize the database (Singleton)."""
        os.makedirs(settings.database_path, exist_ok=True)
        os.makedirs(settings.save_audio_path, exist_ok=True)
        self.db_path = os.path.join(settings.database_path, 'pytify.db')

    def get_connection(self):
        """Return a new database connection with dict_factory enabled."""
        conn = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
        conn.row_factory = self.dict_factory
        return conn

    def create_table(self):
        """Create the songs table if it does not exist."""
        with self.get_connection() as conn, closing(conn.cursor()) as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS songs (
                    song_url TEXT PRIMARY KEY, 
                    yt_id TEXT, 
                    path TEXT, 
                    title TEXT, 
                    date TEXT
                )"""
            )
            conn.commit()

    def add_record(self, song_url, path, title):
        """Add a new record to the database."""
        date = self.get_current_date()
        yt_id = self.get_yt_id(song_url)

        with self.get_connection() as conn, closing(conn.cursor()) as cursor:
            cursor.execute("INSERT OR IGNORE INTO songs VALUES (?,?,?,?,?)", (song_url, yt_id, path, title, date))
            conn.commit()

    def list_all(self):
        """Retrieve all records."""
        with self.get_connection() as conn, closing(conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM songs")
            return cursor.fetchall()

    def get_song(self, yt_id):
        """Retrieve a song by YouTube ID."""
        with self.get_connection() as conn, closing(conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM songs WHERE yt_id = ?", (yt_id,))
            return cursor.fetchone()

    def check_if_exist(self, url):
        """Check if a song already exists in the database."""
        yt_id = self.get_yt_id(url)
        with self.get_connection() as conn, closing(conn.cursor()) as cursor:
            return cursor.execute("SELECT * FROM songs WHERE yt_id = ?", (yt_id,)).fetchone()

    @staticmethod
    def dict_factory(cursor, row):
        """Convert SQLite row into a dictionary."""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    @staticmethod
    def get_yt_id(url):
        """Extract YouTube video ID from URL."""
        u_pars = urlparse(url)
        quer_v = parse_qs(u_pars.query).get('v')
        if quer_v:
            return quer_v[0]
        pth = u_pars.path.split('/')
        return pth[-1] if pth else None

    @staticmethod
    def get_database():
        """Singleton pattern for Database instance."""
        if not Database.database:
            Database.database = Database()
            Database.database.create_table()  # Ensure the table is created at startup
        return Database.database

    @staticmethod
    def get_current_date():
        """Get the current date and time."""
        return datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
