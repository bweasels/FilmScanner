###!/usr/bin/env python
import cv2
import math
import picamera
import datetime
import serial
import os, sys
import subprocess
import time
from decimal import *

getcontext().prec = 8

lonfiles = []
latfiles = []

frame_width = 640
frame_height = 480
points = 100
graph_box = 100

if os.path.exists('/dev/video0') == False:
    rpistr = "sudo modprobe bcm2835-v4l2"
    p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
    time.sleep(5)

# video input from webcam
video_capture = cv2.VideoCapture(0)
video_capture.set(3, frame_width)
video_capture.set(4, frame_height)
out = cv2.VideoWriter('output.mjpg', cv2.CV_FOURCC('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
h_txt = 60
v_txt = frame_height - 100
h_spd = frame_width - 140
v_spd = frame_height - 24
text1 = ""
text2 = ""
fix = '0'
speed = 0
l_spd = 0
gps_count = 0
gps = ""
sf = 50

while True:
    # Capture video feed
    ret, frame = video_capture.read()

    # write ouput video file
    out.write(frame)
    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) and 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()