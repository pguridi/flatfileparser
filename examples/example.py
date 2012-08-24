#!/usr/bin/env python

import os
import time
import sys

sys.path.append("..")

from flatfileparser import FlatReader, LineFormat, BeginsWithCondition
from flatfileparser.ffptypes import *


if __name__ == '__main__':
    start = time.time()

    file_path = os.path.join("coordinates.txt")
    freader = FlatReader(file_path, debug=True)
    
    # Filter Header Lines with a condition (if line begins with "H")
    header_condition = BeginsWithCondition("H")
    # Now define a format for the header lines
    header_format = LineFormat("Header")
    # Just lets get a single field of type STRING (whole line)
    header_format.add_field("header_line", 1, -1, FFP_TYPE_STRING)
    freader.declare_condition(header_condition, header_format)
    
    # Now lets get the real data, in this case the following fields:
    # Field_name    type      begin_column   end_column
    # line          Numeric    1              5
    # point         Numeric    17             25
    # x             Float      46             54
    # y             Float      56             64

    # Define the line format containing these fields:

    sp_format = LineFormat("CoordinatesLine")
    sp_format.add_field("line", 1, 5, FFP_TYPE_NUMERIC)
    sp_format.add_field("point", 17, 25, FFP_TYPE_NUMERIC)
    sp_format.add_field("x", 46, 54, FFP_TYPE_FLOAT)
    sp_format.add_field("y", 56, 64, FFP_TYPE_FLOAT)
    freader.register_line_format(sp_format)

    for record in freader.read_line():
        print record
    
    end = time.time()
    elapsed = end - start
    print "Elapsed time: " + str(elapsed) + " count: " + str(freader.get_count())

