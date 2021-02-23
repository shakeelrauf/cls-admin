from dashboard.models import Sheet


def sheets(request):
    """
      The context processor must return a dictionary.
    """
    sheets = Sheet.objects.all() #query the latest banner image
    return {'sheets':sheets} 