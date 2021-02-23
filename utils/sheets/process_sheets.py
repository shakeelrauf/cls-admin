from environ import Env
import django
django.setup()
from dashboard.models import Sheet
import yaml
import os
import datetime
import pdb
import time
import multiprocessing as mp
env = Env()

class ProcessSheets():
    def get_process_id(self):
        a_yaml_file = open(env('STORAGE_DIR')+"sheet.yml")
        parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
        try:
            if "pid" in dict(parsed_yaml_file):
                pid = parsed_yaml_file['pid']
            else:
                pid = 0
            sheet_id = parsed_yaml_file["sheet_id"]
            os.getpgid(pid)
            status = 'running'
            elapsed = (datetime.datetime.now() - datetime.datetime.strptime(parsed_yaml_file["started"], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
            if elapsed > 59:
                mins_secs = divmod(elapsed, 60)
                mins = int(mins_secs[0])
                secs = int(mins_secs[1])
                elapsed = f"{mins} {('min' if mins == 1  else 'mins.')} {secs} {( 'sec.' if secs == 1 else 'secs.')}"
            else:
                elapsed = f"{int(elapsed)} {(  'sec.' if elapsed == 1 else 'secs.')}"
        except:
            status = elapsed = 'completed'
            sheet_id = 0
        return {"status": status, "elapsed": elapsed, 'pid': pid, "sheet_id" : sheet_id}
    
    def run_script(self, sheet):
        process_sheet = ProcessSheets().get_process_id()
        if process_sheet["status"] == "completed":
            # method_name =  get_method_from_sheet(sheet)
            script_path = env("STORAGE_DIR")+sheet.script_path
            if os.path.exists(script_path):
                process = mp.Process(target=run_script_method,args=(script_path,sheet.id,))
                process.start()
                ProcessSheets().save_process_id({'pid': process.pid,'sheet_id': sheet.id})
        return process_sheet

    def save_process_id(self, attrs):
        missing = []
        for k in ["pid"]:
            if attrs[k] != None:
                missing.append(k)
        attrs['started'] = str(datetime.datetime.now())
        data = attrs
        with open(env('STORAGE_DIR')+"sheet.yml", 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

def run_script_method(script_path, sheet_id):
    exec(open(script_path).read())
    Sheet.objects.filter(id=sheet_id).update(updated_at=datetime.datetime.now())

def get_method_from_sheet(sheet):
        """Dispatch method name"""
        method_name = 'get_and_save_csv_from_db_' + str(sheet.config_name)
        method = eval(method_name)
        return method