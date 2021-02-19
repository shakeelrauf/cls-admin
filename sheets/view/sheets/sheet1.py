from django.shortcuts import render
from utils.server_db import query, csv_report_builder
from datetime import datetime
from django.views.generic import TemplateView
from django.core import serializers
from django.http import HttpResponse
from sheets.forms.get_year_data import GetYearData
from pandas import read_csv
from utils.sheets.actual_vs_quoted import ActualVsQuoted
from utils.sheets.process_sheets import ProcessSheets
import pdb
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import numpy as np
import functools 
import json
from django.http import JsonResponse

class Sheet1View(TemplateView):
    template_name = 'sheet1/index.html'
    
    def get(self, request, sheet):
        context = {}
        data = ActualVsQuoted().get_all_columns_name()
        context["columns"] = data
        return render(request, self.template_name, context=context )

class Sheet1SummaryView(TemplateView):
    template_name = 'sheet1/summary.html'
    
    def get(self, request, sheet):
        sheet = ActualVsQuoted()
        context = {}
        years_list = sorted(sheet.get_years_list(), reverse=True)
        yearly_data = sheet.get_years_summary_data(years_list)
        technicians_data = sheet.get_technicians_data()
        technicians_list = sheet.shape_technicians_data_to_table(technicians_data, years_list)
        technicians_average = sheet.average_of_data(technicians_list)
        golden_ratio =  float(yearly_data[0][3])
        target_golder_ratio = 1
        get_year_form = GetYearData(choices=years_list)
        if golden_ratio > 1:
            difference = "+ " +str(round(golden_ratio - target_golder_ratio, 2)  * 100) + " %"
        else:
            difference  ="- " + str((round(target_golder_ratio - golden_ratio, 2)) * 100) + "%"
        context["golden_ratio"] = {"difference": difference,"golden_ratio": golden_ratio,"target": target_golder_ratio}
        context["form"] = get_year_form
        context["yearly_data"] = yearly_data
        context["first_year"] = years_list[0]
        context["years_list"] = years_list
        context["technicians_list"] = technicians_list
        context["technicians_average"] = technicians_average
        return render(request, self.template_name, context=context )
    
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

class Sheet1SalesPersonSummaryView(TemplateView):
    template_name = 'sheet1/person.html'
    def get(self, request, sheet,year, person):
        sql_string = ('''SELECT
            ViewListInvoices.Invoice,
            ViewListInvoices.Dispatch,
            ViewListInvoices.[Sales Person Name],
            SalesLed.Quan,
            SalesLed.Price,
            DATEDIFF(hour,ViewListDispatches.[Date And Time On],
            ViewListDispatches.[Date And Time Off]), 
            DATEPART(week, ViewListInvoices.[Invoice Date]) AS DatePartInt,
            DATEPART(year, ViewListInvoices.[Invoice Date]) AS DatePartInt,
            DATEPART(month, ViewListInvoices.[Invoice Date]) AS DatePartInt,
            DATEPART(day, ViewListInvoices.[Invoice Date]) AS DatePartInt
            FROM ViewListInvoices 
            INNER JOIN SalesLed ON ViewListInvoices.Invoice = SalesLed.Invoice 
            RIGHT JOIN ViewListDispatches ON ViewListInvoices.Invoice = ViewListDispatches.invoice
            RIGHT JOIN Users ON ViewListDispatches.Tech = Users.TechID
            WHERE (ViewListDispatches.Status = 'complete' OR ViewListDispatches.Status = 'off job') AND
            (SalesLed.Prod LIKE '%Labour%'
            OR SalesLed.Prod = 'Min-Charge')
            AND DATEPART(year, ViewListInvoices.[Invoice Date]) = '{year}'
            AND ViewListInvoices.[Sales Person Name] = '{person}'
            ''').format(person=person, year=year)
        data = query(sql_string)
        context = {"data" : data}
        return render(request, self.template_name, context=context )

def get_data_from_db_server():
    sql_string = ('''SELECT
        ViewListInvoices.[Sales Person Name],
        CAST(SUM(DATEDIFF(hour,ViewListDispatches.[Date And Time On],
        ViewListDispatches.[Date And Time Off])) AS DECIMAL(16,2)) AS Actual, 
        CAST(SUM(SalesLed.Quan) AS DECIMAL(16,2)) AS Quoted,
        DATEPART(year, ViewListInvoices.[Invoice Date]) AS DatePartInt
        FROM ViewListInvoices
        INNER JOIN SalesLed ON ViewListInvoices.Invoice = SalesLed.Invoice 
        RIGHT JOIN ViewListDispatches ON ViewListInvoices.Invoice = ViewListDispatches.invoice
        RIGHT JOIN Users ON ViewListDispatches.Tech = Users.TechID
        WHERE (ViewListDispatches.Status = 'complete' OR ViewListDispatches.Status = 'off job') AND
        (SalesLed.Prod LIKE '%Labour%'
        OR SalesLed.Prod = 'Min-Charge')
        AND ViewListInvoices.[Sales Person Name] in (
                    SELECT Employee.EmpName,
                    FROM Employee INNER JOIN Users ON Employee.EmpNo = Users.TechID
                    RIGHT JOIN  ViewListDispatches on ViewListDispatches.[Tech Name] = Employee.EmpName)
        group by DATEPART(year, ViewListInvoices.[Invoice Date]), 
        ViewListInvoices.[Sales Person Name]
        ORDER BY SUM(DATEDIFF(hour,ViewListDispatches.[Date And Time On],
        ViewListDispatches.[Date And Time Off]))
        ''')
        
    data = query(sql_string)
    return data

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
    
def run_script(request):
    response = ProcessSheets().run_script()
    return JsonResponse(response, safe=False)


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
