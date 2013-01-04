#!/usr/bin/env python

from pluginmanager import PluginManager
import sys
from pymongo import *
from config import *


class Collector:
    """ Main command line interface """
    def __init__(self):
        """ Initialize the plugin manager """
        self.__pluginmanager = PluginManager()

    def parse_input(self):
        """ Validates user input and delegates to the plugin manager """
        if len(sys.argv) > 1:
            print "The following plugins are available:\n"
            self.__pluginmanager.help_all()
        else:
            # Call the command in the given plugin with the
            # remaining arguments
            return self.__pluginmanager.call()


if __name__ == "__main__":
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['ken']

    collection = db['job_data']
    collection.ensure_index([('slug', ASCENDING)])

    collection = db['job']
    collection.ensure_index([('slug', ASCENDING)])

    collector = Collector()
    collector.parse_input()