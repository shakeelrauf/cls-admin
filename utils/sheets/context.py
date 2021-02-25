from pandas import read_csv
from itertools import islice
from numpy import nansum
from gm_dashboard.forms.get_year_data import GetYearData
from utils.sheets.actual_vs_quoted import ActualVsQuoted
from numpy import nanmean
from utils.server_db import query, csv_report_builder
import numpy as np
import pdb
import time


class Context():
    path = ''
    sheet = ''

    def __init__(self, sheet):
        self.path = sheet.csv_path
        self.sheet = sheet
    
    def get_summary_view_context(self):
        return eval(self.sheet.config_name+"_summary_context"+"()")

    def get_index_view_context(self):
        return eval(self.sheet.config_name + "_index_context()")

def actual_vs_quoted_index_context():
    context = {}
    data = ActualVsQuoted().get_all_columns_name()
    context["columns"] = data
    return context

def actual_vs_quoted_summary_context():
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
    return context
