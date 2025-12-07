import os.path

class FileUtil(object):

    @staticmethod 
    def readContent(textFile:str, isUTF8:bool=True):
        # f = open(textFile, encoding='utf-8', mode='r')
        f = open(textFile, encoding='utf-8', mode='r') if isUTF8 else open(textFile, mode='r')
        res = f.read()
        f.close()        
        return res    
    
    #2024.08.13 
    @staticmethod 
    def getFileSizeInByte(file_path:str):
        if os.path.exists(file_path):
            sz = os.path.getsize(file_path)
            return sz
        else:
            return 0
        