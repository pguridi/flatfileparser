# -*- coding: utf-8 *-*
from datetime import datetime

FFP_TYPE_STRING = "string"
FFP_TYPE_REGEX = "regex"
FFP_TYPE_BOOLEAN = "boolean"
FFP_TYPE_NUMERIC = "numeric"
FFP_TYPE_FLOAT = "float"
FFP_TYPE_CONSTANT = "constant value"
FFP_TYPE_DATE = "date"


def strfy(data):
    return str(data)


def numerify(data):
    return int(data)


def boolify(data):
    return bool(data)


def floatify(data):
    return float(data)


def datetify(data, arg):
    try:
        dt = datetime.strptime(data, arg)
        return dt.strftime('%m/%d/%Y')
    except ValueError:
        return None


FFP_TYPES = {FFP_TYPE_STRING: strfy,
            FFP_TYPE_BOOLEAN: boolify,
            FFP_TYPE_NUMERIC: numerify, 
            FFP_TYPE_FLOAT: floatify,
            FFP_TYPE_DATE: datetify}
