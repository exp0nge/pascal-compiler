# coding=utf-8
"""
I/O for Pascal files
"""

import os

PASCAL_FILE_EXT = '.pas'


class PascalFile(object):
    def __init__(self, input_file_location, output_location):
        """

        :param input_file_location: str
        :param output_location: str
        :return:
        """

        self.input_file_location = os.path.join('sample_pascal_code', input_file_location)
        self.output_file_location = output_location
        self.FILE = open(self.input_file_location)

        self.contents = self.FILE.read()

    def io_object(self):
        return self.FILE

    def __unicode__(self):
        return self.input_file_location

    def __del__(self):
        self.FILE.close()
