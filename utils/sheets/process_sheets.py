from environ import Env
import yaml
import os
import datetime
import pdb
import multiprocessing as mp
from utils.sheets.actual_vs_quoted import get_and_save_csv_from_db
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
            os.getpgid(pid)
            status = 'running'
            elapsed = (datetime.datetime.now() - datetime.datetime.strptime(parsed_yaml_file["started"], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
            if elapsed > 59:
                mins_secs = divmod(elapsed, 60)
                mins = mins_secs[0]
                secs = mins_secs[1]
                elapsed = f"{mins} {('min' if mins == 1  else 'mins.')} {secs} {( 'sec.' if secs == 1 else 'secs.')}"
            else:
                elapsed = f"{elapsed} {(  'sec.' if elapsed == 1 else 'secs.')}"
        except:
            status = elapsed = 'completed'
        return {"status": status, "elapsed": elapsed}
    
    def run_script(self):
        process_sheet = ProcessSheets().get_process_id()
        if process_sheet["status"] == "completed":
            process = mp.Process(target=get_and_save_csv_from_db)
            process.start()
            ProcessSheets().save_process_id({'pid': process.pid})
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


    