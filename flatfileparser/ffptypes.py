# -*- coding: utf-8 *-*

FFP_TYPE_STRING = "string"
FFP_TYPE_REGEX = "regex"
FFP_TYPE_BOOLEAN = "boolean"
FFP_TYPE_NUMERIC = "numeric"
FFP_TYPE_FLOAT = "float"
FFP_TYPE_CONSTANT = "constant value"

def strfy(data):
    return str(data)

def numerify(data):
    return int(data)

def boolify(data):
    return bool(data)
    
def floatify(data):
    return float(data)

FFP_TYPES = {FFP_TYPE_STRING: strfy,
            FFP_TYPE_BOOLEAN: boolify,
            FFP_TYPE_NUMERIC: numerify, 
            FFP_TYPE_FLOAT: floatify}
