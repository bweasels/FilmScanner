from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import time


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.framerate = 20
        self._clock = None

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def animate(self, dt):
        # Get the processed image and save texture
        image, texture = App.get_running_app().stream.processImage()
        self.ids.background.texture = texture

        # Write out fps for our information
        self.ids.fps.text = str(round(1 / dt, 1))


##ADD CODE TO CUSTOMIZE BUTTON AND SLIDER COLORS##
class SlowButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _disable(self):
        self.disabled = True

    def _enable(self):
        time.sleep(0.5)
        self.disabled = False