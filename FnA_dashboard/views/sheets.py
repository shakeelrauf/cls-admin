from django.shortcuts import render
from FnA_dashboard.models import FnaSheet
from django.views.generic import TemplateView
from FnA_dashboard.utils.sheet_data  import SheetData
import pdb
from  utils.server_db import query, update_query
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json 

class IndexView(TemplateView):
    def get(self, request, sheet):
        context = {}
        FnaSheet.objects.filter(id=sheet).update(updated_at=datetime.now())
        sheet = FnaSheet.objects.get(id=sheet)
        columns = SheetData(sheet).get_headers()
        context["sheet"] = sheet
        context["columns"] = columns
        context["columns_len"] = range(0,len(columns))
        try:
            return render(request, sheet.code + "/index.html", context=context )
        except:
            return render(request,  "index.html", context=context )

def data_table_server_side(request, sheet):
    sheet = FnaSheet.objects.get(id=sheet)
    res = SheetData(sheet).get_table(request)
    return JsonResponse(res, safe=False)


def get_r3_PO_LED(request, po):
    sql = f"SELECT POLed.[Part], POLed.[Desc], POLed.[Quan], POLed.[Price], POLed.[Amount] FROM POLed WHERE POLed.[PO] = '{po}'"
    result = query(sql)
    res = []
    for row in result:
        res.append(list(row))
    return JsonResponse(res, safe=False)

@csrf_exempt
def update_r3_PO_LED(request):
    attr =  request.POST.get('attribute')
    value = request.POST.get('value')
    part =  request.POST.get('part')
    po =  request.POST.get('po')
    sql_query = f"UPDATE POLed SET {attr} = '{value}' WHERE POLed.[Part] = '{part}' AND POLed.[PO] = '{po}'"
    update_query(sql_query)
    return JsonResponse({}, safe=False)


def get_r3d_PO_LED(request, po):
    sql = f"SELECT POLed.[Part], POLed.[Desc], POLed.[Quan] FROM POLed WHERE POLed.[PO] = '{po}'"
    result = query(sql)
    res = []
    for row in result:
        res.append(list(row))
    return JsonResponse(res, safe=False)

def submit_pos(request):
    pos =  request.POST.get('POS', False)
    data = tuple(json.loads(pos))
    sql_pos  = data if len(data) > 1  else f"('{data[0]}')"
    sql_query = f"UPDATE PO SET OrderPlaced = '-1' WHERE PO.[PO] IN {sql_pos}"
    update_query(sql_query)
    return JsonResponse({"success": True}, safe=False)

def update_follow_up_date(request):
    po = request.POST.get("po")
    folow_up_date = request.POST.get("followUpDate")
    sql = f"UPDATE PO SET DateReq='{folow_up_date}' WHERE PO.[PO] = '{po}'"
    update_query(sql)
    return JsonResponse({"success": True , "msg": f"Successfully Updated {po} PO's Follow up Date"}, safe=False)
