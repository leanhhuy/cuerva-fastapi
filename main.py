# https://fastapi.tiangolo.com/tutorial/background-tasks/
# https://www.youtube.com/watch?v=3JJgJsscdgQ

# https://docs.docker.com/desktop/networking/
# https://docs.docker.com/storage/

# https://rominirani.com/docker-on-windows-mounting-host-directories-d96f3f056a2c

# https://docs.docker.com/get-started/06_bind_mounts/
# https://docs.docker.com/storage/bind-mounts/

# https://fastapi.tiangolo.com/tutorial/bigger-applications/

# https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/

from fastapi import FastAPI
from fastapi import BackgroundTasks, Path
from datetime import datetime, timedelta
from enum import Enum
import os
import glob
import gc
import math
# import requests

# from fastapi.middleware.wsgi import WSGIMiddleware
# from flask import Flask, escape, request

import psycopg2 # pip install psycopg2 # pip uninstall psycopg2

# import psycopg2 # pip install psycopg2 # pip uninstall psycopg2
from pgcopy import CopyManager # pip install pgcopy
# from sshtunnel import SSHTunnelForwarder # pip install sshtunnel

from fastapi_utils.tasks import repeat_every # pip install fastapi-utils

from pydantic import BaseSettings

# flask_app = Flask(__name__)

# @flask_app.route("/")
# def flask_main():
#     name = request.args.get("name", "World")
#     return f"Hello, {escape(name)} from Flask!"

from cuerva_consumption import CuervaConsumption, CuervaDataGap
from cuerva_timescaledb import CuervaTimescaleDb
from log_util import LogUtil
from datetime_util import DateTimeUtil
from cuerva_settings import CuervaSettings
from csv_util import CsvUtil
from network_util import NetworkUtil

# data_dir = "C:\\MARCOS\\UGR\\Cuerva\\Data\\JSON"
# dict_master_to_device = {}
# dict_master_to_device = get_dict_master_to_device()

settings = CuervaSettings()
app = FastAPI()

# app.mount("/v1", WSGIMiddleware(flask_app))

@app.get("/")
async def root():    
    return {"message": "Cuerva FastAPI at " + str(datetime.now())}

# dict_master_to_device = {}
# dict_master_to_device = get_dict_master_to_device()
# print("dict_master_to_device:", dict_master_to_device)

# dict_last_record = {}
# dict_last_record = get_last_records()
# print("dict_last_record:", dict_last_record)


@app.on_event("startup")
async def startup_event():
    # items["foo"] = {"name": "Fighters"}
    # items["bar"] = {"name": "Tenders"}

    # dict_master_to_device = get_dict_master_to_device()
    # settings.dict_master_to_device : dict = get_dict_master_to_device()
    # print("dict_master_to_device LOADED!")
    print("TODO startup_event(): load SETTINGS informations from environment or database!")
    # settings.print_settings()

CUR_JSON_FILE = ""

@app.on_event("startup")
@repeat_every(seconds=120)  # 1 minute
def repeated_task() -> None:
    data_dir = settings.json_data_dir

    # NetworkUtil.test_access_url("https://cajal.ugr.es/")
    # NetworkUtil.test_access_url("http://rt.ugr.es:8920/")

    print("-----------------------------------------------------------------------------")
    full_log_file = LogUtil.start_log_file()
    print("full_log_file:", full_log_file)

    # print("REPEATED TASK:", datetime.now(), "read new JSON files and import to PostGres.")
    LogUtil.write_log("REPEATED TASK:", datetime.now(), "read new JSON files and import to TimescaleDB.")

    count_total = 0    
    if settings.import_json == "1":
        try:
            settings.log_settings(LogUtil.write_log)
            count_total = import_json_data(dataDir=data_dir, subDir="", IMPORT_TO_DB=True, SAVE_TO_CSV=False, round_minute=settings.round_minute, 
                max_minute_fill=settings.max_minute_fill, interpolate=settings.interpolate)
        except Exception as e:
            LogUtil.write_log(datetime.now(), CUR_JSON_FILE)
            LogUtil.write_log(e)
            settings.log_settings(LogUtil.write_log)            
            LogUtil.write_err(datetime.now(), CUR_JSON_FILE)
            LogUtil.write_err(e)

    LogUtil.write_log("FINISHED:", datetime.now(), "import_json_data: count_total =", count_total)
    LogUtil.write_log("Memory release:", gc.collect())    
    print("----------------------------------------------------------------------------- REPEATED TASK end!")


