from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics.texture import Texture
from kivy.clock import Clock

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.framerate = 32
        self._clock = None
        self._invert = False

        self._wb = None
        self._whitePoint = (255, 255, 255)

        self.start()

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self.framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def invert(self):
        self._invert = not self._invert

    def activateWB(self):
        if self._wb is not None:
            self._wb = None
        else:
            self._wb = self._whitePoint

    def setWhitePoint(self, value):
        self._whitePoint = value

    def animate(self, dt):
        image = App.get_running_app().stream.getFrame()
        # cv2.imshow('raw image', image)
        # cv2.waitKey(0)
        # image = np.zeros((640, 800, 3), np.uint8)
        # image = image + 25

        # Set the texture and update the fps counter
        image, texture = processImage(image=image, invert=self._invert, WBPoint=self._wb)
        self.ids.background.texture = texture
        self.ids.fps.text = str(round(1 / dt, 1))


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._clock = None
        self._framerate = 32
        self._invert = False

        # A variety of properties for white balance control
        self._wb = None
        self._whitePoint = (255, 255, 255)
        self._wbCapture = False
        self._wbPoint = (0, 0)

    def start(self):
        self._clock = Clock.schedule_interval(self.animate, 1.0 / self._framerate)

    def stop(self):
        Clock.unschedule(self._clock)

    def invert(self):
        self._invert = not self._invert

    def activateWB(self):
        if self._wb is not None:
            self._wb = None
        else:
            self._wb = self._whitePoint

    def setWhitePoint(self, value):
        self._whitePoint = value

    def getWhitePoint(self):
        return self._whitePoint

    def on_touch_up(self, touch):
        # On touch if within the image, gather the 5x5 grid of pixels and get average bgr for wb
        if (touch.pos[0] < 700.0) & (touch.pos[1] > 110.0):
            # Get the ratio between the onscreen image and actual image
            xRatio = 800.0 / 700.0
            yRatio = 640.0 / 540.0

            # Use the ratio and offsets to get the full image size
            self._wbPoint = (round(touch.pos[0] * xRatio), round((touch.pos[1] - 110) * yRatio))
            self._wbCapture = True

    def animate(self, dt):
        # Make a dummy image for me
        image = App.get_running_app().stream.getFrame()

        # If capturing wb point get it here
        if self._wbCapture:
            # Cut out a 10x10 pixel area to sample white balance from
            sample = image[self._wbPoint[1] - 5:self._wbPoint[1] + 5,
                     self._wbPoint[0] - 5:self._wbPoint[0] + 5, :]

            # average over it and set it as the white point in both the menu and main screen
            self._whitePoint = np.mean(sample, axis=(0, 1))
            self.manager.get_screen('main').setWhitePoint(self._whitePoint)

            # Tell it to capturing white point
            self._wbCapture = False

        image = cv2.resize(image, (720, 576))

        # Process the image according to user inputs
        image, texture = processImage(image=image, invert=self._invert, WBPoint=self._wb)
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