from django.shortcuts import render
from utils.server_db import query, csv_report_builder
from datetime import datetime
from gm_dashboard.models import GMSheet
from django.views.generic import TemplateView
from django.core import serializers
from django.http import HttpResponse
from gm_dashboard.forms.get_year_data import GetYearData
from pandas import read_csv
from utils.sheets.actual_vs_quoted import ActualVsQuoted
from utils.sheets.context import Context
from utils.sheets.process_sheets import ProcessSheets
import pdb
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import numpy as np
import functools 
import json
from django.http import JsonResponse

class IndexView(TemplateView):
    def get(self, request, sheet):
        sheet = GMSheet.objects.get(id=sheet)
        context = Context(sheet).get_index_view_context()
        context["sheet"] = sheet
        return render(request, sheet.config_name + "/index.html", context=context )

class SummaryView(TemplateView):

    def get(self, request, sheet):
        GMSheet.objects.filter(id=sheet).update(updated_at=datetime.now())
        sheet = GMSheet.objects.get(id=sheet)
        context =  Context(sheet).get_summary_view_context()
        context["sheet"] = sheet
        return render(request, sheet.config_name + "/summary.html", context=context )
    
    def post(self, request, sheet):
        year = request.POST.get('year')
        data = ActualVsQuoted().get_specific_year_summary_data(year)
        return render(request, "partials/details_year_data.html", context={"key": year, "values" : data.items()} )


class Sheet1SummaryYearlyView(TemplateView):
    template_name = 'sheet1/yearly.html'
    
    def get(self, request, sheet, year):
        data = get_data_from_db_server()
        context = {}
        data = list(filter(lambda x: x[3] == int(year), data))
        context["result_years"] = data
        context["year"] = year
        return render(request, self.template_name, context=context )

def create_yearly_data(data):
    yearl_data = {}
    for row in data:
        if row[3] is not None:
            if row[3] in yearl_data.keys():
                if row[1] > 0:
                    yearl_data[row[3]]["actual"] = yearl_data[row[3]]["actual"] + row[1]
                if row[2] > 0:
                    yearl_data[row[3]]["quoted"] = yearl_data[row[3]]["quoted"] + row[2]
            else:
                yearl_data[row[3]] = {"actual": 0, "quoted": 0}
                if row[1] > 0:
                    yearl_data[row[3]]["actual"] = row[1]
                if row[2] > 0:
                    yearl_data[row[3]]["quoted"] = row[2]
    sorted_data = sort_yearly(yearl_data)
    
    return sorted_data

def get_winner(request, sheet):
    year = request.POST.get('year')
    data = ActualVsQuoted().get_winner_of_year(year)
    return render(request, "partials/get_leader_details.html", context={"values" : data.items()} )

def get_json_sheet(request, sheet):
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    page = abs(int(offset/limit + 1))
    data = ActualVsQuoted().get_all_json(request)
    json_data = json.loads(data)
    length = len(json_data["data"])
    paginator = Paginator(json_data["data"], int(limit))
    objects = paginator.page(page)
    list_objs= list(objects)
    res = {
        "draw":  int(request.GET['draw']),
        "recordsTotal": length,
        "recordsFiltered": length,
        "data": list_objs,
    }
    return JsonResponse(res, safe=False)


def sort_yearly(data):
    sorted_data = {}
    for i in sorted(data, reverse=True): 
        sorted_data[i] = data[i]
        sorted_data[i]["ratio"] =round(data[i]["quoted"] / data[i]["actual"], 2)
    sorted_data.popitem()
    sorted_data.popitem()
    sorted_data.popitem()
    return sorted_data

def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
