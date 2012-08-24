# -*- coding: utf-8 *-*
#!/usr/bin/env python

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


class FFPParseException(Exception):

    def __init__(self, e):
        super(FFPParseException, self).__init__()
        #self.msg = e



class FFPLineFormatCondition:

    def __init__(self):
        self._line_format = None

    def holds(self, logical_line, logical_line_count):
        """
        Returns True or False depending if holds the condition
        """
        raise NotImplementedException()

    def set_line_format(self, line_format):
        self.line_format = line_format
        
class BeginsWithCondition(FFPLineFormatCondition):

    def __init__(self, char):
        FFPLineFormatCondition.__init__(self)
        self._char = char
        
    def holds(self, logical_line, logical_line_count):
        try:
            if logical_line[0] == self._char:
                return True
            else:
                return False
        except:
            return False


class LineFormat:

    def __init__(self, name):
        self.name = name
        self._fields = []
        self._condition = None

    def add_field(self, field_name, column, lenght, field_type):
        field = {"name": field_name, "start_column": int(column),
            "end_column": int(lenght), "type": field_type}
        self._fields.append(field)

    def getName(self):
        return self.__name

    def getFields(self):
        return self._fields

    def parse(self, line):
        try:
            parsed_dict = {}
            for field in self._fields:
                parsed_dict[field["name"]] = FFP_TYPES[field["type"]](line[field["start_column"]:field["end_column"]])
            return parsed_dict
        except Exception, e:
            raise Exception("Error: %s" % str(e))

    def add_condition(self, condition):
        self._condition = condition



class FlatReader:

    def __init__(self, input_file, debug=False):
        self._debug = debug
        self._input_file = input_file
        self._file_stream = None
        self._ignore_failed_lines = True
        self._errors = []
        self._line_formats = []
        self._conditions = None
        self._logical_line_separator = "\n"
        self._logical_line_counter = 0
        self.open()

    def register_line_format(self, line_format):
        self._line_formats.append(line_format)

    def declare_condition(self, condition, line_format):
        condition.set_line_format(line_format)
        if not self._conditions:
            self._conditions = []
        self._conditions.append(condition)

    def open(self):
        """
        This method opens the file stream
        """
        try:
            self._file_stream = open(self._input_file, "rU")
        except IOError as e:
            raise e

    def read_line(self):
        """
        This method iterates over the file returning objects
        """
        for line in self._file_stream:
            # Skip empty lines
            if not line.strip():
                #self._logical_line_counter += 1
                continue
                
            
            line_processed = False

            # First check if there is any valid condition
            valid_conditions = 0
            for condition in self._conditions:
                if condition.holds(line, self._logical_line_counter):
                    valid_conditions += 1
                    valid_line_format = condition.line_format
            if valid_conditions == 1:
                # Only one valid condition for current line found
                line_processed = True
                yield valid_line_format.parse(line)
            else:
                # 0 or more than 1 valid conditions found for line
                # Lets try with the registered LineFormats
                for line_format in self._line_formats:
                    try:
                        yield line_format.parse(line)
                        line_processed = True
                    except Exception, e:
                        if self._debug:
                            print "[DEBUG] Error parsing line %s: %s with line_format: %s" % (self._logical_line_counter, line, line_format.name),  e
                    if line_processed:
                        break
            if not line_processed:
                # Line was not parsed by any line_format
                if not self._ignore_failed_lines:
                    raise Exception("Line was not parsed by any line_format.")
                else:
                    # Log ignored line
                    if self._debug:
                        print "[DEBUG] Line %s was not parsed by any line_format.\
                    Line content: %s" % (self._logical_line_counter, line)
            else:
                self._logical_line_counter += 1        

    def close(self):
        """
        This method closes the file stream
        """
        if self._file_stream:
            self._file_stream.close()

    def get_count(self):
        """
        This method returns the total items read
        """
        return self._logical_line_counter
