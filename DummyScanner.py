# Kivy graphics imports
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager

# piCamera imports
# from picamera.array import PiRGBArray
# from picamera import PiCamera

# Image processing imports
from threading import Thread
import numpy as np
import time
import cv2
import os

# Class imports
from Classes.dummyCam import DummyVid
from Classes.CustomGUIClasses import BaseScreen, ProgressBar

Config.set('graphics', 'resizable', 0)
Window.size = (800, 480)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class MainScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start()
        self.progressBar = None
        self.triggerConvert = False


class MenuScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._wbPoint = (0, 0)

    def animate(self, dt):
        image, texture = App.get_running_app().stream.processImage()

        self.ids.background.texture = texture
        self.ids.hist.texture = self.genHist(image, 800, 480)

    def on_touch_up(self, touch):
        # On touch if within the image, gather the 10x10 grid of pixels and get average bgr for wb
        # touch.pos[0] x axis [1] is y
        print(touch.pos)
        if (576.0 > touch.pos[0] > 64.0) & (touch.pos[1] > 96.0):
            # Get the ratio between the onscreen image and actual image
            xRatio = 800.0 / 640.0
            yRatio = 640.0 / 384.0

            # Use the ratio and offsets to get the full image size
            wbPoint = (round((touch.pos[0] - 64) * xRatio), round((touch.pos[1] - 96) * yRatio))

            # Get a full sized screen grab and sample the 10x10 area
            image = App.get_running_app().stream.getFrame()
            sample = image[wbPoint[1] - 5: wbPoint[1] + 5,
                     wbPoint[0] - 5: wbPoint[0] + 5, :]

            # average it and set wb
            wbPixel = np.mean(sample, axis=(0, 1))
            App.get_running_app().stream.setWBPixel(wbPixel)

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


class FilmScanner(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stream = DummyVid().start()

    def build(self):
        pass

    def stop(self):
        self.stream.stop()

    def captureImage(self):
        self.root.get_screen('main').stop()
        self.stream.stop()
        shutterSpeed = self.stream.shutterSpeed
        ev = self.stream.exposure_comp
        print('shutter speed: ' + str(shutterSpeed) + " | Exposure Comp: ", str(ev))

        # restart the stream and the main screen
        self.stream.start()
        self.root.get_screen('main').start()

    def triggerConvert(self):
        nFiles = len(os.listdir('./tmp/'))

        self.progressBar = ProgressBar()
        self.progressBar.position = (200, 200)
        self.progressBar.max = float(nFiles + 1)
        self.progressBar.value = 0.0
        self.progressBar.bar_name = "Converting Files"
        self.root.get_screen('main').ids.layout.add_widget(self.progressBar)
        Thread(target=self.convertImages, args=()).start()

    def convertImages(self):
        currentTime = time.strftime("%Y-%m-%d_%H%M%S")
        folder = "./testUSB/" + currentTime
        os.mkdir(folder)
        files = os.listdir('./tmp/')

        for i in range(len(files)):
            print('file: ' + str(i))
            self.progressBar.value += 1.0
            time.sleep(1)
            if i == (len(files) - 2):
                self.progressBar.bar_name = "Transferring Files"

        time.sleep(1)
        self.progressBar.value += 1.0
        time.sleep(1)
        self.root.get_screen('main').ids.layout.remove_widget(self.progressBar)


if __name__ == '__main__':
    FilmScanner().run()
    FilmScanner().stop()
    quit()
