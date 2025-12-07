import psycopg2 # pip install psycopg2 # pip uninstall psycopg2
from pgcopy import CopyManager # pip install pgcopy
from sshtunnel import SSHTunnelForwarder # pip install sshtunnel

from cuerva_settings import CuervaSettings
from log_util import LogUtil

class CuervaTimescaleDb(object):
    settings = None    
    conn = None
    ssh_server = None

    def __init__(self, settings: CuervaSettings) -> None:
        # pass
        self.settings = settings

    def __del__(self):        
        if self.conn is not None:
            self.conn.close()
        if self.ssh_server is not None:
            self.ssh_server.stop()        
        LogUtil.write_log("CuervaTimescaleDb -> destructor() called!")

    def start_conn(self):        
        self.conn, self.ssh_server = CuervaTimescaleDb.get_db_conn(self.settings)
        LogUtil.write_log("CuervaTimescaleDb -> start_conn() called!")

    def close(self):
        if self.conn is not None:
            self.conn.close()
        if self.ssh_server is not None:
            self.ssh_server.stop()

    def select_data_rows(self, query):
        if self.conn is None:
            self.conn, self.ssh_server = CuervaTimescaleDb.get_db_conn(self.settings)
        rows, dictCol = CuervaTimescaleDb.selectToDataRows(query=query, conn=self.conn, cueva_settings=self.settings)
        return rows, dictCol

    def import_data_objects(self, objList, dbTable: str):
        if self.conn is None:
            self.conn, self.ssh_server = CuervaTimescaleDb.get_db_conn(self.settings)
        count_time = CuervaTimescaleDb.importToTimescaleDb_simple_SSH(objList=objList, dbTable=dbTable, cueva_settings=self.settings, conn=self.conn, server=self.ssh_server)
        return count_time


    @staticmethod
    def get_db_conn(cuerva_settings: CuervaSettings):        
        if cuerva_settings.use_ssh == "1":
            # print("get_db_conn() -> use_ssh == 1")

            #         ssh_username: str = "scuser"
            # ssh_password: str = "dc28-qa38"
            # ssh_remote_bind_host: str = "localhost"
            # ssh_remote_bind_port: int = 5435
            # ssh_local_bind_host: str = "localhost"
            # ssh_local_bind_port: int = 6543

            # server = SSHTunnelForwarder(
            #     # 'rt.ugr.es',
            #     ('rt.ugr.es', 2233),
            #     ssh_username="scuser",
            #     ssh_password="dc28-qa38",
            #     remote_bind_address=('localhost', 5435),
            #     # remote_bind_address = ('localhost', 5435),
            #     local_bind_address=('localhost', 6543),  # could be any available port
            # )

            # try:
            server = SSHTunnelForwarder(
                (cuerva_settings.ssh_host, cuerva_settings.ssh_port),
                ssh_username=cuerva_settings.ssh_username,
                ssh_password=cuerva_settings.ssh_password,
                remote_bind_address=(cuerva_settings.ssh_remote_bind_host, cuerva_settings.ssh_remote_bind_port),
                local_bind_address=(cuerva_settings.ssh_local_bind_host, cuerva_settings.ssh_local_bind_port),  # could be any available port
            )
            server.start()

            # print("server:", server)
            # print("server.local_bind_host:", server.local_bind_host)  # show assigned local host
            # print("server.local_bind_port:", server.local_bind_port)  # show assigned local port
                
            # except Exception as e:
            #     print(e)
                # LogUtil.write_log(e)

        # postgres_database: str = "cuerva_database"
        # postgres_username: str = "cuerva_user"
        # postgres_password: str = "ja28-ch18"

        # Create a database connection
        """conn = psycopg2.connect(
            database='cuerva_database',
            # database=database,
            user='cuerva_user',
            password='ja28-ch18',
            host=server.local_bind_host,
            port=server.local_bind_port,
        )"""

        host=cuerva_settings.timescaledb_host
        port=cuerva_settings.timescaledb_port
        if cuerva_settings.use_ssh == "1":
            host=cuerva_settings.ssh_local_bind_host
            port=cuerva_settings.ssh_local_bind_port

        # print("get_db_conn() -> before Connect")
        # print("cuerva_settings.timescaledb_database:", cuerva_settings.timescaledb_database)
        # print("cuerva_settings.timescaledb_username:", cuerva_settings.timescaledb_username)
        # print("cuerva_settings.timescaledb_password:", cuerva_settings.timescaledb_password)
        # print("host:", host)
        # print("port:", port)

        # try:
        conn = psycopg2.connect(
            database= cuerva_settings.timescaledb_database,
            user= cuerva_settings.timescaledb_username,
            password= cuerva_settings.timescaledb_password,
            host=host,
            port=port,
        )

        # except Exception as e:
        #     print(e)
        #     print("cuerva_settings.timescaledb_database:", cuerva_settings.timescaledb_database)
        #     print("cuerva_settings.timescaledb_username:", cuerva_settings.timescaledb_username)
        #     print("cuerva_settings.timescaledb_password:", cuerva_settings.timescaledb_password)
        #     print("host:", host)
        #     print("port:", port)
        #     raise e

        # print("conn.status:", conn.status)
        # print("conn:", conn)

        # print("get_db_conn() -> after Connect")
        if cuerva_settings.use_ssh == "1":
            # print("conn.status:", conn.status)
            return conn, server
        else:
            return conn, None


    @staticmethod
    def importToTimescaleDb_simple_SSH(objList, dbTable, cueva_settings: CuervaSettings, conn=None, server=None):
        # garminObj: GarminObj, jsonFileNamePattern: str, database: str,
        #                    fromDate: datetime.date, toDate: datetime.date):
        # countGeneral = 0
        countTime = 0

        # cols = garminObj.getTimescaleDbColumns()
        cols = []
        if len(objList) > 0:
            firstObj = objList[0]
            cols = firstObj.getTimescaleDbColumns()
        # print("number of column:", len(cols))

        # dbTable = garminObj.getTimescaleDbTable()
        # dbTable = "consumption"
       
        # dbTable = cueva_settings.timescaledb_table        

        # print("dbTable:", dbTable, ", number of column:", len(cols))

        # https: // sshtunnel.readthedocs.io / en / latest /
        # https: // pypi.org / project / sshtunnel /
        # server = SSHTunnelForwarder()
        # SSHTunnelForwarder(
        #     ('rt.ugr.es', 2230),
        #     ssh_username="scuser",
        #     ssh_password="Gd245-kor47",
        #     remote_bind_addresses=('127.0.0.1')
        # )

        """
        server = SSHTunnelForwarder(
            # 'rt.ugr.es',
            ('rt.ugr.es', 2233),
            ssh_username="scuser",
            ssh_password="dc28-qa38",
            remote_bind_address=('localhost', 5435),
            # remote_bind_address = ('localhost', 5435),
            local_bind_address=('localhost', 6543),  # could be any available port
        )        
        server.start()
        print(server.local_bind_host)  # show assigned local port
        print(server.local_bind_port)  # show assigned local port
        """

        """
        # Create a database connection        
        conn = psycopg2.connect(
            database='cuerva_database',
            # database=database,
            user='cuerva_user',
            password='ja28-ch18',
            host=server.local_bind_host,
            port=server.local_bind_port,
        )"""

        internal_conn = False
        if conn is None:        
            conn, server = CuervaTimescaleDb.get_db_conn(cueva_settings)
            internal_conn = True
            
        # print("conn.status:", conn.status)
        
        # values = [ (0, now, 'Jerusalem', 72.2), (1, now, 'New York', 75.6) ]
        values = []

        for obj in objList:
            values.append(obj.toTuple())
            countTime += 1

        copy_mgr = CopyManager(conn, dbTable, cols)
        copy_mgr.copy(values)

        conn.commit()

        if internal_conn:
            conn.close()

            # Stop the SSH tunnel
            if server is not None:
                server.stop()

        # return garminObjects
        return countTime


    @staticmethod
    def selectToDataRows(query, conn, cueva_settings):
        # https://www.linkedin.com/pulse/how-create-pandas-data-frame-postgresql-psycopg-vitor-spadotto/

        # print(type(self.conn), self.conn)
        ssh_server = None

        use_local_conn = False
        if conn is None:
            use_local_conn = True
            # print("selectToDataRows() -> BEFORE get_db_conn")
            conn, ssh_server = CuervaTimescaleDb.get_db_conn(cueva_settings)
            # print("selectToDataRows() -> AFTER get_db_conn")

        # print("selectToDataRows() -> BEFORE execute")
        cursor = conn.cursor()
        cursor.execute(query)

        # print("selectToDataRows() -> AFTER execute")

        cols = []
        for d in cursor.description:
            cols.append(d[0])
        # print(cols)
        dictCol  = {}
        for index, col in enumerate(cols):
            dictCol[col] = index

        rows = cursor.fetchall()
        cursor.close()
        # if len(rows) > 0:
        #     if not isinstance(rows[0], tuple):
        #         rows = [tuple(r) for r in rows]

        # print("selectToDataRows() -> CLOSE")

        if use_local_conn:            
            # print("selectToDataRows() -> use_local_conn")
            conn.close()
            if ssh_server is not None:
                ssh_server.stop()
            # print("selectToDataRows() -> use_local_conn -> CLOSED!")

        # print("rows:", rows)
        # print("dictCol:", dictCol)

        # return rows, cols
        return rows, dictCol


    """
    @staticmethod
    def connect_postgres():
        print("Before connecting Postgres:", datetime.now())

        database = "example"
        # host = "localhost"
        host = "host.docker.internal"
        print("host:", host)    
        port = "5432"
        user = "postgres"
        password = "postgres"

        conn = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
        )
        print(conn)

        status = str(conn.status)    
        print("conn.status:", status)

        query = "SELECT * FROM company"
        cursor = conn.cursor()
        cursor.execute(query)
        cols = []
        for d in cursor.description:
            cols.append(d[0])
        print(cols)

        rows = cursor.fetchall()    
        cursor.close()
        
        conn.close()
        print("After connecting Postgres:", datetime.now())    
        print(rows)

        content = []
        for row in rows:
            content.append(str(row))

        result_file = "/data/saved_result_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
        f = open(result_file, "w")
        # f.write(str(cols))
        f.writelines(content)    
        f.close()
        print("Content written to file", result_file)
        
        return {"message": status + " at " + str(datetime.now())}
        """