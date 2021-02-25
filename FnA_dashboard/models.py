from django.db import models
from gm_dashboard.models import Sheet

# Create your models here.

class FnAManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(sheet_type='FnA')

class FnaSheet(Sheet):
  objects = FnAManager()

  class Meta:
    proxy = True