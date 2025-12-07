from pydantic import BaseSettings
import configparser
import csv

# class CuervaSettings(BaseSettings):
class CuervaSettings(object):

    # data_dir: str = "C:\\MARCOS\\UGR\\Cuerva\\Data\\JSON"
    # /consumption_data

    # dict_master_to_device: dict[str, str] = {
    #     "4320070005": "CcM2-0220050025",
    #     "4320080019": "CcM2-0220050042",
    #     "4320100010": "CcM2-0220060033",
    #     "4320100012": "CcM2-0220090106",
    #     "4320100027": "CcM2-0220050075",
    #     "4320100042": "CcM2-0220090046",
    #     "4320100052": "CcM2-0220050027",
    #     "4320110002": "CcM2-0219110043"
    # }

    import_json: str = "1"    
    json_data_dir: str = "/consumption_data"
    # json_data_dir: str = "C:\\MARCOS\\UGR\\Cuerva\\Data\\JSON"    
    save_gap: str = "0"
    gap_table: str = "data_gap"

    round_minute = True
    max_minute_fill = 5
    interpolate = True

    ssh_host: str = "rt.ugr.es"
    ssh_port: int = 2233

    ssh_username: str = "scuser"
    ssh_password: str = "dc28-qa38"

    ssh_remote_bind_host: str = "localhost"
    ssh_remote_bind_port: int = 5435

    ssh_local_bind_host: str = "localhost"
    ssh_local_bind_port: int = 6543

    timescaledb_database: str = "cuerva_database"
    timescaledb_username: str = "cuerva_user"
    timescaledb_password: str = "ja28-ch18"
    timescaledb_table: str = "consumption"

    def __init__(self):
        config_file = "config.ini"
        configs = configparser.ConfigParser()
        configs.read(config_file)

        sec_import_json = configs["import_json"]
        self.import_json = sec_import_json.get("import_json", "1")
        self.json_data_dir = sec_import_json.get("json_data_dir", "/consumption_data")
        self.save_gap = sec_import_json.get("save_gap", "0")
        self.gap_table = sec_import_json.get("gap_table", "data_gap")

        self.round_minute = str(sec_import_json.get("round_minute", "0")).strip() == "1"
        self.max_minute_fill = int(sec_import_json.get("max_minute_fill", "5"))

        sec_timescaledb = configs["timescaledb"]

        self.use_ssh = sec_timescaledb.get("use_ssh", "0")

        self.ssh_host = sec_timescaledb["ssh_host"]   # ssh_host: str = "rt.ugr.es"
        self.ssh_port = int(sec_timescaledb["ssh_port"])  # ssh_port: int = 2233
        self.ssh_username = sec_timescaledb["ssh_username"]   # ssh_username: str = "scuser"
        self.ssh_password = sec_timescaledb["ssh_password"]   # ssh_password: str = "dc28-qa38"
        self.ssh_remote_bind_host = sec_timescaledb.get("ssh_remote_bind_host", "localhost")   # ssh_remote_bind_host: str = "localhost"
        self.ssh_remote_bind_port = int(sec_timescaledb.get("ssh_remote_bind_port", "5432"))  # ssh_remote_bind_port: int = 5435

        self.ssh_local_bind_host = sec_timescaledb.get("ssh_local_bind_host", "localhost")  # ssh_local_bind_host: str = "localhost"
        self.ssh_local_bind_port = int(sec_timescaledb.get("ssh_local_bind_port", "6543"))  #  ssh_local_bind_port: int = 6543

        self.timescaledb_database = sec_timescaledb["timescaledb_database"]   # timescaledb_database: str = "cuerva"
        self.timescaledb_username = sec_timescaledb["timescaledb_username"]  # timescaledb_username: str = "postgres"
        self.timescaledb_password = sec_timescaledb["timescaledb_password"]   # timescaledb_password: str = "postgres"
        self.timescaledb_host = sec_timescaledb["timescaledb_host"] # timescaledb_host: str = "host.docker.internal"
        self.timescaledb_port = int(sec_timescaledb.get("timescaledb_port", "5432")) # timescaledb_port: int = 5432

        self.timescaledb_table = sec_timescaledb.get("timescaledb_table", "consumption")  # timescaledb_table: str = "consumption"

        # f = open("MasterDevice.csv", 'r')
        # self.dict_master_to_device = {}
        # for line in csv.DictReader(f):
        #     # print(line)
        #     master = line["master"]
        #     device = line["device"]
        #     self.dict_master_to_device[master] = device
        # f.close()


    def print_settings(self):
        print("import_json:", self.import_json)
        print("json_data_dir:", self.json_data_dir)
        print("save_gap:", self.save_gap)
        print("gap_table:", self.gap_table)
        
        print("use_ssh:", self.use_ssh)

        print("ssh_host:", self.ssh_host)
        print("ssh_port:", self.ssh_port)
        print("ssh_username:", self.ssh_username)
        print("ssh_password:", self.ssh_password)
        print("ssh_remote_bind_host:", self.ssh_remote_bind_host)
        print("ssh_remote_bind_port:", self.ssh_remote_bind_port)
        print("ssh_local_bind_host:", self.ssh_local_bind_host)
        print("ssh_local_bind_port:", self.ssh_local_bind_port)

        print("timescaledb_database:", self.timescaledb_database)
        print("timescaledb_username:", self.timescaledb_username)
        print("timescaledb_password:", self.timescaledb_password)
        print("timescaledb_host:", self.timescaledb_host)
        print("timescaledb_port:", self.timescaledb_port)

        print("timescaledb_table:", self.timescaledb_table)

        # for k,v in self.dict_master_to_device.items():
        #     print(k, ":", v)

    def log_settings(self, log_func):        
        log_func("Cuerva Settings ----------------------------")
        log_func("import_json:", self.import_json)
        log_func("json_data_dir:", self.json_data_dir)
        log_func("save_gap:", self.save_gap)
        log_func("gap_table:", self.gap_table)
        
        log_func("use_ssh:", self.use_ssh)

        log_func("ssh_host:", self.ssh_host)
        log_func("ssh_port:", self.ssh_port)
        log_func("ssh_username:", self.ssh_username)
        # 2024.08.13
        #log_func("ssh_password:", self.ssh_password)
        log_func("ssh_password: <self.ssh_password>")
        log_func("ssh_remote_bind_host:", self.ssh_remote_bind_host)
        log_func("ssh_remote_bind_port:", self.ssh_remote_bind_port)
        log_func("ssh_local_bind_host:", self.ssh_local_bind_host)
        log_func("ssh_local_bind_port:", self.ssh_local_bind_port)

        log_func("timescaledb_database:", self.timescaledb_database)
        log_func("timescaledb_username:", self.timescaledb_username)
        # 2024.08.13
        #log_func("timescaledb_password:", self.timescaledb_password)
        log_func("timescaledb_password: <self.timescaledb_password>")
        log_func("timescaledb_host:", self.timescaledb_host)
        log_func("timescaledb_port:", self.timescaledb_port)

        log_func("timescaledb_table:", self.timescaledb_table)

        # log_func("Master to device table:", len(self.dict_master_to_device))
        # for k,v in self.dict_master_to_device.items():
        #     log_func("Master =", k, " -> Device =", v)
        log_func("Cuerva Settings ---------------------------- END.")
