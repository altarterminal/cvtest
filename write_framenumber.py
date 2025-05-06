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
parser.add_argument('-r', '--rows', type=int, default='0')
parser.add_argument('-c', '--cols', type=int, default='0')
parser.add_argument('-p', '--points', type=str, default='')
parser.add_argument('-o', '--out-name', type=str, default='')

args = parser.parse_args()
in_file       = args.in_file
target_height = args.rows
target_width  = args.cols
points        = args.points
out_name      = args.out_name

if not os.access(in_file, os.F_OK) or not os.access(in_file, os.R_OK):
  output_error('invalid file specified <' + in_file + '>')
  sys.exit(1)

if target_height < 0:
  output_error('invalid height specified <' + target_height + '>')
  sys.exit(1)

if target_width < 0:
  output_error('invalid width specified <' + target_width + '>')
  sys.exit(1)

if out_name == "":
  out_name = os.path.basename(in_file) + '_numbered.mp4'
else:
  out_name = in_file.removesuffix('.mp4') + '.mp4'

out_file = './' + out_name

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

point_num = len(points_all) / 2
xs = list(map(lambda x: int(x), points_all[0::2]))
ys = list(map(lambda y: int(y), points_all[1::2]))

#####################################################################
# external library
#####################################################################

try:
  import cv2
B
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

#####################################################################
# prepare video player
#####################################################################

cap = cv2.VideoCapture(in_file)

if not cap.isOpened():
  output_error('file cannot be opened <' + in_file + '>')
  sys.exit(1)

if target_width > 0:
  final_width  = target_width
  final_height = target_height
else:
  final_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  final_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc     = cv2.VideoWriter_fourcc(*'X264')
fps        = float(cap.get(cv2.CAP_PROP_FPS))
final_size = (final_width, final_height)
is_color   = True

#writer = cv2.VideoWriter(out_file, fourcc, fps, final_size, is_color)

#####################################################################
# setting for drawing
#####################################################################

font_face     = cv2.FONT_HERSHEY_SIMPLEX
font_height   = 50
str_thickness = 3

sample_str  = '888888'
is_baseline = False

margin = 20

#####################################################################
# prepare for drawing
#####################################################################

digit_num = len(sample_str)
str_formatter = '0' + str(digit_num) + 'd'

font_scale = cv2.getFontScaleFromHeight(font_face, font_height)
base_size, baseline = cv2.getTextSize(sample_str, font_face, font_scale, str_thickness)

if not is_baseline:
  baseline = 0

str_w     = base_size[0]
str_h     = base_size[1]
str_color = (255, 255, 255)

rect_w         = str_w + margin * 2
rect_h         = str_h + margin * 2 + baseline
rect_color     = (0, 0, 0)
rect_thickness = cv2.FILLED

#####################################################################
# main routine
#####################################################################

frame_number = 1

while True:
  is_frame, frame = cap.read()

  if not is_frame:
    break
  else:
    cur_str = format(frame_number, str_formatter)

    cur_idx = int(frame_number % point_num)
    x = xs[cur_idx]
    y = ys[cur_idx]

    rect_top_left     = (x, y)
    rect_bottom_right = (x + rect_w, y + rect_h)
    cv2.rectangle(frame, rect_top_left, rect_bottom_right, rect_color, rect_thickness)

    str_org = (x + margin, y + margin + str_h)
    cv2.putText(frame, cur_str, str_org, font_face, font_scale, str_color, str_thickness)

    frame_number = frame_number + 1

    cv2.imshow("Test", frame)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
