from threading import Thread
import numpy as np


class DummyVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 640)
        self.previewExposure = False

        # set up variables for this
        self.frame = None
        self.stopped = False

        self._iso = 0
        self._shutterSpeed = 0
        self._awbMode = 'Dummy'
        self._exposure_comp = 0

    def start(self):
        # Start the thread to pull frames from the video stream
        Thread(target=self._update, args=()).start()
        return self

    def _update(self):
        while not self.stopped:
            # Start the thread to pull frames from the video stream
            img = np.zeros((640, 800, 3), np.uint8)
            img[:, :, 0] = img[:, :, 0] + 75
            img[:, :, 1] = img[:, :, 1] + 50
            img[:, :, 2] = img[:, :, 2] + 12
            self.frame = img

    def getFrame(self):
        return self.frame

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    @property
    def iso(self):
        return "Dummy Iso"

    @iso.setter
    def iso(self, value):
        self._iso = value

    @property
    def shutterSpeed(self):
        return "Dummy Shutter Speed"

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self._shutterSpeed = value

    @property
    def awbMode(self):
        return "Dummy AWBMode"

    @awbMode.setter
    def awbMode(self, value):
        self._awbMode = value

    @property
    def exposure_comp(self):
        return "Dummy Exposure Comp"

    @exposure_comp.setter
    def exposure_comp(self, value):
        self._exposure_comp = value

    def getSettings(self):
        return "Dummy Camera Settings"

    def settings(self, shutterSpeed, iso, awbMode):
        self.shutterSpeed = shutterSpeed
        self.iso = iso
        self.awbMode = awbMode
