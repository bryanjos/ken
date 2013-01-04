#!/usr/bin/env python

from plugins import __all__
import multiprocessing as mp
import time
import redis
from config import *


class PluginManager:
    """ Manages available plugins """
    def __init__(self):
        """ Initialize the plugin list """
        self.__plugins = {}
        self.__job_results = {}

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

    def update_queue(self, q):
        for name in sorted(__all__):
            q.put(name)

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

    def do_callback(self,job_slug, data):
        self.__job_results[job_slug].extend(data)


    def do(self):
        from jobops import get_jobs
        jobs = get_jobs()
        pool = mp.Pool()

        for job in jobs:
            self.__job_results[job.slug] = []
            q = mp.Queue(maxsize=len(list_plugins()))
            self.update_queue(q)

            while q.empty() is False:
                name = q.get()
                plugin = self.load_plugin(name)
                print 'Starting polling for %s' % name
                pool.apply_async(plugin, args = (name, job), callback=self.do_callback)
            pool.close()
            pool.join()

            sorted_info = sorted(self.__job_results[job.slug], key=lambda info: info.time, reverse=True)

            #TODO: add NLP to make results more relevant

            red = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            red.publish(job.slug, sorted_info)


def list_plugins():
    return sorted(__all__)