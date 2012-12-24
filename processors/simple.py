from abstractprocessor import AbsProcessor
import riak
import psycopg2
from config import *
from information import Information

class SimpleProcessor(AbsProcessor):
    def __init__(self):
        pass

    def get_keys(self, job):
        client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)

        if job is None:
            return None

        ids = set()
        if job.lat and job.lon:
            coordinates = [str(job.lat), str(job.lon)]
        else:
            coordinates = None

        distance = job.distance * 1609.34 #convert to meters
        time = job.time

        if job.tags:
            for tag in job.tags:

                search_query = client.search('words', 'word:%s*' % tag)

                for result in search_query.run():
                    item = result.get()
                    item_data = item.get_data()
                    ids.update(item_data['ids'])

        new_ids = []
        for id in ids:
            new_ids.append("'%s'" % id)

        return {
            'ids': ",".join(new_ids),
            'time': time,
            'coordinates': " ".join(coordinates) if coordinates else None,
            'distance': distance
        }

    def get_data(self, parameters, page_size, page):
        data = []
        if len(parameters['ids'].strip()) > 0:
            conn = psycopg2.connect(POSTGRES_DB_STRING)
            cur = conn.cursor()
            parameters['limit'] = str(page_size)
            parameters['offset'] = str((page-1) * page_size)


            cur.execute("""
            select source,source_id,creator,time,location,lat,lon,data
            from information
            where source_id in (%(ids)s) and time >= %(time)s and
            (ST_DWithin(geom, ST_GeomFromText('POINT(%(coordinates)s)',4326), %(distance)s) or lat = 0.0 and lon = 0.0)
            order by time desc limit %(limit)s offset %(offset)s;""" % parameters )
            results = cur.fetchall()


            for result in results:
                data.append(
                    Information(
                        result[0],
                        result[1],
                        result[2],
                        result[3],
                        result[7],
                        result[4],
                        result[5],
                        result[6]
                    )
                )

            conn.commit()
            cur.close()
            conn.close()

        return data


    def get_data_since(self, parameters, since):
        conn = psycopg2.connect(POSTGRES_DB_STRING)
        cur = conn.cursor()
        data = []
        parameters['since'] = since

        cur.execute("""
        select source,source_id,creator,time,location,lat,lon,data
        from information
        where source_id in (%(ids)s) and time >= %(since)s and
        (ST_DWithin(geom, ST_GeomFromText('POINT(%(coordinates)s)',4326), %(distance)s) or lat = 0.0 and lon = 0.0)
        order by time desc""" % parameters )
        results = cur.fetchall()


        for result in results:
            data.append(
                Information(
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[7],
                    result[4],
                    result[5],
                    result[6]
                )
            )

        conn.commit()
        cur.close()
        conn.close()

        return data