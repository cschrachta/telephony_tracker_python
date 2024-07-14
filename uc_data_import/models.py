from django.db import models

# Create your models here.
class UCSystemFile(models.Model):
    file = models.FileField(upload_to='uc_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class UCDataImport(models.Model):
    file_name = models.CharField(max_length=255)
    system_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.system_name} - {self.version} - {self.file_name}"