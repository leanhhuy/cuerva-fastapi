import os
from datetime import datetime

class LogUtil(object):
    log_file = ""
    log_dir = ""
    # logFile = FileUtil.getFileNameFull("log/" + logKey + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ".txt")

    err_file = ""

    @staticmethod
    def start_log_file():        
        # if not os.path.exists("log"):
        #     # print("Log folder NOT created!")
        #     # if the demo_folder directory is not present then create it.
        #     os.makedirs("log")
        #     # print("Log folder created!")
        # # else:      
        # #     print("Log folder ALREADY created!")

        cur_time = datetime.now()
        LogUtil.log_file = "log_" + cur_time.strftime('%Y%m%d_%H%M%S') + ".txt"
        LogUtil.log_dir = cur_time.strftime('%Y%m%d')
        # print("LogUtil.log_file:", LogUtil.log_file)
        # print("LogUtil.log_dir:", LogUtil.log_dir)

        LogUtil.err_file = "err_" + cur_time.strftime('%Y%m%d_%H%M%S') + ".txt"

        if not os.path.exists("/log/" + LogUtil.log_dir):
            # print("Log day dir NOT created!")
            os.makedirs("/log/" + LogUtil.log_dir)
        #     print("Log day dir HAS BEEN created!")
        # else:
        #     print("Log day dir ALREADY created!")

        # return LogUtil.log_file, LogUtil.log_date

        full_log_file = "/log/" + LogUtil.log_dir + "/" + LogUtil.log_file
        return full_log_file
    

    @staticmethod
    def start_log_file_if_empty():           
        if LogUtil.log_file == "":
            LogUtil.start_log_file()


    @staticmethod
    def write_log(*args):
        LogUtil.start_log_file_if_empty()
        log_file_full = "/log/" + LogUtil.log_dir + "/" + LogUtil.log_file

        log_content = ""
        for x in args:
            if log_content != "":
                log_content += " "
            log_content += str(x)
        # return result
        # print(log_content)

        try:
            if not os.path.exists(log_file_full):
                f = open(log_file_full, "w")
                # obj = objectList[0]
                f.write(log_content + "\n")
                # f.truncate()        
                f.close()
            else:
                f = open(log_file_full, "a", newline='')
                f.write(log_content + "\n")
                # writer = csv.writer(f)
                # for obj in objectList:
                #     writer.writerow(obj.getValues())
                f.close()
        except Exception as e:
            print(e)

        # if printLog:
        print(log_content)
        # print(args)


    @staticmethod
    def write_err(*args):
        LogUtil.start_log_file_if_empty()
        err_file_full = "/log/" + LogUtil.log_dir + "/" + LogUtil.err_file

        err_content = ""
        for x in args:
            if err_content != "":
                err_content += " "
            err_content += str(x)

        try:
            if not os.path.exists(err_file_full):
                f = open(err_file_full, "w")
                f.write(err_content + "\n")
                f.close()
            else:
                f = open(err_file_full, "a", newline='')
                f.write(err_content + "\n")
                f.close()
        except Exception as e:
            print(e)

        # if printLog:
        print(err_content)
        # print(args)
        