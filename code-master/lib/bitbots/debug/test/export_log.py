'''
Created on 27.08.2014

@author: daniel
'''

"""
ExportLog
^^^^^^^^^
This Class is used to create similar looking logfiles for exporting/analyzing purposes

@author: Daniel Speck
Created on 27.08.2014

History:
* 17.02.15: Edited (Daniel Speck)
"""


class ExportLog():

    logfile = None
    logpath = None
    logheader = None
    logbuffer = ""
    
    def __init__(self, pfile, ppath="/home/darwin/logfiles/"):
        
        self.logfile = pfile
        self.logpath = ppath
        


    def addDataRecord(self, datadict):
        
        if self.logheader == None:
            self.logheader = ""
            for key in datadict:
                self.logheader += str(key) + " "
            self.logheader += "\n"
            self.logbuffer += self.logheader
            
        for key in datadict:
            self.logbuffer += str(datadict[key]) + " "
            
        self.logbuffer += "\n"
 
 
 
    def writeLog(self):
        with open(self.logpath + self.logfile, "a+") as log:
            log.write(self.logbuffer)
        self.logbuffer = ""
        
        
        
        
        
        
