#-*- coding:utf-8 -*-
"""
CameraModule
^^^^^^^^^^^^

Provides camera, can also be simulated

History:
''''''''

* ??.??.??: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)
"""

import os
import time

from bitbots.modules.abstract import AbstractThreadModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_CONFIG, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, DATA_KEY_CAMERA_FRAME_VERSION, \
    DATA_KEY_RAW_IMAGE, DATA_KEY_IPC, DATA_KEY_IMAGE_POSE, DATA_KEY_CAMERA_FOOT_PHASE, DATA_KEY_CAMERA_RESOLUTION, \
    DATA_KEY_IMAGE_FORMAT, DATA_KEY_CAMERA_EXPOSURE_CALLBACK, DATA_KEY_DATA_CAMERA, DATA_KEY_IMAGE_PATH
from bitbots.vision.capture import VideoCapture
from bitbots.modules.keys.visualization_keys import VIZ_KEY_VIZ_ACTIVE, VIZ_KEY_NUMBER_IMAGES, VIZ_KEY_INDEX_IMAGE, \
    VIZ_KEY_REQUEST_NEW_FRAME
from bitbots.util.speaker import say
from bitbots.util.file_management import read_pose_file, read_yuyv_file, load_filenames, get_yuyv_image_size, \
    load_folder_filenames
from bitbots.robot.pypose import PyPose as Pose


class SimCamera(object):
    """
    Gets picture from IPC of the simulationbridge.
    """

    def __init__(self, ipc):
        self.ipc = ipc
        self.exposure_absolute = 0

    def grab(self):
        time.sleep(1)  # simulator gibt x bilder pro sekunde get_image weis nich ob das neu is
        return self.ipc.get_image()


class DataCamera(object):
    """
    Provides the simulated camera, wich reads saved images. Preload can be set to buffer the images before.
    """

    def __init__(self, images, debug, buffer_files=False):
        self.debug = debug.sub("DataCamera")
        self.exposure_absolute = 0
        self.images = images
        self.indexed_images = images
        self.pose = None
        self.data = []
        self.buffer_files = buffer_files
        if buffer_files:
            self.preload()

    def preload(self):
        i = 0
        while self.images:
            name = self.images.pop(0)
            self.debug.log("Lese Frame '%s'" % name)

            yuyv = read_yuyv_file(name)
            pose = read_pose_file(name, default=Pose())
            self.data.append((yuyv, pose))
            i += 1
            if i > 100:
                # wir wollen den spiecher nicht vollständig verfüllen
                break

    def grab(self):

        if self.buffer_files:
            #mit buffer
            if not self.data:
                if self.images:
                    self.preload()
                else:
                    #keine bilder mehr
                    return None
            yuyv, self.pose = self.data.pop(0)
            return yuyv
        else:
            #ohne buffer
            if not self.images:
                #keine bilder mehr
                return None
            name = self.images.pop(0)
            self.debug.log("Lese Frame '%s'" % name)
            self.pose = read_pose_file(name, default=Pose())
            return read_yuyv_file(name)

    def get_image(self, index):
        name = self.indexed_images[index]
        self.pose = read_pose_file(name, default=Pose())
        return  read_yuyv_file(name)


