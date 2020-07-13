# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	# show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# import time
# import picamera
# import picamera.array
#
# with picamera.PiCamera() as camera:
#     with picamera.array.PiRGBArray(camera) as stream:
#         camera.resolution = (800, 600)
#         camera.start_preview()
#         time.sleep(10)
#         camera.capture(stream, 'rgb')
#         # Show size of RGB data
#         print(stream.array.shape)

# # import the necessary packages
# from picamera.array import PiRGBArray
# from picamera import PiCamera
# import time
# import cv2
# import io
#
# # initialize the camera and grab a reference to the raw camera capture
# camera = PiCamera()
# stream = io.BytesIO()
#
# # capture frames from the camera
# for frame in camera.capture_continuous(stream, format="rgb"):
#     # grab the raw NumPy array representing the image, then initialize the timestamp
#     # and occupied/unoccupied text
#     # image = frame.array
#     cv2.imshow('frame', frame)
#     stream.truncate()
#     stream.seek(0)
#     if process(stream):
#         break
#
# cv2.destroyAllWindows()
# #
# # # allow the camera to warmup
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
