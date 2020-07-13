from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from picamera.array import PiRGBArray
from picamera import PiCamera
# from threading import thread
import cv2



class RaspiVid():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = PiCamera(resolution=(800, 480))
        self.output = PiRGBArray(self.camera, size=(800, 480))

    def getFrame(self):
        self.camera.capture(self.output, 'bgr')
        image = self.output.array
        self.output.truncate(0)
        return image


class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stream = RaspiVid()
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

    # def update(self, dt):
    #     # display image from cam in opencv window
    #     ret, frame = self.capture.read()
    #     cv2.imshow("CV2 Image", frame)
    #     # convert it to texture
    #     buf1 = cv2.flip(frame, 0)
    #     buf = buf1.tostring()
    #     texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
    #     # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
    #     texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    #     # display image from the texture
    #     self.img1.texture = texture1


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
