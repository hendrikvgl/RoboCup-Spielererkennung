#-*- coding:utf-8 -*-
from bitbots.modules.basic.motion import get_motion_modules
from bitbots.modules.basic.network import get_network_modules
from bitbots.modules.basic.postprocessing import get_post_processing_modules
from bitbots.modules.basic.vision import get_vision_modules
from bitbots.modules.basic.visualization import get_visualization_modules
from bitbots.modules.basic.walking import get_walking_modules
from bitbots.modules.basic.worldmodel import get_world_model_modules


def get_other_modules():
    return ["bitbots.modules.basic.config_loader_module",
            "bitbots.modules.basic.ipc_module",
            "bitbots.modules.basic.manual_start_module",
            "bitbots.modules.basic.speaker_module",
            "bitbots.modules.basic.torjubel_module",
            "bitbots.modules.basic.dynamic_kick_module",
            "bitbots.modules.basic.dynamic_throw_module",
            "bitbots.modules.basic.remote_control_module"]


def get_enabled_basic_modules():
    # Returns a List of the Activated Modules ins this directory
    out = []
    out.extend(get_visualization_modules())
    out.extend(get_motion_modules())

    out.extend(get_network_modules())
    out.extend(get_post_processing_modules())
    out.extend(get_vision_modules())
    out.extend(get_walking_modules())
    out.extend(get_world_model_modules())
    out.extend(get_other_modules())

    return out