def import_json_data(dataDir, subDir = "", IMPORT_TO_DB = False, SAVE_TO_CSV = True,  round_minute=True, max_minute_fill=5, interpolate=True):
    # https://www.techiedelight.com/list-all-subdirectories-in-directory-python/

    LogUtil.write_log("dataDir:", dataDir, ", subDir:", subDir, ", IMPORT_TO_DB:", IMPORT_TO_DB, ", SAVE_TO_CSV:", SAVE_TO_CSV,
        ", round_minute:", round_minute, ", max_minute_fill:", max_minute_fill, ", interpolate:", interpolate)

    # dict_master_to_device = settings.dict_master_to_device

    db = CuervaTimescaleDb(settings)
    dict_last_record = {}

    if IMPORT_TO_DB:
        # db.start_conn()
        # print("To load last records!")
        dict_last_record = get_last_records(db=db)        
        # print("Last records loaded!")

    count_total = 0

    master_dir_list = []
    for c_d in os.listdir(dataDir):
        master_dir_list.append(c_d) 
    master_dir_list.sort()
    LogUtil.write_log("Casa directories:", master_dir_list)
    # for c_d in casa_dir_list:
    #     LogUtil.write_log(c_d)

    # for c_dir in os.listdir(dataDir):
    for master in master_dir_list:
        master_dir = os.path.join(dataDir, master)
        if os.path.isdir(master_dir) and ( subDir == "" or master == subDir):
            LogUtil.write_log("master_dir:", master_dir)

            csv_file = master_dir + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
            csv_gap_file = master_dir + "_gap_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
            if SAVE_TO_CSV:
                LogUtil.write_log("csv_file:", csv_file)            

            data_gaps = []
            gap_header = "master,device,from_time,to_time,minutes"
            csv_count = 0
            
            last_imported_record = None
            last_record = None

            # device = dict_master_to_device[master]
            # LogUtil.write_log(master + " -> device:" + device)

            # if device in dict_last_record:
            #     last_imported_record = dict_last_record[device]
            #     last_record = dict_last_record[device]
            #     # last_date = last_record.datetime.date()
            # # print(device, "last_date:", last_date)
            # if last_imported_record is not None:
            #     LogUtil.write_log(device + " -> last_record_time:" + str(last_imported_record.datetime))
            if master in dict_last_record:
                last_imported_record = dict_last_record[master]
                last_record = dict_last_record[master]
            if last_imported_record is not None:
                LogUtil.write_log(master + " -> last_record_time:" + str(last_imported_record.datetime))

            dict_time = {}

            day_dir_list = []
            for d_dir in os.listdir(master_dir):
                day_dir_list.append(d_dir)
            day_dir_list.sort()

            for d_dir in day_dir_list:
                day_dir = os.path.join(master_dir, d_dir)
                if os.path.isdir(master_dir):
                    is_new_data = check_is_new_data(d_dir, last_imported_record)
                    LogUtil.write_log(day_dir + " -> is new data: " + str(is_new_data).upper())

                    if is_new_data:
                        json_files = glob.glob(day_dir + "/*.json")
                        json_file_list = []
                        for json_file in json_files:
                            json_file_list.append(json_file)
                        json_file_list.sort()
                        LogUtil.write_log("Count JSON files:" + str(len(json_file_list)))

                        obj_list = []                        
                        count_of_day = 0
                        count_ori = 0
                        count_copied = 0
                        count_duplicated = 0

                        for json_file in json_file_list:
                            CUR_JSON_FILE = json_file

                            # print(json_file)
                            obj = CuervaConsumption()
                            loaded = obj.loadFromJsonFile(json_file)

                            if loaded:
                                existing = False
                                if last_imported_record is not None:
                                    if obj.datetime <= last_imported_record.datetime:
                                        existing = True
                                        # print("OLD FILE:", json_file)
                                if obj.datetime in dict_time:
                                    existing = True
                                    count_duplicated += 1

                                if not existing:
                                    if last_record is not None:
                                        last_minute = last_record.datetime
                                        if obj.datetime == last_minute + timedelta(minutes=1):
                                            obj.consumo = obj.eactive_q14 - last_record.eactive_q14
                                        else:
                                            gap = CuervaDataGap()
                                            gap.master = obj.master
                                            gap.device = obj.device
                                            gap.from_time = last_record.datetime
                                            gap.to_time = obj.datetime
                                            try:
                                                gap.minutes = int((gap.to_time - gap.from_time).total_seconds() / 60)
                                            except Exception as ge:                                                
                                                gap.minutes = 0
                                                LogUtil.write_log(datetime.now(), json_file, ge)
                                                LogUtil.write_err(datetime.now(), json_file, ge)
                                            data_gaps.append(gap)
                                            
                                            # if obj.datetime - timedelta(minutes=6) <= last_minute:

                                            #     cur_minute = last_minute + timedelta(minutes=1)
                                            #     while cur_minute < obj.datetime:
                                            #         new_obj = CuervaConsumption()
                                            #         new_obj.copy(last_record)
                                            #         new_obj.datetime = cur_minute
                                            #         new_obj.consumo = 0
                                            #         new_obj.copied = 1

                                            #         obj_list.append(new_obj)
                                            #         dict_time[cur_minute] = new_obj

                                            #         last_record = new_obj

                                            #         cur_minute += timedelta(minutes=1)
                                            #         count_copied += 1
                                            #         count_of_day += 1

                                            #     obj.consumo = obj.eactive_q14 - last_record.eactive_q14
                                            # else:
                                            #     obj.consumo = 0

                                            minute_diff = math.floor((obj.datetime - last_minute).total_seconds() / 60)
                                            if minute_diff >= 2 and minute_diff <= max_minute_fill + 1:  # change to settings

                                                consumo_incr = 0
                                                if interpolate:
                                                    consumo_incr = (obj.eactive_q14 - last_record.eactive_q14) / minute_diff

                                                for i in range(minute_diff -1):
                                                    new_obj = CuervaConsumption()
                                                    new_obj.copy(last_record)
                                                    new_obj.datetime += timedelta(minutes=1)

                                                    new_obj.eactive_q14 += consumo_incr
                                                    new_obj.consumo = consumo_incr
                                                    new_obj.copied = 1

                                                    obj_list.append(new_obj)
                                                    dict_time[new_obj.datetime] = new_obj

                                                    last_record = new_obj

                                                    count_copied += 1
                                                    count_of_day += 1
                                            
                                            else:
                                                obj.consumo = 0

                                    obj_list.append(obj)
                                    dict_time[obj.datetime] = obj

                                    last_record = obj

                                    count_of_day += 1
                                    count_ori += 1
                                # else:
                                #     count_duplicated += 1
                                    # existing_obj = dict_time[obj.datetime]
                                    # print("Duplicated:", json_file, "with ", existing_obj.data_file)

                        LogUtil.write_log("Count ori:" + str(count_ori) + ", duplicated: " + str(count_duplicated) +
                                  ", copied: " + str(count_copied) + ", total day: " + str(count_of_day))

                        if len(obj_list) > 0:
                            if IMPORT_TO_DB:
                                dbTable = settings.timescaledb_table

                                # count_time = CuervaTimescaleDb.importToTimescaleDb_simple_SSH(obj_list, dbTable, settings, conn=None, server=None)
                                count_time = db.import_data_objects(objList=obj_list, dbTable=dbTable)

                                LogUtil.write_log(master + " - imported records: " + str(count_time))

                                count_total += count_time

                            if SAVE_TO_CSV:
                                if csv_count == 0:
                                    consumo_header = "master,Device,datetime,intensity,voltage,powerfactor,pactive,preactive,papar,temp,frequency,eactive_q14,eactive_q23,ereact_q1,ereact_q2,ereact_q3,ereact_q4,eaparente,consumo,copied"
                                    CsvUtil.writeCsvFile(obj_list, csv_file, consumo_header)
                                else:
                                    CsvUtil.appendCsvFile(obj_list,csv_file)
                                LogUtil.write_log(master + " - saved to CSV: " + str(len(obj_list)))

                                csv_count += len(obj_list)

            if settings.save_gap == "1":
                print("data_gaps:", len(data_gaps))
                if len(data_gaps) > 0:                    
                    gap_table = settings.gap_table

                    # count_gap = CuervaTimescaleDb.importToTimescaleDb_simple_SSH(data_gaps, gap_table, settings, conn=None, server=None)
                    count_gap = db.import_data_objects(objList=data_gaps, dbTable=gap_table)

                    LogUtil.write_log("count_gap:", count_gap)

            if SAVE_TO_CSV:
                LogUtil.write_log(master, "- saved to CSV:", csv_count)                
                CsvUtil.writeCsvFile(data_gaps, csv_gap_file, gap_header)

            LogUtil.write_log(master, "- imported to DB:", count_total)

    return count_total


