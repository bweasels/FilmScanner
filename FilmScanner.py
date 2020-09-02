# Kivy core mechanism imports
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.app import App

# Kivy pre-made object imports
from kivy.graphics.texture import Texture

# Screen manager
from kivy.uix.screenmanager import ScreenManager

# raspberry pi system control
import RPi.GPIO as GPIO
import os

# Image processing imports
from pydng.core import RPICAM2DNG
from threading import Thread
import numpy as np
import subprocess
import time
import cv2

# Import homebrew classes from the file
from Classes.raspiCam import RaspiVid, RaspiCam
from Classes.CustomGUIClasses import BaseScreen, ConversionBar

# Graphical properties
Window.fullscreen = True
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
        self._startup = False

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


class FilmScanner(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # start the camera stream
        self.stream = RaspiVid().start()
        self.camera = RaspiCam()

        # Set up the pwm pin managing the fan
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT)
        self.fan = GPIO.PWM(12, 25000)

        # schedule temp monitor to only fire every second
        self.tempMonitor = Clock.schedule_interval(self.monitorTemp, 1.0)
        self.stream.settings(shutterSpeed=190, iso=100, awbMode='sunlight')

        # create scan counter
        self.scanCounter = 1

        # init progress bar
        self.progressBar = None

    def build(self):
        pass

    def monitorTemp(self, dt):
        # Get temperature from pi system files
        tFile = open('/sys/class/thermal/thermal_zone0/temp')
        temp = float(tFile.read())
        temp = temp / 1000

        # Temperature range
        nominalTemp = 45
        maxTemp = 80

        if temp < nominalTemp:
            fanSpeed = 10
        elif nominalTemp < temp < maxTemp:
            fanSpeed = 100 * (temp - nominalTemp) / (maxTemp - nominalTemp)
        elif temp >= maxTemp:
            fanSpeed = 100

        self.fan.start(fanSpeed)

    def stop(self):
        self.stream.stop()
        Clock.unschedule(self.tempMonitor)
        GPIO.cleanup()

    def captureImage(self):
        # Stop the menu, get the current settings from the stream, and stop the stream
        self.root.get_screen('main').stop()
        ss = self.stream.shutterSpeed
        ev = self.stream.exposure_comp
        # Pi camera uses a scale of +24 to -24 while raspistill uses +10 to -10, so convert
        ev = (ev / 24) * 10
        self.stream.stop()

        # Capture image and increment the scan counter
        self.camera.capture(shutterSpeed=ss, exposureComp=ev, photoNo=self.scanCounter)
        self.scanCounter += 1

        # Restart stream
        self.stream.start()
        self.root.get_screen('main').start()

    def triggerConvert(self):
        nFiles = len(os.listdir('./tmp/'))

        self.progressBar = ConversionBar()
        self.progressBar.position = (200, 200)
        self.progressBar.max = float(nFiles + 2)
        self.progressBar.value = 0.0
        self.progressBar.bar_name = "Converting Files"
        self.root.get_screen('main').ids.layout.add_widget(self.progressBar)
        Thread(target=self.convertImages, args=()).start()

    def convertImages(self):
        ####Re: Changing Bar Name two increments early##########
        # Kivy still doesn't like to play nice with updating, so all name updates
        # come 2 increments late, so I beat them to it.
        ####It's stupid & hackish I KNOW #######################

        # make sure that there is a USB Drive inserted
        currentTime = time.strftime("%Y-%m-%d_%H%M%S")
        if len(os.listdir('/media/pi')) == 0:
            print('Please insert a USB Drive')
            return

        # create a dated output folder
        # folder = os.path.join('/media/pi', os.listdir('/media/pi')[0], currentTime)
        # os.mkdir(folder)
        folder = '/media/pi/"' + os.listdir('/media/pi')[0] + '"/' + currentTime
        cmd = 'mkdir ' + folder
        subprocess.call(cmd, shell=True)

        # Get the images in the tmp folder and use PyDNG to convert
        tempFolder = '/home/pi/Documents/FilmScanner/tmp/'
        files = os.listdir(tempFolder)
        converter = RPICAM2DNG()
        for i in range(len(files)):
            converter.convert(image='./tmp/' + files[i])
            self.progressBar.value += 1.0
            if i == (len(files) - 2):
                self.progressBar.bar_name = "Transferring Files"

        # Move the dngs to the removable drive
        self.progressBar.bar_name = "Deleting tmp files"
        cmd = 'mv ' + tempFolder + '*.dng ' + folder
        subprocess.call(cmd, shell=True)
        self.progressBar.value += 1.0

        # Remove the files in the tmp folder
        cmd = 'rm ' + tempFolder + "*.jpg"
        subprocess.call(cmd, shell=True)
        self.progressBar.value += 1.0

        # Sleep for 1 second so we can enjoy the glory of finishing dis shit then delete the bar
        time.sleep(1)
        self.root.get_screen('main').ids.layout.remove_widget(self.progressBar)


if __name__ == '__main__':
    FilmScanner().run()
    FilmScanner().stop()
    quit()
