import cv2
import numpy as np
from kivy.graphics.texture import Texture
from threading import Thread


class ImageProcessor:
    def __init__(self):

        self._wbPoint = (255, 255, 255)
        self._wbActivate = False
        self._invert = False
        self._texture = None
        self._image = None
        self._stream = None

        self.running = True

    def start(self, stream):
        # Start the thread to pull frames from the video stream
        self._stream = stream
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        # tell the class to shutdown
        self.running = False

    def process(self):
        while self.running:
            image = self._stream.getFrame()
            print(self._stream.iso)
            self.processImage(image)

    def processImage(self, image):
        # For some reason, openCV's images are flipped for Kivy
        image = cv2.flip(image, 0)

        if self._wbActivate:
            # Split image into channels (array notation is more efficient than cv2.split
            b = image[:, :, 0]
            g = image[:, :, 1]
            r = image[:, :, 2]

            # Find the overall luminance of the image to correct to when white balancing
            lum = (self._wbPoint[0] + self._wbPoint[1] + self._wbPoint[2]) / 3

            # perform the white balance, and overwrite the channels
            b = b * lum / self._wbPoint[0]
            g = g * lum / self._wbPoint[1]
            r = r * lum / self._wbPoint[2]

            image = np.dstack((b, g, r))

        # If invert button is pressed, flip that puppy
        if self._invert:
            image = cv2.bitwise_not(image)

        # This is all code to convert it to a bitstream for Kivy
        buffer = image.tostring()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self._texture = texture
        self._image = image

    def getTexture(self):
        return self._texture

    def getImage(self):
        return self._image

    def activateWB(self):
        self._wbActivate = not self._wbActivate

    def invert(self):
        self._invert = not self._invert

    def setWBPoint(self, value):
        self._wbPoint = value
