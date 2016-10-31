# -*- coding: utf-8 *-*
import csv
import logging
import operator
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('flatfileparser.reader')


OPERATORS = {'>': operator.gt,
             '<': operator.lt,
             '>=': operator.ge,
             '<=': operator.le,
             '==': operator.eq,
             "!=": operator.ne}


def str_to_bool(s):
    if s.upper() in ['TRUE', 'YES', 'y']:
        return True
    elif s.upper() in ['FALSE', 'NO', 'n']:
        return False
    else:
        raise ValueError


class BaseLineFormat(object):

    def __init__(self, name):
        self.name = name
        self.reader = None
        self._fields = []
        self.conditions = []

    def get_dict(self):
        return {}

    @property
    def fields(self):
        return self._fields

    def add_condition(self, condition_name):
        self.conditions.append(condition_name)


class CSVLineFormat(BaseLineFormat):

    def __init__(self, name):
        BaseLineFormat.__init__(self, name)
        self.format = "CSV"

    def get_dict(self):
        line_format = {"name": self.name, "fields": []}
        for f in self.fields:
            line_format["fields"].append(f)
        return line_format

    def add_field(self, field_key=None, field_name=None, field_parser="unicode", field_value=None):
        if field_name:
            new_name = field_name
        else:
            new_name = field_key
        self._fields.append({"field_name": new_name, "field_csv_key": field_key,
                             "field_parser": field_parser, "field_value": field_value})

    def parse(self, raw_dict):
        from pprint import pprint
        pprint(raw_dict.keys())
        parsed_dict = {}
        for field in self._fields:
            try:
                if field["field_value"]:
                    # Its a constant value field, no need to parse CSV
                    parsed_dict[field["field_name"]] = field["field_value"]
                    continue

                if field["field_csv_key"]:
                    csv_data = raw_dict[field["field_csv_key"]]
                else:
                    # This field has no CSV key defined, its a "dynamic" field
                    csv_data = raw_dict

                func = self.reader.field_parsers[field["field_parser"]]
                parsed_dict[field["field_name"]] = func(csv_data)
            except Exception, e:
                line_num = self.reader.csv_reader.line_num
                msg = "Parsing failed for field %s of type %s in line %s." % (field["field_name"],
                                                                              field["field_parser"],
                                                                              line_num)
                self.reader.skipped_lines[line_num] = msg
                logger.error(msg)
                logger.exception(e)

        return parsed_dict


class BaseReader(object):

    def __init__(self, input_file):
        self._file_stream = None
        self._input_file = input_file
        self.field_parsers = {"int": int,
                              "long": long,
                              "float": float,
                              "str": str,
                              "unicode": unicode,
                              "bool": str_to_bool}
        self.condition_callbacks = {}
        self.line_formats = []
        self.skipped_lines = {}

    def __enter__(self):
        #self.skipped_lines = {}
        self._file_stream = open(self._input_file, "rU")
        return self._file_stream

    def __exit__(self, type, value, traceback):
        self._file_stream.close()

    def export_schema(self):
        to_export = []
        for l in self.line_formats:
            to_export.append(l.get_dict())
        return to_export

    def import_schema(self, file_name):
        with open(file_name, "r") as f:
            format_list = json.loads(f.read())
            for line_format_dict in format_list:
                line_format = CSVLineFormat(line_format_dict["name"])

                for l in line_format_dict["fields"]:
                    line_format.add_field(**l)
                self.add_line_format(line_format)

    def add_line_format(self, l_format):
        l_format.reader = self
        self.line_formats.append(l_format)

    def register_condition(self, name, callback):
        self.condition_callbacks[name] = callback

    def register_field_parser(self, parser_name, parser_callback):
        self.field_parsers[parser_name] = parser_callback


class CSVReader(BaseReader):

    def __init__(self, input_file):
        BaseReader.__init__(self, input_file)
        self.csv_reader = None

    def __iter__(self):
        return self

    def __enter__(self):
        fd = BaseReader.__enter__(self)
        self.csv_reader = csv.DictReader(fd)
        return self

    def next(self):
        line = self.csv_reader.next()
        for l_format in self.line_formats:
            valid = True
            # Check if there are conditions to be met for this line format
            for cond in l_format.conditions:
                func = self.condition_callbacks[cond]
                if not func(line):
                    valid = False
                    break
            if valid:
                # The conditions (if any) for this line format are met!
                return l_format.parse(line)
            else:
                self.skipped_lines[self.csv_reader.line_num] = "Condition %s failed" % cond
                logger.debug("Skipped line %i due to failed condition." % self.csv_reader.line_num)
                continue


class FlatReader(BaseReader):

    def __init__(self, **args):
        BaseReader.__init__(**args)
        self._ignore_failed_lines = True
        self._errors = []
        self._logical_line_separator = "\n"
        self._logical_line_counter = 0

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

    def get_count(self):
        """
        This method returns the total items read
        """
        return self._logical_line_counter


class FixedLineFormat(BaseLineFormat):

    def __init__(self, name):
        BaseLineFormat.__init__(self, name)
        self.format = "Fixed"

    def add_field(self, field_name, column, lenght, field_type):
        field = {"name": field_name, "start_column": int(column),
            "end_column": int(lenght), "type": field_type}
        self._fields.append(field)

    def parse(self, line):
        try:
            parsed_dict = {}
            for field in self._fields:
                func = self.reader.field_parsers[field["field_parser"]]
                parsed_dict[field["name"]] = func(line[field["start_column"]:field["end_column"]])
            return parsed_dict
        except Exception, e:
            raise Exception("Error: %s" % str(e))
