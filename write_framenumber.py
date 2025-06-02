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
parser.add_argument('--is-round-only', action='store_true')

args = parser.parse_args()
in_file       = args.in_file
points        = args.points
out_dir       = args.out_dir
is_round_only = args.is_round_only

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
# external library
#####################################################################

try:
  import cv2
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

try:
  from PIL import ImageFont, ImageDraw, Image
except ImportError:
  output_error('PIL not found')
  sys.exit(1)

try:
  import qrcode
except ImportError:
  output_error('qrcode not found')
  sys.exit(1)

try:
  import numpy
except ImportError:
  output_error('numpy not found')
  sys.exit(1)

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

points = []
for i in range(point_num):
  points.append((xs[i], ys[i]))

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

font_file  = "/Users/xxxx/Library/Fonts/RictyDiminished-Regular.ttf"
font_size  = 100
font_color = (255, 255, 255)

sample_str = '888888'
margin = 30
rect_color = (0, 0, 0)

#####################################################################
# prepare for drawing
#####################################################################

if not os.access(font_file, os.F_OK) or not os.access(font_file, os.R_OK):
  output_error('invalid font file specified <' + font_file + '>')
  sys.exit(1)

font = ImageFont.truetype(font_file, font_size)

digit_num  = len(sample_str)
str_format = '0' + str(digit_num) + 'd'

frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

dummy_image = Image.new("RGB", (frame_width, frame_height), (0, 0, 0))
dummy_draw  = ImageDraw.Draw(dummy_image)

dboxs = []
for i in range(point_num):
  dbox_original = dummy_draw.textbbox(points[i], sample_str, font=font)
  dbox_margin   = (
    dbox_original[0] - margin,
    dbox_original[1] - margin,
    dbox_original[2] + margin,
    dbox_original[3] + margin
  )
  dboxs.append(dbox_margin)

#####################################################################
# setting for QR code
#####################################################################

qr_version = 1
qr_level   = qrcode.constants.ERROR_CORRECT_H
qr_boxsize = 20
qr_border  = 4
qr = qrcode.QRCode(qr_version, qr_level, qr_boxsize, qr_border)

qr_width  = 300
qr_height = 300
qr_size = (qr_width, qr_height)

#####################################################################
# main routine
#####################################################################

frame_number = 1

while True:
  is_frame, frame = cap.read()

  if not is_frame:
    break
  else:
    frame_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(frame_pil)

    # fill the background at locations of all frame numbers
    for i in range(point_num):
      draw.rectangle(dboxs[i], fill=rect_color)

    # overwrite frame number
    num_str = format(frame_number, str_format)
    point = points[int((frame_number - 1) % point_num)]
    draw.text(point, num_str, fill=font_color, font=font)
    drawn_frame = numpy.array(frame_pil)

    # make qr code
    qr.clear()
    qr.add_data(num_str)
    qr.make()
    qr_image = numpy.asarray(qr.make_image()).astype(numpy.uint8)
    cv2.normalize(qr_image, qr_image, 0, 255, cv2.NORM_MINMAX)
    qr_resized_image = cv2.resize(qr_image, qr_size)
    qr_rgb_image = cv2.cvtColor(qr_resized_image, cv2.COLOR_GRAY2RGB)

    # overwrite qr code
    qr_left   = point[0]
    qr_top    = point[1] + margin*2 + font_size
    qr_right  = qr_left + qr_width
    qr_bottom = qr_top  + qr_height
    drawn_frame[qr_top:qr_bottom, qr_left:qr_right] = qr_rgb_image

    # write out
    out_base = out_dir + '_' + "{0:06d}".format(frame_number) + '.png'
    out_file = out_dir + '/' + out_base
    cv2.imwrite(out_file, drawn_frame)
    print(out_file, flush=True)

    frame_number += 1
    if is_round_only and (frame_number > point_num):
      break

#####################################################################
# cleanup
#####################################################################

cap.release()
