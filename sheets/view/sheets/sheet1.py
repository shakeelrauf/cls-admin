from django.shortcuts import render
from utils.server_db import query, csv_report_builder
import pdb
from datetime import datetime
from django.views.generic import TemplateView
from django.core import serializers
from django.http import HttpResponse
from sheets.forms.get_year_data import GetYearData
from pandas import read_csv
import numpy as np
from itertools import islice


class Sheet1View(TemplateView):
    template_name = 'sheet1/index.html'
    
    def get(self, request, sheet):
        context = {}
        limit = 20
        page  = request.GET.get('page') or 1
        page = int(page)
        offset = limit * page -1
        config_tech = []
        config_Labour = []
        Actual_vs_Quoted_PM=[]
        invoiceList=[]
        dispatchList=[]
        templist=[]
        templist2=[]
        sql_string = ('''SELECT Employee.EmpName,
                Employee.Crew
                FROM Employee INNER JOIN Users ON Employee.EmpNo = Users.TechID
                ''')
        sql_result = query(sql_string)
        config_tech = sorted(sql_result)
        sql_result =[]

        sql_string = ('''SELECT Inven.Part,
                Inven.BillRate
                FROM Inven
                WHERE Inven.Part LIKE '%Labour%'
                OR Inven.Part = 'Min-Charge'
                ''')
        sql_result = query(sql_string)
        config_Labour = sorted(sql_result)
        sql_result =[]

        sql_string = ('''SELECT ViewListInvoices.Invoice,
                ViewListInvoices.Dispatch,
                ViewListInvoices.[Sales Person Name],
                SalesLed.Prod,
                SalesLed.[Desc],
                SalesLed.Quan,
                SalesLed.Price,
                ViewListInvoices.[Invoice Date]
                FROM ViewListInvoices INNER JOIN SalesLed ON ViewListInvoices.Invoice = SalesLed.Invoice
                WHERE (SalesLed.Prod LIKE '%Labour%'
                OR SalesLed.Prod = 'Min-Charge')
                AND ViewListInvoices.[Sales Person Name] IS Not Null
                Order by ViewListInvoices.Invoice
                OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
                ''').format(offset=offset, limit=limit)
                # AND ViewListInvoices.Invoice = '0000145046'

        sql_result = query(sql_string)
        invoiceList = sorted(sql_result)
        sql_result =[]
            
        my_sheet = 'ActualVSQuoted' # change it to your sheet name, you can find your sheet name at the bottom left of your excel file
        file_name = 'ActualVSQuoted.csv' # change it to the name of your excel file
        df = read_csv(file_name)
        pdb.set_trace()
        print(df.head())
       # pdb.set_trace()

        total = ('''SELECT Count(*) as Total
                FROM ViewListInvoices INNER JOIN SalesLed ON ViewListInvoices.Invoice = SalesLed.Invoice
                WHERE (SalesLed.Prod LIKE '%Labour%'
                OR SalesLed.Prod = 'Min-Charge')
                AND ViewListInvoices.[Sales Person Name] IS Not Null
                ''')
                # AND ViewListInvoices.Invoice = '0000145046'
        total_result = query(total)
        totalInvoice = sorted(total_result)
        totalPages = int(int(totalInvoice[0][0])/limit)
        sql_string = ('''SELECT ViewListDispatches.Dispatch,
                ViewListDispatches.invoice,
                ViewListDispatches.[Tech Name],
                ViewListDispatches.Status,
                ViewListDispatches.[Date And Time On],
                ViewListDispatches.[Date And Time Off],
                ViewListDispatches.[Date completed]
                FROM ViewListDispatches RIGHT JOIN Users ON ViewListDispatches.Tech = Users.TechID
                WHERE (ViewListDispatches.Status = 'complete' OR ViewListDispatches.Status = 'off job')
                ''')
                #AND ViewListDispatches.Dispatch = '96689'
        # pdb.set_trace()
        sql_result = query(sql_string)
        dispatchList = sorted(sql_result)
        sql_result =[]

        # add total labour charges together reduce invoicelist pull labour rates from config_labour
        InvLstCnt = len(invoiceList) - 1
        check = invoiceList[InvLstCnt][0]
        while InvLstCnt >= 0:
            invnum = invoiceList[InvLstCnt][0]
            dispnum = invoiceList[InvLstCnt][1]
            pm = invoiceList[InvLstCnt][2]
            QHrsQty = invoiceList[InvLstCnt][5]
            QHrsBill = invoiceList[InvLstCnt][6]
            ActualHrs = ''
            weekNum = datetime.date(invoiceList[InvLstCnt][7])
            weekNum = weekNum.strftime("%U")
            year = datetime.date(invoiceList[InvLstCnt][7])
            year = year.strftime("%Y")
            month = datetime.date(invoiceList[InvLstCnt][7])
            month = month.strftime("%m")
            day = datetime.date(invoiceList[InvLstCnt][7]) 
            day = day.strftime("%d")

            totalhrsqty = 0
            totalhrsbill = 0
            minlabcharge = False
            Labourcode = invoiceList[InvLstCnt][3]

            while check == invnum:
                totalhrsqty += QHrsQty
                totalhrsbill += QHrsBill
                #find labour rate add to if labour code changes 
                if Labourcode == invoiceList[InvLstCnt][3]:
                    result = list(filter(lambda x: x[0] ==Labourcode, config_Labour))
                    labourRate = result[0][1]
                else:
                    result = list(filter(lambda x: x[0] ==Labourcode, config_Labour))
                    labourRate += result[0][1]
                InvLstCnt -= 1
                if InvLstCnt >= 0: 
                    check = invoiceList[InvLstCnt][0]
                else:
                    check=''
                if Labourcode == 'MIN-CHARGE':
                    minlabcharge = True
                else:
                    try:
                        totalhrsbill = (totalhrsqty*labourRate)/labourRate
                    except:
                        labourRate = 0.01
                        totalhrsbill = (totalhrsqty*labourRate)/labourRate

            if minlabcharge == True:
                totalhrsqty = 1   
                totalhrsbill = 1
                minlabcharge = False

            templist = (invnum,dispnum,pm,totalhrsqty,totalhrsbill,ActualHrs,weekNum,year,month,day)
            templist2.append(templist)
            print("prossesing invoice check: " + str(InvLstCnt))
        invoiceList = templist2        
        templist=[]
        templist2=[]
        #add tech hours tech names and time they worked to the invoice list.    
        InvLstCnt = len(invoiceList) -1
        check = invoiceList[InvLstCnt][1]
        #add all techs to header below based on config_tech list
        templist = ['Invoice #','Dispatch #','Sales Person','Quoted Hours Qty','Quoted Hours Billed','Actual Hours','Week#','Year','Month','Day']
        # pdb.set_trace()
        get_tech_data()
        
        for row in config_tech:
            templist.insert(len(templist), row[0],)
        templist2.append(templist)

        tl2row = 1 #templist 2 row id
        while InvLstCnt >= 0:     
            invnum = invoiceList[InvLstCnt][0]
            dispnum = invoiceList[InvLstCnt][1]
            pm = invoiceList[InvLstCnt][2]
            QHrsQty = invoiceList[InvLstCnt][3]
            QHrsBill = invoiceList[InvLstCnt][4]
            ActualHrs = ''
            weekNum = invoiceList[InvLstCnt][6]
            year =invoiceList[InvLstCnt][7]
            month = invoiceList[InvLstCnt][8]
            day = invoiceList[InvLstCnt][9]
            
            result = list(filter(lambda x: x[0] == check, dispatchList))
            totaltime = 0
            #calcualsste time for techs on site
            for row in result:
                timeon = row[4]
                timeoff = row[5]
                try:
                    Duration = timeoff - timeon
                    Duration_In_Seconds = Duration.total_seconds()
                    Minutes = divmod(Duration_In_Seconds, 60)[0]
                    Minutes = float(abs(Minutes))
                    Hours_temp = Minutes/60
                except:
                    Hours_temp = 0
                totaltime += Hours_temp
                totaltime = round(totaltime,2)
            templist = [invnum,dispnum,pm,QHrsQty,QHrsBill,totaltime,weekNum,year,month,day]
            x=len(templist2[0])
            x -= 11
            insertindex = 10

            while x >= 0:
                templist.insert(insertindex ,'0')
                x -= 1
                insertindex += 1
            templist2.append(templist)

            #list all techs on this invoice
            for row in result:

                timeoff = row[5]
                timeon = row[4]
                try:
                    Duration = timeoff - timeon
                    Duration_In_Seconds = Duration.total_seconds()
                    Minutes = divmod(Duration_In_Seconds, 60)[0]
                    Minutes = float(abs(Minutes))
                    Hours_temp = Minutes/60
                except:
                    Hours_temp = 0
                Hours_temp = round(Hours_temp,2)
                #pdb.set_trace()

                techname = str(row[2])
                techname = templist2[0].index(row[2])
                Hours_temp = Hours_temp + int(templist2[tl2row][techname])
               
                templist2[tl2row][techname] = Hours_temp
            tl2row += 1    
            InvLstCnt -= 1
            check = invoiceList[InvLstCnt][1]
            print("Calcualting dispatches: " + str(InvLstCnt))

        #Calculate tech ratios from total times and up date list. 
        #get tech count start and end for list items . 
        techcount = len(config_tech) + 10
        
        techhour = 0
        #overall efficiency
        e = 0
        #actual hours
        a = 0
        #quoted
        q =0
        #tech efficiance 
        t1e = 0
        x = len(templist2)
        for row in templist2:
            itemid = 10
            try:
                while itemid < techcount:
                    techhour = float(row[itemid])
                    if techhour > 0:
                        #change hours to efficanse 
                        #load E and A
                        q = row[3]
                        a = row[5]
                        e = q/a
                        t1e = 100 - (techhour / a) * (100 - e)
                        t1e = round(t1e, 2)
                        row[itemid] = t1e

                    itemid += 1
            except:
                pass #header nothng to do
            x -= 1
            print("ratio calculation : " + str(x))    

        Actual_vs_Quoted_PM = templist2
        templist=()
        templist2=()

        CSVList = Actual_vs_Quoted_PM
        Actual_vs_Quoted_PM=[]
        context["header"] = CSVList[0]
        del CSVList[0]
        context["data"] = CSVList
        context["total_pages"] = range(1,totalPages)
        context["total_pages_count"] =  totalPages
        context["current_page"] =  page
        context["next_page"] = page+ 1
        context["prev_page"] = page - 1

        return render(request, self.template_name, context=context )



