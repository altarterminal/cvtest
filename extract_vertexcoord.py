#!/usr/bin/env python3

######################################################################
# default library
######################################################################

import os
import sys
import argparse

#####################################################################
# utility
#####################################################################

def output_error(msg):
  print('ERROR:' + os.path.basename(__file__) + ': ' + msg, file=sys.stderr)

def output_warn(msg):
  print('WARN:' + os.path.basename(__file__) + ': ' + msg, file=sys.stderr)

def output_info(msg):
  print('INFO:' + os.path.basename(__file__) + ': ' + msg, file=sys.stderr)

#####################################################################
# parameter
#####################################################################

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)

args = parser.parse_args()
input_file = args.input_file

if not os.access(input_file, os.F_OK) or not os.access(input_file, os.R_OK):
  output_error('invalid file specified <' + input_file + '>')
  sys.exit(1)

#####################################################################
# external library
#####################################################################

try:
  import cv2
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

#####################################################################
# mouse event
#####################################################################

def onMouse(event, x, y, flag, params):
  raw_image   = params["raw_image"]
  window_name = params["window_name"]
  point_list  = params["point_list"]
  max_num     = params["max_num"]

  float_point = (x, y)
  cur_num = len(point_list)

  if event == cv2.EVENT_LBUTTONDOWN:
    if cur_num < max_num:
      point_list.append(float_point)

  if event == cv2.EVENT_RBUTTONDOWN:
    if cur_num > 0:
      point_list.pop(-1)

  cur_num = len(point_list)

  overlap_image = raw_image.copy()
  h = raw_image.shape[0]
  w = raw_image.shape[1]
 
  c_blue  = (255, 0, 0)
  c_green = (0, 255, 0)
  c_red   = (0, 0, 255)

  radar_thin   = 1
  point_radius = 4
  side_thin    = 2 

  cv2.line(overlap_image, (x, 0), (x, h), c_blue, radar_thin)
  cv2.line(overlap_image, (0, y), (w, y), c_blue, radar_thin)

  for i in range(cur_num):
    point = point_list[i]
    cv2.circle(overlap_image, point, point_radius, c_red, cv2.FILLED)

  for i in range(1, cur_num):
    prev_point = point_list[i-1]
    next_point = point_list[i]
    cv2.line(overlap_image, prev_point, next_point, c_green, side_thin)

  if cur_num == max_num:
    head_point = point_list[0]
    tail_point = point_list[max_num-1]
    cv2.line(overlap_image, head_point, tail_point, c_green, side_thin)

  if 0 < cur_num and cur_num < max_num:
    tail_point = point_list[cur_num-1]
    cv2.line(overlap_image, float_point, tail_point, c_green, side_thin)

  cv2.imshow(window_name, overlap_image)

#####################################################################
# main routine
#####################################################################

# input all data

raw_image = cv2.imread(input_file)

window_name = "MouseEvent"
point_list = []
max_num = 4
params = {
  "raw_image":   raw_image,
  "window_name": window_name,
  "point_list":  point_list,
  "max_num":     max_num,
}

cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, onMouse, params)
cv2.imshow(window_name, raw_image)
cv2.waitKey(0)

for i in range(len(point_list)):
  print("{},{}".format(point_list[i][0], point_list[i][1]))

cv2.destroyAllWindows()