class CameraModule(AbstractThreadModule):
    def __init__(self):
        super(CameraModule, self).__init__(
            requires=[DATA_KEY_IPC, DATA_KEY_CONFIG, VIZ_KEY_REQUEST_NEW_FRAME,VIZ_KEY_INDEX_IMAGE], #todo the viz keys are only required for visualization
            provides=[
                DATA_KEY_RAW_IMAGE,
                DATA_KEY_IMAGE_POSE,
                DATA_KEY_CAMERA_FRAME_VERSION,
                DATA_KEY_CAMERA_RESOLUTION,
                DATA_KEY_CAMERA_FOOT_PHASE,
                DATA_KEY_CAMERA_CAPTURE_TIMESTAMP]
        )

        self.die = False
        self.set(DATA_KEY_IMAGE_POSE, None)
        self.set(DATA_KEY_RAW_IMAGE, None)
        self.set(DATA_KEY_CAMERA_FOOT_PHASE, 0)
        self.set(DATA_KEY_CAMERA_FRAME_VERSION, -1)
        self.set(DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, None)

        self.simulation = False
        self.data_camera = False
        self.viz_active = False
        self.image_index = 0
        self.cap = None

    def start(self, data):
        super(CameraModule, self).start(data)
        config = data[DATA_KEY_CONFIG]["vision"]
        self.new_camera = config["newCamera"]
        self.viz_active = data.get(VIZ_KEY_VIZ_ACTIVE, False)
        self.image_index = data.get(VIZ_KEY_INDEX_IMAGE, 0)

        if self.new_camera:
            self.exposure_absolute = config["CAMERA_EXPOSURE_ABSOLUTE"]
        else:
            self.exposure_absolute = config["CAMERA_EXPOSURE_ABSOLUTE"] * 40
        data[DATA_KEY_CAMERA_EXPOSURE_CALLBACK] = self.camera_exposure_request
        if data.get("Simulation", False):
            # wenn wir in einer Simulation sind, wollen wir anders auf die
            # Bilder zugreifen (kommen dann von der Motion aus dem Simulator)
            # Die haben eine andere Auflösung!!
            self.debug.warning("Simulation Mode")
            self.simulation = True
            h, w = data[DATA_KEY_IPC].get_image().shape
            dim = (int(w / 3), h)
            data[DATA_KEY_CAMERA_RESOLUTION] = dim
            data[DATA_KEY_IMAGE_FORMAT] = 'RGB'
            self.cap = SimCamera(data[DATA_KEY_IPC])
        elif data.get(DATA_KEY_DATA_CAMERA, False):
            # wir benutzen bilder als kamera
            self.simulation = False
            self.data_camera = True
            #prüfen ob wir bilder vorladen wollen
            buffer_files = data.get("Buffer", False)
            #Pfad zu den zu ladenden Bildern
            images = data.get(DATA_KEY_IMAGE_PATH, False)
            #print "images1: " + str(images)
            images = load_folder_filenames(images)
            #print "images2: " + str(images)
            if not images:
                #falls der Pfad falsch ist
                raise SystemExit(
                    "No Imagesfiles found. Please check if the path is right and setted in the data dictionary")
            data[VIZ_KEY_NUMBER_IMAGES] = len(images)
            print len(images)
            data[DATA_KEY_IMAGE_FORMAT] = 'YUYV'
            width, height = get_yuyv_image_size(read_yuyv_file(images[0]))
            data[DATA_KEY_CAMERA_RESOLUTION] = (width, height)
            self.cap = DataCamera(images, self.debug, buffer_files)
        else:
            self.simulation = False
            self.set_up_camera(data)
            if self.cap:
                data[DATA_KEY_IMAGE_FORMAT] = 'YUYV'
            else:
                say("No Camera Found!")
                raise SystemExit("No Camera")
            data[DATA_KEY_CAMERA_RESOLUTION] = (self.cap.width, self.cap.height)

    def update(self, data):
        if self.die:
            raise SystemExit("No Camera")

        super(CameraModule, self).update(data)

    def set_up_camera(self, data):
        if not self.cap and not self.simulation and not self.data_camera:
            dev = os.listdir('/dev/')
            video_devs = []
            for name in dev:
                if name[0:5] == "video":
                    video_devs.append(name)
            if not video_devs:
                raise SystemError("No Video Device found in /dev/")
            # Webcam starten
            for video_dev in video_devs:
                try:
                    vision_config = data[DATA_KEY_CONFIG]["vision"]
                    debug_m(2, "Starte Kamera auf /dev/%s" % video_dev)
                    width, height = vision_config["CameraResolution"]
                    self.cap = VideoCapture('/dev/%s' % video_dev, width, height)
                    self.cap.set_noop_image_decoder()
                    self.cap.white_balance_auto = False
                    self.cap.white_balance = vision_config["CAMERA_WHITE_BALANCE"]  #0.5
                    self.cap.brightness = vision_config["CAMERA_BRIGHTNESS"]  #0.5
                    self.cap.focus_auto = False
                    self.cap.focus_absolute = vision_config["CAMERA_FOCUS_ABSOLUTE"]  #10
                    self.cap.gain_auto = vision_config["CAMERA_GAIN_AUTO"]
                    self.cap.gain = vision_config["CAMERA_GAIN"]
                    self.cap.saturation = vision_config["CAMERA_SATURATION"]
                    self.cap.exposure_auto = 1
                    self.cap.exposure_auto_priority = False
                    self.cap.exposure_absolute = self.exposure_absolute
                    self.cap.contrast = vision_config["CAMERA_CONTRAST"]
                    self.cap.max_fps = vision_config["MAX_FPS"]

                    self.cap.start()
                    return True
                except Exception as e:
                    self.debug.error(e, "Error in Camera Module: ")
                    self.cap = None
                    raise
            return False
        return True  # Kamera ist schon initialisiert

    def camera_exposure_request(self, factor):
        debug_m(3, "Callback success")
        if self.new_camera is True:
            factor = -factor
        if factor > 0:
            self.cap.exposure_absolute = (self.cap.exposure_absolute + 1) * 1.333
        else:
            self.cap.exposure_absolute = max(self.cap.exposure_absolute * 0.75, 1.0)
        debug_m(3, "Exposure: %d " % self.cap.exposure_absolute)
        debug_m(3, "Exposure", self.cap.exposure_absolute)

    def run(self):

        #time_offset = time.time()
        version = 0
        while True:
            try:
                if not self.set_up_camera(None):
                    # Kamera wurde nicht initialisiert
                    break

                if self.cap is None:
                    break

                while True:
                    if self.viz_active and self.data_camera:
                        #print "camera 3"
                        if self.get(VIZ_KEY_REQUEST_NEW_FRAME):
                            self.image_index = self.get(VIZ_KEY_INDEX_IMAGE, 0)
                            print "get frame %d" % self.image_index
                            pic = self.cap.get_image(self.image_index)
                            self.set(VIZ_KEY_REQUEST_NEW_FRAME, False)
                        else:
                            continue
                    else:
                        pic = self.cap.grab()

                    if pic is None:
                        raise Exception("No more images")
                    if self.get(DATA_KEY_DATA_CAMERA, False):
                        pose = self.cap.get_pose()
                    else:
                        pose = self.get(DATA_KEY_IPC).get_pose()

                    version += 1
                    self.set(DATA_KEY_RAW_IMAGE, pic)
                    self.set(DATA_KEY_CAMERA_FOOT_PHASE, self.get(DATA_KEY_IPC).get_walking_foot_phase())
                    self.set(DATA_KEY_IMAGE_POSE, pose)
                    self.set(DATA_KEY_CAMERA_FRAME_VERSION, version)
                    self.set(DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, time.time())

                    if version % 50 == 0 and not self.viz_active:
                        debug_m(3, "Frame #%d abgefragt" % version)

                    """
                    if debug:
                        try:
                            base = "frame-%04d" % version
                            with open(base + ".yuv", "wb") as fp:
                                fp.write(pic.tostring())

                            with open(base + ".json", "wb") as fp:
                                json.dump(pose.positions, fp)

                            with open(base + "-goals.json", "wb") as fp:
                                json.dump(pose.goals, fp)

                            with open(base + "-time.txt", "wb") as fp:
                                fp.write(str(time.time() - time_offset))

                        except IOError:
                            pass
                    """

            except Exception as e:
                self.debug.error(e, "Error in Camera Module: ")
                self.cap = None  # da ist ein fehler aufgetreten

        self.debug.warning("Keine Kamera, alles abbrechen!")
        self.die = True


def register(ms):
    ms.add(CameraModule, "Camera",
           requires=[DATA_KEY_IPC,
                     #DATA_KEY_DATA_CAMERA, geht nicht, weil das in runtime über kommandozeile bereitgestellt wird
                     DATA_KEY_CONFIG
                     ],
           provides=[
               DATA_KEY_RAW_IMAGE,
               DATA_KEY_IMAGE_POSE,
               DATA_KEY_CAMERA_FRAME_VERSION,
               DATA_KEY_CAMERA_FOOT_PHASE,
               DATA_KEY_CAMERA_RESOLUTION,
               DATA_KEY_IMAGE_FORMAT,
               DATA_KEY_CAMERA_EXPOSURE_CALLBACK,
               DATA_KEY_CAMERA_CAPTURE_TIMESTAMP
               ])
