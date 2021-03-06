from cnf import CNF
import re
import os

class SatWriter(object):
    def write_output(self, output_path, output):
        with open(output_path, 'w') as f:
            f.write(output)

class SatReader(object):
    COMMENT_LINE_PATTERN='c.*'
    INFO_LINE_PATTERN='p\s*cnf\s*(\d*)\s*(\d*)'
        
    def read_input(self, input_path):
        print("Read input from file {}".format(input_path))
        comment_line_regex = re.compile(self.COMMENT_LINE_PATTERN)
        info_line_regex = re.compile(self.INFO_LINE_PATTERN)
        formula = []
        num_props, num_clauses = 0, 0

        with open(input_path, 'r') as input_file:
            for line in input_file.readlines():
                line = line.strip()
                if line == "%" or not line:
                    continue
                if not comment_line_regex.match(line):
                    infos = info_line_regex.match(line)
                    if infos:
                        num_props = int(infos.group(1))
                        num_clauses = int(infos.group(2))
                    else:
                        raw_props = line.rstrip('\n').split()
                        props = []
                        for prop in raw_props:
                            prop = int(prop)
                            if prop != 0:
                                props.append(prop)
                        formula.append(props)
        return CNF(num_props, num_clauses, formula)
