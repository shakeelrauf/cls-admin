from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from gm_dashboard.models import GMSheet
from utils.sheets.process_sheets import ProcessSheets
from django.views.decorators.csrf import csrf_exempt

import time
import pdb

class DashboardIndexView(TemplateView):
    template_name = 'dashboard/index.html'
    def get(self, request):
        sheets = GMSheet.objects.all()
        context = {}
        context["sheets"] = sheets
        res = ProcessSheets().get_process_id()
        if res['status'] == 'running':
            context['running'] = res
        return render(request, self.template_name, context=context )

class SheetStatusView(TemplateView):
    def post(self, request):
        res = ProcessSheets().get_process_id()
        return JsonResponse(res, safe=False)

class RunSheetScriptView(TemplateView):
    def post(self, request, sheet):
        sheet =  GMSheet.objects.get(pk=sheet)
        if sheet:
            res = ProcessSheets().run_script(sheet)
            return JsonResponse(res, safe=False)

@csrf_exempt
def update_sheet(request):
    id = int(request.POST['id'])
    value = (request.POST['value'])
    sheet = GMSheet.objects.filter(id=id).update(display_name=value)
    return JsonResponse(sheet, safe=False)
