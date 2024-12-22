#!/usr/bin/env python3

#####################################################################
# import
#####################################################################

import os
import sys
import argparse
import cv2
import numpy

#####################################################################
# parameter
#####################################################################

parser = argparse.ArgumentParser()
parser.add_argument('template',   type=str)
parser.add_argument('target',     type=str)
parser.add_argument('-x', '--cord_x', type=int, default='-1')
parser.add_argument('-y', '--cord_y', type=int, default='-1')
parser.add_argument('-d', '--delta', type=int, default='5')
args = parser.parse_args()

template_file = args.template
target_file = args.target
cord_x = args.cord_x
cord_y = args.cord_y
delta = args.delta

def print_error(msg):
    file_name = os.path.basename(__file__) 
    print('ERROR:' + file_name + ':' + msg, file=sys.stderr)

if not os.access(template_file, os.F_OK):
    print_error('invalid template specified')
    sys.exit(1)

if not os.access(target_file, os.F_OK):
    print_error('invalid target specified')
    sys.exit(1)

my_int_min = -2147483648
my_int_max = 2147483647

if cord_x == -1:
    x_lower = my_int_min
    x_upper = my_int_max
else:
    x_lower = cord_x - delta
    x_upper = cord_x + delta

if cord_y == -1:
    y_lower = my_int_min
    y_upper = my_int_max
else:
    y_lower = cord_y - delta
    y_upper = cord_y + delta

#####################################################################
# main routine
#####################################################################

threshold = 0.95

template_img = cv2.imread(template_file) 
target_img = cv2.imread(target_file)

template_img_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
target_img_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

raw_result = cv2.matchTemplate(target_img_gray, template_img_gray, cv2.TM_CCOEFF_NORMED)

candidate_result = numpy.where(raw_result >= threshold)
candidate_num = len(candidate_result[0])

if candidate_num <= 0:
    sys.exit(1)

_, max_val, _, max_loc = cv2.minMaxLoc(raw_result)
max_loc_x = max_loc[0]
max_loc_y = max_loc[1]

if x_lower <= max_loc_x and max_loc_x <= x_upper and \
   y_lower <= max_loc_y and max_loc_y <= y_upper:
    print("{} {}".format(max_loc_x, max_loc_y))
    sys.exit(0)
else:
    sys.exit(1)

