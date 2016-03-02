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
        if not input_file_location.endswith('.pas'):
            raise IOError(u'File does not have a valid extension, found {0:s}, required: {1:s}'
                          .format(input_file_location[-4:]),
                          PASCAL_FILE_EXT)
        elif not os.path.isfile(os.path.realpath(input_file_location)):
            raise IOError('%s is not a file.' % input_file_location)

        self.input_file_location = input_file_location
        self.output_file_location = output_location
        self.FILE = open(self.input_file_location)

        self.contents = self.FILE.read()

    def io_object(self):
        return self.FILE

    def __unicode__(self):
        return self.input_file_location

    def __del__(self):
        self.FILE.close()
