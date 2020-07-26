# Functions for comparison
import numpy as np
import cv2


def f1(image, pixel):
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]

    lum = (pixel[0] + pixel[1] + pixel[2]) / 3

    b = b * lum / pixel[0]
    g = g * lum / pixel[1]
    r = r * lum / pixel[2]

    image = np.dstack((b, g, r))
    return image


def f2(image, pixel):
    b, g, r = cv2.split(image)

    lum = (pixel[0] + pixel[1] + pixel[2]) / 3

    b = b * lum / pixel[0]
    g = g * lum / pixel[1]
    r = r * lum / pixel[2]

    image = cv2.merge((b, g, r))
    return image


def f3(image, pixel):
    b, g, r = np.dsplit(image, image.shape[-1])

    lum = (pixel[0] + pixel[1] + pixel[2]) / 3

    b = b * lum / pixel[0]
    g = g * lum / pixel[1]
    r = r * lum / pixel[2]

    image = np.dstack((b, g, r))
    return image


# Doing a couple initial imshows to make sure that this works
img = np.zeros((640, 800, 3), np.uint8)
img[:, :, 0] = img[:, :, 0] + 25
img[:, :, 1] = img[:, :, 1] + 50
img[:, :, 2] = img[:, :, 2] + 75
wbPixel = (75, 75, 75)

# cv2.imshow("Initial Image", img)
# cv2.imshow('F1', f1(img, wbPixel))
# cv2.imshow("F2", f2(img, wbPixel))
# cv2.imshow('F3', f3(img, wbPixel))
# cv2.waitKey()

# Reporting
import time
import random
import statistics

functions = f1, f2, f3
times = {f.__name__: [] for f in functions}

for i in range(10000):  # adjust accordingly so whole thing takes a few sec
    func = random.choice(functions)
    t0 = time.time()
    func(img, wbPixel)
    t1 = time.time()
    times[func.__name__].append((t1 - t0) * 1000)

for name, numbers in times.items():
    print('FUNCTION:', name, 'Used', len(numbers), 'times')
    print('\tMEDIAN', statistics.median(numbers))
    print('\tMEAN  ', statistics.mean(numbers))
    print('\tSTDEV ', statistics.stdev(numbers))
