def get_post_processing_modules():
    return ["bitbots.modules.basic.postprocessing.ball_info_filter_module",
            "bitbots.modules.basic.postprocessing.ball_speed_module",
            "bitbots.modules.basic.postprocessing.ball_time_module",
            "bitbots.modules.basic.postprocessing.goal_post_info_filter_module",
            "bitbots.modules.basic.postprocessing.goalie_line_intersection_module"]