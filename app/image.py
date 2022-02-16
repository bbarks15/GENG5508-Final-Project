#!/usr/bin/env python3

import numpy as np
import cv2
from urllib import request
from socket import timeout
import os

# Each color is a tuple of the upper and lower bounds of the [H, S, V]
# need to by np arrays because python
# H = h/2       0 <= h <= 360
# S = s*255     0.0 <= s <= 1.0
# V = v*255     0.0 <= v <= 1.0
color_threshold = {}
color_threshold["yellow"] = (np.array([33, 120, 120]), np.array([40, 255, 255]))
color_threshold["green"]  = (np.array([50, 120, 30]), np.array([65, 255, 255]))
color_threshold["orange"]    = (np.array([170, 120, 120]), np.array([179, 255, 255]))

color_vals = {
"orange" : (0,0,255),
"green" : (0,255,0),
"yellow" : (0,255,255)
}

# 640
# 480

# Loop through each color and find the biggest occurence
def locate_colors(img):
    objects = {}
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    for color, threshold in color_threshold.items():
        (lower, upper) = threshold
        mask = cv2.inRange (hsv, lower, upper)
        cnts = cv2.findContours(mask.copy(),
                                  cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)[-2]


        if len(cnts)>0:
            area = max(cnts, key=cv2.contourArea)
            (x1, y1, w, h) = cv2.boundingRect(area)
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), color_vals[color], 2)
            cv2.putText(img, color, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, (0, 0, 0), 1)
            objects[color] = (320 - (x1 + w/2), 240 - (y1 + w/2))

    return objects


def url_to_image(url):
    while True:
        try:
            resp = request.urlopen(url, timeout=1)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            return image
        except timeout:
            print("DEAD")
            pass


def main():
    ip_addr = "192.168.1.116"
    image_url = f"http://{ip_addr}:4242/current.jpg?annotations=off"
    while True:
        img = url_to_image(image_url)
        objects = locate_colors(img)
        for color, location in objects.items():
            (x, y) = location
            print(f"Color {color} is ({x}, {y}) from center")
        cv2.imshow('image',img)
        cv2.waitKey(5)

if __name__ == "__main__":
    main()
