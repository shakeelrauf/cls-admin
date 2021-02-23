from utils.server_db import query, csv_report_builder
from sheets.forms.get_year_data import GetYearData
from pandas import read_csv
from itertools import islice
from numpy import nansum
from dashboard.models import Sheet
from numpy import nanmean
from os import path
import numpy as np
import pdb
import time
import environ
env = environ.Env()

class ActualVsQuoted():
    path = ''

    def __init__(self):
        file_path = env('STORAGE_DIR') + Sheet.objects.get(config_name='actual_vs_quoted').csv_path
        if not path.exists(file_path):
            raise Exception(f"Please check files at {file_path}")
        self.path = file_path

    def get_years_summary_data(self,years):
        df = read_csv(self.path)
        total_yearly_list = []
        for year in years:
            year_data = []
            year_data.append(year)
            qhrs = df.loc[df['Year'] == year, 'Quoted Hours Billed'].sum()
            ahrs = df.loc[df['Year'] == year, 'Actual Hours'].sum()
            ratio = qhrs /ahrs
            year_data.append(qhrs)
            year_data.append(ahrs)
            year_data.append(ratio)
            total_yearly_list.append(year_data)
        return total_yearly_list
    

    def get_specific_year_summary_data(self,year):
        df = read_csv(self.path)
        data = df[df['Year'] == int(year)].groupby(['Sales Person']).agg({'Quoted Hours Billed': 'sum', 'Actual Hours': 'sum' })
        data.columns = ['QuotedHours', 'ActualHours']
        data['Ratio'] = data['QuotedHours']/data['ActualHours']
        data = data.replace([np.inf, -np.inf], np.nan)
        return data.sort_values('Ratio', ascending=False).head(4).T.to_dict()

    def get_winner_of_year(self, year): 
        df = read_csv(self.path)
        data = df[df['Year'] == int(year)].groupby(['Sales Person']).agg({'Quoted Hours Billed': 'sum', 'Actual Hours': 'sum' })
        data.columns = ['QuotedHours', 'ActualHours']
        data['Ratio'] = data['QuotedHours']/data['ActualHours']
        data = data.replace([np.inf, -np.inf], np.nan)
        return data.sort_values('Ratio', ascending=False).head(1).T.to_dict()

    def get_all_json(self, request):
        order_col = request.GET['order[0][column]']
        order_dir = request.GET['order[0][dir]']
        if order_dir == 'asc':
            order_dir = True 
        else:
            order_dir = False
        df = read_csv(self.path)
        columns = list(df.columns)
        columns_length = len(columns)
        search_columns = {}
        for i in range(0, columns_length):
            if request.GET[f'columns[{i}][search][value]'] != '':
                search_columns[columns[i]] = request.GET[f'columns[{i}][search][value]']
        order_col = columns[int(order_col)]
        if order_col != '':
            df = df.sort_values(by=order_col, ascending=order_dir)
        for key in search_columns:
            df = df.loc[df[key].astype(str).str.contains(search_columns[key])]
        return df.to_json(orient='split', index=False)

    def get_all_columns_name(self):
        df = read_csv(self.path)
        return list(df.columns)

    def get_technicians_data(self):
        df = read_csv(self.path)
        aggre_eq = {}
        for column in df.columns[10:]:
            aggre_eq[column] =  nanmean
        df = df.replace(0, None)
        data = df.groupby('Year').agg(aggre_eq) 
        return data

    def average_of_data(self, data):
        average_array = []
        array = [[],[],[]]  
        for index in range(1,4):
            for row in data:
                array[index-1].append(row[index])
        for ar in array:
            average_array.append(Average(ar))
        return average_array

    def get_years_list(self):
        df = read_csv(self.path)
        data = df.groupby('Year').mean() 
        dictionary = data.T.to_dict()
        keys = list(dictionary.keys())
        years = keys[-3:]
        return years

    def shape_technicians_data_to_table(self, data, years):
        dictionary = data.T.to_dict()
        technicians_data = {}
        current_year = years[2]
        sorted_data = {k: v for k, v in sorted(dictionary[current_year].items(), key=lambda item: item[1], reverse=True)}
        top_technicians = list(take(15, sorted_data.items()))
        technicians_data[current_year] = top_technicians
        top_technicians_list = []
        for tech in top_technicians:
            top_technicians_list.append(list(tech))
        for year in years:
            if year != current_year:
                for tech in top_technicians_list:
                    tech.append(round(dictionary[year][tech[0]], 2))
        return top_technicians_list


    def get_years_from_db(self):
        sql_string = ('''SELECT 
        DISTINCT(DATEPART(year, ViewListInvoices.[Invoice Date])) AS Year
        FROM ViewListInvoices 
        ORDER BY Year DESC
        OFFSET 0 ROWS FETCH NEXT 3 ROWS ONLY
        ''')
        years = query(sql_string)
        years_list = []
        for year in years: 
            years_list.append(year[0])
        return years_list

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def Average(lst): 
    return sum(lst) / len(lst) 


