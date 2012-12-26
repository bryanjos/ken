#!/usr/bin/env python

from plugins import __all__
import multiprocessing as mp
import time
from config import POLLING_INTERVAL


class PluginManager:
    """ Manages available plugins """
    def __init__(self):
        """ Initialize the plugin list """
        self.__plugins = {}
        self.__taskQueue = mp.Queue(maxsize=len(list_plugins()))

        for name in sorted(__all__):
            self.__taskQueue.put(name)

    def load_plugin(self, plugin_name):
        """ Loads a single plugin given its name """
        if not plugin_name in __all__:
            raise KeyError("Plugin " + plugin_name + " not found")
        try:
            plugin = self.__plugins[plugin_name]
        except KeyError:
            # Load the plugin only if not loaded yet
            module = __import__("plugins." + plugin_name, fromlist=["plugins"])
            plugin = module.load()
            self.__plugins[plugin_name] = plugin
        return plugin

    #Intent is for when interval is hit, then
    #poll for plugins that have finished and don't run those that aren't yet
    def call(self):
        while True:
            print 'Polling'
            self.do()
            time.sleep(POLLING_INTERVAL)

    def help_all(self):
        """ Prints the help for all registered plugins """
        for name in list_plugins():
            print name

    def do_callback(self, name):
        print 'Done %s, putting it back in the queue' % name
        self.__taskQueue.put(name)

    def do(self):
        from jobops import get_jobs
        jobs = get_jobs()
        pool = mp.Pool()
        while self.__taskQueue.empty() is False:
            name = self.__taskQueue.get()
            plugin = self.load_plugin(name)
            print 'Starting polling for %s' % name
            pool.apply_async(plugin, args = (name, jobs), callback=self.do_callback)




def list_plugins():
    return sorted(__all__)