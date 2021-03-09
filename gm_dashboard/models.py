from django.db import models
from os import environ as env
from datetime import date

class Sheet(models.Model):
    CSV_FILES = [{"display_name": "Actual Vs Quoted", "csv_path": env['STORAGE_DIR'] + 'ActualVSQuoted.csv', "script_path": env['STORAGE_DIR'], "config_name": "actual_vs_quoted"}]
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    display_name = models.TextField()
    config_name = models.TextField()
    csv_path = models.TextField()
    script_path = models.TextField()
    code = models.TextField()
    TYPE_CHOICES = [
        ('FnA', 'FnA'),
        ('GM', 'GM')
    ]
    sheet_type = models.CharField(max_length=25, choices=TYPE_CHOICES)

    @property
    def is_seen_today(self):
        return date.today() == self.updated_at.date()

class GMManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(sheet_type='GM')

class GMSheet(Sheet):
  objects = GMManager()

  class Meta:
    proxy = True