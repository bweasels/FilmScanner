# Kivy graphics imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
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


sm = Builder.load_file('camappv2.kv')


class CamAppV2(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize the live stream
        # self.stream = RaspiVid().start()
        # self.stream.lockSettings()
        # self.img1 = Image()
        # self.img1.anim_delay = 0.00
        self.framerate = 32
        #
        # # Add the buttons for the menus
        # self.menu = Button(text='Menu', font_size=40, size_hint=(0.2, 0.2), pos=(800 * 0.8, 640 * 0.8),
        #                    background_color=(0.5, 0.5, 0.5, 0.25))

    def build(self):
        Clock.schedule_interval(self.animate, 1.0 / self.framerate)
        return

    def animate(self, dt):
        image = np.zeros((640, 800, 3), np.uint8)
        image = image + 25
        # image = self.stream.getFrame()
        image = cv2.flip(image, 0)
        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.img1.texture = texture

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
        buffer = histImg.tostring()
        texture = Texture.create(size=(hist_w, hist_h), colorfmt='bgra')
        texture.blit_buffer(buffer, colorfmt='bgra', bufferfmt='ubyte')
        return texture


if __name__ == '__main__':
    CamAppV2().run()
