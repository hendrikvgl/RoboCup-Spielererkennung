# -*- coding:utf-8 -*-
import cv2

class VideoGrabber():

    def __init__(self, device):
        self.cap = cv2.VideoCapture(device)


    def grab_frame_return_grey(self):
        ret, frame = self.cap.read()
        return frame

    def destroy(self):
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()