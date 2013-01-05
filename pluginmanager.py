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
        self.__processor = None

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

    def load_processor(self):
        if self.__processor is None:
            module = __import__("processors." + PROCESSOR_NAME, fromlist=["processors"])
            processor = module.load()
            self.__processor = processor
        else:
            processor = self.__processor

        return processor


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
                if 'rss' in name:
                    for feed in RSS_FEEDS:
                        pool.apply_async(plugin, args = (job,feed,), callback=self.do_callback)
                else:
                    pool.apply_async(plugin, args = (job,), callback=self.do_callback)
            pool.close()
            pool.join()

            self.process_results(job, self.__job_results[job.slug])


    def process_results(self, job, job_results):
        self.update_time(job)
        sorted_info = sorted(job_results, key=lambda info: info.time, reverse=True)

        #TODO: add NLP to make results more relevant
        processed_data = self.load_processor().process(job, sorted_info)

        red = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        red.publish(job.slug, processed_data)

        self.save_data(processed_data)


    def update_time(self, job):
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['job_metadata']

        job_data = {'slug': job.slug, 'since': int(time.time()) }
        jobDataFromDB = collection.find_one({"slug": job.slug})

        if jobDataFromDB is None:
            collection.insert(job_data)
        else:
            collection.update({"slug": job.slug}, job_data)

    def save_data(self, data):
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['job_info']

        for item in data:
            itemFromDB = collection.find_one({"id": item.id})
            if itemFromDB is None:
                collection.insert(item.__dict__)



def list_plugins():
    return sorted(__all__)