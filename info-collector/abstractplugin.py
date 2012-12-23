#!/usr/bin/env python

import sys
import datetime
import riak
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
from config import *
from jobops import *
from nltk.tokenize import word_tokenize, sent_tokenize

class AbsPlugin:

    def execute(self, task_queue, name):
        try:
            jobs = get_jobs()
            for job in jobs:
                self.insert_data(self.get_data(job))
        except:
            print "Unexpected error:", sys.exc_info()[0]
            client = riak.RiakClient(port=RIAK_PORT)

            bucket = client.bucket('error_log')
            if bucket.search_enabled() is False:
                bucket.enable_search()

                now = datetime.datetime.now()
                value = bucket.new(str(now), data={'time': str(now), 'value':sys.exc_info()[0]})
                value.store()

        task_queue.put(name)



    def get_data(self, job):
        raise NotImplementedError()

    def insert_data(self,data):
        conn = psycopg2.connect(POSTGRES_DB_STRING)
        cur = conn.cursor()
        cur.executemany("""INSERT INTO information(source,source_id,creator,time,location,lat,lon,data,geom)
        select %(source)s, %(id)s, %(creator)s, %(time)s, %(location)s, %(lat)s, %(lon)s, %(data)s, ST_GeomFromText('POINT(%(lat)s %(lon)s)',4326)
         where not exists (select %(id)s from information)""",
        data)
        conn.commit()
        cur.close()
        conn.close()

        client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
        bucket = client.bucket('words')
        if bucket.search_enabled() is False:
            bucket.enable_search()

        for item in data:

            for sentence in sent_tokenize(item.data):
                for word in word_tokenize(sentence):
                    data = bucket.get(word).get_data()
                    if data is None:
                        data = {'id': item['id'], 'word':word, 'ids': [item['id']]}
                    else:
                        data['ids'].append(item['id'])

                    value = bucket.new(word, data=data)
                    value.store()