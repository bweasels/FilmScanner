# Kivy import
from kivy.graphics.texture import Texture

# Raspicam imports
from picamera.array import PiRGBArray
from picamera import PiCamera

# Basic Python IO Imports
from threading import Thread
import numpy as np
import subprocess

# OpenCV
import cv2


class RaspiVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (640, 480)
        self.previewExposure = False

        # variables to hold the various pieces of the stream
        self.camera = None # PiCamera(resolution=self.res)
        self.output = None # PiRGBArray(self.camera, size=self.res)
        self.stream = None # self.camera.capture_continuous(self.output, format='bgr', use_video_port=True, resize=(800, 480))

        # Internal data variables
        self.frame = None
        self.stopped = False

        # variables for image post processing
        self._invert = False
        self._wb = False
        #self._wbPixel = (255, 255, 255)
        self._balance = (0, 0, 0)

    def start(self):
        # Set stopped to false to keep _update looping
        self.stopped = False

        # Initalize camera output and stream
        self.camera = PiCamera(resolution=self.res)
        self.camera.iso = 100
        cv2.waitKey(2000)

        # self.camera.exposure_mode = 'off'

        self.output = PiRGBArray(self.camera, size=self.res)
        self.stream = self.camera.capture_continuous(self.output, format='bgr', use_video_port=True, resize=(640, 480))

        # Start the thread to pull frames from the video stream
        Thread(target=self._update, args=()).start()
        return self

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    def _update(self):
        # keep looping and keep the stream open
        print("Successfully started update")
        for f in self.stream:
            self.frame = f.array
            self.output.truncate(0)

            # if told to stop close out camera
            if self.stopped:
                self.stream.close()
                self.output.close()
                self.camera.close()
                return

    def getFrame(self):
        return self.frame

    def processImage(self):
        # For some reason, openCV's images are flipped for Kivy, either way capture it
        image = cv2.flip(self.getFrame(), 0)

        if self._wb:
            b, g, r = cv2.split(image)

            b = self._balance[0] * b
            g = self._balance[1] * g
            r = self._balance[2] * r

            image = np.uint8(cv2.merge((b, g, r)))

        # If invert button is pressed, flip that puppy
        if self._invert:
            image = cv2.bitwise_not(image)

        # This is all code to convert it to a bitstream for Kivy
        buffer = image.tostring()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        return image, texture

    def invert(self):
        self._invert = not self._invert

    def activateWB(self):
        self._wb = not self._wb

    def setWBPixel(self, value):
        lum = (value[0] + value[1] + value[2]) / 3
        b_lum = lum / value[0]
        g_lum = lum / value[1]
        r_lum = lum / value[2]
        self._balance = (b_lum, g_lum, r_lum)

    @property
    def iso(self):
        return self.camera.iso

    @iso.setter
    def iso(self, value):
        self.camera.iso = value

    @property
    def shutterSpeed(self):
        return self.camera.exposure_speed

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self.camera.shutter_speed = value

    @property
    def awbMode(self):
        return self.camera.awb_mode

    @awbMode.setter
    def awbMode(self, value):
        self.camera.awb_mode = value

    @property
    def exposure_comp(self):
        return self.camera.exposure_compensation

    @exposure_comp.setter
    def exposure_comp(self, value):
        self.camera.exposure_compensation = value

    def getSettings(self):
        ag = self.iso[0]
        dg = self.iso[1]
        ss = self.shutterSpeed
        output = "Analog Gain: " + str(ag) + " | Digital Gain: " + str(dg) + " | Shutter Speed: " + str(ss)
        return output

    def settings(self, shutterSpeed, iso, awbMode):
        self.shutterSpeed = shutterSpeed
        self.iso = iso
        self.awbMode = awbMode


class RaspiCam:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 480)
        self.previewExposure = False

        self.camera = None
        # set up variables for this
        self.frame = None
        self.stopped = False

#    def capture(self, fname):
    def capture(self, shutterSpeed, exposureComp, photoNo):
        cv2.waitKey(500)
        filename = './tmp/scan' + str(photoNo) + '.jpg'
        print(filename)
        cmd = 'raspistill -md 3 -ex snow -mm backlit -awb off -ag 1 -dg 1 -awbg 3.625,1.402 ' \
              '-t 500 -ev ' + str(exposureComp) + ' -ss ' + str(shutterSpeed) + ' -r -o ' + filename
        print(cmd)
        subprocess.call(cmd, shell=True)

    @property
    def shutterSpeed(self):
        return self.camera.shutter_speed

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self.camera.shutter_speed = value

    @property
    def iso(self):
        return self.camera.iso

    @iso.setter
    def iso(self, value):
        self.camera.iso = value

    @property
    def exposureComp(self):
        return self.camera.exposureComp

    @exposureComp.setter
    def exposureComp(self, value):
        self.camera.exposure_compensation = value