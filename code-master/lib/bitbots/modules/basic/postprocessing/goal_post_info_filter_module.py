#-*- coding:utf-8 -*-

"""
GoalPostInfoDataFilterModule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 This module tries to collect goal data.

History:
''''''''

* 09.04.14: Created (Sheepy Keßler)

* 06.08.14: Refactor (Marc Bestmann)

* 07.01.15: DBScan & Refactoring (Daniel Speck)

"""

import time
import numpy

from collections import deque, namedtuple, OrderedDict

from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_GOAL_INFO_FILTERED, DATA_KEY_GOAL_FOUND, DATA_KEY_IS_NEW_FRAME, \
    DATA_KEY_GOAL_INFO

from bitbots.util.algorithms.dbscan import DBScan
from bitbots.util.algorithms.objmlp import NeuralNetworkClass

from bitbots.debug.test.export_log import ExportLog


class GoalPostInfoDataFilterModule(AbstractModule):
    """
    FilterModule for filtering raw goal post information via a customized DBScan algorithm
    """


    def start(self, data):
        """
        Starting the filter module, initilization of buffers and stuff

        :param data: BitBots data object
        """

        ##############################################
        ### namedtuple object -> for filtered data ###
        ##############################################
        goalinfo = namedtuple("goalinfo", ["u_center", "v_center", "u_post1", "v_post1", "u_post2", "v_post2", "time"])
        data[DATA_KEY_GOAL_INFO_FILTERED] = goalinfo(u_center=0, v_center=0,
                                                     u_post1=0, v_post1=0,
                                                     u_post2=0, v_post2=0,
                                                     time=time.time())

        #####################
        ### debug toggles ###
        #####################
        self.printDebugToConsole = False   # toggles printing of debug information in console
        self.lastPrintDebugToConsole = time.time()
        self.pipeDebugIntoFile = False    # toggles saving of debug information into the debug file

        ########################################
        ### initialization things for DBScan ###
        ########################################
        self.dbscanBufferPost1 = deque()  # dbscan raw data buffer for post 1
        self.dbscanBufferPost2 = deque()  # dbscan raw data buffer for post 1

        self.dbscanBufferSize = 60        # DBScan buffer size

        self.twoGoalPostsSeen = False     # defines if one or two goal posts are seen



    def update(self, data):
        """
        Update method, starts dbscan filtering

        :param data: BitBots data object
        """

        # If no new frame is recored, than cancel exection because new information is needed
        if not data[DATA_KEY_IS_NEW_FRAME]:
            return 0

        # Cancel execution if no goal is found, because goal information is needed
        if not data[DATA_KEY_GOAL_FOUND]:
            return 1

        # store goal information in local variable
        goal_info = data[DATA_KEY_GOAL_INFO]

        # only start calculation if exactly two goal posts are found
        if len(goal_info) > 0:
            self.__dbscanStart(data)

        # debug stuff
        debug_m(2, "GOAL_INFO_FILTERED", DATA_KEY_GOAL_INFO_FILTERED)

        # Print debug infos to terminal
        if self.printDebugToConsole and self.lastPrintDebugToConsole < time.time() - 1:

            DebugString = "[GoalFilter] => "
            DebugString += "| u: " + str(round(data[DATA_KEY_GOAL_INFO_FILTERED].u_center, 2)).rjust(8) + " | "
            DebugString += "| v: " + str(round(data[DATA_KEY_GOAL_INFO_FILTERED].v_center, 2)).rjust(8) + " |"
            print(DebugString)
            self.lastPrintDebugToConsole = time.time()


    def __dbscanStart(self, data):
        """
        Starts dbscan calculation & checks requirements

        :param data: BitBots data object

        :param goal_info: data[DATA_KEY_GOAL_INFO] | raw data of goal information
        """

        # buffer goal post data for dbscan
        self.__dbscanBuffer(data)

        # start calculation
        self.__dbscanCalcAndNeuralNetFilter(data)



    def __dbscanBuffer(self, data):
        """
        Buffers data for dbscan calculation

        :param data: BitBots data object
        """
        if len(data[DATA_KEY_GOAL_INFO]) > 1:
            self.twoGoalPostsSeen = True
        else:
            self.twoGoalPostsSeen = False

        # collect current data
        x1, y1, u1, v1 = data[DATA_KEY_GOAL_INFO][0]       # first goal post
        if self.twoGoalPostsSeen:
            x2, y2, u2, v2 = data[DATA_KEY_GOAL_INFO][1]   # second goal post

        # delete entries which are too old
        # todo: get pastSeconds from config
        pastSeconds = 5  # seconds after buffer entries should be deleted

        while len(self.dbscanBufferPost1) > 0 and self.dbscanBufferPost1[0]["time"] < (time.time() - pastSeconds):
            self.dbscanBufferPost1.popleft()

        if self.twoGoalPostsSeen:
            while len(self.dbscanBufferPost2) > 0 and self.dbscanBufferPost2[0]["time"] < (time.time() - pastSeconds):
                self.dbscanBufferPost2.popleft()

        # delete entries in buffer to ensure a buffer size of <= self.dbscanBufferSize
        if len(self.dbscanBufferPost1) >= self.dbscanBufferSize:
            self.dbscanBufferPost1.popleft()

        if self.twoGoalPostsSeen:
            if len(self.dbscanBufferPost2) >= self.dbscanBufferSize:
                self.dbscanBufferPost2.popleft()

        # add current data to buffer
        if u1 <= 20000 and v1 <= 20000:
            self.dbscanBufferPost1.append({"time": time.time(), "u": u1, "v": v1})

        if self.twoGoalPostsSeen and u2 <= 20000 and v2 <= 20000:
            self.dbscanBufferPost2.append({"time": time.time(), "u": u2, "v": v2})



    def __dbscanCalcAndNeuralNetFilter(self, data):
        """
        Start dbscan calculation to filter raw data,
        initialize the neural net to filter/calibrate data

        :param data: BitBots data object
        """

        #####################
        ### initilization ###
        #####################

        post1u_filtered = None
        post1v_filtered = None

        post2u_filtered = None
        post2v_filtered = None

        goalcenteru = None
        goalcenterv = None

        goalcenterunfilteredu = None
        goalcenterunfilteredv = None

        #########################
        ### DBSCAN parameters ###
        #########################

        minPoints = 5   # minimum number of points to build a cluster
        epsilon = 75.0  # range to search for neighboring points

        ##############
        ### Post 1 ###
        ##############

        if len(self.dbscanBufferPost1) > 0:
            # Post 1 - raw u, v values
            post1rawx = numpy.array([elem["u"] for elem in self.dbscanBufferPost1])
            post1rawv = numpy.array([elem["v"] for elem in self.dbscanBufferPost1])

            # Post 1 - create a DBScan object and start calculation
            post1scan = DBScan(post1rawx, post1rawv, minPoints, epsilon)

            # Post 1 - extract filtered data out of the DBScan object
            post1u_values, post1v_values = post1scan.getFilteredData()

            # Post 1 - calculate the mean out of the filtered data
            post1u_filtered = numpy.mean(post1u_values)
            post1v_filtered = numpy.mean(post1v_values)

        ##############
        ### Post 2 ###
        ##############

        if len(self.dbscanBufferPost2) > 0:
            # Post 2 - raw u, v values
            post2rawx = numpy.array([elem["u"] for elem in self.dbscanBufferPost2])
            post2rawv = numpy.array([elem["v"] for elem in self.dbscanBufferPost2])

            # Post 2 - create a DBScan object and start calculation
            post2scan = DBScan(post2rawx, post2rawv, minPoints, epsilon)

            # Post 2 - extract filtered data out of the DBScan object
            post2u_values, post2v_values = post2scan.getFilteredData()

            # Post 2 - calculate the mean out of the filtered data
            #todo hier kommen irgendwo warnings wegen aufruf von mean auf was leerem
            post2u_filtered = numpy.mean(post2u_values)
            post2v_filtered = numpy.mean(post2v_values)


        ###################
        ### Goal center ###
        ###################

        if (post1u_filtered is not None) and\
            (post1v_filtered is not None) and\
            (post2u_filtered is not None) and\
            (post2v_filtered is not None):

            goalcenteru = (post1u_filtered + post2u_filtered) / 2.0
            goalcenterv = (post1v_filtered + post2v_filtered) / 2.0

        #######################
        ### Log/debug stuff ###
        #######################

        if self.pipeDebugIntoFile:
            exportLog = ExportLog("GoalDBScan.log")
            exportData = OrderedDict()

            x1, y1, u1, v1 = data[DATA_KEY_GOAL_INFO][0]  # collect current raw values for debugging/logging - post 1
            x2, y2, u2, v2 = data[DATA_KEY_GOAL_INFO][1]  # collect current raw values for debugging/logging - post 2

            goalcenterunfilteredu = (u1 + u2) / 2.0
            goalcenterunfilteredv = (v1 + v2) / 2.0

            exportData["post1_u_raw"] = str(u1)
            exportData["post1_v_raw"] = str(v1)
            exportData["post2_u_raw"] = str(u2)
            exportData["post2_v_raw"] = str(v2)
            exportData["post1_u_filtered"] = str(post1u_filtered)
            exportData["post1_v_filtered"] = str(post1v_filtered)
            exportData["post2_u_filtered"] = str(post2u_filtered)
            exportData["post2_v_filtered"] = str(post2v_filtered)
            exportData["goalcenter_u_filtered"] = str(goalcenteru)
            exportData["goalcenter_v_filtered"] = str(goalcenterv)
            exportData["goalcenter_u_unfiltered"] = str(goalcenterunfilteredu)
            exportData["goalcenter_v_unfiltered"] = str(goalcenterunfilteredv)

            exportLog.addDataRecord(exportData)
            exportLog.writeLog()

        ######################################
        ### Goal information - named tuple ###
        ######################################

        # prepare an object for filtered information
        goalinfo = namedtuple("goalinfo", ["u_center", "v_center", "u_post1", "v_post1", "u_post2", "v_post2", "time"])


        ##########################################
        ### Neural net - calibration/filtering ###
        ##########################################

        #inputLength = 2         # input length of input layer
        #outputLength = 2        # output length of output layer
        #hiddenLayer = [10, 5]   # hidden layer configuration (amount of hidden layers & neurons for each layer)

        # Create the neural net (MLP)
        #net = NeuralNetworkClass.NeuralNetwork(inputLength, hiddenLayer, outputLength)

        # Load saved configuration (weights & bias)
        #net.loadWeightsAndBias("/home/darwin/logfiles/")

        # filter/calibrate the goal center information via the neural net
        #goalcenteru, goalcenterv = net.calculate([goalcenteru/10000.0, goalcenterv/10000.0])["output"]

        # normalize the goal information again
        #goalcenteru *= 10000
        #goalcenterv *= 10000

        #########################
        ### Set filtered data ###
        #########################

        data[DATA_KEY_GOAL_INFO_FILTERED] = goalinfo(u_center=goalcenteru,
                                                     v_center=goalcenterv,
                                                     u_post1=post1u_filtered,
                                                     v_post1=post1v_filtered,
                                                     u_post2=post2u_filtered,
                                                     v_post2=post2v_filtered,
                                                     time=time.time())

        debug_m(3, "goal_center_u", str(goalcenteru))
        debug_m(3, "goal_center_v", str(goalcenterv))

        debug_m(3, "post1_u", str(post1u_filtered))
        debug_m(3, "post1_v", str(post1v_filtered))

        debug_m(3, "post2_u", str(post2u_filtered))
        debug_m(3, "post2_v", str(post2v_filtered))



def register(ms):
    ms.add(GoalPostInfoDataFilterModule, "GoalPostInfoDataFilter",
           requires=[DATA_KEY_GOAL_INFO,
                     DATA_KEY_IS_NEW_FRAME],
           provides=[DATA_KEY_GOAL_INFO_FILTERED])