# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import io

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
stream = io.BytesIO()

# capture frames from the camera
for frame in camera.capture_continuous(stream, format="jpg"):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    cv2.imshow('frame', image)
    stream.truncate()
    stream.seek(0)
    if process(stream):
        break

cv2.destroyAllWindows()
#
# # allow the camera to warmup
# time.sleep(0.1)
# i = 0
# while i < 1000:
#     # grab an image from the camera
#     camera.capture(rawCapture, format="bgr")
#     image = rawCapture.array
#
#     # display the image on screen and wait for a keypress
#     cv2.imshow("Image", image)
#     i = i + 1
