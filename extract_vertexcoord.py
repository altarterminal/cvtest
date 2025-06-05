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
parser.add_argument('-r', '--rows', type=int, default='0')
parser.add_argument('-c', '--cols', type=int, default='0')
parser.add_argument('-p', '--print', action='store_true')

args = parser.parse_args()
input_file  = args.input_file
target_height = args.rows
target_width  = args.cols
is_print      = args.print

if not os.access(input_file, os.F_OK) or not os.access(input_file, os.R_OK):
  output_error('invalid file specified <' + input_file + '>')
  sys.exit(1)

if target_height < 0:
  output_error('invalid height specified <' + target_height + '>')
  sys.exit(1)

if target_width < 0:
  output_error('invalid width specified <' + target_width + '>')
  sys.exit(1)

#####################################################################
# external library
#####################################################################

try:
  import cv2
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

try:
  import numpy as np
except ImportError:
  output_error('numpy not found')
  sys.exit(1)

#####################################################################
# function for drawing
#####################################################################

def draw_radar(image, x, y, w, h):
  radar_thickness = 1
  radar_color = (255, 0, 0)

  cv2.line(image, (x, 0), (x, h), radar_color, radar_thickness)
  cv2.line(image, (0, y), (w, y), radar_color, radar_thickness)

def draw_vertex(image, point_list):
  point_num = len(point_list)

  if point_num == 0:
    return

  vertex_radius = 4
  vertex_color = (0, 0, 255)

  for i in range(point_num):
    point = point_list[i]
    cv2.circle(image, point, vertex_radius, vertex_color, cv2.FILLED)

def draw_side(image, point_list):
  point_num = len(point_list)

  if point_num <= 1:
    return

  side_thickness = 2
  side_color = (0, 255, 0)

  for i in range(1, point_num):
    prev_point = point_list[i - 1]
    next_point = point_list[i]
    cv2.line(image, prev_point, next_point, side_color, side_thickness)

  if point_num < max_num:
    return

  head_point = point_list[0]
  tail_point = point_list[max_num - 1]
  cv2.line(image, head_point, tail_point, side_color, side_thickness)

def draw_ongoing(image, point_list, x, y, max_num):
  point_num = len(point_list)

  if point_num <= 0 or max_num <= point_num:
    return

  ongoing_thickness = 2
  ongoing_color = (0, 255, 0)

  tail_point = point_list[point_num - 1]
  cv2.line(image, [x, y], tail_point, ongoing_color, ongoing_thickness)

def draw_coord(image, x, y):
  delta      = 20
  font_face  = cv2.FONT_HERSHEY_DUPLEX
  font_scale = 1.0
  coord_str  = '(' + str(x) + ', ' + str(y) + ')'
  org        = (x + delta, y - delta)
  color      = (128, 128, 128)
  thickness  = 3

  cv2.putText(image, coord_str, org, font_face, font_scale, color, thickness)

#####################################################################
# function for mouse event
#####################################################################

def on_event_add(x, y, flag, params):
  raw_image   = params["raw_image"]
  window_name = params["window_name"]
  point_list  = params["point_list"]
  width       = params["width"]
  height      = params["height"]
  max_num     = params["max_num"]

  if len(point_list) < max_num:
    point_list.append([x, y])

  image = raw_image.copy()
  draw_radar(image, x, y, width, height)
  draw_side(image, point_list)
  draw_vertex(image, point_list)
  draw_coord(image, x, y)
  cv2.imshow(window_name, image)

def on_event_delete(x, y, flag, params):
  raw_image   = params["raw_image"]
  window_name = params["window_name"]
  point_list  = params["point_list"]
  width       = params["width"]
  height      = params["height"]
  max_num     = params["max_num"]

  if point_list:
    point_list.pop(-1)

  image = raw_image.copy()
  draw_radar(image, x, y, width, height)
  draw_side(image, point_list)
  draw_ongoing(image, point_list, x, y, max_num)
  draw_vertex(image, point_list)
  draw_coord(image, x, y)
  cv2.imshow(window_name, image)

def on_event_steady(x, y, flag, params):
  raw_image   = params["raw_image"]
  window_name = params["window_name"]
  point_list  = params["point_list"]
  width       = params["width"]
  height      = params["height"]
  max_num     = params["max_num"]

  image = raw_image.copy()
  draw_radar(image, x, y, width, height)
  draw_side(image, point_list)
  draw_ongoing(image, point_list, x, y, max_num)
  draw_vertex(image, point_list)
  draw_coord(image, x, y)
  cv2.imshow(window_name, image)

def on_mouse_event(event, x, y, flag, params):
  if   event == cv2.EVENT_LBUTTONDOWN:
    on_event_add(x, y, flag, params)
  elif event == cv2.EVENT_RBUTTONDOWN:
    on_event_delete(x, y, flag, params)
  elif event == cv2.EVENT_MOUSEMOVE:
    on_event_steady(x, y, flag, params)
  else:
    pass

#####################################################################
# prepare
#####################################################################

if input_file.endswith('.jpg') or input_file.endswith('.png'):
  is_image = True
  raw_image = cv2.imread(input_file)
else:
  is_image = False
  cap = cv2.VideoCapture(input_file)

  if not cap.isOpened():
    output_error('cannot open video')
    sys.exit(1)

  is_frame, raw_image = cap.read()
  if not is_frame:
    output_error('cannot get the head frame')
    sys.exit(1)

window_name = "Perspective Transform"
point_list  = []
raw_width   = raw_image.shape[1]
raw_height  = raw_image.shape[0]
max_num     = 4

params = {
  "raw_image":   raw_image,
  "window_name": window_name,
  "point_list":  point_list,
  "width":       raw_width,
  "height":      raw_height,
  "max_num":     max_num,
}

cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, on_mouse_event, params)

#####################################################################
# main routine
#####################################################################

cv2.imshow(window_name, raw_image)

while True:
  keycode = cv2.waitKey(0) & 0xFF

  if   keycode == 0x71:
    # [q]
    cv2.destroyAllWindows()
    sys.exit(0)
  elif keycode == 0x0D:
    # [Enter]
    if len(point_list) < max_num:
      output_warn("Specify the FOUR points")
    else:
      break
  elif keycode == 0x6E:
    # [n]
    if is_image:
      output_warn("The input data is an image")
    else:
      is_frame, raw_image = cap.read()
      if not is_frame:
        output_warn('No frame is left')
      else:
        params["raw_image"] = raw_image
        params["point_list"].clear()
        cv2.imshow(window_name, raw_image)
  else:
    output_info("[q] for quit of [Enter] for term input")

#####################################################################
# post process
#####################################################################

if target_width <= 0:
  final_width = raw_width
else:
  final_width = target_width

if target_height <= 0:
  final_height = raw_height
else:
  final_height = target_height

final_list = [
  [0, 0],
  [final_width, 0],
  [final_width, final_height],
  [0, final_height]
]

src_points = np.float32(point_list)
dst_points = np.float32(final_list)

M = cv2.getPerspectiveTransform(src_points, dst_points)
dst_img = cv2.warpPerspective(raw_image, M, (final_width, final_height))

cv2.namedWindow('Transformed Image')
cv2.imshow('Transformed Image', dst_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

if is_print:
  print("src: {}".format(point_list))
  print("dst: {}".format(final_list))

print(M)
