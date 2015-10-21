#Send image data to v4l2loopback using python
#Remember to do sudo modprobe v4l2loopback first!
#Released under CC0 by Tim Sheerman-Chase, 2013
#Extended under CC0 by Nils Rokita / Hamburg Bit-bots, for Videostreaming in Robocup

# This script relays on some code out of the Hambur-BitBots frameork

# To create a virtual video device:
# - enable the module:
# $ sudo modprobe v4l2loopback
# create a videodevice, the last number is the number of the videodevice
# sudo mknod /dev/video1 c 81 1
# sudo chmod o+rw /dev/video1

# =========  CONFIGS ==========

teams = ['Invisibles',
        'AUTMan',
        'FUmanoids',
        'Bold Hearts',
        'CIT Brains',
        'Photon',
        'RND',
        'FALCONBOTS',
        'Hamburg Bit-Bots',
        'Hanuman-KMUTT',
        'I-KID',
        'KUDOS',
        'MRL-HSL',
        'NUbots',
        'Plymouth Humanoid',
        'Rhoban Football Club',
        'RoBIU',
        'RoboFEI-HT',
        'RoboPatriots',
        'Snobots',
        'Team Mexico',
        'TH-MOS',
        'WF Wolves',
        'WF Wolves',]




import fcntl
import sys

import os
from v4l2 import *

from bitbots.vision.capture import VideoCapture
from bitbots.util import get_config


from PIL import Image, ImageDraw, ImageFont
from numpy import array

def set_up_camera(devs=["video0"]):
    """
    This method sets up the camera.
    :param devs: A list of device names to try to open, the first working is used
    :return: VideoCapure
    """
    if True:
        video_devs = devs
        for video_dev in video_devs:
                vision_config = get_config()["vision"]
                #debug_m(2, "Starte Kamera auf /dev/%s" % video_dev)
                width, height = (1184, 656) #vision_config["CameraResolution"]
                cap = VideoCapture('/dev/%s' % video_dev, width, height)
                cap.set_noop_image_decoder()
                cap.white_balance_auto = True
                #cap.white_balance = vision_config["CAMERA_WHITE_BALANCE"]  #0.5
                cap.brightness = 0.6 #vision_config["CAMERA_BRIGHTNESS"]  #0.5
                cap.focus_auto = False
                cap.focus_absolute = 1 #vision_config["CAMERA_FOCUS_ABSOLUTE"]  #10
                cap.gain_auto = True #vision_config["CAMERA_GAIN_AUTO"]
                #cap.gain = vision_config["CAMERA_GAIN"]
                cap.saturation = vision_config["CAMERA_SATURATION"]
                cap.exposure_auto = 1
                cap.exposure_auto_priority = True
                #cap.exposure_absolute = self.exposure_absolute
                cap.contrast = vision_config["CAMERA_CONTRAST"]
                cap.max_fps = vision_config["MAX_FPS"]

                cap.start()
                return cap
        return False
    return True  # Kamera ist schon initialisiert


from bitbots.game.receiver import GameStateReceiver2

receiver = GameStateReceiver2(team=99, player=1,
                                    addr=('0.0.0.0', 3838))



if __name__=="__main__":
    devName = '/dev/video1'
    if len(sys.argv) >= 2:
        devName = sys.argv[1]
    width = 1184
    height = 656
    if not os.path.exists(devName):
        print "Warning: device does not exist",devName
    device = open(devName, 'wrb', 0)

    print(device)
    capability = v4l2_capability()
    print "get capabilities result", (fcntl.ioctl(device, VIDIOC_QUERYCAP, capability))
    print "capabilities", hex(capability.capabilities)

    fmt = V4L2_PIX_FMT_YUYV
    #fmt = V4L2_PIX_FMT_YVU420

    print("v4l2 driver: " + capability.driver)
    format = v4l2_format()
    format.type = V4L2_BUF_TYPE_VIDEO_OUTPUT
    format.fmt.pix.pixelformat = fmt
    format.fmt.pix.width = width
    format.fmt.pix.height = height
    format.fmt.pix.field = V4L2_FIELD_NONE
    format.fmt.pix.bytesperline = width * 2
    format.fmt.pix.sizeimage = width * height * 2
    format.fmt.pix.colorspace = V4L2_COLORSPACE_JPEG

    print "set format result", (fcntl.ioctl(device, VIDIOC_S_FMT, format))
    #Note that format.fmt.pix.sizeimage and format.fmt.pix.bytesperline
    #may have changed at this point

    cam = set_up_camera()

    fontPath = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    font  =  ImageFont.truetype ( fontPath, 60 )
    font2  =  ImageFont.truetype ( fontPath, 40 )
    font3 = ImageFont.truetype ( fontPath, 50)
    goal1 = 1
    goal2 = 4
    team1 = "Nobody"
    team2 = "Nobody"
    import threading


    t = threading.Thread(target=receiver.receive_forever)
    t.daemon = True
    t.start()

    import math
    while True:
        #ret, img = cam.read()
        pic = cam.grab()
        #pic.putText("Huhuhu")


        img = Image.fromarray(pic )
        d = ImageDraw.Draw(img)
        data = receiver.get_last_state()
        if data:
            goal1 = data.teams[0].score
            goal2 = data.teams[1].score
            team1 = teams[data.teams[0].team_number]
            team2 = teams[data.teams[1].team_number]
        #cv2.putText(img, "%20s" % team1, (60, 60), 0, 0.8, (255, 255, 255), 2)
        #cv2.putText(img, "%s" % team2, (190, 60), 0, 0.8, (255, 255, 255), 2)
        #cv2.imwrite('test333.png', img)
        #pic = ConvertToYUYV(img.shape[0]* img.shape[1] * 2 , img.shape[0] * 2, img)
        #cv2.
        d.text((width/2 - 250, 10), "% 30s     %d : %d    %s" % (team1, goal1, goal2, team2), font=font)
        d.text((1900,10), "Gamestate: %s" % (data.game_state.split('_')[1] if data else 'Unknown'), font=font2)
        d.text((10,10), "Time: %2d:%02d" % (
            ((math.floor(data.seconds_remaining / 60), data.seconds_remaining % 60) if data.seconds_remaining > 0 else
            (math.floor(data.seconds_remaining / 60) + 1, 60 - ( data.seconds_remaining % 60)))
            if data else (0,0)), font=font3)
        #pic2 = array(Image.alpha_composite(img, txt))
        #print pic

        device.write(array(img))#array(data))
        #gevent.sleep(0)
        print 2
        #os.write(device.fileno(), buff)
        #time.sleep(1./30.)
