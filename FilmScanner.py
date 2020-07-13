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



class RaspiVid():
    def __init__(self, **kwargs):
        super().__init__(**kwargs, res=(800, 480), previewExposure=False)
        # Set up the camera

        self.camera = PiCamera(resolution=res)

        # if previewExposure:
        #    self.camera.shutter_speed = 10
        #    self.camera.awb_mode = 'sunlight'
        #    self.iso = 100
        self.output = PiRGBArray(self.camera, size=res)
        self.stream = self.camera.capture_continuous(self.output, format='bgr', use_video_port=True)

        # set up variables for this
        self.frame = None
        self.stopped = False

    def start(self):
        # Start the thread to pull frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def getFrame(self):
        return self.frame

    def update(self):
        # keep looping and keep the stream open
        print(self.camera._get_camera_settings())
        for f in self.stream:
            self.frame = f.array
            self.output.truncate(0)

            # if told to stop close out camera
            if self.stopped:
                self.stream.close()
                self.output.close()
                self.camera.close()
                return

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stream = RaspiVid().start()
        self.img1 = Image()
        self.img1.anim_delay = 0.00
        self.framerate = 32

    def build(self):
        layout = BoxLayout()
        layout.add_widget(self.img1)
        Clock.schedule_interval(self.animate, 1.0/self.framerate)
        return layout

    def animate(self, dt):
        image = self.stream.getFrame()
        image = cv2.flip(image, 0)
        # cv2.imshow('test', image)
        # key = cv2.waitKey(3) & 0xFF
        # if key == ord('q'):
        #     exit(0)

        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture


if __name__ == '__main__':
    CamApp().run()
    RaspiVid.stop()
    cv2.destroyAllWindows()
