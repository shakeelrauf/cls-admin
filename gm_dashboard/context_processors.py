from gm_dashboard.models import GMSheet
from FnA_dashboard.models import FnaSheet
import pdb


def gm_sheets(request):
    """
      The context processor must return a dictionary.
    """
    sheets = GMSheet.objects.all() #query the latest banner image
    return {'gm_sheets':sheets} 


def fna_sheets(request):
    """
      The context processor must return a dictionary.
    """
    sheets = FnaSheet.objects.all() #query the latest banner image
    return {'fna_sheets':sheets} 