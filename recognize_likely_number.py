#!/usr/bin/env python3

######################################################################
# default library
######################################################################

import os
import sys
import argparse
import glob
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
parser.add_argument('file_pattern', type=str)

args = parser.parse_args()
file_pattern = args.file_pattern

glob_list = glob.glob(file_pattern)
file_list = list(filter(lambda x: os.access(x, os.F_OK), glob_list))

if not file_list:
  output_error('no file found <' + file_pattern + '>')
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
# prepare
#####################################################################

detector = cv2.QRCodeDetectorAruco()

pattern = re.compile(r'^[0-9]{6}$')

#####################################################################
# recognized frame numbers
#####################################################################

number_list = []

for file in file_list:
  image = cv2.imread(file)

  if image is None:
    output_error('cannot open file as image <' + file + '>')
    sys.exit(1)

  _, info_list, _, _ = detector.detectAndDecodeMulti(image)

  # It is assumed that there is only one QR code
  if len(info_list) != 1:
    continue

  if pattern.match(info_list[0]) is None:
    continue

  number_list.append(info_list[0])

#####################################################################
# determine the representative frame number
#####################################################################

if not number_list:
  output_error('recognize failed <' + file_pattern + '>')
  sys.exit(1)

print(sorted(number_list, reverse=True)[0])
