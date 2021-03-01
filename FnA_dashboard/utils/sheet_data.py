from utils.server_db import query
import pdb

class SheetData(object):
    def __init__(self, sheet):
        self.sheet = sheet

    HEADERS = {
        "R-3": {
            "keys": ["PO.PO", "PO.Date", "Vendor.Company"],
            "headers": ["PO", "Date", "Vendor Name"]
        },
        "R-3-A": {
            "keys" : ["POLed.[Part]", "CAST(POLed.[Desc] AS NVARCHAR(100))","POLed.[Quan]","POLed.[Received]", "(POLed.[Quan] - POLed.[Received]) ","PO.[PO]","convert(varchar(10), cast(PO.[Date] as date), 101)","convert(varchar(10), cast(PO.[DateReq] as date), 101)", "PO.[ShipName]"],
            "headers" : ["Part Number","Description", "Qty Ordered", "Qty Received", "Balance", "PO Number", "Entry Date", "Expected Date", "Vendor Name"]
        }, 
        "R-3-B": {
            "keys": ["InvQuan.[Part]", "ViewListItems.[Description]", "InvQuan.[MinQuan]", "InvQuan.[ReOrder]", "ViewListItems.[Quantity In Stock]"],
            "headers": ["Part" , "Description", "Min order point", "ReOrder Point", "Quantity In Stock"]
        },
        "R-3-C": {
            "keys" : ["Inven.[Part]", "CAST(Inven.[Desc] AS NVARCHAR(100))", "Inven.[BPrice]"],
            "headers" : ["Part Number","Description", "Base Price"]
        }
    }
    QUERIES = {
        "R-3": {
            "data" : f"SELECT {', '.join(HEADERS['R-3']['keys'])} FROM PO LEFT JOIN Vendor ON PO.Vendor = Vendor.Vendor",
            "count" : "SELECT COUNT(*) FROM PO LEFT JOIN Vendor ON PO.Vendor = Vendor.Vendor "
        },
        "R-3-A": {
            "data" : f"Select {', '.join(HEADERS['R-3-A']['keys'])} FROM PO INNER  JOIN POLed on PO.[PO] = POLed.[PO]",
            "count" : "Select COUNT(*) FROM PO INNER  JOIN POLed on PO.[PO] = POLed.[PO]",
        },
        "R-3-B": {
            "data" : f"Select {', '.join(HEADERS['R-3-B']['keys'])} FROM InvQuan LEFT JOIN ViewListItems ON InvQuan.Part = ViewListItems.[Item]",
            "count" : "Select COUNT(*) FROM InvQuan LEFT JOIN ViewListItems ON InvQuan.Part = ViewListItems.[Item]",
        },
        "R-3-C": {
            "data" : f"Select {', '.join(HEADERS['R-3-C']['keys'])} FROM Inven ",
            "count" : "Select COUNT(*) FROM Inven",
            "conditions": "Inven.[BPrice] <= 0 AND Inven.[Type] = 'I'"
        }
    }

    def get_headers(self):
        headers = self.HEADERS.get(self.sheet.code, {}).get("headers")
        return headers
    
    def get_headers_keys(self):
        headers = self.HEADERS.get(self.sheet.code, {}).get("keys")
        return headers

    def get_pagination_query(self, sql_query, offset, limit, order_by, order_dir):
        ordered_query = self.order_query(sql_query, order_by, order_dir)
        limit_and_offset_query = ordered_query + f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        return limit_and_offset_query

    def get_total(self):
        sql_query = self.QUERIES.get(self.sheet.code, {}).get("count")
        return query(sql_query)

    def get_conditions(self, sql_query):
        conditional_query = sql_query + " " + self.QUERIES.get(self.sheet.code, {}).get('conditions') 
        return conditional_query

    def order_query(self,sql_query, order_by, order_dir):
        sql_query += f"ORDER BY {order_by} {order_dir}"
        return sql_query
    


    def search_data_query(self, sql_query, request):
        columns = self.get_headers_keys()
        sql_query = sql_query + " WHERE" 
        if  "conditions" in self.QUERIES.get(self.sheet.code, {}):
            sql_query = self.get_conditions(sql_query)
            sql_query += " AND"
        columns_length = len(columns)    
        for i in range(0, columns_length):
            sql_query += f" {columns[i]} LIKE '%{request.GET[f'columns[{i}][search][value]']}%' "
            if i != columns_length-1:
                sql_query += "AND "
        return sql_query

    def get_count(self):    
        sql_query = self.QUERIES.get(self.sheet.code, {}).get("count")  
        if  "conditions" in self.QUERIES.get(self.sheet.code, {}):
            sql_query += " WHERE "
            sql_query = self.get_conditions(sql_query)
        return sql_query

    def get_table(self, request):
        offset = int(request.GET['start'])
        limit = int(request.GET['length'])
        columns = self.get_headers_keys()
        order_col = columns[int(request.GET['order[0][column]'])]
        order_dir = (request.GET['order[0][dir]']).upper()
        sql_query = self.QUERIES.get(self.sheet.code, {}).get("data")
        sql_query = self.search_data_query(sql_query, request)
        sql_query = self.get_pagination_query(sql_query, offset, limit, order_col, order_dir)
        count_query = self.get_count()
        count = query(count_query)[0][0]
        data = query(sql_query)
        list_objs = []
        for row in data:
            list_objs.append(list(row))
        res = {
            "draw":  int(request.GET['draw']),
            "recordsTotal": count,
            "recordsFiltered": count,
            "data": list_objs,
        }
        return res