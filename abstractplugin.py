#!/usr/bin/env python

import sys
import datetime
from pymongo import *
from config import *
import traceback
import time

class AbsPlugin:
    def __call__(self, name, jobs):
        print 'execute: %s' % name
        return self.execute(name, jobs)

    def execute(self, name, job):
        data = []
        try:
            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['job_data']

            job_data = collection.find_one({"slug": job.slug})

            if job_data is None:
                since = job.time
            else:
                since = job_data['since']

            data = self.get_data(job, since)

            self.update_time(job)
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'
            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['errors']

            now = datetime.datetime.now()
            collection.insert({'time': str(now), 'error': sys.exc_info()[0], 'stacktrace': traceback.print_exc()})

        print 'end execute: %s' % name
        return name, data


    def get_data(self, job, since):
        raise NotImplementedError()


    def update_time(self, job):
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['job_data']

        job_data = {'slug': job.slug, 'since': int(time.time()) }

        if collection.find_one({"slug": job.slug}) is None:
            collection.insert(job_data)
        else:
            jobDataFromDB = collection.find_one({"slug": job.slug})
            job_data['_id'] = jobDataFromDB['_id']
            collection.update({"slug": job.slug}, job_data)







