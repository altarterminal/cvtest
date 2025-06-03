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

args    = parser.parse_args()
in_file = args.in_file

if not os.access(in_file, os.F_OK) or not os.access(in_file, os.R_OK):
  output_error('invalid file specified <' + in_file + '>')
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
  import numpy
except ImportError:
  output_error('numpy not found')
  sys.exit(1)

#####################################################################
# prepare
#####################################################################

image = cv2.imread(in_file)

if image is None:
  output_error('cannot open file as image <' + in_file + '>')
  sys.exit(1)

detector = cv2.QRCodeDetectorAruco()

#####################################################################
# main routine
#####################################################################

is_exist, infos, _, _ = detector.detectAndDecodeMulti(image)

if not is_exist:
  output_error('QR code not found <' + in_file + '>')
  sys.exit(1)

recognized_strings = \
  list(filter(lambda x: x != "", infos))

if len(recognized_strings) == 0:
  output_error('decode failed <' + in_file + '>')
  sys.exit(1)

valid_strings = \
  list(filter(lambda x: re.match(r'^[0-9]{6}$', x) != None, recognized_strings))

if len(valid_strings) == 0:
  output_error('recognize failed <' + in_file + '>')
  sys.exit(1)

print(sorted(valid_strings, reverse=True)[0])
