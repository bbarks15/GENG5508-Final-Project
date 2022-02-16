#!/usr/bin/env python3

from urx import Robot
from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper

from image import *
from done import done_message

import cv2

import math3d as m3d
import time

a = 0.5
v = 0.2

scan_start = [-0.4282310644732874, -1.570743684504425, -1.5707963705062866, -0.7854277056506653, 1.5708061456680298, -8.885060445606996e-06]
scan_end = [0.6781067848205566, -1.5707585029379807, -1.5708080530166626, -0.7853933137706299, 1.5707809925079346, -8.408223287403871e-06]
home = (0.500,-0.100,0.500,2.4,-2.4,1)
home_j = [0, -1.570769096897795, -1.5707969665527344, -0.7853799623302002, 1.570780873298645, 0]

# [0, -pi/2, -pi/2, -pi/4, pi/2, 0]
# [0, -1.570769096897795, -1.5707969665527344, -0.7853799623302002, 1.570780873298645, 0]

#588.6 --> 142.9 =
bins = {
  "orange" : (0.100,0.500,0.500,2.4,-2.4,1),
  "yellow" : (-0.500,0.100,0.500,2.4,-2.4,1),
  "green" : (-0.100,-0.500,0.500,2.4,-2.4,1),
}

bins_j = {
  "orange" : [-1.4466946760760706, -1.5707816047264096, -1.570809245109558, -0.7854049962810059, 1.5707685947418213, -3.3680592672169496e-05],
  "yellow" : [-2.6419530550586146, -1.5708066425719203, -1.5707944631576538, -0.7854159635356446, 1.5708194971084595, 1.5974044799804688e-05],
  "green" :  [-1.9364078680621546, -1.5707949327318893, -1.5708081722259521, -0.785416917209961, 1.570767879486084, -8.408223287403871e-06],
}


ip_addr = "192.168.1.116"
image_url = f"http://{ip_addr}:4242/current.jpg?annotations=off"
rob = Robot(ip_addr)
robotiqgrip = Robotiq_Two_Finger_Gripper(rob, force=1)
v = 0.05


def wait():
  while True:
    time.sleep(0.1)
    if rob.is_program_running():
      return


# scans workarea for objects
def scan():
    rob.movej(scan_start, acc=0.8, vel=1, wait = True)

    rob.movej(scan_end, acc=0.8, vel=0.2, wait = False)
    while True:
      img = url_to_image(image_url)
      objects = locate_colors(img)
      cv2.imshow('image', img)
      cv2.waitKey(50)
      if len(objects) > 0:
        rob.stop()
        return True, list(objects.items())[0][0]
      elif not rob.is_program_running():
        return False, None


# centers gripper over detected object
def find_and_move(color):
  while True:
    img = url_to_image(image_url)
    objects = locate_colors(img)

    if len(objects) == 0:
      return False

   # obj = objects.items()
   # print(obj)
    try:
      (dx,dy) = objects[color]
      dy-=40
      if abs(dx) > 10 and abs(dy) < 200:
        v = abs(dx)/500
        rob.speedj((-v if dx > 0 else v, 0, 0, 0, 0, 0), a, 0.01*abs(dx))
      elif abs(dy) > 10:
        v = abs(dy)/500
        dv = -v/2 if dy > 0 else v/2
        rob.speedl_tool((0, -dv, dv, 0, 0, 0), a, 0.01*abs(dy))
      else:
        return True

      cv2.imshow('image', img)
      cv2.waitKey(25)
    except:
      pass


# picks up an object and moves it to the bin
def place_in_bin(color):
  # lower tool
  pos = rob.get_pos()
  pos[2] = 0.1429
  rob.set_pos(pos,0.2,0.5)

  # rob.movel((0,0, -0.4457, 0, 0, 0), a, 0.25, relative=True)
  robotiqgrip.close_gripper()

  rob.movel((0,0, 0.2, 0, 0, 0), a, 1, relative=True)

  rob.movej(bins_j[color],a,1, wait=True)
  robotiqgrip.open_gripper()


def main():
  print("running")

  input("press enter to continue")

  while True:
    found, color = scan()
    if not found:
      print(done_message)
      rob.speedj((1,0, 0, 0, 0, 0), a, 0)
      rob.close()
      exit(0)

    if not find_and_move(color):
      continue
    place_in_bin(color)

main()
