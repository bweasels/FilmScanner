# Kivy core mechanism imports
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window

# Kivy pre-made object imports
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.graphics.texture import Texture

# Screen manager
from kivy.uix.screenmanager import ScreenManager, Screen

# raspberry pi imports
from gpiozero import CPUTemperature
import RPi.GPIO as GPIO

# Image processing imports
import cv2
import numpy as np

# Import homebrew classes from the file
from raspiCam import RaspiVid, RaspiCam
from CustomGUIClasses import BaseScreen

# Graphical properties
# Window.fullscreen = True
Config.set('graphics', 'resizable', 0)
Window.size = (800, 480)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class MainScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start()


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
        if (64.0 < touch.pos[0] < 576.0) & (touch.pos[1] > 96.0):
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


class CamApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # start the camera stream
        self.stream = RaspiVid().start()
        self.camera = RaspiCam()
        # Set up the pwm pin managing the fan
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT)
        self.fan = GPIO.PWM(12, 25000)

        # schedule temp monitor to only fire every second
        self.tempMonitor = Clock.schedule_interval(self.monitorTemp, 1.0)
        # self.stream.settings(shutterSpeed=10, iso=100, awbMode='sunlight')

    def build(self):
        pass

    def monitorTemp(self, dt):
        cpu = CPUTemperature()
        roomTemp = 25
        maxTemp = 85
        self.fan.start(100 * (cpu.temperature - roomTemp) / (maxTemp - roomTemp))

    def stop(self):
        self.stream.stop()
        Clock.unschedule(self.tempMonitor)
        GPIO.cleanup()

    def captureImage(self):
        # Stop the menu, get the current settings from the stream, and stop the stream
        print('started capturing image')
        self.root.get_screen('main').stop()
        ss = self.stream.shutterSpeed
        ev = self.stream.exposure_comp
        self.stream.stop()

        # Captured image
        self.camera.capture(shutterSpeed=ss, exposureComp=ev)
        print('Captured Full DNG')
        # cv2.waitKey(10)
        # self.camera.capture(fname='fname.dng')
        # print('captured photo')
        # restart the stream and the main screen
        self.stream.start()
        self.root.get_screen('main').start()
        print('restarted stream')


if __name__ == '__main__':
    CamApp().run()
    CamApp().stop()
    quit()
