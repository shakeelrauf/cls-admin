
from django.shortcuts import redirect

def redirect_to_gm(request):
    response = redirect('/gm/')
    return response