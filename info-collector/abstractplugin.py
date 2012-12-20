#!/usr/bin/env python

import sys
import datetime
import riak
import psycopg2
from config import *

class AbsPlugin:

    def execute(self):
        try:
            self.insert_data(self.get_data())
        except:
            print "Unexpected error:", sys.exc_info()[0]
            client = riak.RiakClient(port=RIAK_PORT)

            bucket = client.bucket('error_log')
            if bucket.search_enabled() is False:
                bucket.enable_search()

                now = datetime.datetime.now()
                value = bucket.new(str(now), data={'time': str(now), 'value':sys.exc_info()[0]})
                value.store()



    #must override
    def get_data(self):
        return []

    def insert_data(self, data):
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

        for item in data:

            bucket = client.bucket('source')
            if bucket.search_enabled() is False:
                bucket.enable_search()

            value = bucket.new(item['id'], data={'id': item['id'], 'value':item['source'].lower()})
            value.store()

            bucket = client.bucket('creator')
            if bucket.search_enabled() is False:
                bucket.enable_search()

            value = bucket.new(item['id'], data={'id': item['id'], 'value':item['creator'].lower()})
            value.store()


            bucket = client.bucket('time')
            if bucket.search_enabled() is False:
                bucket.enable_search()

            value = bucket.new(item['id'], data={'id': item['id'], 'value':item['time']})
            value.store()

            if len(item['location']) > 0:
                bucket = client.bucket('location')
                if bucket.search_enabled() is False:
                    bucket.enable_search()

                value = bucket.new(item['id'], data={'id': item['id'], 'value':item['location'].lower()})
                value.store()

            bucket = client.bucket('data')
            if bucket.search_enabled() is False:
                bucket.enable_search()

            value = bucket.new(item['id'], data={'id': item['id'], 'value':item['data'].lower()})
            value.store()