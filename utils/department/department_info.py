
class Department_Data:
    def __init__(self, department):
        self.department = department

    HEADERS = {
        "Purchasing": {
            "Scorecard": ["Purchasing Report", "Parts On Order", "Stock vs M/M", "Follow Up", "Items Vs PO's older then 90", "Non Stock", "RGA"],
            "Compliance": ["Base Cost = 0", "Preferred Vendor = Null", "Cost Vs Sell", "Min/Max <> Sales Trends"],
            "headers": ["Scorecard", "Compliance"]
        },
        "Accounting": {
            "AR Scorecard": ["PO need", "inbox AR unread", "Uninvoiced"],
            "AR Compliance": ["Appliance of accounting", "C.O.A Vs Account", "Invoice COG=0", "Missing Customer Emails"],
            "AP Scorecard": ["Account payable"],
            "AP Compliance": ["Missing reciets"],
            "headers": ["AR Scorecard", "AR Compliance", "AP Scorecard", "AP Compliance"]
        },
        "Collections": {
            "Scorecard": ["Collections", "30 Day Rolling", "Last 365 COD"],
            "Compliance": ["Missing Customer Emails"],
            "headers": ["Scorecard", "Compliance"]
        },
        "FnA": {
            "Scorecard": ["420 Report", "420 Trending", "Cash report", "Daily cash in", "Daily cash out"],
            "Compliance": ["weekly vs previous year", "monthly vs previous year", "quater vs previous", "ytd vs prior"],
            "headers": ["Scorecard", "Compliance"]
        },
        "GM": {
            "Scorecard": ["Actual Vs Quoted", "Actual Vs Invoiced", "Daily margin"],
            "Compliance": [],
            "headers": ["Scorecard", "Compliance"]
        },
    }
    
    def get_sidebar(self):
        headers = self.HEADERS.get(self.department, {}).get("headers")

        side_dict = {}
        for head in headers:
            side_dict[head] = self.HEADERS.get(self.department, {}).get(head)
        return headers, side_dict, self.department     
    
    def get_headers(self):
        headers = self.HEADERS.get(self.department, {}).get("headers")
        return headers

    def get_items(self, item_name):
        items = self.HEADERS.get(self.department, {}).get(item_name)
        return items


def read_write_department(department=None, is_write=False):
    filename = "utils/department/department.txt"
    lines = []
    if department:
        outF = open(filename, "w")
        outF.write(department)
        outF.close()
    else:
        myfile = open(filename, "r")
        department = ""
        while myfile:
            department = myfile.readline()
            break
        myfile.close()
    
    return department
