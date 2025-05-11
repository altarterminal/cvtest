#!/usr/bin/env python3

######################################################################
# default library
######################################################################

import os
import sys
import argparse
import re

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
parser.add_argument('in_file', type=str)
parser.add_argument('-p', '--points', type=str, default='')
parser.add_argument('-d', '--out-dir', type=str, default='', help='output direcotry')
parser.add_argument('-r', '--is-only-round', action='store_true')

args = parser.parse_args()
in_file = args.in_file
points  = args.points
out_dir = args.out_dir
is_only_round = args.is_only_round

if not os.access(in_file, os.F_OK) or not os.access(in_file, os.R_OK):
  output_error('invalid file specified <' + in_file + '>')
  sys.exit(1)

if out_dir == "":
  out_dir = os.path.splitext(os.path.basename(in_file))[0] + '_numbered'

if os.path.isfile(out_dir):
  output_error('<' + out_dir + '> exists as file')
  sys.exit(1)
elif not os.access(out_dir, os.W_OK):
  output_info('output directory is newly created <' + out_dir + '>')
  os.makedirs(out_dir)
else:
  pass

#####################################################################
# prepare points information
#####################################################################

if re.match(r'^[0-9]+(,[0-9]+)*$', points) == None:
  output_error('invalid points specified <' + points + '>')
  sys.exit(1)

points_all = points.split(",")

if len(points_all) % 2 != 0:
  output_error('invalid number of points specified')
  sys.exit(1)

point_num = int(len(points_all) / 2)
xs = list(map(lambda x: int(x), points_all[0::2]))
ys = list(map(lambda y: int(y), points_all[1::2]))

#####################################################################
# external library
#####################################################################

try:
  import cv2
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

#####################################################################
# prepare video capture
#####################################################################

cap = cv2.VideoCapture(in_file)

if not cap.isOpened():
  output_error('capture cannot be opened <' + in_file + '>')
  sys.exit(1)

#####################################################################
# setting for drawing
#####################################################################

font_face      = cv2.FONT_HERSHEY_TRIPLEX
font_height    = 50
font_thickness = 3
font_color     = (255, 255, 255)

sample_str  = '888888'
is_baseline = False

margin = 20

rect_color     = (0, 0, 0)
rect_thickness = cv2.FILLED

#####################################################################
# prepare for drawing
#####################################################################

digit_num  = len(sample_str)
str_format = '0' + str(digit_num) + 'd'

font_scale = cv2.getFontScaleFromHeight(font_face, font_height)
base_size, baseline = cv2.getTextSize(sample_str, font_face, font_scale, font_thickness)

if not is_baseline:
  baseline = 0

str_w = base_size[0]
str_h = base_size[1]

rect_w = str_w + margin * 2
rect_h = str_h + margin * 2 + baseline

#####################################################################
# main routine
#####################################################################

frame_number = 0

while True:
  is_frame, frame = cap.read()

  if not is_frame:
    break
  else:
    for i in range(point_num):
      rect_top_left     = (xs[i], ys[i])
      rect_bottom_right = (xs[i] + rect_w, ys[i] + rect_h)
      cv2.rectangle(frame, rect_top_left, rect_bottom_right, rect_color, rect_thickness)

    num_str = format(frame_number, str_format)
    point_idx = int(frame_number % point_num)
    str_org = (xs[point_idx] + margin, ys[point_idx] + margin + str_h)
    cv2.putText(frame, num_str, str_org, font_face, font_scale, font_color, font_thickness)

    out_base = out_dir + '_' + "{0:06d}".format(frame_number) + '.png'
    out_file = out_dir + '/' + out_base
    cv2.imwrite(out_file, frame)
    print(out_file, flush=True)

    frame_number += 1
    if (frame_number == point_num) and is_only_round:
      break

#####################################################################
# cleanup
#####################################################################

cap.release()
