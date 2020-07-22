from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import numpy as np

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '640')

class RaspiVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 480)
        self.previewExposure = False

        self.camera = PiCamera(resolution=self.res)


        self.output = PiRGBArray(self.camera, size=self.res)
        self.stream = self.camera.capture_continuous(self.output, format='bgr', use_video_port=True)

        # set up variables for this
        self.frame = None
        self.stopped = False

    def start(self):
        # Start the thread to pull frames from the video stream
        Thread(target=self._update, args=()).start()
        return self

    def getFrame(self):
        return self.frame

    def _update(self):
        # keep looping and keep the stream open
        # print(self.camera._get_camera_settings())
        for f in self.stream:
            self.frame = f.array
            self.output.truncate(0)
            print(self.settings())

            # if told to stop close out camera
            if self.stopped:
                self.stream.close()
                self.output.close()
                self.camera.close()
                return

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    @property
    def settings(self):
        ag = self.camera.analog_gain
        dg = self.camera.digital_gain
        ss = self.camera.exposure_speed

        output = "Analog Gain: " + str(ag) + " | Digital Gain: " + str(dg) + " | Shutter Speed: " + str(ss)
        return output

    @settings.setter
    def settings(self, shutterSpeed, iso, awbMode):
        self.camera.shutter_speed = shutterSpeed
        self.camera.iso = iso
        self.camera.awb_mode = awbMode

# class CamApp(App):
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.stream = RaspiVid().start()
#         self.stream.settings(shutterSpeed=10, iso=100, awbMode='daylight')
#         self.img1 = Image()
#         self.img1.anim_delay = 0.00
#         self.framerate = 32
#
#     def build(self):
#         layout = BoxLayout()
#         layout.add_widget(self.img1)
#         Clock.schedule_interval(self.animate, 1.0 / self.framerate)
#         return layout
#
#     def animate(self, dt):
#         image = self.stream.getFrame()
#         image = cv2.flip(image, 0)
#
#         buffer = image.tostring()
#
#         texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
#         texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
#         self.img1.texture = texture

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.framerate = 32
        self._clock = None
        self._stream = None
        self.start()

    def start(self):
        self._stream = RaspiVid.start()
        self._stream.settings(shutterSpeed=10, iso=100, awbMode='daylight')
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        self._stream.stop()
        Clock.unschedule(self._clock)

    def animate(self, dt):
        # image = np.zeros((640, 800, 3), np.uint8)
        # image = image + 25
        image = self._stream.getFrame()
        image = cv2.flip(image, 0)

        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.background.texture = texture

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._clock = None
        self.framerate = 32

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def animate(self, dt):
        image = np.zeros((640, 800, 3), np.uint8)
        image = image + 25
        # image = self.stream.getFrame()
        image = cv2.flip(image, 0)

        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
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
    RaspiVid.stop()
    cv2.destroyAllWindows()