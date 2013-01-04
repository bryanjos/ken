#!/usr/bin/env python

from plugins import __all__
import multiprocessing as mp
import time
import redis
from pymongo import *
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

    def do_callback(self, data):
        self.__job_results[data[0]].extend(data[1])


    def do(self):
        from jobops import get_jobs
        jobs = get_jobs()
        pool = mp.Pool()

        for job in jobs:
            self.__job_results[job.slug] = []

            for name in sorted(__all__):
                plugin = self.load_plugin(name)
                print 'Starting polling for %s' % name
                pool.apply_async(plugin, args = (job,), callback=self.do_callback)
            pool.close()
            pool.join()

            self.update_time(job)
            sorted_info = sorted(self.__job_results[job.slug], key=lambda info: info.time, reverse=True)

            #TODO: add NLP to make results more relevant

            red = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            red.publish(job.slug, sorted_info)


    def update_time(self, job):
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['job_data']

        job_data = {'slug': job.slug, 'since': int(time.time()) }
        jobDataFromDB = collection.find_one({"slug": job.slug})

        if jobDataFromDB is None:
            collection.insert(job_data)
        else:
            collection.update({"slug": job.slug}, job_data)


def list_plugins():
    return sorted(__all__)