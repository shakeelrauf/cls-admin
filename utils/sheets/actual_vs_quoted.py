from pandas import read_csv
from itertools import islice
from numpy import nansum
from gm_dashboard.models import GMSheet
from gm_dashboard.forms.get_year_data import GetYearData
from numpy import nanmean
from utils.server_db import query, csv_report_builder
import numpy as np
import pdb
import time
import environ
env = environ.Env()

class ActualVsQuoted():
    path = ''

    def __init__(self):
        self.path = env('STORAGE_DIR') + GMSheet.objects.get(config_name='actual_vs_quoted').csv_path

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

def get_and_save_csv_from_db_actual_vs_quoted():
    time.sleep(100)
    config_tech = []
    config_Labour = []
    invoiceList=[]
    dispatchList=[]

    Actual_vs_Quoted_PM=[]
    templist=[]
    templist2=[]

    #load Config files from ESC
    sql_string = ('''SELECT Employee.EmpName,
            Employee.Crew
            FROM Employee INNER JOIN Users ON Employee.EmpNo = Users.TechID
            ''')
    sql_result = query(sql_string)
    config_tech = sorted(sql_result.get_list())
    sql_result =[]

    #Find Labour rates 
    sql_string = ('''SELECT Inven.Part,
            Inven.BillRate
            FROM Inven
            WHERE Inven.Part LIKE '%Labour%'
            OR Inven.Part = 'Min-Charge'
            ''')
    sql_result = query(sql_string)
    config_Labour = sorted(sql_result.get_list())
    sql_result =[]

    #laod all Invocices that have a Labour part number in it. 
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
            
            ''')
            # AND ViewListInvoices.Invoice = '0000147490'
    sql_result = query(sql_string)
    invoiceList = sorted(sql_result.get_list())
    sql_result =[]

    #laod All Dispatches that are complete or tech is off job 
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
            #AND ViewListDispatches.Dispatch = '98199'
    sql_result = query(sql_string)
    dispatchList = sorted(sql_result.get_list())
    sql_result =[]

    # Add total labour charges together reduce invoicelist pull labour rates from config_labour
    InvLstCnt = len(invoiceList) - 1
    check = invoiceList[InvLstCnt][0]
    while InvLstCnt >= 0:
        #Fixed items to be copied over while merging duplicated invoice lines 
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
        Labourcode = invoiceList[InvLstCnt][3]
        
        #Min charges to be calculated differently 
        minlabcharge = False

        #Vars to be updated based on labour items and amount per line in each invoice. 
        totalhrsqty = 0
        totalhrsbill = 0
        
        while check == invnum:
        #bug need to add next 2 lines 
            QHrsQty = invoiceList[InvLstCnt][5]
            QHrsBill = invoiceList[InvLstCnt][6]
        #-------------------------------------------
            totalhrsqty += QHrsQty
        # Bug remove next 1 lines     
        #    totalhrsbill += QHrsBill
        #---------------------------------------------    
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
            #bug Fix remove next 7 lines    
            #    try:
            #        totalhrsbill = (totalhrsqty*totalhrsbill)/labourRate
            #        totalhrsbill = round(totalhrsbill,2)
            #    except:
            #        labourRate = 0.01
            #        totalhrsbill = (totalhrsqty*totalhrsbill)/labourRate
            #        totalhrsbill = round(totalhrsbill,2)
            #----------------------------------------------------------------------------------------------------
                # Bug fix Add next 7 lines 
                try:
                    totalhrsbill = totalhrsbill + ((QHrsBill*QHrsQty)/labourRate)
                    totalhrsbill = round(totalhrsbill,2)
                except:
                    labourRate = 0.01
                    totalhrsbill = totalhrsbill + ((QHrsBill*QHrsQty)/labourRate)
                    totalhrsbill = round(totalhrsbill,2)
                #---------------------------------------------------------------------------------------------------------

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
        #calcualte time for techs on site
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
                    q = row[4]
                    a = row[5]
                    e = q/a*100
                    t1e = (100 - (techhour / a) * (100 - e))
                    t1e = round(t1e, 2)
                    row[itemid] = t1e
                else:
                    row[itemid] = ''
                itemid += 1
        except:
            pass #header nothng to do
        x -= 1
        print("ratio calculation : " + str(x))    

    Actual_vs_Quoted_PM = templist2
    templist=()
    templist2=()

    resultFyle = +'ActualVSQuoted.csv'
    CSVList = Actual_vs_Quoted_PM
    file_name = 'ActualVSQuoted.csv'
    csv_report_builder(resultFyle,file_name,CSVList)
    Actual_vs_Quoted_PM=[]
