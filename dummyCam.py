from threading import Thread
import numpy as np
import cv2
from kivy.graphics.texture import Texture


class DummyVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (640, 480)
        self.previewExposure = False

        # set up variables for this
        self.frame = None
        self.stopped = False

        # variables for image capture
        self._iso = 0
        self._shutterSpeed = 0
        self._awbMode = 'Dummy'
        self._exposure_comp = 0

        # variables for image post processing
        self._invert = False
        self._wb = False
        self._wbPixel = (255, 255, 255)

    def start(self):
        # Start the thread to pull frames from the video stream
        Thread(target=self._update, args=()).start()
        return self

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    def _update(self):
        while not self.stopped:
            # Start the thread to pull frames from the video stream
            img = np.zeros((640, 640, 3), np.uint8)
            img[:, :, 0] = img[:, :, 0] + 75
            img[:, :, 1] = img[:, :, 1] + 50
            img[:, :, 2] = img[:, :, 2] + 12
            self.frame = img

    def getFrame(self):
        return self.frame

    def processImage(self):
        # For some reason, openCV's images are flipped for Kivy, either way capture it
        image = cv2.flip(self.getFrame(), 0)

        if self._wb:
            b, g, r = cv2.split(image)

            lum = (self._wbPixel[0] + self._wbPixel[1] + self._wbPixel[2]) / 3

            b = (lum / self._wbPixel[0]) * b
            g = (lum / self._wbPixel[1]) * g
            r = (lum / self._wbPixel[2]) * r

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
        self._wbPixel = value

    @property
    def iso(self):
        return "Dummy Iso"

    @iso.setter
    def iso(self, value):
        self._iso = value

    @property
    def shutterSpeed(self):
        return "Dummy Shutter Speed"

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self._shutterSpeed = value

    @property
    def awbMode(self):
        return "Dummy AWBMode"

    @awbMode.setter
    def awbMode(self, value):
        self._awbMode = value

    @property
    def exposure_comp(self):
        return "Dummy Exposure Comp"

    @exposure_comp.setter
    def exposure_comp(self, value):
        self._exposure_comp = value

    def getSettings(self):
        return "Dummy Camera Settings"

    def settings(self, shutterSpeed, iso, awbMode):
        self.shutterSpeed = shutterSpeed
        self.iso = iso
        self.awbMode = awbMode
