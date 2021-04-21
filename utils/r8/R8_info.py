import pdb
import py_compile
import compileall
import os



def read_write_warehouse(warehouses=None, is_write=False):
    filename = "utils/r8/primary.txt"
    lines = []
    if warehouses:
        outF = open(filename, "w")
        outF.write(warehouses)
        outF.close()
        # pdb.set_trace()
        # py_compile.compile("/FnA_dashboard/utils/sheet_data.py")
        # compileall.compile_file('/FnA_dashboard/utils/sheet_data.py')
        os.rmdir("/FnA_dashboard/utils/__pycache__")
        print('File saved')
    else:
        myfile = open(filename, "r")
        warehouses = ""
        while myfile:
            warehouses = myfile.readline()
            if warehouses:
                warehouses = warehouses.replace('[', '(')
                warehouses = warehouses.replace(']', ')')
            break
        myfile.close()
    return str(warehouses)


def read_warehouse():
    filename = "utils/r8/primary.txt"
    lines = []
    myfile = open(filename, "r")
    warehouses = ""
    while myfile:
        warehouses = myfile.readline()
        # if warehouses:
        #     warehouses = warehouses.replace('[', '(')
        #     warehouses = warehouses.replace(']', ')')
        #     warehouses = warehouses.strip("\"")
        break
    myfile.close()
    
    warehouses = '(' + warehouses + ')'
    print(warehouses)
    return str(warehouses)