#!/usr/bin/env python

import sys
import datetime
import riak
import psycopg2
from config import *
from jobops import *
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import traceback

class AbsPlugin:

    def execute(self, task_queue, name):
        try:
            jobs = get_jobs()
            for job in jobs:
                self.insert_data(self.get_data(job))
        except:
            print '>>> traceback <<<'
            traceback.print_exc()
            print '>>> end of traceback <<<'
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

        for item in data:

            cur.execute("""INSERT INTO information(source,source_id,creator,time,location,lat,lon,data,geom)
            values( %(source)s, %(id)s, %(creator)s, %(time)s, %(location)s, %(lat)s, %(lon)s, %(data)s, ST_GeomFromText(%(geom)s,4326))
            """, item.to_json())

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