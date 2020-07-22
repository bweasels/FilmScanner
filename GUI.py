# Kivy graphics imports
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config

# piCamera imports
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from threading import Thread

# Image processing imports
import cv2
import numpy as np

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '640')


def processImage(image, invert, WBPoint):
    # For some reason, openCV's images are flipped for Kivy
    image = cv2.flip(image, 0)

    # If invert button is pressed, flip that puppy
    if invert:
        image = cv2.bitwise_not(image)

    # Perform more processing here

    #
    buffer = image.tostring()
    texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
    texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
    return image, texture


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.framerate = 32
        self._clock = None
        self._invert = False
        self.start()

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def invert(self, value):
        self._invert = value

    def animate(self, dt):
        image = np.zeros((640, 800, 3), np.uint8)
        image = image + 25

        # Set the texture and update the fps counter
        image, texture = processImage(image=image, invert=self._invert, WBPoint=(0,0,0))
        self.ids.background.texture = texture
        self.ids.fps.text = str(round(1 / dt, 1))


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._clock = None
        self.framerate = 32
        self._invert = False

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def invert(self):
        self._invert = not self._invert

    def animate(self, dt):
        # Make a dummy image for me
        image = np.zeros((640, 800, 3), np.uint8)
        image = image + 32

        # Process the image according to user inputs and
        image, texture = processImage(image=image, invert=self._invert, WBPoint=(0, 0, 0))
        self.ids.background.texture = texture
        self.ids.hist.texture = self.genHist(image, 720, 576)

    def genHist(self, image, hist_w, hist_h):
        # Initial variables
        histSize = 256
        histRange = (0, 256)
        bgr_planes = cv2.split(image)
        bin_w = int(round(hist_w / histSize))

        # Calculate Histogram for each channel
        b_hist = cv2.calcHist(bgr_planes, [0], None, [histSize], histRange, accumulate=False)
        g_hist = cv2.calcHist(bgr_planes, [1], None, [histSize], histRange, accumulate=False)
        r_hist = cv2.calcHist(bgr_planes, [2], None, [histSize], histRange, accumulate=False)

        # Normalize each for 0-256 so that they fit on the same plot
        cv2.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)

        # Make image with the plot
        histImg = np.zeros((hist_h, hist_w, 4), dtype=np.uint8)

        # For each x axis point, plot out the histogram y axis point
        for i in range(1, histSize):
            cv2.line(histImg, (bin_w * (i - 1), hist_h - int(np.round(b_hist[i - 1]))),
                     (bin_w * i, hist_h - int(np.round(b_hist[i]))),
                     (255, 0, 0, 255), thickness=2)
            cv2.line(histImg, (bin_w * (i - 1), hist_h - int(np.round(g_hist[i - 1]))),
                     (bin_w * i, hist_h - int(np.round(g_hist[i]))),
                     (0, 255, 0, 255), thickness=2)
            cv2.line(histImg, (bin_w * (i - 1), hist_h - int(np.round(r_hist[i - 1]))),
                     (bin_w * i, hist_h - int(np.round(r_hist[i]))),
                     (0, 0, 255, 255), thickness=2)

        # Convert the histogram numpy array to a kivy recognizable image
        histImg = cv2.flip(histImg, 0)
        buffer = histImg.tostring()
        texture = Texture.create(size=(hist_w, hist_h), colorfmt='bgra')
        texture.blit_buffer(buffer, colorfmt='bgra', bufferfmt='ubyte')
        return texture


class WindowManager(ScreenManager):
    pass


class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        pass


if __name__ == '__main__':
    CamApp().run()
