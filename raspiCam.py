from picamera.array import PiRGBArray
from pydng.core import RPICAM2DNG
from picamera import PiCamera
from threading import Thread
from io import BytesIO
import time
import cv2


class RaspiVid:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 640)
        self.previewExposure = False

        # variables to hold the various pieces of the stream
        self.camera = PiCamera(resolution=self.res)
        self.output = PiRGBArray(self.camera, size=self.res)
        self.stream = self.camera.capture_continuous(self.output, format='bgr', use_video_port=True, resize=(800, 640))

        # Internal data variables
        self.frame = None
        self.stopped = False

        # variables for image post processing
        self._invert = False
        self._wb = False
        self._wbPixel = (255, 255, 255)

    def start(self):
        # Start the thread to pull frames from the video stream
        Thread(target=self._update, args=()).start()
        return self

    def stop(self):
        # tell the class to shutdown
        self.stopped = True

    def _update(self):
        # keep looping and keep the stream open
        for f in self.stream:
            self.frame = f.array
            self.output.truncate(0)

            # if told to stop close out camera
            if self.stopped:
                self.stream.close()
                self.output.close()
                self.camera.close()
                return

    def getFrame(self):
        return self.frame

    def processImage(self):
        # For some reason, openCV's images are flipped for Kivy, either way capture it
        image = cv2.flip(self.getFrame(), 0)

        if self._wb:
            b, g, r = cv2.split(image)

            lum = (self._wbPixel[0] + self._wbPixel[1] + self._wbPixel[2]) / 3

            b = (lum / self._wbPixel[0]) * b
            g = (lum / self._wbPixel[1]) * g
            r = (lum / self._wbPixel[2]) * r

            image = np.uint8(cv2.merge((b, g, r)))

        # If invert button is pressed, flip that puppy
        if self._invert:
            image = cv2.bitwise_not(image)

        # This is all code to convert it to a bitstream for Kivy
        buffer = image.tostring()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        return image, texture

    def invert(self):
        self._invert = not self._invert

    def activateWB(self):
        self._wb = not self._wb

    def setWBPixel(self, value):
        self._wbPixel = value

    @property
    def iso(self):
        return self.camera.analog_gain, self.camera.digital_gain

    @iso.setter
    def iso(self, value):
        self.camera.iso = value

    @property
    def shutterSpeed(self):
        return self.camera.shutter_speed

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self.camera.shutter_speed = value

    @property
    def awbMode(self):
        return self.camera.awb_mode

    @awbMode.setter
    def awbMode(self, value):
        self.camera.awb_mode = value

    @property
    def exposure_comp(self):
        return self.camera.exposure_compensation

    @exposure_comp.setter
    def exposure_comp(self, value):
        self.camera.exposure_compensation = value

    def getSettings(self):
        ag = self.iso[0]
        dg = self.iso[1]
        ss = self.shutterSpeed
        output = "Analog Gain: " + str(ag) + " | Digital Gain: " + str(dg) + " | Shutter Speed: " + str(ss)
        return output

    def settings(self, shutterSpeed, iso, awbMode):
        self.shutterSpeed = shutterSpeed
        self.iso = iso
        self.awbMode = awbMode

class RaspiCam:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up the camera
        self.res = (800, 640)
        self.previewExposure = False

        self.camera = PiCamera(sensor_mode=3)
        self.camera.start_preview()
        self.camera.awb_mode = 'off'
        self.camera.iso = 100

        # set up variables for this
        self.frame = None
        self.stopped = False

    def capture(self, fname):
        # Start the thread to pull frames from the video stream
        Thread(target=self._capture, args=(fname)).start()
        return self

    def _capture(self, fname):
        stream = BytesIO()
        time.sleep(0.1)
        self.camera.capture(stream, 'jpeg', bayer=True)
        d = RPICAM2DNG()
        output = d.convert(stream)
        with open('file.dng', 'wb') as f:
            f.write(output)
        time.sleep(10)
        self.camera.stop_preview()

        stream.close()
        self.camera.close()

    @property
    def shutterSpeed(self):
        return self.camera.shutter_speed

    @shutterSpeed.setter
    def shutterSpeed(self, value):
        self.camera.shutter_speed = value

    @property
    def iso(self):
        return self.camera.iso

    @iso.setter
    def iso(self, value):
        self.camera.iso = value

    @property
    def exposureComp(self):
        return self.camera.exposureComp

    @exposureComp.setter
    def exposureComp(self, value):
        self.camera.exposure_compensation = value
