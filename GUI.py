from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from threading import Thread
import cv2
import numpy as np


class MainScreen(Screen):
    pass


class MenuScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass


sm = Builder.load_file('camapp.kv')

class CamApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize the live stream
        # self.stream = RaspiVid().start()
        # self.stream.lockSettings()
        # self.img1 = Image()
        # self.img1.anim_delay = 0.00
        # self.framerate = 32
        #
        # # Add the buttons for the menus
        # self.menu = Button(text='Menu', font_size=40, size_hint=(0.2, 0.2), pos=(800 * 0.8, 640 * 0.8),
        #                    background_color=(0.5, 0.5, 0.5, 0.25))

    def build(self):
        # layout = FloatLayout(size=(800, 640))
        # layout.add_widget(self.img1)
        # layout.add_widget(self.menu)
        # Clock.schedule_interval(self.animate, 1.0 / self.framerate)
        # return layout
        Clock.schedule_interval(self.animate, 1.0/32)
        return sm

    def animate(self, dt):
        background = self.root.get_screen('main').ids.img1
        image = np.zeros((800, 620, 3), np.uint8)
        # image = self.stream.getFrame()
        image = cv2.flip(image, 0)

        buffer = image.tostring()

        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        background.texture = texture


if __name__ == '__main__':
    CamApp().run()
