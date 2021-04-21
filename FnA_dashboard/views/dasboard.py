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
from utils.department.department_info import read_write_department, Department_Data

class DepartmentDashboard(TemplateView):
    def get(self, request, department_name):
        context = {}
        sidebar_data = Department_Data(department_name).get_headers()
        context["columns"] = columns
        context["columns_len"] = range(0,len(columns))
        try:
            return render(request, sheet.code + "/index.html", context=context )
        except:
            return render(request,  "index.html", context=context )


def department_dashboard(department_name):
    context = {}
    sidebar_data = Department_Data(department_name)
    context["headers"], sidebar_data_content, context["department_name"] = sidebar_data.get_sidebar()

    fna = fna_sheets(request)['fna_sheets']
    gm = gm_sheets(request)['gm_sheets']

    fna_display_name = list(fna.values_list('display_name', flat=True))
    fna_display_name = [x.lower() for x in fna_display_name]

    gm_display_name = list(gm.values_list('display_name', flat=True))
    gm_display_name = [x.lower() for x in gm_display_name]

    for key, data in sidebar_data_content.items():
        final_sidebar = []
        for item in data:
            if item.lower() in fna_display_name:
                fna_item_index = fna_display_name.index(item.lower())
                sheet_id = fna[fna_item_index].id

                sheet = FnaSheet.objects.get(id=sheet_id)
                res = SheetData(sheet).get_count()

                final_sidebar.append({
                    'id': sheet_id,
                    'display_name': fna[fna_item_index].display_name,
                    'actual': res,
                    'target': 0,
                    'streek': 0
                })
            elif item.lower() in gm_display_name:
                gm_item_index = gm_display_name.index(item.lower())
                final_sidebar.append({
                    'id': gm[gm_item_index].id,
                    'display_name': gm[gm_item_index].display_name,
                    'actual': 0,
                    'target': 0,
                    'streek': 0
                })
            else:
                final_sidebar.append({
                    'id': 0,
                    'display_name': item,
                    'actual': 0,
                    'target': 0,
                    'streek': 0
                })
        sidebar_data_content[key] = final_sidebar

    context['sidebar_data'] = sidebar_data_content

    return context