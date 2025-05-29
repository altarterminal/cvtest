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
parser.add_argument('in_file', type=str)
parser.add_argument('-o', '--out-name', type=str, default='')
parser.add_argument('-d', '--out-dir', type=str, default='.')
parser.add_argument('-c', '--cols', type=int, required=True)
parser.add_argument('-r', '--rows', type=int, required=True)
parser.add_argument('-m', '--homography-matrix-files', type=str)
args = parser.parse_args()

in_file      = args.in_file
out_name     = args.out_name
out_dir      = args.out_dir
out_width    = args.cols
out_height   = args.rows
matrix_files = args.homography_matrix_files

if not os.access(in_file, os.F_OK) or not os.access(in_file, os.R_OK):
  output_error('invalid file specified <' + in_file + '>')
  sys.exit(1)

if out_width <= 0:
  output_error('invalid width specified <' + out_width + '>')
  sys.exit(1)

if out_height <= 0:
  output_error('invalid height specified <' + out_height + '>')
  sys.exit(1)

if out_name == "":
  out_name_prefix = os.path.basename(in_file) + '_transformed'
else:
  out_name_prefix = os.path.splitext(os.path.basename(out_name))[0]

if os.path.isfile(out_dir):
  output_error('<' + out_dir + '> exists as file')
  sys.exit(1)
elif not os.access(out_dir, os.W_OK):
  output_info('output directory is newly created <' + out_dir + '>')
  os.makedirs(out_dir)
else:
  pass

out_size = (out_width, out_height)

#####################################################################
# external library
#####################################################################

try:
  import cv2
except ImportError:
  output_error('opencv not found')
  sys.exit(1)

try:
  import numpy
except ImportError:
  output_error('numpy not found')
  sys.exit(1)

#####################################################################
# prepare matrix
#####################################################################

matrix_file_list = matrix_files.split(",")

matrix_list = []

for matrix_file in matrix_file_list:
  if not os.access(matrix_file, os.F_OK) or not os.access(matrix_file, os.R_OK):
    output_error('invalid file specified <' + matrix_file + '>')
    sys.exit(1)

  try:
    M = numpy.loadtxt(matrix_file)
  except ValueError:
    output_error('invalid contents are included <' + matrix_file + '>')
    sys.exit(1)

  matrix_list.append(M)

#####################################################################
# prepare capture
#####################################################################

cap = cv2.VideoCapture(in_file)

if not cap.isOpened():
  output_error('cannot open video <' + in_file + '>')
  sys.exit(1)

#####################################################################
# main routine
#####################################################################

frame_number = 1

while True:
  is_frame, frame = cap.read()

  if is_frame:
    for roi_number, matrix in enumerate(matrix_list, 1):
      out_base = out_name_prefix       + '_' + \
        "{0:06d}".format(frame_number) + '_' + \
        "{0:02d}".format(roi_number)   + '.png'
      out_file = out_dir + '/' + out_base

      transformed_frame = cv2.warpPerspective(frame, matrix, out_size)

      cv2.imwrite(out_file, transformed_frame)
      print(out_base, flush=True)

    frame_number += 1
  else:
    break

#####################################################################
# cleanup
#####################################################################

cap.release()
