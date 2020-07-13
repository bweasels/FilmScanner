from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2

class RaspiVid():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = PiCamera(resolution=(800, 600), framerate=32)
        self.frame = PiRGBArray(self.camera, size=(800, 600))

    def getFrame(self):
        image = self.frame.array
        self.frame.truncate(0)
        return(image)

class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img1 = Image()
        self.capture = cv2.VideoCapture(0)

    def build(self):
        self.img1 = Image()
        layout = BoxLayout()
        layout.add_widget(self.img1)

        # opencv2 stuffs
        self.capture = cv2.VideoCapture(0)
        cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0 / 33.0)
        return layout

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
