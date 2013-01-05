#!/usr/bin/env python

import sys
import datetime
from pymongo import *
from config import *
import traceback

class AbsPlugin:
    def __call__(self, job, extra_data=None):
        self.set_extra_data(extra_data)
        return self.execute(job)

    def execute(self, job):
        data = []
        try:
            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['job_metadata']

            job_data = collection.find_one({"slug": job.slug})

            if job_data is None:
                since = job.time
            else:
                since = job_data['since']

            data = self.get_data(job, since)
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'
            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['errors']

            now = datetime.datetime.now()
            collection.insert({'time': str(now), 'error': sys.exc_info()[0], 'stacktrace': traceback.print_exc()})

        return (job.slug, data)


    def get_data(self, job, since):
        raise NotImplementedError()

    def set_extra_data(self, data):
        pass







