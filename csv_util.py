import csv

class CsvUtil(object):

    @staticmethod
    def writeCsvFile(objectList, csvFile, header):
        # https://www.onlinetutorialspoint.com/python/how-to-convert-python-list-of-objectList-to-csv-file-example.html
        if len(objectList) > 0:
            # appendLog(LogUtil.logFile, str(len(objectList)) + " rows: " + csvFile, True)
            
            f = open(csvFile, "w")
            # obj = objectList[0]
            # f.write(obj.getHeader() + "\n")
            f.write(header + "\n")
            # f.write(obj.getHeader())
            # f.truncate()        
            f.close()
            
            # with open(filename, 'w', newline='') as f:
            f = open(csvFile, "a", newline='')
            writer = csv.writer(f)
            for obj in objectList:
                writer.writerow(obj.getValues())
            f.close()
        # else:
        #     appendLog(LogUtil.logFile, "No data: " + csvFile, True)


    @staticmethod
    def appendCsvFile(objectList, csvFile):
        # https://www.onlinetutorialspoint.com/python/how-to-convert-python-list-of-objectList-to-csv-file-example.html
        if len(objectList) > 0:
            # appendLog(LogUtil.logFile, str(len(objectList)) + " rows: " + csvFile, True)
            
            # f = open(csvFile, "w")            
            # # obj = objectList[0]
            # # f.write(obj.getHeader() + "\n")
            # f.write(header + "\n")
            # # f.write(obj.getHeader())
            # # f.truncate()        
            # f.close()
            
            # with open(filename, 'w', newline='') as f:
            f = open(csvFile, "a", newline='')
            writer = csv.writer(f)
            for obj in objectList:
                writer.writerow(obj.getValues())
            f.close()
        # else:
        #     appendLog(LogUtil.logFile, "No data: " + csvFile, True)
