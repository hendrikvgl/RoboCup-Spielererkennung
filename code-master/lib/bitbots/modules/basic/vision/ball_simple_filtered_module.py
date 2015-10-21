"""
BallSimpleFilteredModule
^^^^^^^^^^^^^^^^^^^^^^^^
This module tries to filter the ball information in a simple but
most times relatively efficient way.

@author: Daniel Speck (2speck@informatik.uni-hamburg.de)
Created on 22.08.2014
"""

import time
import math
import numpy

from collections import deque, OrderedDict, namedtuple

from bitbots.modules.abstract.abstract_module import AbstractModule, debug_m

#from bitbots.debug.test.GoalieDebug import GoalieDebug
#from bitbots.debug.test.GoalieExportLog import GoalieExportLog

from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME, \
    DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_BALL_LAST_SEEN, \
    DATA_KEY_BALL_INFO_SIMPLE_FILTERED, DATA_KEY_WALKING_RUNNING

# TODO: implement config data
# from bitbots.util import get_config

# Original ballinfo from DATA_KEY_BALL_INFO
# ballinfo -> namedtuple("BallInfo", ("u", "v", "x", "y", "radius", "rating", "distance"))


class BallSimpleFilteredModule(AbstractModule):
    """
    FilterClass -> some simple filters for filtering inexact values of ballinfo
    
    returns a namedtuple of filtered ball information:
    
       namedtuple("filteredBallInfo", ("u", "v", "distance", "angle", "uestimate", "vestimate", "time"))
        
           u/v: vertical/horizontal distance to the ball
           distance: shortest linear distance to the ball ( distance = sqrt(u**2 + v**2) )
           angle: angle under which the ball is seen
           uestimate/vestimate: estimated u/v position of the ball in the future
           time: timestamp (time.time()) of the ball information
    """

    def start(self, data):
        """
        initialization
        """
                
        # u,v -> vertikale/horizontale Entfernung zum Ball
        # distance -> Luftlinienentfernung zum Ball
        # angle -> Winkel, unter dem der Ball gesehen wird
        # time -> Zeitpunkt, zu dem die Ballinfos gespeichert wurden

        # initialize things
        self.balls_info = deque([])  # queue of ball information dictionaries
        
        # configuration things
        self.balls_info_maxlength = 10  # maximum queue length
        
        # NamedTuple
        self.nmball = namedtuple("nmball",
                                          ("u", "v", "distance", "angle", "time"))
        
        # current values
        self.filteredCurrent = dict()
        
        # old values
        self.filteredOld = dict()

        # create and/or use logfile
        #self.log = GoalieDebug("SimpleFilter.log")
        #self.exportLog = GoalieExportLog("SimpleFilterExport.txt")

        # TODO: implement config data
        # load config
        # config = get_config()

    def update(self, data):
        """
        filter/calculate ball information
        """
        
        # set data as field
        self.data = data
        
        # If data record is older than 3 seconds discard data record
        self.balls_info = deque(item for item in self.balls_info if item["time"] >= (time.time() - 3)) 
        
        # Skip all things if no ball is found or new frame is loaded
        if not (self.data[DATA_KEY_BALL_FOUND] and self.data[DATA_KEY_IS_NEW_FRAME]):
            return
        
        # update queue -> save/add current ball data in queue
        self.fillBuffer()
       
        # calculate filtered data
        self.filterData()
        
        # set filtered/ready data
        self.data[DATA_KEY_BALL_INFO_SIMPLE_FILTERED] = self.filteredBallInfo

        # send debug
        debug_m(3, "u", int(self.filteredBallInfo.u))
        debug_m(3, "v", int(self.filteredBallInfo.v))
        debug_m(3, "distance", int(self.filteredBallInfo.distance))
        debug_m(3, "uestimate", int(self.filteredBallInfo.uestimate))
        debug_m(3, "vestimate", int(self.filteredBallInfo.vestimate))
        debug_m(3, "angle", int(self.filteredBallInfo.angle))
        debug_m(3, "time", int(self.filteredBallInfo.time))

    def convertDict(self, dictionary, nmname):
        """
        helper: convert a dictionary to a named tuple
        """
        return namedtuple(str(nmname), dictionary.keys())(**dictionary)
    
    def convertNamedTuple(self, some_named_tuple):
        """
        helper: convert a namedtuple to a dictionary
        """
        return dict((s, getattr(some_named_tuple, s)) for s in some_named_tuple._fields) 

    def fillBuffer(self):
        """
        fill/update buffer
        """
        
        if len(self.balls_info) < self.balls_info_maxlength:  # does the queue have empty slots? 
            self.addNewBallToList()
        else:  # queue is full, so delete oldest entry and add newest one
            self.balls_info.popleft()
            self.addNewBallToList()
    
    def addNewBallToList(self):
        """
        add the current data record of ball information to buffer
        """
        
        # temp container
        tmp_ball = dict()
        
        # collect current ball information
        tmp_ball["u"] = self.data[DATA_KEY_BALL_INFO].u
        tmp_ball["v"] = self.data[DATA_KEY_BALL_INFO].v
        tmp_ball["distance"] = self.data[DATA_KEY_BALL_INFO].distance
        tmp_ball["angle"] = 1  # initialize to 1, calculated later
        tmp_ball["rating"] = self.data[DATA_KEY_BALL_INFO].rating
        tmp_ball["walking"] = self.data[DATA_KEY_WALKING_RUNNING]
        tmp_ball["time"] = time.time()  # timestamp of new data record
        
        # add new data record of the ball to our buffer
        self.balls_info.append(tmp_ball)
        
    def filterData(self):    
        """
        filters the ball data records with mean and standard deviation,
        after cleaning the data records the weighted mean is calculated
        and used for calculating the angle and other ball information attributes
        """
        
        u_list = list(item["u"] for item in self.balls_info)
        v_list = list(item["v"] for item in self.balls_info)
        
        # standard deviaton
        u_std = numpy.std(u_list)
        v_std = numpy.std(v_list)
        
        # mean values
        u_mean = numpy.mean(u_list)
        v_mean = numpy.mean(v_list)
        
        # filter all data which has a greater absolute distance in comparison
        # to the mean + standard deviation
        # list of tuples (itemvalue, itemrating)
        u_filtered_list = self.filterBadListEntries("u", u_std, u_mean)
        v_filtered_list = self.filterBadListEntries("v", v_std, v_mean)
        
        # weighted mean values of filtered lists
        u_filtered = self.getWeightedMean(u_filtered_list)
        v_filtered = self.getWeightedMean(v_filtered_list)
        
        distance_filtered = math.sqrt(u_filtered ** 2 + v_filtered ** 2)
        
        # filtered angle
        angle_filtered = math.degrees(math.atan2(v_filtered, u_filtered))
        
        # set/update old data
        try:
            self.filteredOld = self.filteredCurrent.copy()
        except: #todo refactor
            pass

        # build filtered data
        filtered_data = dict()
        filtered_data["u"] = u_filtered
        filtered_data["v"] = v_filtered
        filtered_data["distance"] = distance_filtered 
        filtered_data["angle"] = angle_filtered
        try:
            filtered_data["uestimate"] = self.filteredOld["uestimate"]  # last value
            filtered_data["vestimate"] = self.filteredOld["vestimate"]  # last value
        except:
            filtered_data["uestimate"] = 1  # default value
            filtered_data["vestimate"] = 1  # default value
            
        filtered_data["time"] = time.time()

        # calculate filtered uestimate, vestimate
        try:
            # time difference between old and current filtered data record
            timediff = float(filtered_data["time"] - self.filteredOld["time"])
            
            # factor to correct the u/v movement to mm/s from mm/timediff
            perSecCorrector = 1.0 / timediff
            
            # factor to get the estimate in seconds
            # 0.7 e.g. would be the estimated u/v position 0.7 seconds in future
            futureseconds = 0.7
            
            # u/v movement (difference between the old and current position vector)
            u_mov = self.calcFilteredMovement("u", u_filtered)
            v_mov = self.calcFilteredMovement("v", v_filtered)
            
            # calculate the new estimated u/v positions in future
            filtered_data["uestimate"] = u_filtered + u_mov * perSecCorrector * futureseconds
            filtered_data["vestimate"] = v_filtered + v_mov * perSecCorrector * futureseconds

        except:
            pass
        
        # Set filteredCurrent to the freshly filtered_data data record
        self.filteredCurrent = filtered_data

        # set calculated data
        self.filteredBallInfo = self.convertDict(self.filteredCurrent, "filteredBallInfo")

    def filterBadListEntries(self, item, std, mean):
        """
        :param item: the value to filter ( u or v ball information )
        :type item: String
        
        :param std: standard deviation of the unfiltered buffered items ( u or v )
        :type std: float
        
        :param mean: mean of the unfiltered buffered items ( u or v )
        :type mean: float
        
        :returns: returns a list of filtered u or v tuples (filtered_u_value, u_rating) 
        """
        # if walking is active, tense up standard deviation filter
        if self.data[DATA_KEY_WALKING_RUNNING]:
            std = std * 0.9
        
        # Add only entries in range of standard deviation
        # absolute distance of (mean - current_value) should be smaller than standard deviation
        locbuffer = list(
                         (x[item], x["rating"]) for x in self.balls_info
                          if math.fabs(mean - x[item]) <= std
                          )
                
        # If most values are corrupted (to far away from mean), repeat
        # selection with a more moderate/relaxed standard deviation filter
        if len(locbuffer) < 3:  # filtered too many entries?
            if len(self.balls_info) >= 3:  # enough data records in buffer?
                return self.filterBadListEntries(item, std * 1.25, mean)
            else:  # too less data records in buffer, so simply return now
                return list((x[item], x["rating"]) for x in self.balls_info)
        else:  # filtering worked fine
            return locbuffer

    def getWeightedMean(self, listdata):
        """
        Calculate the weighted Mean of u or v
        
        :param listdata: a list of tuples of u or v ball information
        :type list: list((u_value, u_rating))
        """
        
        # create a list with just itemValues
        itemValues = list(x[0] for x in listdata)
        
        # create a list with itemWeights ( weight is 100.0 - rating )
        itemWeights = list(
                           (100.0 - x[1])
                           if (100.0 - x[1]) > 0
                           else
                           0.1
                           for x in listdata
                           )
        
        # If the sum of itemWeights is zero for some reason, simply add 1 to the last values weight
        if not(numpy.sum(itemWeights) > 0):
            weightvalue = itemValues.pop() + 1
            itemWeights.append(weightvalue) 
        
        # return the weighted mean of itemValues
        return numpy.average(itemValues, weights=itemWeights)

    def calcFilteredMovement(self, item, newValue):
        """
        calculate the difference between the new filtered value and the last filtered value ( u or v )
        
        :param item: u or v
        :type item: String
        
        :param newValue: actual u or v value
        :type newValue: float
        """
        
        return float(newValue) - float(self.filteredOld[item])


# register module
def register(ms):
    ms.add(BallSimpleFilteredModule, "BallSimpleFiltered",
           requires=[
               DATA_KEY_IS_NEW_FRAME,
               DATA_KEY_BALL_INFO,
               DATA_KEY_BALL_FOUND,
               DATA_KEY_BALL_LAST_SEEN,
               DATA_KEY_WALKING_RUNNING,
               ],
           provides=[
               DATA_KEY_BALL_INFO_SIMPLE_FILTERED])
