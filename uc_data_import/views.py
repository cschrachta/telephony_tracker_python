import os
import shutil
import tarfile
import environ
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from .forms import UploadFileForm
from django.core.management import call_command
from django.http import HttpResponse
from .models import UCSystemFile
from .utils import handle_uploaded_file
from .tasks import process_uploaded_uc_file


env = environ.Env(DEBUG=(bool, False))
env.read_env(env_file='telephony_tracker/.env')

DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")

def handle_uploaded_file(f, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    # Extract the .tar file
    if tarfile.is_tarfile(file_path):
        with tarfile.open(file_path, 'r') as tar:
            tar.extractall(path=directory)
        os.remove(file_path)  # Optionally remove the original .tar file after extraction

def detect_uc_system(header_file_path):
    with open(header_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("CCM :"):
                return "cisco_uc"
    return "unknown"

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', request.FILES['file'].name.split('.')[0])
            handle_uploaded_file(request.FILES['file'], upload_dir)

            # Detect UC system type
            header_file_path = os.path.join(upload_dir, 'header.txt')
            uc_system_type = detect_uc_system(header_file_path)

            if uc_system_type == "cisco_uc":
                db_name = "cisco_uc_database"
                call_command('import_uc_data', upload_dir, db_name)
            else:
                return render(request, 'uc_data_import/upload.html', {'form': form, 'error': 'Unknown UC system type'})

            return redirect('success')

    else:
        form = UploadFileForm()
    return render(request, 'uc_data_import/upload.html', {'form': form})

def success(request):
    return render(request, 'uc_data_import/success.html')

def upload_uc_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_path = handle_uploaded_file(file)
        # Trigger the Celery task
        process_uploaded_uc_file.delay(str(file_path))
        
        return HttpResponse(f"File uploaded and saved to {file_path}")
    return render(request, 'upload.html')
