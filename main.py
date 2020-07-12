###!/usr/bin/env python
import cv2
import math
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
# check for gps on USB
gps_con = 0
if os.path.exists('/dev/ttyUSB0') == True:
    ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=10)
    gps_con = 1

if os.path.exists('/dev/ttyUSB1') == True and gps_con == 0:
    ser = serial.Serial('/dev/ttyUSB1', 4800, timeout=10)
    gps_con = 1

# video input from webcam
video_capture = cv2.VideoCapture(0)
video_capture.set(3, frame_width)
video_capture.set(4, frame_height)
out = cv2.VideoWriter('output.mjpg', cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
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
    if gps_con == 1:
        gps = ser.readline()
        if gps[0: 1] != "$":
            ser.flushInput()

    if gps[1: 6] == "GPGGA":
        fix = '0'
        gps1 = gps.split(',', 12)
        if len(gps) > 68 and (gps1[3] == "N" or gps1[3] == "S"):
            fix = gps1[6]
    elif gps[1: 6] == "GPRMC" and fix != '0':
        gps2 = gps.split(',', 12)
        if len(gps) > 60 and (gps2[4] == "N" or gps2[4] == "S"):
            timestamp = (gps2[1])[:2] + ":" + (gps2[1])[2:4] + ":" + (gps2[1])[4:6]
            lon = int(gps2[3][0:2]) + Decimal(int(gps2[3][2:4])) / Decimal(60) + Decimal(int(gps2[3][5:9])) / Decimal(
                360000)
            lat = int(gps2[5][0:3]) + Decimal(int(gps2[5][3:5])) / Decimal(60) + Decimal(int(gps2[5][6:10])) / Decimal(
                360000)
            if gps_count == 0 or ((lon != lonfiles[0] or lat != latfiles[0]) and timestamp[7:8] == "0"):
                lonfiles.insert(0, lon)
                latfiles.insert(0, lat)
                if gps_count >= points:
                    del lonfiles[points]
                    del latfiles[points]
                    gps_count = points
                else:
                    gps_count += 1

            text1 = timestamp + " " + str(lon) + " " + gps2[4] + " " + str(lat) + " " + gps2[6]
    elif gps[1: 6] == "GPVTG" and fix != '0':
        gps3 = gps.split(',', 8)
        if len(gps) > 26 and gps3[2] == "T":
            text2 = "    " + gps3[7]
            speed = float((gps3[7]))
            l_spd = len(str(int(speed)))
            text2 = str(int(speed)) + "     " + gps3[1]
    hrx = h_spd + int(49 * math.sin((speed / 40) - 2))
    hry = v_spd - int(49 * math.cos((speed / 40) - 2))

    if fix == '1':
        cv2.line(frame, (20, frame_height - 16), (frame_width - 20, frame_height - 16), (20, 20, 20), 25, 4)
        cv2.putText(frame, text1, (h_txt - 47, v_txt + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.circle(frame, (h_spd, v_spd), 52, (58, 58, 58), -1, 8)
        cv2.line(frame, (h_spd, v_spd), (hrx, hry), (200, 200, 200), 2, 4)
        cv2.circle(frame, (h_spd, v_spd), 32, (28, 28, 28), -1, 4)
        cv2.putText(frame, text2, (h_spd - (5 * (int(l_spd * 1.4))), v_spd + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 1)
    elif fix == '2' or fix == '3':
        cv2.putText(frame, text, (h_txt - 47, v_txt + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.line(frame, (h_spd, v_spd), (hrx, hry), (200, 200, 200), 2, 4)
        cv2.circle(frame, (h_spd, v_spd), 52, (28, 28, 28), 1, 8)
        cv2.circle(frame, (h_spd, v_spd), 32, (28, 28, 28), -1, 4)
        cv2.putText(frame, text2, (h_spd - (5 * (int(l_spd * 1.4))), v_spd + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 1)
    else:
        cv2.putText(frame, "Waiting for GPS data...", (h_txt - 47, v_txt + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 0, 255), 1)

    if len(lonfiles) > 2:
        cv2.rectangle(frame, (frame_width - graph_box, 0), (frame_width, graph_box), (0, 0, 0), -1)

        if timestamp[7:8] == "0":
            sf = 50
            lonmax = [x - lon for x in lonfiles]
            latmax = [x - lat for x in latfiles]

            lonsf = latsf = lonsn = latsn = 10000000
            if max(lonmax) != 0:
                lonsf = abs(Decimal((graph_box / 2) - 10) / (Decimal(max(lonmax))))
            if max(latmax) != 0:
                latsf = abs(Decimal((graph_box / 2) - 10) / (Decimal(max(latmax))))
            if min(lonmax) != 0:
                lonsn = abs(Decimal((graph_box / 2) - 10) / (Decimal(min(lonmax))))
            if min(latmax) != 0:
                latsn = abs(Decimal((graph_box / 2) - 10) / (Decimal(min(latmax))))
            sf = min(lonsf, latsf, latsn, lonsn)
        for mcounter in range(0, gps_count - 2, 1):
            if mcounter == 0:
                cv2.line(frame, (
                ((lonmax[mcounter]) * sf) + frame_width - (graph_box / 2), ((latmax[mcounter]) * sf) + (graph_box / 2)),
                         (((lonmax[mcounter + 1]) * sf) + frame_width - (graph_box / 2),
                          ((latmax[mcounter + 1]) * sf) + (graph_box / 2)), (0, 0, 255), 3, 4)
            else:
                cv2.line(frame, (
                ((lonmax[mcounter]) * sf) + frame_width - (graph_box / 2), ((latmax[mcounter]) * sf) + (graph_box / 2)),
                         (((lonmax[mcounter + 1]) * sf) + frame_width - (graph_box / 2),
                          ((latmax[mcounter + 1]) * sf) + (graph_box / 2)), (200, 200, 0), 1, 4)

    # write ouput video file
    out.write(frame)
    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) and 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()