def get_last_records(db: CuervaTimescaleDb=None):
    dict_last_record = {}

    # last_records_sql = """SELECT * FROM (
    #     SELECT device, datetime, intensity, voltage, power_factor, eactive_q14, eactive_q23, ereact_q1, ereact_q2, ereact_q3, ereact_q4,
    #            pactive, preactive, papar, temp, frequency, eaparente, consumo, id,
    #         RANK() OVER (
    #             PARTITION BY device
    #             ORDER BY device, datetime DESC
    #         ) rank_number
    #     FROM consumption
    # ) s
    # WHERE rank_number = 1"""
    last_records_sql = """SELECT * FROM (
        SELECT master, device, datetime, intensity, voltage, power_factor, eactive_q14, eactive_q23, ereact_q1, ereact_q2, ereact_q3, ereact_q4,
               pactive, preactive, papar, temp, frequency, eaparente, consumo, id,
            RANK() OVER (
                PARTITION BY master
                ORDER BY master, datetime DESC
            ) rank_number
        FROM consumption
    ) s
    WHERE rank_number = 1"""

    # print(last_records_sql)

    # print("main.get_last_records() -> Before load last records!")
    if db is not None:
        rows, dictCol = db.select_data_rows(last_records_sql)
    else:
        rows, dictCol = CuervaTimescaleDb.selectToDataRows(last_records_sql, None, settings)
    # print("main.get_last_records() -> After last records loaded!")

    # print(dictCol)
    # print(type(rows), rows)

    # last_records = []
    for row in rows:
        obj = CuervaConsumption()
        loaded = obj.load_from_data_row(row, dictCol)                
        if loaded:
            obj.datetime = DateTimeUtil.to_timezone_naive(obj.datetime)

            # dict_last_record[obj.device] = obj
            dict_last_record[obj.master] = obj

    LogUtil.write_log("Last data records:", len(dict_last_record))
    for k, v in dict_last_record.items():
        LogUtil.write_log("Device =", k, ", id =", v.id, ", time =", v.datetime)

    return dict_last_record


