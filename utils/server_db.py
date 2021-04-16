import pyodbc
from datetime import datetime
import csv

def query(sql_string):
    t = datetime.now()
    tmsstart = t.strftime('%f')

    server = r'CLS-SQL1\ESC' 
    database = 'CLSESC' 
    username = 'Python' 
    password = '!j4Steve12' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute(sql_string)
    sql_result = list(cursor.fetchall())
    #sql_result = list(cursor.fetchmany(50))
    cnxn.close
    t = datetime.now()
    tmsstop = t.strftime('%f')
    querytime = (int(tmsstop) - int(tmsstart))
    querytime = abs(querytime) / 1000
    textline = ("Query run times MillSeconds: " + str(querytime))
    #write_log(LogFilePath, textline)
    return sql_result

def update_query(sql_string):
    t = datetime.now()
    tmsstart = t.strftime('%f')

    server = r'CLS-SQL1\ESC' 
    database = 'CLSESC' 
    username = 'Python' 
    password = '!j4Steve12' 
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    sql_result = cursor.execute(sql_string)
    cnxn.commit()
    t = datetime.now()
    tmsstop = t.strftime('%f')
    querytime = (int(tmsstop) - int(tmsstart))
    querytime = abs(querytime) / 1000
    textline = ("Query run times MillSeconds: " + str(querytime))
    #write_log(LogFilePath, textline)
    return sql_result
    #------------------------
#-----------------------
def csv_report_builder(resultFyle,file_name,CSVList):
    resultFyle = resultFyle
    file_name = file_name
    CSVList = CSVList

    with open(resultFyle, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in CSVList:
            csv_writer.writerow (row)
    print(' CSV File: ' + file_name + ': completed successfully!')
    CSVList=[]
#-----------------