class Sheet1SummaryView(TemplateView):
    template_name = 'sheet1/summary.html'
    
    def get(self, request, sheet):
        #data = get_data_from_db_server(#)
        #pdb.set_trace()
        context = {}
        #sql_string = ('''SELECT 
       # DISTINCT(DATEPART(year, ViewListInvoices.[Invoice Date])) AS Year
        #FROM ViewListInvoices 
        #ORDER BY Year DESC
        #OFFSET 0 ROWS FETCH NEXT 3 ROWS ONLY
        #''')
        #years = query(sql_string)
        #years_list = []
        #for year in years: 
         #   years_list.append(year[0])
        years_list  =[2020, 2019, 2018]
        yearly_data = get_years_data(years_list)
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
        context["technicians_list"] =  get_technicians_data(years_list)
        return render(request, self.template_name, context=context )
    
    def post(self, request, sheet):
        
        year = request.POST.get('year')
        data = get_year_data(year)
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
    
def get_years_data(years):
    file_name = 'ActualVSQuoted.csv' # change it to the name of your excel file
    df = read_csv(file_name)
    total_yearly_list = []
    for year in years:
        year_data = []
        year_data.append(year)
        qhrs = df.loc[df['Year'] == year, 'Quoted Hours Qty'].sum()
        ahrs = df.loc[df['Year'] == year, 'Actual Hours'].sum()
        ratio = qhrs /ahrs
        year_data.append(qhrs)
        year_data.append(ahrs)
        year_data.append(ratio)
        total_yearly_list.append(year_data)
    return total_yearly_list

def get_year_data(year):
    file_name = 'ActualVSQuoted.csv'
    df = read_csv(file_name)
    data = df[df['Year'] == int(year)].groupby(['Sales Person']).agg({'Quoted Hours Qty': 'sum', 'Actual Hours': 'sum' })
    data.columns = ['QuotedHours', 'ActualHours']
    data['Ratio'] = data['QuotedHours']/data['ActualHours']
    data = data.replace([np.inf, -np.inf], np.nan)
    return data.sort_values('Ratio', ascending=False).head(4).T.to_dict()

def get_technicians_data(years):
    file_name = 'ActualVSQuoted.csv'
    df = read_csv(file_name)
    aggre_eq = {}
    for column in df.columns[10:]:
        aggre_eq[column] =  'sum'
    data = df.groupby('Year').agg(aggre_eq)
    dictionary = data.T.to_dict()
    technicians_data = {}
    current_year = 2020
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
     

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))