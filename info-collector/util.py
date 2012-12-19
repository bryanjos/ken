import riak
import psycopg2
from config import RIAK_HOST, RIAK_PORT, POSTGRES_DB_STRING

def get_job(job_name):
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    return bucket.get(job_name).get_data()

def save_job(job):
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    value = bucket.new(job['name'], data=job)
    value.store()

def get_jobs():
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    return bucket.get_keys()


def get_keys(job_name):
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    job = bucket.get(job_name).get_data()

    if job is None:
        return None

    ids = set()
    coordinates = job['coordinates']
    distance = job['distance']
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


    return ids, coordinates, distance, time


def get_data(ids, coordinates, distance, time):
    conn = psycopg2.connect(POSTGRES_DB_STRING)
    cur = conn.cursor()
    data = []

    if coordinates[0] > 0 and coordinates[1] > 0:
        cur.execute("""
        select source,source_id,creator,time,location,lat,lon,data from information where source_id in (%s) and time >= $s and ST_DWithin(geom, 'POINT(%s $s)', %s);
        """ % (",".join(ids), time, coordinates[0], coordinates[1], distance) )
        results = cur.fetchall()
    else:
        cur.execute("""
        select source,source_id,creator,time,location,lat,lon,data from information where source_id in (%s) and time >= $s
        """ % (",".join(ids), time) )
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