#!/usr/bin/env python

import re

from sed.engine import (
    StreamEditor,
    call_main,
    ACCEPT, REPEAT, NEXT,
    ANY
)


CREATE_TABLE = re.compile(r'''
    ^
    CREATE\sTABLE
    .*
    $
''', re.VERBOSE)

GO = re.compile(r'''
    ^
    GO
    $
''', re.VERBOSE)

class StreamEditorEDWTables(StreamEditor):
    table = [
        [[CREATE_TABLE, NEXT], ],
        [[GO, ACCEPT], [ANY, REPEAT]],
    ]

    def apply_match(self, i, dict_matches):
        counter_regex = re.compile(r'''
            ^
            \s*
            \[counter\]
            \s+
            \[int\]
            \s+
            (?P<identity>IDENTITY\(.+?\))
            .*
            $
        ''', re.VERBOSE)
        start, end = dict_matches["start"], dict_matches["end"]
        if not (end is None):
            table_name = self.lines[start].split('.')[1].replace("[", "").replace("]", "").replace("(", "")

            # Replace `[counter] IDENTITY...` with `[counter]`
            for (counter_i, counter_d) in self.find_line(counter_regex, self.lines[start:end]):
                matching = counter_d["identity"]
                src = start + counter_i
                self.lines[src] = self.lines[src].replace(matching, "")
            
            # Change the schema name to DA
            self.lines[start] = self.lines[start].replace("[dbo]", "[DA]")

            # Change name of clustered index to new naming
            old_constraint_name = re.compile(r""".*CONSTRAINT (?P<constraint_name>\[PK_.*?\])""")
            new_constraint_name = "[PK_{0}_{1}_{2}]".format("DA", "billing", table_name)
            for (constraint_i, constraint_d) in self.find_line(old_constraint_name, self.lines[start:end]):
                matching = constraint_d["constraint_name"]
                src = start + constraint_i
                self.lines[src] = self.lines[src].replace(matching, new_constraint_name)

            # Change segment name
            column_names = ["counter"]
            underscore_column_names = ",".join(column_names)
            comma_column_names = ",".join(column_names)
            new_segment_name = "[PS_{0}_DA]([{1}])".format(underscore_column_names, comma_column_names)
            old_segment_name = re.compile(r"""^.*\s+ON\s+(?P<segment>\[PRIMARY\])""")
            for (segment_i, segment_d) in self.find_line(old_segment_name, self.lines[start:end]):
                matching = segment_d["segment"]
                src = start + segment_i
                self.lines[src] = self.lines[src].replace(matching, new_segment_name)

            # Trim off unrelated stuff from file
            file_end = len(self.lines)
            self.delete_range((end + 1, file_end - 1))
            self.delete_range((0, start - 1))

if __name__ == '__main__':
    call_main(StreamEditorEDWTables)
