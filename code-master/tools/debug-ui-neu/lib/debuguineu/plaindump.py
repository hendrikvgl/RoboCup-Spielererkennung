import os
import time
from bitbots.util import get_config

__author__ = 'sheepy'


class DebugPlainDumper(object):

    def __init__(self):
        debug_conf = get_config()["debugui"]
        self.dump_data_in_plain = debug_conf["DUMP_RECEIVING_DATA_IN_PLAIN"]
        self.dump_data_file_path = debug_conf["DUMP_FILE_PATH"]
        self.clear_dump_file_on_startup = debug_conf["CLEAR_DUMP_FILE_PATH_ON_STARTUP"]

        # Add the dump file if it not exists by now
        self.setup_dump_file()

        # Add the Filter Chain Elements for Specific Debug Messages
        self.filter_chain_elements = [
            ball_info_fce,
            ball_info_data_filter_fce,
            goalie_line_intersection_fce,
            goal_info_fce
        ]


    def setup_dump_file(self):
        if self.dump_data_in_plain and \
                (
                    not os.path.exists(self.dump_data_file_path)
                    or self.clear_dump_file_on_startup):
            with open(self.dump_data_file_path, 'w') as f:
                f.write("# Dump of Debug Data in Plain for further Processing\n")

    def dump(self, message_type, name, value):
        if not self.dump_data_in_plain:
            return

        shall_dump = self.apply_filter_chain(message_type, name)

        if shall_dump:
            with open(self.dump_data_file_path, 'a') as f:
                f.write('{"time": "%s", "type": "%s", "name": "%s",  value: "%s"}\n' % (str(time.time()), str(message_type), str(name), str(value)))

    def apply_filter_chain(self, message_type, name):
        filter_results = [fkt(message_type, name) for fkt in self.filter_chain_elements]
        return True in filter_results




def ball_info_fce(message_type, name):
    return "Module.Vision.BallInfo" in name \
        and message_type == "number"

def ball_info_data_filter_fce(message_type, name):
    return "Module.BallInfoDataFilter.DataBallInfoFiltered" in name \
        and message_type == "number"

def goalie_line_intersection_fce(message_type, name):
    return "Module.GoalieLineIntersection" in name \
        and message_type == "number"

def goal_info_fce(message_type, name):
    return "Module.Vision.GoalInfo" in name \
        and message_type == "number"