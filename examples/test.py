#!/usr/bin/env python

import os
import time

from flatfileparser import FlatReader, LineFormat, BeginsWithCondition
from flatfileparser.ffptypes import *
#YAFFP_TYPE_NUMERIC,YAFFP_TYPE_STRING, YAFFP_TYPE_FLOAT


if __name__ == '__main__':
    start = time.time()

    filePath = os.path.join("preplot_grande.s")
    freader = FlatReader(filePath)
    
    # Add the format for header lines:
    header_condition = BeginsWithCondition("H")
    header_format = LineFormat("Header")
    header_format.add_field("header_line", 1, -1, FFP_TYPE_STRING)
    freader.declare_condition(header_condition, header_format)
    
    # Add the format for SP lines
    sp_format = LineFormat("SP")
    sp_format.add_field("line", 1, 5, FFP_TYPE_NUMERIC)
    sp_format.add_field("point", 17, 25, FFP_TYPE_NUMERIC)
    sp_format.add_field("x", 46, 54, FFP_TYPE_FLOAT)
    sp_format.add_field("y", 56, 64, FFP_TYPE_FLOAT)
    freader.register_line_format(sp_format)

#    try:
    for record in freader.read_line():
        print record
#    except Exception, e:
#        print "Error parsing file: ", e
    end = time.time()
    elapsed = end - start
    print "Elapsed time: " + str(elapsed) + " count: " + str(freader.get_count())

