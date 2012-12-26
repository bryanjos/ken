#!/usr/bin/env python

import sys
import datetime
import riak
import psycopg2
import redis
from config import *
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import traceback
from jobops import process_job_since
import time
from processors import simple

class AbsPlugin:

    def __call__(self, name, jobs):
        print 'execute: %s' % name
        return self.execute(name, jobs)

    def execute(self, name, jobs):
        try:
            for job in jobs:
                data = self.get_data(job)
                self._insert(data)
                self._tokenize(data)
                self._reduce(job)
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'
            client = riak.RiakClient(port=RIAK_PORT)

            bucket = client.bucket('error_log')
            if bucket.search_enabled() is False:
                bucket.enable_search()

                now = datetime.datetime.now()
                value = bucket.new(str(now), data={'time': str(now), 'error':sys.exc_info()[0], 'stacktrace': traceback.print_exc()})
                value.store()
        print 'end execute: %s' % name
        return name



    def get_data(self, job):
        raise NotImplementedError()


    def _insert(self, data):
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(POSTGRES_DB_STRING)
            cur = conn.cursor()

            for item in data:

                cur.execute("""INSERT INTO information(source,source_id,creator,time,location,lat,lon,data,geom)
                values( %(source)s, %(id)s, %(creator)s, %(time)s, %(location)s, %(lat)s, %(lon)s, %(data)s, ST_GeomFromText(%(geom)s,4326))
                """, item.to_json())

            conn.commit()
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


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
                            word = word.encode("utf8","ignore").lower()
                            data = bucket.get(word).get_data()
                            if data is None:
                                data = {'word':word, 'ids': [item.id]}
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
        client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
        bucket = client.bucket('job_data')

        if bucket.search_enabled() is False:
            bucket.enable_search()

        job_data = bucket.get(job.slug).get_data()
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

        job_data = {'since': int(time.time()), 'information': info_json}

        value = bucket.new(job.slug, data=job_data)
        value.store()







