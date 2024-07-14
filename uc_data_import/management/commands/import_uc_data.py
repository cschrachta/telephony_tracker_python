import os
import psycopg2
import pandas as pd
from django.core.management.base import BaseCommand
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Import UC data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory containing CSV files')
        parser.add_argument('db_name', type=str, help='Name of the database to create and populate')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']
        db_name = kwargs['db_name']
        
        # Load database connection details from .env file
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")

        # Function to create a PostgreSQL connection to the default database
        def create_default_connection():
            try:
                conn = psycopg2.connect(
                    dbname="postgres",
                    user=DB_USER,
                    password=DB_PASSWORD,
                    host=DB_HOST,
                    port=DB_PORT
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                return conn
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error connecting to default database: {e}"))
                return None

        # Function to create a new database
        def create_database():
            conn = create_default_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(f"CREATE DATABASE {db_name};")
                    self.stdout.write(self.style.SUCCESS(f"Database {db_name} created successfully."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating database {db_name}: {e}"))
                finally:
                    cursor.close()
                    conn.close()

        # Function to create a connection to a specific database
        def create_connection():
            try:
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    host=DB_HOST,
                    port=DB_PORT
                )
                return conn
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error connecting to database {db_name}: {e}"))
                return None

        # Function to create a table dynamically based on CSV file header
        def create_table_from_csv(conn, table_name, columns):
            cursor = conn.cursor()
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, " + ", ".join([f"{col} TEXT" for col in columns]) + ");"
            try:
                cursor.execute(create_table_query)
                conn.commit()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating table {table_name}: {e}"))
            finally:
                cursor.close()

        # Function to insert data into the table
        def insert_data_from_csv(conn, table_name, df):
            cursor = conn.cursor()
            columns = df.columns.tolist()
            insert_query = f"INSERT INTO {table_name} (" + ", ".join(columns) + ") VALUES (" + ", ".join(["%s"] * len(columns)) + ")"
            try:
                for row in df.itertuples(index=False, name=None):
                    cursor.execute(insert_query, row)
                conn.commit()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error inserting data into table {table_name}: {e}"))
            finally:
                cursor.close()

        # Function to process all CSV files in a directory for a specific database
        def process_csv_files():
            create_database()
            conn = create_connection()
            if not conn:
                return
            
            for filename in os.listdir(directory):
                if filename.endswith(".csv"):
                    file_path = os.path.join(directory, filename)
                    table_name = os.path.splitext(filename)[0]  # Use the filename (without extension) as table name
                    df = pd.read_csv(file_path)
                    columns = df.columns.tolist()
                    
                    # Create table and insert data
                    create_table_from_csv(conn, table_name, columns)
                    insert_data_from_csv(conn, table_name, df)
            
            conn.close()

        # Execute the processing function
        process_csv_files()