from utils.server_db import query
import pdb
import yaml
import os
from utils.r8.R8_info import read_warehouse


settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
config_file = os.path.join(PROJECT_ROOT, 'config.yml')
a_yaml_file = open(config_file)
parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
primary_warehouse_list = read_warehouse()


class SheetData(object):
    def __init__(self, sheet):
        self.sheet = sheet

    HEADERS = {
        "R-3": {
            "keys": ["PO.PO", "FORMAT(PO.Date, 'yyyy-MM-dd ')", "Vendor.Company"],
            "headers": ["PO", "Date", "Vendor Name"]
        },
        "R-3-A": {
            "keys": ["POLed.[Part]", "CAST(POLed.[Desc] AS NVARCHAR(100))", "POLed.[Quan]", "POLed.[Received]",
                     "(POLed.[Quan] - POLed.[Received]) ", "PO.[PO]", "FORMAT (PO.Date, 'yyyy-MM-dd ')",
                     "FORMAT (PO.DateReq, 'yyyy-MM-dd ')", "Vendor.[Company]"],
            "headers": ["Part Number", "Description", "Qty Ordered", "Qty Received", "Balance", "PO Number",
                        "Entry Date", "Expected Date", "Vendor Name"]
        },
        "R-3-B": {
            "keys": ["InvQuan.[Part]", "ViewListItems.[Description]", "InvQuan.[MinQuan]", "InvQuan.[ReOrder]",
                     "ViewListItems.[Quantity In Stock]"],
            "headers": ["Part", "Description", "Min order point", "ReOrder Point", "Quantity In Stock"]
        },
        "R-3-C": {
            "keys": ["Inven.[Part]", "CAST(Inven.[Desc] AS NVARCHAR(100))", "Inven.[BPrice]"],
            "headers": ["Part Number", "Description", "Base Price"]
        },
        "R-3-D": {
            "keys": ["PO.[PO]", "FORMAT (PO.[Date], 'yyyy-MM-dd ')", "Vendor.[Company]",
                     "FORMAT (PO.DateReq, 'yyyy-MM-dd ')"],
            "headers": ["PO", "Date", "Vendor", "Follow Up Date"]
        },
        "R-3-E": {
            "keys": ["Vendor.[Company]", "VenPartsFirst.[Part]", "VenPartsFirst.[VenPart]",
                     "VenPartsFirst.[LastPurchasePrice]", "FORMAT (VenPartsFirst.[DateLastPurchase], 'yyyy-MM-dd ')"],
            "headers": ["Vendor Name", "Part", "Description", "Last Purchase Price", "Date Last Purchase"]
        },
        "R-3-F": {
            "keys": ["Inven.[Part]", "CAST(Inven.[Desc] AS NVARCHAR(100))", "Vendor.[Company]"],
            "headers": ["Part", "Description", "Vendor"]
        },
        "R-3-G": {
            "keys": ["Inven.[Part]", "CAST(Inven.[Desc] AS NVARCHAR(100))", "Inven.[Bprice]", "Inven.[PriceA]",
                     "Inven.[PriceB]", "Inven.[PriceC]"],
            "headers": ["Part", "Description", "Base Cost", "Price A", "Price B", "Price C"]
        },
        "R-3-H": {
            "keys": ["Inven.[Part]", "CAST(Inven.[Desc] AS NVARCHAR(100))", "Inven.[CostDB]", "Inven.[SalesCR]"],
            "headers": ["Part", "Description", "CostDB", "SalesCR"]
        },
        "R-3-I": {
            "keys": ["ViewListItems.[Item]", "CAST(ViewListItems.[Description]  AS NVARCHAR(100))",
                     "ViewListItems.[Vendor Company]", "ViewListItems.[Quantity in Stock]", "InvQuan.[WH]",
                     "InvQuan.[Aisle]"],
            "headers": ["Part", "Description", "Vendor Name", "Qty In Stock", "Warehouse", "Aisle"]
        },
        "R-3-J": {
            "keys": ["InvenAct.[Part]", "MAX(CAST(InvenAct.[PartDesc] AS NVARCHAR(100)))", "MAX(InvenAct.[WH])",
                     "SUM(InvenAct.[Quan])", "MIN(InvenAct.Cost)", "MAX(InvenAct.Cost)"],
            "headers": ["Part", "Description", "WH", "Quan", "Lowest Cost Purchased", "Highest Cost Purchased"]
        },
        "R-8": {
            "keys": ["Warehous.[WH]","Warehous.[Desc]","Warehous.[Inactive]"],
            "headers": ["WH ID", "Name", "Status"]
        },
        "R-8-P": {
            "keys": ["Warehous.WH", "Warehous.[Desc]", "SUM(CAST(InvenAct.Count AS DECIMAL(10,2)))",  "SUM(CAST(InvenAct.Quan AS DECIMAL(10,2)))"],
            "headers": ["Primary Warehouse", "Description", "Total Inventory Items", "Total Cost"]
        },
        "R-8-I": {
            "keys": ["Warehous.WH", "Warehous.[Desc]", "SUM(CAST(InvenAct.Count AS DECIMAL(10,2)))",  "SUM(CAST(InvenAct.Quan AS DECIMAL(10,2)))"],
            "headers": ["Primary Warehouse", "Description", "Total Inventory Items", "Total Cost"]
        },
        "R-5": {
            "keys": ["Customer.CustNo", "LastName", "Customer.Add1"],
            "headers": ["Customer Number", "Customer Name", "Address"]
        },
        "R-25": {
            "keys": ["LastName","Dispatch","FORMAT(RecDate, 'yyyy-MM-dd ')"],
            "headers": ["Customer Name", "Dispatch Number", "Received Date"]
        },
    }
    QUERIES = {
        "R-3": {
            "data": f"SELECT {', '.join(HEADERS['R-3']['keys'])} FROM PO LEFT JOIN Vendor ON PO.Vendor = Vendor.Vendor ",
            "count": "SELECT COUNT(*) FROM PO LEFT JOIN Vendor ON PO.Vendor = Vendor.Vendor ",
            "conditions": "PO.[OrderPlaced] NOT IN ('-1') AND PO.[Status]  = 'O'"
        },
        "R-3-A": {
            "data": f"Select {', '.join(HEADERS['R-3-A']['keys'])} FROM PO INNER  JOIN POLed on PO.[PO] = POLed.[PO] INNER  JOIN Vendor on PO.Vendor = Vendor.[Vendor] ",
            "count": "Select COUNT(*) FROM PO INNER  JOIN POLed on PO.[PO] = POLed.[PO]",
            "conditions": "PO.[Status]  = 'O' AND (POLed.[Quan] - POLed.[Received]) > 0"
        },
        "R-3-B": {
            "data": f"Select {', '.join(HEADERS['R-3-B']['keys'])} FROM InvQuan LEFT JOIN ViewListItems ON InvQuan.Part = ViewListItems.[Item]",
            "count": "Select COUNT(*) FROM InvQuan LEFT JOIN ViewListItems ON InvQuan.Part = ViewListItems.[Item]",
            "conditions": "ViewListItems.[Quantity In Stock] > 0.0 AND InvQuan.[MinQuan] = 0.0"
        },
        "R-3-C": {
            "data": f"Select {', '.join(HEADERS['R-3-C']['keys'])} FROM Inven ",
            "count": "Select COUNT(*) FROM Inven",
            "conditions": "Inven.[BPrice] <= 0 AND Inven.[Type] = 'I'"
        },
        "R-3-D": {
            "data": f"Select {', '.join(HEADERS['R-3-D']['keys'])} FROM PO LEFT JOIN Vendor on PO.[Vendor] = Vendor.[Vendor]",
            "count": "Select COUNT(*) FROM PO LEFT JOIN Vendor on PO.[Vendor] = Vendor.[Vendor]",
            "conditions": "PO.[Status]  = 'O'"
        },
        "R-3-E": {
            "data": f'''WITH VenPartsFirst AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY VenParts.vendor ORDER BY VenParts.[DateLastPurchase] DESC) AS row_number FROM VenParts 
                            WHERE VenParts.[DateLastPurchase] IS NOT NULL
                            AND VenParts.[DateLastPurchase] <= ( GETDATE() - {parsed_yaml_file['r-3-e']['days']}  )
                        ) 
                        Select {', '.join(HEADERS['R-3-E']['keys'])} FROM VenPartsFirst LEFT JOIN Vendor on VenPartsFirst.Vendor = Vendor.Vendor''',
            "count": f'''WITH VenPartsFirst AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY VenParts.vendor ORDER BY VenParts.[DateLastPurchase] DESC) AS row_number FROM VenParts 
                            WHERE VenParts.[DateLastPurchase] IS NOT NULL 
                            AND VenParts.[DateLastPurchase] <= ( GETDATE() - {parsed_yaml_file['r-3-e']['days']}  )
                        ) 
                        Select COUNT(*) FROM VenPartsFirst  LEFT JOIN Vendor on VenPartsFirst.Vendor = Vendor.Vendor''',
            "conditions": "row_number = 1"
        },
        "R-3-F": {
            "data": f"Select {', '.join(HEADERS['R-3-F']['keys'])} FROM Inven LEFT JOIN Vendor on Inven.[Vendor] = Vendor.[Vendor]",
            "count": "Select COUNT(*) FROM Inven LEFT JOIN Vendor on Inven.[Vendor] = Vendor.[Vendor]",
            "conditions": "Inven.[Type]  = 'I' AND Inven.[Vendor] IS NULL"
        },
        "R-3-G": {
            "data": f"Select {', '.join(HEADERS['R-3-G']['keys'])} FROM Inven",
            "count": "Select COUNT(*) FROM Inven",
            "conditions": "Inven.[Bprice]  >= (Inven.[PriceA]/2)"
        },
        "R-3-H": {
            "data": f"Select {', '.join(HEADERS['R-3-H']['keys'])} FROM Inven",
            "count": "Select COUNT(*) FROM Inven",
            "conditions": """Inven.[SalesCR] != 'BAC' AND 
            (CONVERT(INT,
                    CASE
                    WHEN IsNumeric(CONVERT(VARCHAR(12), Inven.[CostDB])) = 1 THEN CONVERT(VARCHAR(12),Inven.[CostDB])
                    ELSE 0 END) - 
            CONVERT(INT,
                    CASE
                    WHEN IsNumeric(CONVERT(VARCHAR(12), Inven.[SalesCR])) = 1 THEN CONVERT(VARCHAR(12),Inven.[SalesCR])
                    ELSE 0 END))  <> 6000"""
        },
        "R-3-I": {
            "data": f"Select {', '.join(HEADERS['R-3-I']['keys'])} FROM ViewListItems LEFT JOIN InvQuan ON ViewListItems.[Item] = InvQuan.[Part]",
            "count": "Select COUNT(*) FROM ViewListItems LEFT JOIN InvQuan ON ViewListItems.[Item] = InvQuan.[Part]",
            "conditions": f"InvQuan.[WH] = '{parsed_yaml_file['r-3-i']['WH']}' AND ViewListItems.[Quantity in Stock] > 0 AND (InvQuan.[Aisle] = null OR InvQuan.[Aisle] = 'SO')"
        },
        "R-3-J": {
            "data": f"Select {', '.join(HEADERS['R-3-J']['keys'])} FROM InvenAct GROUP BY InvenAct.Part, InvenAct.WH",
            "count": "Select COUNT(*) OVER () FROM InvenAct GROUP BY InvenAct.Part, InvenAct.WH",
            "conditions": f"InvenAct.WH LIKE '{parsed_yaml_file['r-3-j']['WH']}' AND SUM(InvenAct.[Quan])>0",
            "GROUP_BY": True
        },
        "R-8": {
            "data": f"Select {', '.join(HEADERS['R-8']['keys'])} FROM Warehous",
            "count": "Select COUNT(*) FROM Warehous",
            "conditions": "Warehous.[Inactive]  != '-1'"
        },
        "R-8-P": {
            "data": f"Select {', '.join(HEADERS['R-8-P']['keys'])} FROM Warehous INNER JOIN InvenAct ON Warehous.WH = InvenAct.WH GROUP BY Warehous.WH,Warehous.[Desc] ",
            "count": "Select COUNT(Warehous.WH) FROM Warehous INNER JOIN InvenAct ON Warehous.WH = InvenAct.WH GROUP BY Warehous.WH",
            "conditions": f"Warehous.WH IN {primary_warehouse_list}",
            "GROUP_BY": True
        },
        "R-8-I": {
            "data": f"Select {', '.join(HEADERS['R-8-I']['keys'])} FROM Warehous INNER JOIN InvenAct ON Warehous.WH = InvenAct.WH GROUP BY Warehous.WH,Warehous.[Desc],Warehous.[Inactive] ",
            "count": "Select COUNT(Warehous.WH) FROM Warehous INNER JOIN InvenAct ON Warehous.WH = InvenAct.WH GROUP BY Warehous.WH,Warehous.[Desc],Warehous.[Inactive]",
            "conditions": f"Warehous.WH NOT IN {primary_warehouse_list} AND Warehous.[Inactive]  != '-1'",
            "GROUP_BY": True
        },
        "R-5": {
            "data": f"Select {', '.join(HEADERS['R-5']['keys'])} FROM Customer INNER JOIN Location ON Customer.CustNo = Location.CustNo",
            "count": "Select COUNT(*) FROM Customer INNER JOIN Location ON Customer.CustNo = Location.CustNo",
            "conditions": "Email='' AND Email2='' AND Email3='' AND Email4='' AND Email5='' AND Email6='' AND Customer.CustNo !='0000000'"
        },
        "R-25": {
            "data": f"Select {', '.join(HEADERS['R-25']['keys'])} FROM Dispatch INNER JOIN Customer ON Customer.CustNo = Dispatch.CustNo",
            "count": "Select COUNT(*) FROM Dispatch INNER JOIN Customer ON Customer.CustNo = Dispatch.CustNo",
            "conditions": "Complete IS NOT NULL AND Invoiced = '0'"
        },
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

    def order_query(self, sql_query, order_by, order_dir):
        sql_query += f"ORDER BY {order_by} {order_dir}"
        return sql_query

    def search_data_query(self, sql_query, request):
        columns = self.get_headers_keys()
        if "GROUP_BY" in self.QUERIES.get(self.sheet.code, {}):
            sql_query = sql_query + " HAVING"
        else:
            sql_query = sql_query + " WHERE"
        if "conditions" in self.QUERIES.get(self.sheet.code, {}):
            sql_query = self.get_conditions(sql_query)
            sql_query += " AND"
        columns_length = len(columns)
        for i in range(0, columns_length):
            sql_query += f" {columns[i]} LIKE '%{request.GET[f'columns[{i}][search][value]']}%' "
            if i != columns_length - 1:
                sql_query += "AND "
        return sql_query

    def get_count(self):
        sql_query = self.QUERIES.get(self.sheet.code, {}).get("count")
        if "conditions" in self.QUERIES.get(self.sheet.code, {}):
            if "GROUP_BY" in self.QUERIES.get(self.sheet.code, {}):
                sql_query = sql_query + " HAVING"
            else:
                sql_query = sql_query + " WHERE"
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
            "draw": int(request.GET['draw']),
            "recordsTotal": count,
            "recordsFiltered": count,
            "data": list_objs,
        }
        return res
