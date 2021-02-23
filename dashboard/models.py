from django.db import models
from os import environ as env


# Create your models here.
class Sheet(models.Model):
    CSV_FILES = [{"display_name": "Actual Vs Quoted", "csv_path": env['STORAGE_DIR'] + 'ActualVSQuoted.csv', "script_path": env['STORAGE_DIR'], "config_name": "actual_vs_quoted"}]
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    display_name = models.TextField()
    config_name = models.TextField()
    csv_path = models.TextField()
    script_path = models.TextField()

    def create_default_sheets():
        print('creating or fetching csv files')
        for sheet in Sheet.CSV_FILES:
            obj = Sheet.objects.filter(config_name=sheet['config_name'])
            if not obj:
                Sheet.objects.create(csv_path=sheet['csv_path'], display_name=sheet['display_name'], config_name=sheet['config_name'], script_path=sheet['script_path'] )
