# uc_data_import/tasks.py
from celery import shared_task
from .utils import process_uc_data

@shared_task
def process_uploaded_uc_file(file_path, system_name, version):
    import_uc_data(file_path, system_name, version)
    # Add your data processing logic here
  