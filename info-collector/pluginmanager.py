#!/usr/bin/env python

from plugins import __all__
from multiprocessing import Process


class PluginManager:
    """ Manages available plugins """
    def __init__(self):
        """ Initialize the plugin list """
        self.__plugins = {}

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

    def call(self):
        for name in sorted(__all__):
            """ Calls the execute function on the given plugin """
            try:
                plugin = self.load_plugin(name)
                p = Process(target=plugin.execute)
                p.start()
                p.join()
            except KeyError:
                self.help_all()

    def help_all(self):
        """ Prints the help for all registered plugins """
        for name in list_plugins():
            print name


def list_plugins():
    return sorted(__all__)