def check_is_new_data(d_dir, last_imported_record):
    if len(d_dir.strip()) != 8:
        return False
    data_date = datetime.strptime(d_dir, "%Y%m%d").date()        
    if data_date.year < 2022:
        return False

    if last_imported_record is None:
        return True
    else:        
        if data_date > last_imported_record.datetime.date():
            # print(d_dir, "- data_date:", data_date, "-> New data!")
            return True
        else:
            if data_date == last_imported_record.datetime.date():
                h = last_imported_record.datetime.hour
                m = last_imported_record.datetime.minute
                if h == 23 and m == 59:
                    return False
                else:
                    return True
            else:
                # print(d_dir, "- data_date:", data_date, "-> Old data!")
                return False


@app.post("/convert_json_to_csv", status_code=200)
async def convert_json_to_csv(input_dir: str, sub_dir: str):    
     import_json_data(dataDir=input_dir, subDir=sub_dir, IMPORT_TO_DB=False, SAVE_TO_CSV=True)


@app.post("/cleanse_csv", status_code=200)
async def cleanse_csv(input_dir: str, output_dir: str):
    print("input_dir:", input_dir)
    print("output_dir:", output_dir)

    # https://www.geeksforgeeks.org/python-list-files-in-a-directory/
    csv_files = os.listdir(input_dir)
    # prints all files
    print(csv_files)
    
    for csv_file in csv_files:
        if os.path.isfile(input_dir + "\\" + csv_file) and csv_file.lower().endswith(".csv"):           
            print(csv_file)

            temp_obj = CuervaConsumption()
            temp_obj_list = temp_obj.loadFromCsvFile(input_dir + "\\" + csv_file)
            print("temp_obj_list:", len(temp_obj_list))

            obj_list = []
            dict_time = {}
            last_record = None

            data_gaps = []

            for obj in temp_obj_list:
                if obj.datetime not in dict_time:                    
                    if last_record is not None:                       
                        if obj.datetime > last_record.datetime + timedelta(minutes=1):
                            gap = CuervaDataGap()
                            gap.device = obj.device
                            gap.from_time = last_record.datetime
                            gap.to_time = obj.datetime
                            gap.minutes = (gap.to_time - gap.from_time).total_seconds() / 60

                            data_gaps.append(gap)

                        last_minute = last_record.datetime
                        if obj.datetime == last_minute + timedelta(minutes=1):
                            obj.consumo = obj.eactive_q14 - last_record.eactive_q14
                        else:
                            if obj.datetime - timedelta(minutes=6) <= last_minute:
                                cur_minute = last_minute + timedelta(minutes=1)
                                while cur_minute < obj.datetime:
                                    new_obj = CuervaConsumption()
                                    new_obj.copy(last_record)
                                    new_obj.datetime = cur_minute
                                    new_obj.consumo = 0
                                    new_obj.copied = 1

                                    obj_list.append(new_obj)
                                    dict_time[cur_minute] = new_obj

                                    last_record = new_obj

                                    cur_minute += timedelta(minutes=1)
                                    # count_copied += 1
                                    # count_of_day += 1

                                obj.consumo = obj.eactive_q14 - last_record.eactive_q14
                            # else:
                            #     obj.consumo = 0
                    # else:
                    #     obj.consumo = 0
                    
                    obj_list.append(obj)                    
                    dict_time[obj.datetime] = obj
                    last_record = obj                   

            # appendLog(LogUtil.logFile, "Count ori:" + str(count_ori) + ", duplicated: " + str(count_duplicated) +
            #             ", copied: " + str(count_copied) + ", total day: " + str(count_of_day), True)

            processed_file = (output_dir + "\\" + csv_file.lower()).replace(".csv", "_processed.csv")
            gap_file = (output_dir + "\\" + csv_file.lower()).replace(".csv", "_gap.csv")
            print("processed_file:", processed_file)
            print("gap_file :", gap_file)

            gap_header = "device,from_time,to_time,minutes" 
            CsvUtil.writeCsvFile(data_gaps, gap_file, gap_header)

            consumo_header = "Device,datetime,intensity,voltage,powerfactor,pactive,preactive,papar,temp,frequency,eactive_q14,eactive_q23,ereact_q1,ereact_q2,ereact_q3,ereact_q4,eaparente,consumo,copied"
            CsvUtil.writeCsvFile(obj_list, processed_file, consumo_header)

    return {"message": "" }


