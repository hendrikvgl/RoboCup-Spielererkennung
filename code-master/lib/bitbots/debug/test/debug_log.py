from __future__ import division
import datetime
"""
DebugLog
^^^^^^^^
This Class is used to create similar looking logfiles

@author: Jackie Huynh
Created on 27.08.2014

History:
* 28.08.14: Edited (Dennis Rupnow)
* 17.02.15: Refactoring (Daniel Speck)
"""

class DebugLog():

    LOGTIMEFORMAT = "%H:%M:%S"                                        # formatting of the time
    LOGLINESEPERATOR = "======================================="      # seperator
    LOGSMALLLINESEPERATOR= "---------------------------------------"  # different seperator

    logfile = ""                                                      # name of the logfile
    logpath = ""                                                      # path to the logfile
    strbuffer = []                                                    # buffer to store the string to log
    TSflag = True                                                     # global TimeStamp Flag

    def __init__(self, fname, path="/home/darwin/logfiles/"):
        """
        creates a logfile
        """
        self.LOGPATH = path
        self.logfile = fname

    def appendStrBuffer(self, value, tsflag):
        """
        used to append a string to the buffer with it's time and a tsflag
        tsflag: True, if the next String should have a timestamp in the logfile ([H:M:S]),
                False, if not
        """
        time = datetime.datetime.now()
        self.strbuffer.append((str(value), time, tsflag))

    def givePercentage(self, value1, value2):
        """
        gives the percentage of two values and returns it in a sentence
        """
        percentage = round(100 / (value2 / value1), 2)
        self.appendStrBuffer(str(value1) + " ist " + str(percentage) + "% von " + str(value2), False)

    def add(self, value):
        """
        simply to add any string to the log
        """
        self.appendStrBuffer(value, False)

    def addSeperator(self):
        """
        used to add a seperator to the log (" | ")
        """
        self.appendStrBuffer(" | ", False)

    def addSpacesRight(self, value, width):
        """
        used to add a string to the buffer and to add an amount of spaces right to it
        the amount of spaces will be calculated so that when the length of the string varies,
        the formatting won't get screwed
        """
        self.appendStrBuffer(value, False)
        for i in range(1, width + 1 - len(value)):
            self.appendStrBuffer(" ", False)

    def addSpacesLeft(self, value, width):
        """
        used to add a string to the buffer and to add an amount of spaces left to it
        the amount of spaces will be calculated so that when the length of the string varies,
        the formatting won't get screwed
        """
        for i in range(1, width + 1 - len(value)):
            self.appendStrBuffer(" ", False)
        self.appendStrBuffer(value, False)

    def addLineseperator(self):
        """
        adds a set lineseperator to the log
        """
        self.appendStrBuffer(self.LOGLINESEPERATOR, False)

    def addSmallLineseperator(self):
        """
        adds a set (smaller) lineseperator to the log
        """
        self.appendStrBuffer(self.LOGSMALLLINESEPERATOR, False)

    def newLine(self):
        """
        used to go into a new line of the log
        """
        self.appendStrBuffer("\n", True)

    def getFormattedTime(self, time):
        """
        returns the formatted [H:M:S] time of the saved times
        """
        return time.strftime(self.LOGTIMEFORMAT)

    def logWrite(self):
        """
        used to write the StringBuffer into the logfile
        this method uses the stored tsflags to determine wether or not TimeStamps have to be added
        """
        strContainer = ""
        for item in self.strbuffer:
            if self.TSflag:
                strContainer += "[" + self.getFormattedTime(item[1]) + "] " + item[0]
            else:
                strContainer += item[0]
            if item[2]:
                self.TSflag = True
            else:
                self.TSflag = False
        with open(self.LOGPATH + self.logfile, "a+") as glogfile:
            glogfile.write(strContainer)
        self.strbuffer = []

    def clearFile(self):
        """
        used to clear the content of the logfile
        """
        with open(self.LOGPATH + self.logfile, "w"):
            pass