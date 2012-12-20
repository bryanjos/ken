from abstractprocessor import AbsProcessor
import riak
import psycopg2
from config import *

class SimpleProcessor(AbsProcessor):
    def __init__(self):
        pass

    def get_keys(self, job):
        client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)

        if job is None:
            return None

        ids = set()
        if job['lat'] and job['lon']:
            coordinates = [job['lat'], job['lon']]
        else:
            coordinates = None

        distance = job['distance'] * 1609.34 #convert to meters
        time = job['time']

        for source in job['sources']:
            search_query = client.search('source', source)

            for result in search_query.run():
                item = result.get()
                item_data = item.get_data()
                ids.add(item_data['id'])


        for location in job['location']:
            search_query = client.search('location', location)

            for result in search_query.run():
                item = result.get()
                item_data = item.get_data()
                ids.add(item_data['id'])


        for tag in job['tags']:
            search_query = client.search('creator', '%s*' % tag)

            for result in search_query.run():
                item = result.get()
                item_data = item.get_data()
                ids.add(item_data['id'])

            search_query = client.search('data', '%s*' % tag)

            for result in search_query.run():
                item = result.get()
                item_data = item.get_data()
                ids.add(item_data['id'])


        return {
            'ids': ",".join(ids),
            'time': time,
            'coordinates': " ".join(coordinates),
            'distance': distance
        }

    def get_data(self, parameters):
        conn = psycopg2.connect(POSTGRES_DB_STRING)
        cur = conn.cursor()
        data = []

        if parameters['coordinates']:
            cur.execute("""
            select source,source_id,creator,time,location,lat,lon,data
            from information
            where source_id in (%(ids)s) and time >= $(time)s and
            (ST_DWithin(geom, 'POINT(%(coordinates)s)', %(distance)s) or lat = 0.0 and lon = 0.0);
            """ % parameters )
            results = cur.fetchall()
        else:
            cur.execute("""
            select source,source_id,creator,time,location,lat,lon,data
            from information
            where source_id in (%(ids)s) and time >= $(time)s
            """ % parameters)
            results = cur.fetchall()


        for result in results:
            data.append(
                {
                    'source': result[0],
                    'source_id': result[1],
                    'creator': result[2],
                    'time': result[3],
                    'location': result[4],
                    'lat': result[5],
                    'lon': result[6],
                    'data': result[7]
                }
            )

        conn.commit()
        cur.close()
        conn.close()

        return data