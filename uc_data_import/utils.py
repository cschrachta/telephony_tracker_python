import os
import tarfile
from django.conf import settings
from django.db import connection
from pathlib import Path
import csv
import psycopg2
from .models import UCDataImport


def handle_uploaded_file(uploaded_file):
    upload_dir = Path(settings.MEDIA_ROOT) / 'uc_system_uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / uploaded_file.name

    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # Now untar the file if it's a tar file
    if tarfile.is_tarfile(file_path):
        with tarfile.open(file_path) as tar:
            tar.extractall(path=upload_dir / uploaded_file.name.rsplit('.', 1)[0])
    
    return file_path



def extract_tar_file(file_path, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall(path=extract_to)

def get_system_info(extracted_path):
    header_file = os.path.join(extracted_path, 'header.txt')
    with open(header_file, 'r') as file:
        for line in file:
            if line.startswith('CCM :'):
                system_info = line.split(':')[1].strip()
                break
    return system_info

def create_database_and_tables(system_info, extracted_path):
    db_name = f"{system_info.replace('.', '_')}_db"
    connection = psycopg2.connect(
        dbname='postgres',
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST']
    )
    connection.autocommit = True
    cursor = connection.cursor()
    
    # Create database
    cursor.execute(f"CREATE DATABASE {db_name};")
    
    connection.close()
    
    # Connect to the new database and create tables
    connection = psycopg2.connect(
        dbname=db_name,
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST']
    )
    cursor = connection.cursor()
    
    for csv_file in os.listdir(extracted_path):
        if csv_file.endswith('.csv'):
            table_name = os.path.splitext(csv_file)[0]
            with open(os.path.join(extracted_path, csv_file), 'r') as file:
                reader = csv.reader(file)
                columns = next(reader)
                cursor.execute(f"CREATE TABLE {table_name} ({', '.join([f'{col} TEXT' for col in columns])});")
                
                for row in reader:
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join([f'%s' for _ in row])});", row)
    
    connection.commit()
    connection.close()

def import_uc_data(file_path, system_name, version):
    extract_to = os.path.join(settings.MEDIA_ROOT, 'extracted')
    extract_tar_file(file_path, extract_to)
    system_info = get_system_info(extract_to)
    create_database_and_tables(system_info, extract_to)


def create_tables_from_csv(directory):
    # This function assumes the CSV files have headers that match the table columns
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            table_name = filename.split('.')[0]
            csv_path = os.path.join(directory, filename)
            create_table_from_csv(table_name, csv_path)

def create_table_from_csv(table_name, csv_path):
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        columns = ', '.join([f'"{header}" TEXT' for header in headers])

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')

            for row in reader:
                placeholders = ', '.join(['%s'] * len(row))
                cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', row)

def process_uc_data(file_path, system_name, version):
    extract_to = os.path.join(settings.MEDIA_ROOT, 'extracted_uc_data')
    extract_tar_file(file_path, extract_to)
    create_tables_from_csv(extract_to)