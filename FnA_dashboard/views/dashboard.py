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
from gm_dashboard.context_processors import fna_sheets, gm_sheets
from django.core.paginator import Paginator
from utils.server_db import query

class DepartmentDashboard(TemplateView):
    def get(self, request, department_name):
        context = {}
        columns = Department_Data(department_name).get_headers()
        # context["columns"] = columns
        # context["columns_len"] = range(0,len(columns))
        
        context["columns"] = {}
        for c in columns:
            context["columns"][c] = dashboard_datatable(request, c, department_name)

        return render(request, "dashboard.html", context=context )


class DatatableClass():
    def __init__(self, id, name, actual):
        self.id = id
        self.name = name
        self.actual = actual

    def get_obj(self):
        return self


def format_datatable_request(datatables):
    request = {}
    request["draw"] = int(datatables.get('draw')) if datatables.get('draw') else ''
    request["start"] = int(datatables.get('start')) if datatables.get('start') else ''
    request["total"] = int(datatables.get('length')) if datatables.get('length') else ''
    request["ordercol"] = int(datatables.get('order[0][column]')) if datatables.get('order[0][column]') else ''
    request["order"] = datatables.get('order[0][dir]') if datatables.get('order[0][dir]') else ''
    request["reverse"] = request["order"] == "asc"
    return request


def ordering_datatable_response(order_list, formatted_req, request):
    # members_order_list = order_list

    formatted_req["total"] = len(order_list) if formatted_req["total"] == -1 else formatted_req["total"]

    filtered_count = len(order_list)

    # members_order_list = sort_datatable_data(members_order_list, formatted_req, 1, ORDER_COLS_MEMBERS_LISTING)

    members_order_list = order_list[formatted_req["start"]:formatted_req["start"] + formatted_req["total"]]
    paginator = Paginator(members_order_list, formatted_req["total"])
    return [paginator, filtered_count]


def response_dump(paginator, start, draw, total_uses):
    try:
        data = paginator.page(0).object_list
    except:
        data = paginator.page(1).object_list
    resp = {
        "draw": draw,
        "recordsTotal": total_uses,
        "recordsFiltered": total_uses,
        "data": list(data)
    }
    return resp


def dashboard_datatable(request, item_name, department_name):
    context = {}
    columns_name = Department_Data(department_name).get_items(item_name)
    fna = fna_sheets(request)['fna_sheets']
    gm = gm_sheets(request)['gm_sheets']

    fna_display_name = list(fna.values_list('display_name', flat=True))
    fna_display_name = [x.lower() for x in fna_display_name]

    gm_display_name = list(gm.values_list('display_name', flat=True))
    gm_display_name = [x.lower() for x in gm_display_name]
    
    final_list = []
    for item in columns_name:
        if item.lower() in fna_display_name:
            fna_item_index = fna_display_name.index(item.lower())
            sheet_id = fna[fna_item_index].id

            sheet = FnaSheet.objects.get(id=sheet_id)
            res = SheetData(sheet).get_count()
            res = query(res)[0][0]
            # obj = DatatableClass(sheet_id, fna[fna_item_index].display_name, res)
            # final_list.append(obj.get_obj())
            final_list.append({
                'id': sheet_id,
                'display_name': fna[fna_item_index].display_name,
                'actual': res,
                'target': 0,
                'streek': 0
            })

        elif item.lower() in gm_display_name:
            gm_item_index = gm_display_name.index(item.lower())
            final_list.append({
                'id': gm[gm_item_index].id,
                'display_name': gm[gm_item_index].display_name,
                'actual': 0,
                'target': 0,
                'streek': 0
            })
        else:
            final_list.append({
                'id': 0,
                'display_name': item,
                'actual': 0,
                'target': 0,
                'streek': 0
            })

    return final_list

    # formatted_req = format_datatable_request(request.GET)
    # paginator, filtered_count = ordering_datatable_response(final_list, formatted_req, request)
    # return JsonResponse(response_dump(paginator, formatted_req["start"], formatted_req["draw"], filtered_count))


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
