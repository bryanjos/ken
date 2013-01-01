from abstractprocessor import AbsProcessor
import riak
from pymongo import *
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
            coordinates = [job.lat, job.lon]
        else:
            coordinates = None

        distance = job.distance
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
            'ids': list(ids),
            'time': time,
            'coordinates': coordinates if coordinates else None,
            'distance': distance
        }

    def get_data(self, parameters, page_size, page):
        data = []
        if len(parameters['ids']) > 0:

            parameters['limit'] = page_size
            parameters['offset'] = (page-1) * page_size

            connection = Connection(MONGODB_HOST, MONGODB_PORT)
            db = connection['ken']
            collection = db['information']

            results = collection.find(
                {
                    "time": {"$gt": parameters['time']},
                    "id": {"$in": parameters['ids']},
                    "coordinates":
                         { "$within":
                              { "$center":
                                    [ parameters['coordinates'] , parameters['distance'] / 3963.192 ]
                              }
                         }


                }
            ).skip(parameters['offset']).limit(parameters['limit']).sort("time", DESCENDING)


            for info in results:
                data.append(
                    Information(
                        info['source'],
                        info['id'],
                        info['creator'],
                        info['time'],
                        info['data'],
                        info['location'],
                        info['lat'],
                        info['lon']
                    )
                )


            results = collection.find(
                {
                    "time": {"$gt": parameters['time']},
                    "id": {"$in": parameters['ids']},
                    "lat": 0
                }
            ).skip(parameters['offset']).limit(parameters['limit']).sort("time", DESCENDING)


            for info in results:
                data.append(
                    Information(
                        info['source'],
                        info['id'],
                        info['creator'],
                        info['time'],
                        info['data'],
                        info['location'],
                        info['lat'],
                        info['lon']
                    )
                )

            return data


    def get_data_since(self, parameters, since):

        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = connection['ken']
        collection = db['information']

        results = collection.find(
            {
                "time": {"$gt": since},
                "id": {"$in": parameters['ids']},
                "coordinates":
                    { "$within":
                          { "$center":
                                [ parameters['coordinates'] , parameters['distance'] / 3963.192 ]
                          }
                    }
            }
        )


        data = []
        for info in results:
            data.append(
                Information(
                    info['source'],
                    info['id'],
                    info['creator'],
                    info['time'],
                    info['data'],
                    info['location'],
                    info['lat'],
                    info['lon']
                )
            )


        results = collection.find(
            {
                "time": {"$gt": since},
                "id": {"$in": parameters['ids']},
                "lat": 0
            }
        )

        for info in results:
            data.append(
                Information(
                    info['source'],
                    info['id'],
                    info['creator'],
                    info['time'],
                    info['data'],
                    info['location'],
                    info['lat'],
                    info['lon']
                )
            )

        return data