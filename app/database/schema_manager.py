import argparse
import sqlite3
from os import listdir, path
from os.path import isfile
from models.constants import SCHEMA_MIGRATIONS_DIRECTORY
from database.database_manager import DatabaseManager


class SchemaManager:
    def __init__(self, database_connection: sqlite3.Connection):
        self.__database_connection = database_connection

    def update_schema(self):
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        # Installs all the new migrations
        for i in range(current_version, latest_version):
            with open(
                path.join(SCHEMA_MIGRATIONS_DIRECTORY, f"{i:04}.sql"), "r"
            ) as migration_file:
                self.__database_connection.executescript(migration_file.read())
                self.__database_connection.commit()
                self.increment_version()

    def get_current_version(self):
        return self.__database_connection.execute("PRAGMA user_version").fetchone()[0]

    def increment_version(self):
        new_version = self.get_current_version() + 1
        self.__database_connection.execute(f"PRAGMA user_version = {new_version}")
        self.__database_connection.commit()

    def get_latest_version(self):
        return len(
            [
                migration_file
                for migration_file in listdir(SCHEMA_MIGRATIONS_DIRECTORY)
                if isfile(path.join(SCHEMA_MIGRATIONS_DIRECTORY, migration_file))
            ]
        )
