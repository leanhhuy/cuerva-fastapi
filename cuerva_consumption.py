import json
import math
from file_util import FileUtil
from string_util import StringUtil
from datetime_util import DateTimeUtil
import csv
import datetime

class CuervaDataGap(object):
    master = ""
    device = ""
    from_time = None
    to_time = None
    minutes = None

    def getValues(self):
        values = [
            self.master,
            self.device,
            self.from_time,
            self.to_time,
            self.minutes
        ]
        return values
    
    def getTimescaleDbColumns(self):
        cols = [
            "master",
            "device",
            "from_time",
            "to_time",
            "minutes"
        ]
        return cols
    
    def toTuple(self):
        values = [
            self.master,
            self.device,
            self.from_time,
            self.to_time,
            self.minutes
        ]
        return tuple(values)


class CuervaConsumption(object):
    master = ""
    device = ""
    datetime = None
    data_date = None

    id_plant = None
    alias = None
    model = None
    serial = None
    timestamp = None
    CCM_FW = None
    opti_entries = None

    intensity = None
    voltage = None
    power_factor = None
    pactive = None
    preactive = None
    papar = None
    temp = None
    frequency = None
    eactive_q14 = None
    eactive_q23 = None
    ereact_q1 = None
    ereact_q2 = None
    ereact_q3 = None
    ereact_q4 = None
    eaparente = None

    consumo = 0
    copied = 0

    data_file = None

    def loadFromJsonFile(self, jsonFile, round_minute=True):
        # 2024.08.13
        if FileUtil.getFileSizeInByte(jsonFile) == 0:
            return False

        content = FileUtil.readContent(jsonFile, True)
        # print(content)
        json_content = json.loads(content)
        # print(json_content)

        master = json_content["master"]
        self.master = master

        analyzer = json_content["analyzer"]
        # print(analyzer)
        # print("len(analyzer)", len(analyzer))
        if len(analyzer) > 0:
            data = analyzer[0]
            # print(data)

            self.device = data["name"]

            if len(data["timestamp"].strip()) != 13:
                return False
            timestamp = StringUtil.getSubStringLeft(str(data["timestamp"]).strip(), 10)
            if round_minute:
                timestamp_val = math.floor(int(timestamp) / 60) * 60
            self.datetime = DateTimeUtil.readTimeStamp(timestamp_val)

            self.data_date = self.datetime.date()
            # print("self.datetime:", type(self.datetime), self.datetime)

            """
            self.id_plant = data["ID_plant"]
            self.alias = data["alias"]
            self.model = data["model"]
            self.serial = data["serial"]
            self.timestamp = data["timestamp"]
            self.CCM_FW = data["CCM_FW"]
            # opti_entries = None
            """

            if "Params" not in data:
                return False                
            params = data["Params"]

            cols = [
                "i", "v", "pf", "eact_q14", "eact_q23", "ereact_q1", "ereact_q2", "ereact_q3", "ereact_q4", 
                "pac", "pre", "pap", "temp", "freq", "eapa"           
            ]
            for col in cols:
                if col not in params:
                    return False

            self.intensity = params["i"]
            self.voltage = params["v"]
            self.power_factor = params["pf"]

            self.eactive_q14 = params["eact_q14"]
            self.eactive_q23 = params["eact_q23"]

            self.ereact_q1 = params["ereact_q1"]
            self.ereact_q2 = params["ereact_q2"]
            self.ereact_q3 = params["ereact_q3"]
            self.ereact_q4 = params["ereact_q4"]

            self.pactive = params["pac"]
            self.preactive = params["pre"]
            self.papar = params["pap"]
            self.temp = params["temp"]
            self.frequency = params["freq"]
            self.eaparente = params["eapa"]

            # self.consumo = data[""]
            # es eactive_q14[x] - eactive_q14[x - 1]

            self.data_file = jsonFile
            return True
        else:
            return False


    def load_from_data_row(self, row, dictCol):
        for field_name in dictCol:
            index = dictCol[field_name]
            val = row[index]
            setattr(self, field_name, val)
        return True


    def loadFromCsvFile(self, csvFile):
        obj_list = []

        # userFile = FileUtil.getFileNameFull("config/UserList.csv")
        f = open(csvFile, 'r')
        for line in csv.DictReader(f):
            obj = CuervaConsumption()

            # u.Watch = line["Watch"]
            # u.Code = line["Code"]
            # u.User = line["User"]

            if "master" in line: 
                obj.master = line["master"]

            obj.device = line["Device"]

            # obj.datetime = datetime.datetime(line["datetime"])
            timestamp = line["datetime"]
            obj.datetime = datetime.datetime.strptime(timestamp, "%m/%d/%Y %H:%M")
            obj.data_date = obj.datetime.date()

            # self.id_plant = data["ID_plant"]
            # self.alias = data["alias"]
            # self.model = data["model"]
            # self.serial = data["serial"]
            # self.timestamp = data["timestamp"]
            # self.CCM_FW = data["CCM_FW"]
            # opti_entries = None

            obj.intensity = float(line["intensity"])
            obj.voltage = float(line["voltage"])
            obj.power_factor = float(line["powerfactor"])

            obj.pactive = float(line["pactive"])
            obj.preactive = float(line["preactive"])
            obj.papar = float(line["papar"])
            obj.temp = float(line["temp"])
            obj.frequency = float(line["frequency"])

            obj.eactive_q14 = float(line["eactive_q14"])
            obj.eactive_q23 = float(line["eactive_q23"])

            obj.ereact_q1 = float(line["ereact_q1"])
            obj.ereact_q2 = float(line["ereact_q2"])
            obj.ereact_q3 = float(line["ereact_q3"])
            obj.ereact_q4 = float(line["ereact_q4"])

            obj.eaparente = float(line["eaparente"])

            if "consumo" in line:
                obj.consumo = float(line["consumo"])
            # es eactive_q14[x] - eactive_q14[x - 1]
            if "copied" in line:
                obj.copied = int(line["copied"])

            obj_list.append(obj)
        f.close()

        return obj_list

    def getTimescaleDbColumns(self):
        cols = [
            "master",
            "device",
            "datetime",

            "intensity",
            "voltage",
            "power_factor",

            "pactive",
            "preactive",
            "papar",
            "temp",
            "frequency",

            "eactive_q14",
            "eactive_q23",

            "ereact_q1",
            "ereact_q2",
            "ereact_q3",
            "ereact_q4",

            "eaparente",
            "consumo",
            "copied"
        ]
        return cols


    def toTuple(self):
        values = [
            self.master,
            self.device,
            self.datetime,

            self.intensity,
            self.voltage,
            self.power_factor,

            self.pactive,
            self.preactive,
            self.papar,
            self.temp,
            self.frequency,

            self.eactive_q14,
            self.eactive_q23,

            self.ereact_q1,
            self.ereact_q2,
            self.ereact_q3,
            self.ereact_q4,

            self.eaparente,
            self.consumo,
            self.copied
        ]
        return tuple(values)


    def copy(self, obj):
        self.master = obj.master
        self.device = obj.device
        self.datetime = obj.datetime

        self.data_date = obj.data_date

        self.id_plant = obj.id_plant
        self.alias = obj.alias
        self.model = obj.model
        self.serial = obj.serial
        self.timestamp = obj.timestamp
        self.CCM_FW = obj.CCM_FW
        # opti_entries = None

        self.intensity = obj.intensity
        self.voltage = obj.voltage
        self.power_factor = obj.power_factor

        self.eactive_q14 = obj.eactive_q14
        self.eactive_q23 = obj.eactive_q23

        self.ereact_q1 = obj.ereact_q1
        self.ereact_q2 = obj.ereact_q2
        self.ereact_q3 = obj.ereact_q3
        self.ereact_q4 = obj.ereact_q4

        self.pactive = obj.pactive
        self.preactive = obj.preactive
        self.papar = obj.papar
        self.temp = obj.temp
        self.frequency = obj.frequency
        self.eaparente = obj.eaparente

        # self.consumo = data[""]
        return True


    def getValues(self):
        # Device,datetime,intensity,voltage,powerfactor,pactive,preactive,papar,temp,frequency,eactive_q14,eactive_q23,ereact_q1,ereact_q2,ereact_q3,ereact_q4,eaparente,consumo,copied
        values = [
            self.master,
            self.device,
            self.datetime,
            self.intensity,
            self.voltage,
            self.power_factor,
            self.pactive,
            self.preactive,
            self.papar,
            self.temp,
            self.frequency,
            self.eactive_q14,
            self.eactive_q23,
            self.ereact_q1,
            self.ereact_q2,
            self.ereact_q3,
            self.ereact_q4,
            self.eaparente,
            self.consumo,
            self.copied
        ]
        return values