@app.post("/import_csv", status_code=200)
async def import_csv(input_file: str):
    print("input_file:", input_file)
    temp_obj = CuervaConsumption()
    obj_list = temp_obj.loadFromCsvFile(input_file)
    print("obj_list :", len(obj_list ))
    if len(obj_list) > 0:
        device = obj_list[0].device                
        count_time = CuervaTimescaleDb.importToTimescaleDb_simple_SSH(obj_list, settings.timescaledb_table, settings, conn=None, server=None)

        # appendLog(LogUtil.logFile, device + " - imported records: " + str(count_time), True)
        LogUtil.write_log(device + " - imported records: " + str(count_time))

    return {"count_import": len(obj_list)}


@app.get("/check_data_gap", status_code=200)
async def check_data_gap(dataDir):
    # dataDir = settings.data_dir
    print("dataDir:", dataDir)

    working_dir = os.getcwd()
    print(working_dir)

    header = "device,from_time,to_time,minutes" 
    report_files = []

    for c_dir in os.listdir(dataDir):
        # if c_dir == "4320100027":
        #     print(c_dir)
        casa_dir = os.path.join(dataDir, c_dir)
        if os.path.isdir(casa_dir):
            print(casa_dir)

            last_record = None            
            dict_time = {}

            data_gaps = []
            count_gap = 0
            count_minute = 0

            day_dir_list = []
            for d_dir in os.listdir(casa_dir):
                day_dir_list.append(d_dir)
            day_dir_list.sort()

            for d_dir in day_dir_list:
                print(d_dir)
                day_dir = os.path.join(casa_dir, d_dir)
                if os.path.isdir(casa_dir):
                    json_files = glob.glob(day_dir + "\\*.json")
                    json_file_list = []
                    for json_file in json_files:
                        json_file_list.append(json_file)
                    json_file_list.sort()                        
                    # print("Count JSON files:", len(json_file_list))
                    # appendLog(LogUtil.logFile, "Count JSON files:" + str(len(json_file_list)), True)
                    
                    for json_file in json_file_list:
                        # print(json_file)
                        obj = CuervaConsumption()
                        loaded = False
                        try:                        
                            loaded = obj.loadFromJsonFile(json_file)
                        except Exception as e:
                            print(json_file)
                            print(e)
                            
                        if loaded:
                            if obj.datetime not in dict_time:
                                if last_record is not None:
                                    if obj.datetime > last_record.datetime + timedelta(minutes=1):
                                        gap = CuervaDataGap()
                                        gap.device = obj.device
                                        gap.from_time = last_record.datetime
                                        gap.to_time = obj.datetime
                                        gap.minutes = (gap.to_time - gap.from_time).total_seconds() / 60

                                        data_gaps.append(gap)  
                                        # print(gap)        

                                        count_gap += 1
                                        count_minute += gap.minutes

                                dict_time[obj.datetime] = obj
                                last_record = obj
                        else:
                            print("Cound not load:", json_file)


            print(casa_dir, ", count_gap:", count_gap, "count_minute:", count_minute)

            report_file = working_dir + "\\data_gap_" + c_dir + "_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"            
            CsvUtil.writeCsvFile(data_gaps, report_file, header)

            print(casa_dir, datetime.now(), report_file)
            report_files.append(report_file)
            
    print(report_files)
    print("-----------------------------------------------------------------------------")
    return {"report_file": report_file, "count_gap": count_gap, "count_minute": count_minute }


