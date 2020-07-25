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


class RaspiVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 640)
        self.previewExposure = False

        self.camera = PiCamera(resolution=self.res)


        self.output = PiRGBArray(self.camera, size=self.res)
        self.stream = self.camera.capture_continuous(self.output, format='bgr', use_video_port=True, resize=(800, 640))

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
            # print(self.settings)

            # if told to stop close out camera
            if self.stopped:
                self.stream.close()
                self.output.close()
                self.camera.close()
                return

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    # # def settings(self):
    #     ag = self.camera.analog_gain
    #     dg = self.camera.digital_gain
    #     ss = self.camera.exposure_speed
    #
    #     output = "Analog Gain: " + str(ag) + " | Digital Gain: " + str(dg) + " | Shutter Speed: " + str(ss)
    #     return output

    def settings(self, shutterSpeed, iso, awbMode):
        self.camera.shutter_speed = shutterSpeed
        self.camera.iso = iso
        self.camera.awb_mode = awbMode

class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stream = RaspiVid().start()
        self.stream.settings(shutterSpeed=10, iso=100, awbMode='sunlight')
        self.img1 = Image()
        self.img1.anim_delay = 0.00
        self.framerate = 32

    def build(self):
        layout = BoxLayout()
        layout.add_widget(self.img1)
        Clock.schedule_interval(self.animate, 1.0 / self.framerate)
        return layout

    def animate(self, dt):
        image = self.stream.getFrame()
        image = cv2.flip(image, 0)

        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture


if __name__ == '__main__':
    CamApp().run()
    RaspiVid.stop()
    cv2.destroyAllWindows()