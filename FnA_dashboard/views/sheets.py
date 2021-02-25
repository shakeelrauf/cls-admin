from django.shortcuts import render
from FnA_dashboard.models import FnaSheet
from django.views.generic import TemplateView
from FnA_dashboard.utils.sheet_data  import SheetData
import pdb
from django.http import JsonResponse


class IndexView(TemplateView):
    def get(self, request, sheet):
        context = {}
        sheet = FnaSheet.objects.get(id=sheet)
        context["sheet"] = sheet
        context["columns"] = SheetData(sheet).get_headers()
        return render(request, sheet.code + "/index.html", context=context )


def data_table_server_side(request, sheet):
    sheet = FnaSheet.objects.get(id=sheet)
    res = SheetData(sheet).get_table(request)
    return JsonResponse(res, safe=False)
