#!/usr/bin/env python

import sys
import datetime
import riak
import redis
from pymongo import *
from config import *
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import traceback
from jobops import process_job_since
import time
from processors import simple
import threading

class AbsPlugin:
    def __call__(self, name, jobs):
        print 'execute: %s' % name
        return self.execute(name, jobs)

    def execute(self, name, jobs):
        try:
            for job in jobs:
                connection = Connection(MONGODB_HOST, MONGODB_PORT)
                db = connection['ken']
                collection = db['job_data']

                job_data = collection.find_one({"slug": job.slug})

                if job_data is None:
                    since = job.time
                else:
                    since = job_data['since']

                data = self.get_data(job, since)
                i = threading.Thread(target=self._insert, args=(data,))
                t = threading.Thread(target=self._tokenize, args=(data,))

                i.start()
                t.start()
                i.join()
                t.join()

                self._reduce(job)
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
        return name


    def get_data(self, job, since):
        raise NotImplementedError()


    def _insert(self, data):
        try:
            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['information']

            for item in data:
                if collection.find_one({"source_id": item.id}) is None:
                    collection.insert(item.to_json())
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'


    def _tokenize(self, data):
        client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
        bucket = client.bucket('words')
        if bucket.search_enabled() is False:
            bucket.enable_search()

        for item in data:
            for sentence in sent_tokenize(item.data):
                for word in word_tokenize(sentence):
                    if word not in stopwords.words('english') and word not in STOP_WORDS:
                        try:
                            word = word.encode("utf8", "ignore").lower()
                            data = bucket.get(word).get_data()
                            if data is None:
                                data = {'word': word, 'ids': [item.id]}
                            else:
                                data['ids'].append(item.id)
                                data['ids'] = list(set(data['ids']))

                            value = bucket.new(word, data=data)
                            value.store()
                        except:
                            print '>>> traceback <<<'
                            traceback.print_exc()
                            print '>>> end of traceback <<<'


    def _reduce(self, job):
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['job_data']

        job_data = collection.find_one({"slug": job.slug})

        if job_data is None:
            info_json = []
            since = job.time
        else:
            info_json = job_data['information']
            since = job_data['since']

        info = process_job_since(simple.SimpleProcessor(), job, since)

        new_info = []
        for i in reversed(info):
            i_json = i.to_json()
            new_info.append(i_json)

        info_json.extend(new_info)

        red = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        red.publish(job.slug, new_info)

        job_data = {'slug': job.slug, 'since': int(time.time()), 'information': info_json}

        if collection.find_one({"slug": job.slug}) is None:
            collection.insert(job_data)
        else:
            jobDataFromDB = collection.find_one({"slug": job.slug})
            job_data['_id'] = jobDataFromDB['_id']
            collection.update({"slug": job.slug}, job_data)







