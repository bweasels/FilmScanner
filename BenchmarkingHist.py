# Functions for comparison
import numpy as np
import cv2


def f1(image, hist_w, hist_h):
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


def f2(image, hist_w, hist_h):
    # Initial variables
    histSize = 256
    histRange = (0, 256)
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]
    bgr_planes = [b, g, r]

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


# Doing a couple initial imshows to make sure that this works
img = np.zeros((640, 800, 3), np.uint8)
img[:, :, 0] = img[:, :, 0] + 25
img[:, :, 1] = img[:, :, 1] + 50
img[:, :, 2] = img[:, :, 2] + 75
hist_w = 720
hist_h = 576

# cv2.imshow("Initial Image", img)
# cv2.imshow('F1', f1(img, wbPixel))
# cv2.imshow("F2", f2(img, wbPixel))
# cv2.imshow('F3', f3(img, wbPixel))
# cv2.waitKey()

# Reporting
import time
import random
import statistics

functions = f1, f2
times = {f.__name__: [] for f in functions}

for i in range(10000):  # adjust accordingly so whole thing takes a few sec
    func = random.choice(functions)
    t0 = time.time()
    func(img, hist_w, hist_h)
    t1 = time.time()
    times[func.__name__].append((t1 - t0) * 1000)

for name, numbers in times.items():
    print('FUNCTION:', name, 'Used', len(numbers), 'times')
    print('\tMEDIAN', statistics.median(numbers))
    print('\tMEAN  ', statistics.mean(numbers))
    print('\tSTDEV ', statistics.stdev(numbers))
