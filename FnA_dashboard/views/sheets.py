from django.shortcuts import render
from FnA_dashboard.models import FnaSheet
from django.views.generic import TemplateView
from FnA_dashboard.utils.sheet_data  import SheetData
import pdb
from  utils.server_db import query
from django.http import JsonResponse


class IndexView(TemplateView):
    def get(self, request, sheet):
        context = {}
        sheet = FnaSheet.objects.get(id=sheet)
        context["sheet"] = sheet
        context["columns"] = SheetData(sheet).get_headers()
        try:
            return render(request, sheet.code + "/index.html", context=context )
        except:
            return render(request,  "index.html", context=context )

def data_table_server_side(request, sheet):
    sheet = FnaSheet.objects.get(id=sheet)
    res = SheetData(sheet).get_table(request)
    return JsonResponse(res, safe=False)


def get_PO_LED(request, po):
    sql = f"SELECT POLed.[Part], POLed.[Desc], POLed.[Quan], POLed.[Price], POLed.[Amount] FROM POLed WHERE POLed.[PO] = '{po}'"
    result = query(sql)
    res = []
    for row in result:
        res.append(list(row))
    return JsonResponse(res, safe=False)
