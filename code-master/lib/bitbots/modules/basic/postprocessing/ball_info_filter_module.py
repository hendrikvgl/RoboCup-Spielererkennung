#-*- coding:utf-8 -*-

"""
BallInfoDataFilterModule
^^^^^^^^^^^^^^^^^^^^^^^^

This module tries to filter the ballposition

History:
''''''''

* 3.4.14: Created (Sheepy Keßler)

* 06.08.14 Refactor (Marc Bestmann)

"""
import numpy as np
import operator

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_BALL_INFO_FILTERED, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, DATA_KEY_BALL_INFO, \
    DATA_KEY_BALL_FOUND, DATA_KEY_IS_NEW_FRAME
from bitbots.modules.abstract.abstract_module import debug_m


class BallInfoDataFilterModule(AbstractModule):
    """
    Very simple implementation, to determine how fast a Ball moves towards the Robot.
    If the Ball moves, but not towards the robot, the speed would be 0
    """

    def __init__(self):
        self.ball_info_buffer_list = []
        self.weight_list = [1, 2, 1]
        self.weight_list_count = len(self.weight_list)
        self.weight_quotient = sum(self.weight_list)

        self.variance_factor = 150
        self.ball_info_speed_buffer_list = []
        self.speed_buffer_list_counter = 5

        self.ball_info_uv_prediction_buffer_list = []
        self.ball_info_uv_prediction_buffer_count = 6

    def start(self, data):
        #Initialisiere BallSpeed mit "NotFound"
        data[DATA_KEY_BALL_INFO_FILTERED] = {"uvbuffer": [None, None],
                                             "uvvariance": [None, None],
                                             "uvprediction": [None, None],
                                             "uvgrade": [None, None]}

    def buffered_uv_value(self, ball_info, data):
        # Add it
        self.ball_info_buffer_list.append([ball_info.u, ball_info.v])
        # If we have to much elements we slice the first one off
        if len(self.ball_info_buffer_list) > self.weight_list_count:
            self.ball_info_buffer_list = self.ball_info_buffer_list[1:]

        # Calculate the actual buffered value
        u_summed, v_summed, fact = 0, 0, 0
        for i in range(len(self.ball_info_buffer_list)):
            u, v = self.ball_info_buffer_list[i]
            u_summed += u * self.weight_list[i]
            v_summed += v * self.weight_list[i]
            fact += self.weight_list[i]
        u_summed /= fact
        v_summed /= fact

        data[DATA_KEY_BALL_INFO_FILTERED]["uvbuffer"] = [u_summed, v_summed]

    def prediction_uv_values_with_linear_regression(self, ball_info, data, cam_timestamp):

        self.ball_info_uv_prediction_buffer_list.append([ball_info.u, ball_info.v, cam_timestamp])

        # If we have to much elements we slice the first one off
        if len(self.ball_info_uv_prediction_buffer_list) > self.ball_info_uv_prediction_buffer_count:
            self.ball_info_uv_prediction_buffer_list = self.ball_info_uv_prediction_buffer_list[1:]

        if len(self.ball_info_uv_prediction_buffer_list) >= 4:

            timestamps = [e[2] for e in self.ball_info_uv_prediction_buffer_list]
            min_t = min(timestamps)
            max_t = max(timestamps)

            if max_t - min_t > 1:
                #say("To much time variance for estimation")
                data[DATA_KEY_BALL_INFO_FILTERED]["uvprediction"] = [None, None]
                data[DATA_KEY_BALL_INFO_FILTERED]["uvgrade"] = [None, None]
                self.ball_info_uv_prediction_buffer_list = []
            else:
                u, v, mu, mv = self.calculate_regression_delegate()

                # WARNING --- V Value not implemented by now
                data[DATA_KEY_BALL_INFO_FILTERED]["uvprediction"] = [u, v]
                data[DATA_KEY_BALL_INFO_FILTERED]["uvgrade"] = [mu, mv]

    def calculate_regression_delegate(self):
        yu = [e[0] for e in self.ball_info_uv_prediction_buffer_list]
        yv = [e[1] for e in self.ball_info_uv_prediction_buffer_list]
        timestamps = [e[2] for e in self.ball_info_uv_prediction_buffer_list]
        return self.calculate_regression(yu, yv, timestamps)

    def calculate_regression(self, yu, yv, timestamps, look_into_future=1):

        # Save how much data points we have
        number_values = len(yu)

        if number_values <= 1:
            return None, None, None, None


        # Normalizing the Timestamps - beginning at zero by subtracting the minimum
        normalize_level = min(timestamps)
        timestamps = [time_value - normalize_level for time_value in timestamps]

        # The relative time value of the latest point in data row
        # This means how much time we actually go back in time to estimate
        current_time_offset = max(timestamps)

        errors = []

        for k in range(len(timestamps) + 1):
            if k == len(timestamps):
                new_number_values = number_values
                new_yu = yu[:]
                new_yv = yv[:]
                new_timestamps = timestamps[:]
            else:
                new_number_values = number_values
                new_number_values -= 1

                new_yu = yu[:]
                new_yu.pop(k)

                new_yv = yv[:]
                new_yv.pop(k)

                new_timestamps = timestamps[:]
                new_timestamps.pop(k)

            intothefuture = max(timestamps) + look_into_future

            A = np.vstack([new_timestamps, np.ones(new_number_values)]).T
            mu, cu = np.linalg.lstsq(A, new_yu)[0]
            mv, cv = np.linalg.lstsq(A, new_yv)[0]

            # Look 5 steps into the future
            estimate_u = mu * (intothefuture) + cu
            estimate_v = mv * (intothefuture) + cv

            # Calculating the time we have left until the estimation is crossing u = 0
            time_left_till_crossing_zero_u = -cu / mu
            #print "Time left until crossing zero", time_left_till_crossing_zero_u

            # Calculate on which point v is at this point
            estimated_v_at_u_crosses_zero = mv * (time_left_till_crossing_zero_u) + cv
            #print "Estimated v on u=0", estimated_v_at_u_crosses_zero

            error = 0

            for i in range(len(new_timestamps)):
                zeitpunkt = new_timestamps[i]
                u_real, v_real = new_yu[i], new_yv[i]
                e_u = mu * (zeitpunkt) + cu
                e_v = mv * (zeitpunkt) + cv

                error += np.sqrt((u_real - e_u) ** 2 + (v_real - e_v) ** 2)

            #print "Error:", error, "for ", min(new_timestamps), "to", max(new_timestamps), "without ", timestamps[k]
            if k == len(timestamps):
                errors.append([error, None, estimate_u, estimate_v, mu, mv])
            else:
                errors.append([error, timestamps[k], estimate_u, estimate_v, mu, mv])

        min_index, min_value = min(enumerate(errors), key=operator.itemgetter(1))
        min_error = errors[min_index]
        complete_error = errors[-1]

        if complete_error[0] > 10 * min_error[0]:
            return min_error[2], min_error[3], min_error[4], min_error[5]
        else:
            return complete_error[2], complete_error[3], complete_error[4], complete_error[5]

    def ball_moving(self, ball_info, data):

        # Add it
        self.ball_info_speed_buffer_list.append([ball_info.u, ball_info.v])
        # If we have to much elements we slice the first one off
        if len(self.ball_info_speed_buffer_list) > self.speed_buffer_list_counter:
            self.ball_info_speed_buffer_list = self.ball_info_speed_buffer_list[1:]

        us = [e[0] for e in self.ball_info_speed_buffer_list]
        vs = [e[1] for e in self.ball_info_speed_buffer_list]

        np_array_us = np.array(us)
        np_array_vs = np.array(vs)

        #umean = np_array_us.mean()
        uvar = np_array_us.var()

        #vmean = np_array_vs.mean()
        vvar = np_array_vs.var()

        debug_m(3, DATA_KEY_BALL_INFO_FILTERED + ".BallUVListVariance.u", uvar)
        debug_m(3, DATA_KEY_BALL_INFO_FILTERED + ".BallUVListVariance.v", vvar)

        data[DATA_KEY_BALL_INFO_FILTERED]["uvvariance"] = [uvar, vvar]

    def update(self, data):
        if not data[DATA_KEY_IS_NEW_FRAME]:
            return 0

        if not data[DATA_KEY_BALL_FOUND]:
            return 1

        ball_info = data[DATA_KEY_BALL_INFO]

        self.buffered_uv_value(ball_info, data)
        self.ball_moving(ball_info, data)
        self.prediction_uv_values_with_linear_regression(ball_info, data, data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP])


def register(ms):
    ms.add(BallInfoDataFilterModule, "BallInfoDataFilterModule",
           requires=[DATA_KEY_BALL_INFO, DATA_KEY_BALL_FOUND, DATA_KEY_IS_NEW_FRAME, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP],
           provides=[DATA_KEY_BALL_INFO_FILTERED])