def appendLog(logFile, logContent, printLog:bool=True):
    print(logContent)

    # if not os.path.exists(logFile):
    #     writeLog(logFile, "")
        
    # # with open(filename, 'w', newline='') as f:
    # f = open(logFile, "a", newline='')
    # f.write(logContent + "\n")
    # # writer = csv.writer(f)
    # # for obj in objectList:
    # #     writer.writerow(obj.getValues())
    # f.close()
    # if printLog:
    #     print(logContent)


def writeLog(logFile, logContent, printLog:bool=True):
    f = open(logFile, "w")
    # obj = objectList[0]
    f.write(logContent + "\n")
    # f.truncate()        
    f.close()
    if printLog:
        print(logContent)


""" ---------------------------------------------------------------------- """

"""
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/background/{text}")
async def send_notification(text: str, background_tasks: BackgroundTasks):        
    background_tasks.add_task(print_text, text, message="some notification")
    print("Background task is called at ", datetime.now())
    return {"message": text + ": Background task is created in the background at " + str(datetime.now())}
   

@app.get("/test")
async def test_dir():        
    # background_tasks.add_task(print_text, text, message="some notification")
    print("Before read_file is called:", datetime.now())        
    # return {"message": text + ": Background task is created in the background at " + str(datetime.now())}
    # print_text(text="Hola!", message="Vale!")
    content = read_local_file()
    print("After read_file is called:", datetime.now())        
    return {"message": content + " at " + str(datetime.now())}


def read_local_file():
    f = open('C:\\MARCOS\\UGR\\Altius-SN\\FastAPI\\fastapi-app\\requirements.txt', "r")
    content  = f.read()
    f.close()    
    return content
    # print(outDir)


def print_text(text: str, message=""):    
    # with open("log.txt", mode="w") as email_file:
    #     content = f"notification for {email}: {message}"
    #     email_file.write(content)
    print("Background task starts at ", datetime.now())
    # print(text)
    # print(message)
    # print(datetime.now())
    curDir = os.getcwd()
    print(curDir)
    
    if os.path.isfile("curDir.txt"):
        print("curDir.txt ", "exists!")
    if os.path.isfile(curDir + "/curDir.txt"):
        print(curDir + "/curDir.txt ", "exists!")
    # if os.path.isfile(curDir + "\curDir.txt"):
    #     print(curDir + "\curDir.txt ", "exists!")
    if os.path.isfile(curDir + "/./curDir.txt"):
        print(curDir + "/./curDir.txt", " exists!")

    f = open("curDir.txt", "r")
    outDir = f.read()
    f.close()
    print(outDir)

    # fileName = curDir + "/" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
    # fileName = curDir + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
    fileName = outDir + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
    print(text, fileName)
    f = open(fileName, "w")
    f.write(text)
    f.close()

    print(os.path.isfile(fileName))
    f = open(fileName, "r")
    content = f.read()
    f.close()
    print(content)    

    print("Background task ends at ", datetime.now())

@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"item_id": item_id}

# @app.get("/users/me")
# async def read_user_me():
#     return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

# @app.get("/users")
# async def read_users2():
#     return ["Bean", "Elfo"]

@app.get("/models/{model_name}")
async def get_model(model_name:ModelName):
    if model_name is ModelName.alexnet:
        return { "model_name": model_name, "message":"Dee Learning FTW!" }
    if model_name is ModelName.lenet:
        return { "model_name": model_name, "message":"LeCNN all the images!" }
    return { "model_name": model_name, "message":"Have some residuales!" }

@app.get("/files/{file_path:path}")
async def read_file(file_path:str):
    return {"file_path": file_path}

    """
